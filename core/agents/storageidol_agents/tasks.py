"""
Celery task definitions — entry points from the API.

All LangGraph invocations happen inside Celery tasks so they run
asynchronously off the webhook request path.

Tasks:
  - handle_whatsapp_message  — invoked per WhatsApp inbound message
  - handle_voice_turn        — invoked per voice turn (via LiveKit bridge)
  - run_debt_stage           — invoked by the D+N scheduler for each debt case
  - evaluate_conversation    — post-conversation LLM judge evaluation
  - ingest_feedback_csv      — read feedback.csv and store rows in DB
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import yaml
from celery import Celery
from python_ulid import ULID

from .graphs.registry import load_graph
from .state import AgentState, Channel, ClientConfig

logger = logging.getLogger(__name__)

# ── Celery app ────────────────────────────────────────────────────────────────
app = Celery(
    "storageidol",
    broker=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
)
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


# ── Config loader (cached per worker process) ─────────────────────────────────
_config_cache: dict[str, ClientConfig] = {}


def _load_config(client_id: str) -> ClientConfig:
    if client_id not in _config_cache:
        config_path = f"/app/clients/{client_id}/config.yaml"
        with open(config_path) as f:
            raw = yaml.safe_load(f)
        _config_cache[client_id] = ClientConfig.from_dict(raw)
    return _config_cache[client_id]


# ── WhatsApp inbound message ──────────────────────────────────────────────────
@app.task(name="handle_whatsapp_message", bind=True, max_retries=3)
def handle_whatsapp_message(
    self,
    client_id: str,
    conversation_id: str,
    contact_phone: str,
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Invoke the client's LangGraph for an inbound WhatsApp message.

    Returns a dict with `reply` (the text to send back) and updated state fields.
    """
    try:
        return asyncio.run(_run_whatsapp(client_id, conversation_id, contact_phone, messages))
    except Exception as exc:
        logger.exception("WhatsApp task failed for client=%s conv=%s", client_id, conversation_id)
        raise self.retry(exc=exc, countdown=2**self.request.retries)


