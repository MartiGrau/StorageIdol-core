"""
Module: intent/storage

Self-storage intent classifier. Categorises inbound messages from tenants
into actionable intents specific to the self-storage domain.

State inputs:
    user_message: latest user message
    messages: full conversation history

State outputs:
    detected_intent: one of the STORAGE_INTENTS
    intent_confidence: 0.0-1.0
    next_node: routing target ("faq_rag" | "crm_lookup" | "debt" | "lead" | "escalation")
    should_escalate: True if the intent requires human intervention
"""

from __future__ import annotations

import json
import logging

from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, ClientConfig

logger = logging.getLogger(__name__)

# All intents this classifier can detect
STORAGE_INTENTS = {
    "payment_query":     "crm_lookup",   # Questions about invoices, payments
    "contract_info":     "crm_lookup",   # Questions about their contract/unit
    "unit_availability": "faq_rag",      # Available units, sizes, prices
    "access_issue":      "faq_rag",      # Gate codes, access hours
    "move_out":          "crm_lookup",   # Terminating contract
    "insurance_query":   "faq_rag",      # Insurance coverage questions
    "general_faq":       "faq_rag",      # Any other FAQ
    "complaint":         "escalation",   # Formal complaint → human
    "debt_negotiation":  "debt",         # User responding to debt collection
    "new_lead":          "lead",         # Prospect asking about renting
    "speak_to_human":    "escalation",   # Explicit escalation request
    "unknown":           "faq_rag",      # Fallback to FAQ
}

_CLASSIFICATION_PROMPT = """Classify the customer's intent in a self-storage business context.

Available intents:
{intents}

Output ONLY valid JSON:
{{"intent": "<intent_key>", "confidence": 0.0-1.0, "reason": "<brief_reason>"}}

Rules:
- Choose the single best matching intent.
- Set confidence below 0.6 if genuinely ambiguous.
- "speak_to_human" has highest priority — detect it from any phrasing.
- "complaint" if the user expresses strong dissatisfaction or uses legal language.
"""


def storage_intent_node(config: ClientConfig):
    """Returns a LangGraph node for self-storage intent classification."""

    intent_list = "\n".join(
        f"  - {k}: {_intent_description(k)}" for k in STORAGE_INTENTS
    )

    async def _node(state: dict) -> dict:
        s = AgentState(**state)
        llm = ClaudeClient(client_id=s.client_id, trace_id=s.langfuse_trace_id)

        response = await llm.complete(
            messages=[{"role": "user", "content": s.user_message}],
            task=Task.CLASSIFICATION,
            system=_CLASSIFICATION_PROMPT.format(intents=intent_list),
            cache_system=True,
            max_tokens=128,
        )

        try:
            data = json.loads(response.content)
            intent = data.get("intent", "unknown")
            confidence = float(data.get("confidence", 0.5))
        except (json.JSONDecodeError, ValueError):
            intent = "unknown"
            confidence = 0.0

        next_node = STORAGE_INTENTS.get(intent, "faq_rag")
        should_escalate = next_node == "escalation"

        return {
            "detected_intent": intent,
            "intent_confidence": confidence,
            "next_node": next_node,
            "should_escalate": should_escalate,
            "escalation_reason": f"Intent: {intent}" if should_escalate else None,
        }

    return _node


def _intent_description(intent: str) -> str:
    descriptions = {
        "payment_query": "Questions about invoices, pending payments, receipts",
        "contract_info": "Questions about their unit contract, terms, dates",
        "unit_availability": "Asking about available storage units, sizes, prices",
        "access_issue": "Problems accessing the facility, gate codes, hours",
        "move_out": "Wants to cancel/terminate their contract",
        "insurance_query": "Questions about insurance coverage for stored items",
        "general_faq": "General questions about the facility or services",
        "complaint": "Expressing strong dissatisfaction or formal complaint",
        "debt_negotiation": "Responding to a debt/payment reminder",
        "new_lead": "Prospect interested in renting a storage unit",
        "speak_to_human": "Explicitly requesting to speak with a human agent",
        "unknown": "Cannot classify — fallback to FAQ",
    }
    return descriptions.get(intent, intent)
