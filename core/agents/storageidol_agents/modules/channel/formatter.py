"""
Module: channel/formatter

Channel-aware response formatter — the LAST node in every client graph.

Why this exists: business logic modules (intent, auth, CRM, debt) produce a
`raw_reply` with the informational content. This module adapts that content
to the channel's UX conventions:

  VOICE (LiveKit → ElevenLabs TTS):
    - Plain spoken sentences. No markdown. No URLs (read as "enlace de pago").
    - Max 2-3 sentences. End with an open question or clear next step.
    - Numbers and dates read naturally: "quince de junio" not "15/06".
    - No emojis.

  WHATSAPP (WhatsApp Cloud API):
    - Can use WhatsApp markdown: *bold*, lists (- item), emojis.
    - Can include clickable payment links.
    - Can be 4-6 lines for complex information.
    - Emojis add warmth but use sparingly.
    - Key facts (amount, date, contract number) should be bold.

The formatter makes ONE additional Claude Haiku call to reformat the raw reply.
Haiku is fast and cheap — this is pure reformatting, not reasoning.

If `raw_reply` is already set by a module, formatter adapts it.
If only `reply` is set (already formatted by the module), formatter is a no-op
for WhatsApp but still ensures voice-safe output.
"""

from __future__ import annotations

import logging

from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, Channel, ClientConfig

logger = logging.getLogger(__name__)

_VOICE_FORMAT_SYSTEM = """You are reformatting a customer service response for a VOICE call (text-to-speech).

Rules:
- Convert to natural spoken Spanish. No markdown. No asterisks. No bullet points. No URLs.
- If there is a payment link, say: "Le enviaré el enlace de pago por WhatsApp."
- Keep it to 2-3 sentences maximum.
- End with a clear open question or next step.
- Dates: "el quince de junio" not "15/06/2026".
- Numbers: "cuarenta y cinco euros" not "45 €".
- Never mention internal codes, IDs, or system names.
"""

_WHATSAPP_FORMAT_SYSTEM = """You are reformatting a customer service response for WhatsApp.

Rules:
- Use WhatsApp markdown: *bold* for key facts (amounts, dates, names).
- Use emoji sparingly for warmth (1-2 max).
- Structure with short lines; use "-" for lists if there are multiple items.
- Payment links should be on their own line as a clickable URL.
- Keep conversational tone — not formal or robotic.
- Maximum 6 lines.
"""


def channel_formatter_node(config: ClientConfig):
    """
    Returns a LangGraph node that reformats the reply for the current channel.

    Place this as the LAST node before END in every client graph.
    """

    async def _node(state: dict) -> dict:
        s = AgentState(**state)

        # If there's no reply yet, nothing to format
        if not s.reply:
            return {}

        # For WhatsApp, Claude modules already write decent text.
        # Only invoke the formatter if the channel actually needs transformation.
        if s.channel == Channel.VOICE:
            formatted = await _format_for_voice(s, config)
            return {"reply": formatted}
        elif s.channel == Channel.WHATSAPP:
            formatted = await _format_for_whatsapp(s, config)
            return {"reply": formatted}

        return {}

    return _node


async def _format_for_voice(state: AgentState, config: ClientConfig) -> str:
    """Reformat the reply for spoken TTS output."""
    llm = ClaudeClient(client_id=state.client_id, trace_id=state.langfuse_trace_id)
    response = await llm.complete(
        messages=[{"role": "user", "content": f"Original response:\n{state.reply}"}],
        task=Task.CLASSIFICATION,      # Haiku — cheap, fast, no reasoning needed
        system=_VOICE_FORMAT_SYSTEM,
        cache_system=True,
        max_tokens=256,
    )
    return response.content.strip()


async def _format_for_whatsapp(state: AgentState, config: ClientConfig) -> str:
    """Reformat the reply for WhatsApp markdown."""
    # Only reformat if the reply contains raw data that needs structuring
    # (e.g. JSON from CRM, or a long unformatted paragraph)
    needs_formatting = (
        state.crm_data is not None  # Has structured CRM data to present
        or len(state.reply) > 300   # Long reply that benefits from structure
    )

    if not needs_formatting:
        return state.reply

    llm = ClaudeClient(client_id=state.client_id, trace_id=state.langfuse_trace_id)
    response = await llm.complete(
        messages=[{"role": "user", "content": f"Original response:\n{state.reply}"}],
        task=Task.CLASSIFICATION,      # Haiku
        system=_WHATSAPP_FORMAT_SYSTEM,
        cache_system=True,
        max_tokens=512,
    )
    return response.content.strip()
