"""
AgentState — the typed state object threaded through every LangGraph node.

Design principles:
  - ALL state is in this object; nodes read from it and write back to it.
  - Nodes must be pure(ish) functions: (AgentState, config) → AgentState.
  - No global singletons inside nodes — pass config explicitly.
  - The state is serialisable (pydantic) so it can be checkpointed by LangGraph.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, Field


class Channel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    VOICE = "voice"


class AuthMethod(str, enum.Enum):
    PHONE_DNI = "phone_dni"
    EMAIL_ID = "email_id"
    NONE = "none"


class DebtBehavior(str, enum.Enum):
    SOFT = "soft"
    HARD = "hard"


class IntentClassifier(str, enum.Enum):
    STORAGE = "storage"
    FINANCIAL = "financial"
    GENERIC = "generic"


class ClientConfig(BaseModel):
    """
    Non-secret per-client settings, loaded from clients/<id>/config.yaml at startup.

    This is the runtime representation of config.yaml — values only, no logic.
    Secrets (API keys) are in environment variables, not here.
    """

    client_id: str
    brand_name: str
    language: str = "es"
    timezone: str = "Europe/Madrid"

    # Modules enabled
    customer_service: bool = True
    debt_collection: bool = False
    lead_management: bool = False
    voice: bool = False

    # Agent composition
    intent_classifier: IntentClassifier = IntentClassifier.STORAGE
    auth_method: AuthMethod = AuthMethod.PHONE_DNI
    debt_behavior: DebtBehavior = DebtBehavior.SOFT

    # Voice
    elevenlabs_voice_id: str = ""
    stt_provider: str = "deepgram"
    voice_language: str = "es-ES"

    # Knowledge base
    knowledge_base_path: str = "knowledge-base/"
    embedding_model: str = "text-embedding-3-small"

    # Escalation
    escalation_webhook_url: str | None = None
    escalation_triggers: list[str] = Field(default_factory=list)

    # Per-client model overrides — falls back to packages/llm defaults when empty
    model_overrides: dict[str, str] = Field(default_factory=dict)

    # EU AI Act Art. 50 disclosure wording — presence is mandatory, wording is configurable
    disclosure: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ClientConfig":
        """Parse from a raw config.yaml dict."""
        modules = raw.get("modules", {})
        agent = raw.get("agent", {})
        voice = raw.get("voice", {})
        kb = raw.get("knowledge_base", {})
        esc = raw.get("escalation", {})
        return cls(
            client_id=raw.get("client_id", ""),
            brand_name=raw.get("brand_name", ""),
            language=raw.get("language", "es"),
            timezone=raw.get("timezone", "Europe/Madrid"),
            customer_service=modules.get("customer_service", True),
            debt_collection=modules.get("debt_collection", False),
            lead_management=modules.get("lead_management", False),
            voice=modules.get("voice", False),
            intent_classifier=IntentClassifier(agent.get("intent_classifier", "storage")),
            auth_method=AuthMethod(agent.get("auth_method", "phone_dni")),
            debt_behavior=DebtBehavior(agent.get("debt_behavior", "soft")),
            elevenlabs_voice_id=voice.get("elevenlabs_voice_id", ""),
            stt_provider=voice.get("stt_provider", "deepgram"),
            voice_language=voice.get("language", "es-ES"),
            knowledge_base_path=kb.get("path", "knowledge-base/"),
            embedding_model=kb.get("embedding_model", "text-embedding-3-small"),
            escalation_webhook_url=esc.get("webhook_url"),
            escalation_triggers=esc.get("triggers", []),
            model_overrides=raw.get("model_overrides") or {},
            disclosure=raw.get("disclosure") or {},
        )


class AgentState(BaseModel):
    """
    The state object threaded through the entire LangGraph for a single turn.

    Each node receives this state, may update fields, and returns the updated state.
    LangGraph merges the returned dict into the current state (reducer pattern).
    """

    # ── Conversation context ──────────────────────────────────────────────────
    client_id: str
    channel: Channel
    conversation_id: str | None = None
    contact_id: str | None = None

    # Inbound message
    messages: list[dict[str, Any]] = Field(default_factory=list)

    # The latest user message text (extracted by the entry node)
    user_message: str = ""

    # ── Auth state ────────────────────────────────────────────────────────────
    auth_verified: bool = False
    auth_method_used: AuthMethod | None = None
    contact_phone: str | None = None
    contact_name: str | None = None
    contact_crm_id: str | None = None

    # ── Intent ───────────────────────────────────────────────────────────────
    detected_intent: str | None = None     # e.g. "payment_query", "contract_info"
    intent_confidence: float = 0.0

    # ── Conversation module outputs ───────────────────────────────────────────
    kb_answer: str | None = None           # Answer from FAQ RAG
    crm_data: dict[str, Any] | None = None # Data retrieved from MCP CRM tool

    # ── Debt collection state ─────────────────────────────────────────────────
    debt_case_id: str | None = None
    debt_amount: float | None = None
    debt_stage: str | None = None          # d3 | d10 | d20 | d30

    # ── Lead qualification state ──────────────────────────────────────────────
    lead_id: str | None = None
    lead_qualified: bool = False
    unit_size_m2: float | None = None
    unit_duration_months: int | None = None
    budget_eur: float | None = None

    # ── Escalation ────────────────────────────────────────────────────────────
    should_escalate: bool = False
    escalation_reason: str | None = None

    # ── Response ──────────────────────────────────────────────────────────────
    reply: str = ""           # The final text to send back to the user/caller

    # ── Routing ──────────────────────────────────────────────────────────────
    next_node: str | None = None   # Explicit routing override (used by intent module)

    # ── Metadata ─────────────────────────────────────────────────────────────
    langfuse_trace_id: str | None = None
    turn_count: int = 0         # Number of turns in this conversation
    mcp_errors: list[str] = Field(default_factory=list)  # Non-fatal MCP tool errors

    class Config:
        # Allow mutation (LangGraph nodes return updated dicts, not full replacements)
        arbitrary_types_allowed = True
