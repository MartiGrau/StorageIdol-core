"""
Module: intent/generic

General-purpose intent classifier for clients not in the self-storage domain.
Detects whether the user wants: customer service, sales, debt, or human escalation.

State inputs / outputs: same pattern as intent/storage.
"""

from __future__ import annotations

import json
import logging

from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, ClientConfig

logger = logging.getLogger(__name__)

GENERIC_INTENTS = {
    "information_request": "faq_rag",
    "account_query":       "crm_lookup",
    "sales_inquiry":       "lead",
    "payment_or_debt":     "debt",
    "complaint":           "escalation",
    "speak_to_human":      "escalation",
    "unknown":             "faq_rag",
}

_PROMPT = """Classify the customer's intent.

Available intents:
- information_request: looking for general information
- account_query: questions about their specific account
- sales_inquiry: interested in purchasing or signing up
- payment_or_debt: about payments, invoices, or debt
- complaint: expressing dissatisfaction
- speak_to_human: explicitly requesting a human agent
- unknown: cannot classify

Output ONLY valid JSON: {{"intent": "<key>", "confidence": 0.0-1.0}}
"""


def generic_intent_node(config: ClientConfig):
    """Returns a LangGraph node for generic multi-domain intent classification."""

    async def _node(state: dict) -> dict:
        s = AgentState(**state)
        llm = ClaudeClient(client_id=s.client_id, trace_id=s.langfuse_trace_id)

        response = await llm.complete(
            messages=[{"role": "user", "content": s.user_message}],
            task=Task.CLASSIFICATION,
            system=_PROMPT,
            cache_system=True,
            max_tokens=64,
        )

        try:
            data = json.loads(response.content)
            intent = data.get("intent", "unknown")
            confidence = float(data.get("confidence", 0.5))
        except (json.JSONDecodeError, ValueError):
            intent = "unknown"
            confidence = 0.0

        next_node = GENERIC_INTENTS.get(intent, "faq_rag")
        return {
            "detected_intent": intent,
            "intent_confidence": confidence,
            "next_node": next_node,
            "should_escalate": next_node == "escalation",
        }

    return _node
