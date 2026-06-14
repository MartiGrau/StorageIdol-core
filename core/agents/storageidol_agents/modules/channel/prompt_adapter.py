"""
Channel prompt adapter — injects channel-specific instructions into module system prompts.

Usage in any module node:
    from ..channel.prompt_adapter import channel_instructions

    system = f"You are a helpful assistant for {config.brand_name}.\n\n" + \
             channel_instructions(state.channel)

This keeps channel awareness out of each module's core logic and centralised here.
"""

from ...state import Channel

_VOICE_INSTRUCTIONS = """
CHANNEL: VOICE (telephone call, text-to-speech)
- Respond in natural spoken Spanish. No markdown, no asterisks, no lists, no URLs.
- Keep your answer to 2-3 sentences maximum.
- Speak dates naturally: "el quince de junio" not "15/06".
- Speak numbers naturally: "cuarenta y cinco euros" not "45 €".
- If you need to provide a URL, say: "Le enviaré el enlace por WhatsApp".
- End your response with a brief question or offer of further help.
"""

_WHATSAPP_INSTRUCTIONS = """
CHANNEL: WHATSAPP (messaging app)
- You can use WhatsApp markdown: *bold* for key facts, - for bullet lists.
- You can include URLs as clickable links.
- Use 1-2 emojis where natural (not on every message).
- You can be slightly more detailed than in a phone call (max 6 lines).
- Use a friendly, warm but professional tone.
"""


def channel_instructions(channel: Channel) -> str:
    """Return the channel-specific system prompt addition for any module."""
    if channel == Channel.VOICE:
        return _VOICE_INSTRUCTIONS.strip()
    elif channel == Channel.WHATSAPP:
        return _WHATSAPP_INSTRUCTIONS.strip()
    return ""
