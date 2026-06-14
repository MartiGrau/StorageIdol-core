"""
Module: conversation/crm_lookup

Retrieves the contact's data from the client's CRM via the MCP server,
then generates a personalised answer.

This module is used when the intent requires CRM data (payment_query,
contract_info, move_out) AND the contact is already authenticated.

State inputs:
    contact_crm_id, user_message, detected_intent
    (MCP client injected via state.mcp_client)

State outputs:
    crm_data: dict of raw CRM data
    reply: personalised response incorporating CRM data
"""

from __future__ import annotations

import json
import logging

from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, ClientConfig

logger = logging.getLogger(__name__)

_ANSWER_SYSTEM = """You are a helpful customer service assistant for {brand_name}.

The customer is authenticated. Here is their account information:
{crm_data}

Answer their question accurately and concisely using the data above.
Do NOT invent data not present in the account information.
If the data does not address their question, say you'll escalate to the team.
Language: {language}.
"""


def crm_lookup_node(config: ClientConfig):
    """Returns a LangGraph node for CRM-based personalised responses."""

    async def _node(state: dict) -> dict:
        s = AgentState(**state)

        # Contact must be authenticated to use CRM lookup
        if not s.auth_verified or not s.contact_crm_id:
            return {
                "reply": "Necesito verificar su identidad antes de acceder a su cuenta. "
                         "¿Puede indicarme su número de teléfono y DNI?",
                "next_node": "auth",
            }

        # Fetch CRM data via MCP
        crm_data = await _fetch_crm_data(s)
        if crm_data is None:
            return {
                "reply": "Lo siento, en este momento no puedo acceder a su cuenta. "
                         "Voy a ponerle en contacto con un agente.",
                "should_escalate": True,
                "escalation_reason": "CRM lookup failed",
            }

        # Generate personalised answer
        llm = ClaudeClient(client_id=s.client_id, trace_id=s.langfuse_trace_id)
        system = _ANSWER_SYSTEM.format(
            brand_name=config.brand_name,
            language=config.language,
            crm_data=json.dumps(crm_data, ensure_ascii=False, indent=2),
        )
        response = await llm.complete(
            messages=[{"role": "user", "content": s.user_message}],
            task=Task.CONVERSATION,
            system=system,
            cache_system=False,
            max_tokens=512,
        )

        return {
            "crm_data": crm_data,
            "reply": response.content,
        }

    return _node


async def _fetch_crm_data(state: AgentState) -> dict | None:
    """
    Call MCP tools to get the contact's contracts and invoices.

    Returns merged dict or None on failure (non-fatal).
    """
    mcp_client = getattr(state, "mcp_client", None)
    if mcp_client is None:
        logger.warning("No MCP client for CRM lookup")
        return None

    try:
        results: dict = {}

        contracts_result = await mcp_client.call_tool(
            "get_contracts", {"crm_id": state.contact_crm_id}
        )
        if contracts_result.get("ok"):
            results["contracts"] = contracts_result.get("data", [])

        invoices_result = await mcp_client.call_tool(
            "get_unpaid_invoices", {"crm_id": state.contact_crm_id}
        )
        if invoices_result.get("ok"):
            results["unpaid_invoices"] = invoices_result.get("data", [])

        return results or None
    except Exception:
        logger.exception("CRM MCP tool call failed")
        return None
