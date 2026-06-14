"""
Module: debt/soft

Handles soft-tone debt collection interactions (D+3 and D+10 stages).

Tone: friendly, empathetic, solution-focused. Never threatening.
Uses payment links when the debtor shows willingness.
Escalates to D+20 (hard) if no resolution after N turns.

State inputs:
    debt_case_id, debt_amount, debt_stage, user_message
    auth_verified (must be True — debt module requires authentication)

State outputs:
    reply: the debt conversation response
    debt_stage: updated stage if progressed
    should_escalate: True if human handoff needed
"""

from __future__ import annotations

import logging

from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, ClientConfig

logger = logging.getLogger(__name__)

_SOFT_SYSTEM = """You are a polite payment recovery assistant for {brand_name}.

Customer account information:
- Outstanding amount: {amount} EUR
- Collection stage: {stage}
- Customer name: {name}

Your goals:
1. Remind them of the outstanding balance kindly.
2. Offer a payment link if they seem ready to pay.
3. If they ask about a payment plan, acknowledge and escalate to the team.
4. NEVER use threatening language, legal threats, or aggressive tone.
5. If they claim to have already paid, escalate immediately.

Payment link: {payment_link}

Language: {language}.
"""

_MAX_SOFT_TURNS = 3   # After this many turns without resolution, flag for escalation


def debt_soft_node(config: ClientConfig):
    """Returns a LangGraph node for soft-tone debt collection."""

    async def _node(state: dict) -> dict:
        s = AgentState(**state)

        if not s.auth_verified:
            return {
                "reply": "Para gestionar su cuenta, necesito verificar su identidad primero.",
                "next_node": "auth",
            }

        # Check escalation triggers in config
        if _should_escalate(s, config):
            return {
                "should_escalate": True,
                "escalation_reason": "Debt escalation trigger detected",
                "reply": "Entiendo su situación. Voy a ponerle en contacto con "
                         "nuestro equipo para ayudarle con esto directamente.",
            }

        payment_link = _get_payment_link(s, config)

        llm = ClaudeClient(client_id=s.client_id, trace_id=s.langfuse_trace_id)
        system = _SOFT_SYSTEM.format(
            brand_name=config.brand_name,
            amount=s.debt_amount or "desconocido",
            stage=s.debt_stage or "d3",
            name=s.contact_name or "estimado cliente",
            payment_link=payment_link or "no disponible en este momento",
            language=config.language,
        )

        response = await llm.complete(
            messages=s.messages,
            task=Task.CONVERSATION,
            system=system,
            max_tokens=512,
        )

        # If too many turns without resolution, push to hard collection
        updates: dict = {"reply": response.content}
        if s.turn_count >= _MAX_SOFT_TURNS and not s.debt_stage == "resolved":
            updates["debt_stage"] = "d20"  # Trigger scheduler to advance stage
            logger.info(
                "Advancing debt case %s to hard collection (turns=%d)",
                s.debt_case_id, s.turn_count
            )

        return updates

    return _node


def _should_escalate(state: AgentState, config: ClientConfig) -> bool:
    """Check if any escalation trigger is present in the user message."""
    msg = state.user_message.lower()
    for trigger in config.escalation_triggers:
        if trigger.lower() in msg:
            return True
    # Always escalate if user claims to have paid
    if any(phrase in msg for phrase in ["ya pagué", "ya he pagado", "ya lo pagué"]):
        return True
    return False


def _get_payment_link(state: AgentState, config: ClientConfig) -> str | None:
    """Build a payment link from the config template and debt case data."""
    if not state.debt_amount:
        return None
    # Payment link format varies per client — config provides the base URL
    # The MCP debt tool generates the actual prefilled link
    return None  # Will be populated by MCP tool call in a full implementation
