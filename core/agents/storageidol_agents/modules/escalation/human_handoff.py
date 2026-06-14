"""
Module: escalation/human_handoff

Handles human escalation: pauses the session, prepares a handoff summary,
notifies the on-call agent via webhook (Slack, Teams, etc.), and sends
a holding message to the user.

State inputs:
    should_escalate, escalation_reason
    messages (full history for the summary)
    contact_name, detected_intent

State outputs:
    reply: holding message to the user
    (side-effect: webhook notification to on-call agent)
"""

from __future__ import annotations

import logging
from datetime import timezone, datetime

import httpx

from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, ClientConfig

logger = logging.getLogger(__name__)

_SUMMARY_SYSTEM = """Summarise this customer service conversation for a human agent.

Include:
- Customer name and intent
- Key facts discussed (debt amount, contract details, etc.)
- Why escalation was triggered
- Recommended next action

Be concise (5-8 bullet points max). Language: English (for internal use).
"""

_HOLDING_REPLY_ES = (
    "Entendido. He puesto su caso en manos de uno de nuestros agentes, "
    "que se pondrá en contacto con usted en breve. "
    "¿Hay algo más que pueda hacer por usted mientras tanto?"
)


def human_handoff_node(config: ClientConfig):
    """Returns a LangGraph node for human escalation."""

    async def _node(state: dict) -> dict:
        s = AgentState(**state)
        llm = ClaudeClient(client_id=s.client_id, trace_id=s.langfuse_trace_id)

        # Generate handoff summary for the human agent
        summary_response = await llm.complete(
            messages=s.messages,
            task=Task.CONVERSATION,
            system=_SUMMARY_SYSTEM,
            cache_system=False,
            max_tokens=512,
        )
        summary = summary_response.content

        # Fire-and-forget webhook notification
        if config.escalation_webhook_url:
            await _notify_webhook(
                webhook_url=config.escalation_webhook_url,
                client_id=s.client_id,
                contact_name=s.contact_name,
                conversation_id=s.conversation_id,
                reason=s.escalation_reason,
                summary=summary,
            )

        return {
            "reply": _HOLDING_REPLY_ES,
            "should_escalate": True,
        }

    return _node


async def _notify_webhook(
    webhook_url: str,
    client_id: str,
    contact_name: str | None,
    conversation_id: str | None,
    reason: str | None,
    summary: str,
) -> None:
    """POST a Slack/Teams-compatible webhook notification (fire-and-forget)."""
    payload = {
        "text": f"🚨 *Escalation — {client_id}*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Client:* {client_id}\n"
                        f"*Contact:* {contact_name or 'Unknown'}\n"
                        f"*Conversation:* {conversation_id or 'N/A'}\n"
                        f"*Reason:* {reason or 'N/A'}\n"
                        f"*Time:* {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                        f"*Summary:*\n{summary}"
                    ),
                },
            }
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
    except Exception:
        # Never let webhook failure propagate to the agent — log and continue
        logger.warning("Escalation webhook notification failed", exc_info=True)
