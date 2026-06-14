"""
Module: auth/phone_dni

Validates a contact's identity by asking for their phone number and DNI
(Spanish national ID). Uses the client's MCP `auth` tool to verify
against the CRM.

State inputs:
    user_message: latest message from the user
    auth_verified: current auth state (False on first call)
    contact_phone: phone collected so far (None if not yet asked)

State outputs:
    auth_verified: True if both phone + DNI validated
    contact_phone, contact_name, contact_crm_id: populated on success
    reply: prompt asking for phone/DNI, or confirmation/error message
    next_node: "intent" (re-route after auth) or stays in auth flow
"""

from __future__ import annotations

import json
import logging

from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, AuthMethod, ClientConfig

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an identity verification assistant for {brand_name}.

Your task is to collect and verify the customer's phone number and DNI (Spanish national ID).

Rules:
- First ask for their phone number in a friendly way.
- Once you have a phone number, ask for their DNI.
- When you have both, output ONLY a JSON object: {{"phone": "...", "dni": "..."}}
- If the user provides both in one message, extract both immediately.
- Be brief and professional. Language: {language}.
- Never reveal that you are AI or discuss topics outside of identity verification.
"""

_AUTH_TOOL_SYSTEM = """Extract phone number and DNI from the conversation.
Output JSON only: {{"phone": "<e164_or_null>", "dni": "<dni_or_null>", "ready": <true_if_both_present>}}"""


def phone_dni_node(config: ClientConfig):
    """
    Returns a LangGraph node function for phone+DNI authentication.

    The returned function is the actual node — it's a closure over `config`.
    """
    async def _node(state: dict) -> dict:
        s = AgentState(**state)
        llm = ClaudeClient(client_id=s.client_id, trace_id=s.langfuse_trace_id)

        system = _SYSTEM_PROMPT.format(
            brand_name=config.brand_name,
            language=config.language,
        )

        # Extract structured data from conversation so far
        extract_response = await llm.complete(
            messages=s.messages,
            task=Task.CLASSIFICATION,
            system=_AUTH_TOOL_SYSTEM,
            cache_system=False,
            max_tokens=256,
        )

        try:
            extracted = json.loads(extract_response.content)
        except (json.JSONDecodeError, ValueError):
            extracted = {}

        phone = extracted.get("phone") or s.contact_phone
        dni = extracted.get("dni")
        ready = bool(phone and dni)

        if ready:
            # Call MCP auth tool to verify against CRM
            auth_result = await _verify_with_mcp(s, phone, dni)
            if auth_result["verified"]:
                return {
                    "auth_verified": True,
                    "auth_method_used": AuthMethod.PHONE_DNI,
                    "contact_phone": phone,
                    "contact_name": auth_result.get("name"),
                    "contact_crm_id": auth_result.get("crm_id"),
                    "reply": f"Perfecto, {auth_result.get('name', 'le')} hemos verificado su identidad. ¿En qué le puedo ayudar?",
                    "next_node": "intent",
                }
            else:
                return {
                    "auth_verified": False,
                    "reply": "Lo siento, no hemos podido verificar sus datos. ¿Puede confirmar su número de teléfono y DNI?",
                }
        elif phone and not s.contact_phone:
            # Just collected phone, now ask for DNI
            return {
                "contact_phone": phone,
                "reply": "Gracias. Ahora, ¿puede indicarme su número de DNI?",
            }
        else:
            # Nothing collected yet — ask for phone
            response = await llm.complete(
                messages=s.messages,
                task=Task.CONVERSATION,
                system=system,
                max_tokens=256,
            )
            return {"reply": response.content}

    return _node


async def _verify_with_mcp(state: AgentState, phone: str, dni: str) -> dict:
    """
    Call the client's MCP auth tool to verify phone+DNI.

    Returns {"verified": bool, "name": str, "crm_id": str}.
    On MCP failure, returns {"verified": False} — never raises.
    """
    # MCP tool calls are made via the LangGraph MCP integration.
    # In the real implementation, state carries the MCP client injected
    # by the Celery task. Here we show the interface; the actual call is:
    #   result = await mcp_client.call_tool("auth", {"phone": phone, "dni": dni})
    #
    # For testability, the MCP client is expected in state.mcp_client (added by tasks.py).
    # We use a duck-type check so tests can inject a mock.
    mcp_client = getattr(state, "mcp_client", None)
    if mcp_client is None:
        logger.warning("No MCP client available for auth verification")
        return {"verified": False}

    try:
        result = await mcp_client.call_tool("verify_identity", {"phone": phone, "dni": dni})
        if result.get("ok"):
            data = result.get("data", {})
            return {
                "verified": True,
                "name": data.get("name"),
                "crm_id": data.get("id"),
            }
        return {"verified": False}
    except Exception:
        logger.exception("MCP auth tool call failed")
        return {"verified": False}