async def _run_whatsapp(
    client_id: str,
    conversation_id: str,
    contact_phone: str,
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    config = _load_config(client_id)
    graph = load_graph(client_id, config)

    # Resolve or create contact in DB
    contact_id = await _get_or_create_contact(client_id, contact_phone)

    state = AgentState(
        client_id=client_id,
        channel=Channel.WHATSAPP,
        conversation_id=conversation_id,
        contact_id=contact_id,
        contact_phone=contact_phone,
        messages=messages,
        user_message=messages[-1]["content"] if messages else "",
        langfuse_trace_id=conversation_id,
    )

    # LangGraph requires a dict; we use state.model_dump()
    result = await graph.ainvoke(state.model_dump())

    reply = result.get("reply", "")
    if not reply:
        reply = "Lo siento, ha ocurrido un error. Por favor, inténtelo de nuevo."

    # Send reply via WhatsApp (the API layer handles this via the return value)
    return {
        "reply": reply,
        "conversation_id": conversation_id,
        "should_escalate": result.get("should_escalate", False),
        "detected_intent": result.get("detected_intent"),
    }


# ── Post-conversation judge ───────────────────────────────────────────────────
@app.task(name="evaluate_conversation", bind=True)
def evaluate_conversation_task(
    self,
    client_id: str,
    conversation_id: str,
) -> dict[str, Any]:
    """Run the LLM judge on a completed conversation and store the score."""
    try:
        config = _load_config(client_id)
        result = asyncio.run(
            _run_judge(client_id, conversation_id, config.brand_name)
        )
        return result or {}
    except Exception as exc:
        logger.exception("Judge task failed for conv=%s", conversation_id)
        raise self.retry(exc=exc, countdown=30)


async def _run_judge(
    client_id: str, conversation_id: str, brand_name: str
) -> dict | None:
    from .judge import evaluate_conversation
    score = await evaluate_conversation(
        conversation_id=conversation_id,
        client_id=client_id,
        brand_name=brand_name,
    )
    if score:
        return {"score": score.score, "success": score.success, "reason": score.reason}
    return None


# ── D+N debt scheduler ────────────────────────────────────────────────────────
@app.task(name="run_debt_stage")
def run_debt_stage(client_id: str, debt_case_id: str, stage: str) -> None:
    """
    Send a staged debt collection message (WhatsApp or voice) for a debt case.

    Called by the Celery Beat scheduler when next_action_at is due.
    """
    asyncio.run(_send_debt_message(client_id, debt_case_id, stage))


async def _send_debt_message(
    client_id: str, debt_case_id: str, stage: str
) -> None:
    from storageidol_whatsapp import WhatsAppClient, TemplateComponent
    import os

    config = _load_config(client_id)

    # Load debt stage config
    stage_config = next(
        (s for s in _get_debt_stages(config) if s["day"] == _stage_day(stage)),
        None,
    )
    if not stage_config:
        logger.warning("No debt stage config for stage=%s client=%s", stage, client_id)
        return

    # Load debt case from DB
    async with __import__("storageidol_db").get_session(client_id) as session:
        from sqlalchemy import select
        from storageidol_db import DebtCase, Contact

        result = await session.execute(
            select(DebtCase).where(
                DebtCase.id == debt_case_id,
                DebtCase.client_id == client_id,
            )
        )
        case = result.scalar_one_or_none()
        if not case:
            logger.warning("Debt case %s not found", debt_case_id)
            return

        contact_result = await session.execute(
            select(Contact).where(Contact.id == case.contact_id)
        )
        contact = contact_result.scalar_one_or_none()

    if not contact or not contact.phone:
        logger.warning("No contact phone for debt case %s", debt_case_id)
        return

    # Send via WhatsApp if in channels
    channels = stage_config.get("channel", ["whatsapp"])
    if "whatsapp" in channels:
        wa_client = WhatsAppClient(
            phone_number_id=os.environ["WHATSAPP_PHONE_NUMBER_ID"],
            access_token=os.environ["WHATSAPP_ACCESS_TOKEN"],
        )
        template_name = stage_config["template"]
        components = [
            TemplateComponent(
                type="body",
                parameters=[
                    {"type": "text", "text": contact.name or "cliente"},
                    {"type": "text", "text": str(case.amount)},
                ],
            )
        ]
        await wa_client.send_template(
            to=contact.phone,
            name=template_name,
            language=config.language,
            components=components,
        )
        logger.info("Sent debt template %s to %s (stage=%s)", template_name, contact.phone, stage)

    # Voice call for D+20 and D+30
    if "voice" in channels and config.voice:
        # Trigger an outbound LiveKit call (handled by the voice service)
        # The voice service picks up the `OUTBOUND_CALL` event from Redis
        import json
        from redis.asyncio import Redis
        redis = Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
        await redis.publish("voice:outbound", json.dumps({
            "client_id": client_id,
            "phone": contact.phone,
            "debt_case_id": debt_case_id,
            "stage": stage,
        }))
        await redis.aclose()


def _get_debt_stages(config: ClientConfig) -> list[dict]:
    # Stages come from the raw YAML — load them each time to avoid stale cache
    config_path = f"/app/clients/{config.client_id}/config.yaml"
    with open(config_path) as f:
        raw = yaml.safe_load(f)
    return raw.get("debt", {}).get("stages", [])


def _stage_day(stage: str) -> int:
    return {"d3": 3, "d10": 10, "d20": 20, "d30": 30}.get(stage, 3)


# ── Feedback CSV ingestion ────────────────────────────────────────────────────
@app.task(name="ingest_feedback_csv")
def ingest_feedback_csv(client_id: str, csv_path: str) -> int:
    """
    Read feedback.csv and store unprocessed rows in the DB.

    Returns the number of new rows ingested.
    """
    return asyncio.run(_ingest_feedback(client_id, csv_path))


async def _ingest_feedback(client_id: str, csv_path: str) -> int:
    import csv
    from python_ulid import ULID
    from storageidol_db import FeedbackRow, get_session

    new_rows = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(row for row in f if not row.startswith("#"))
        rows_to_insert = []
        for row in reader:
            if row.get("resolved", "").lower() == "true":
                continue  # Skip already-resolved rows
            rows_to_insert.append(FeedbackRow(
                id=str(ULID()),
                client_id=client_id,
                conversation_id=row.get("conversation_id") or None,
                environment=row.get("environment", "prod"),
                category=row.get("category", "other"),
                description=row.get("description", ""),
                expected_behavior=row.get("expected_behavior") or None,
                actual_behavior=row.get("actual_behavior") or None,
                priority=row.get("priority", "medium"),
                resolved=False,
            ))

    if rows_to_insert:
        async with get_session(client_id) as session:
            session.add_all(rows_to_insert)
        new_rows = len(rows_to_insert)
        logger.info("Ingested %d feedback rows for client=%s", new_rows, client_id)

    return new_rows


# ── Celery Beat scheduler config (D+N staging) ────────────────────────────────
# Beat schedule is configured in core/agents/storageidol_agents/scheduler/staging.py


# ── Helpers ───────────────────────────────────────────────────────────────────
async def _get_or_create_contact(client_id: str, phone: str) -> str:
    """Get the contact ID for a phone number, creating a new contact if needed."""
    from storageidol_db import Contact, get_session
    from sqlalchemy import select
    from python_ulid import ULID

    async with get_session(client_id) as session:
        result = await session.execute(
            select(Contact).where(
                Contact.client_id == client_id,
                Contact.phone == phone,
            )
        )
        contact = result.scalar_one_or_none()
        if contact:
            return contact.id

        new_contact = Contact(
            id=str(ULID()),
            client_id=client_id,
            phone=phone,
        )
        session.add(new_contact)
        return new_contact.id
