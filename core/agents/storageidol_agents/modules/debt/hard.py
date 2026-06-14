"""
Module: debt/hard

Handles hard-tone debt collection interactions (D+20 and D+30 stages).

Tone: firm, clear consequences, but NOT threatening (Meta compliance).
D+30 always escalates to human recovery team.

State inputs / outputs: same pattern as debt/soft.
"""

from __future__ import annotations

import logging

from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, ClientConfig

logger = logging.getLogger(__name__)

_HARD_SYSTEM = """You are a firm but professional payment recovery specialist for {brand_name}.

Customer account information:
- Outstanding amount: {amount} EUR
- Collection stage: {stage} (advanced stage — previous reminders sent)
- Customer name: {name}

Your goals:
1. Clearly communicate the urgency of the outstanding balance.
2. Explain the consequences of non-payment (access restriction, not legal threats).
3. Offer the payment link as the immediate resolution path.
4. If stage is d30, always escalate to the human team.

Important rules:
- NEVER make legal threats or use language that implies criminal consequences.
- NEVER be rude or disrespectful.
- If the customer is in distress, show empathy.

Payment link: {payment_link}
Language: {language}.
"""


def debt_hard_node(config: ClientConfig):
    """Returns a LangGraph node for firm-tone debt collection."""

    async def _node(state: dict) -> dict:
        s = AgentState(**state)

        if not s.auth_verified:
            return {
                "reply": "Para gestionar su cuenta, necesito verificar su identidad.",
                "next_node": "auth",
            }

        # D+30 always escalates
        if s.debt_stage == "d30":
            return {
                "should_escalate": True,
                "escalation_reason": "D+30 — automatic human escalation",
                "reply": "Su caso ha sido escalado a nuestro equipo de gestión. "
                         "Un especialista se pondrá en contacto con usted en breve.",
            }

        # Check for escalation triggers
        for trigger in config.escalation_triggers:
            if trigger.lower() in s.user_message.lower():
                return {
                    "should_escalate": True,
                    "escalation_reason": f"Trigger: {trigger}",
                    "reply": "Voy a ponerle en contacto con nuestro equipo directamente.",
                }

        llm = ClaudeClient(client_id=s.client_id, trace_id=s.langfuse_trace_id)
        system = _HARD_SYSTEM.format(
            brand_name=config.brand_name,
            amount=s.debt_amount or "desconocido",
            stage=s.debt_stage or "d20",
            name=s.contact_name or "estimado cliente",
            payment_link="[enlace de pago generado por MCP]",
            language=config.language,
        )

        response = await llm.complete(
            messages=s.messages,
            task=Task.REASONING,  # Opus for hard debt — higher stakes
            system=system,
            max_tokens=512,
        )

        return {"reply": response.content}

    return _node
