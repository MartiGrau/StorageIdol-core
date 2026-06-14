"""
Module: lead/qualify_storage

Qualifies a storage lead by collecting unit size, duration, and budget,
then hands off to sales with a complete lead profile.

State inputs:
    user_message, contact_phone, contact_name

State outputs:
    lead_id, lead_qualified
    unit_size_m2, unit_duration_months, budget_eur
    reply
"""

from __future__ import annotations

import json
import logging

from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, ClientConfig

logger = logging.getLogger(__name__)

_QUALIFY_SYSTEM = """You are a friendly sales assistant for {brand_name}, a self-storage company.

Your goal is to qualify this lead by learning:
1. How much storage space they need (in m²)
2. How long they plan to store (weeks/months)
3. Their approximate budget (optional)

Rules:
- Ask ONE question at a time.
- Be conversational, not form-like.
- When you have enough information, output JSON at the end of your reply:
  [LEAD_DATA: {{"size_m2": X, "duration_months": X, "budget_eur": X_or_null}}]
- If the user says they are not interested, set: [LEAD_DATA: {{"not_interested": true}}]

Language: {language}.
"""


def qualify_storage_node(config: ClientConfig):
    """Returns a LangGraph node for storage lead qualification."""

    async def _node(state: dict) -> dict:
        s = AgentState(**state)
        llm = ClaudeClient(client_id=s.client_id, trace_id=s.langfuse_trace_id)

        system = _QUALIFY_SYSTEM.format(
            brand_name=config.brand_name,
            language=config.language,
        )
        response = await llm.complete(
            messages=s.messages,
            task=Task.CONVERSATION,
            system=system,
            max_tokens=512,
        )

        content = response.content
        updates: dict = {"reply": content}

        # Extract structured lead data if present
        if "[LEAD_DATA:" in content:
            try:
                start = content.index("[LEAD_DATA:") + len("[LEAD_DATA:")
                end = content.index("]", start)
                lead_json = content[start:end].strip()
                lead_data = json.loads(lead_json)

                if lead_data.get("not_interested"):
                    updates["lead_qualified"] = False
                    updates["next_node"] = "end"
                else:
                    updates["unit_size_m2"] = lead_data.get("size_m2")
                    updates["unit_duration_months"] = lead_data.get("duration_months")
                    updates["budget_eur"] = lead_data.get("budget_eur")
                    updates["lead_qualified"] = True
                    # Strip the JSON marker from the reply
                    updates["reply"] = content[:content.index("[LEAD_DATA:")].strip()

            except (ValueError, json.JSONDecodeError):
                logger.debug("Could not parse LEAD_DATA from response")

        return updates

    return _node
