"""
storageidol-voice — LiveKit Agents voice pipeline.

STT: Deepgram (real-time streaming)
LLM: Claude via LangGraph graph (shared with WhatsApp — no logic duplication)
TTS: ElevenLabs (streaming, per-client voice ID)
Telephony: LiveKit native SIP (inbound + outbound PSTN — no Twilio bridge)

Usage (as a standalone LiveKit Agent worker):
    from storageidol_voice import run_voice_worker

    asyncio.run(run_voice_worker(client_id="retras"))
"""

from .agent import VoiceAgent, VoiceAgentConfig, run_voice_worker

__all__ = ["VoiceAgent", "VoiceAgentConfig", "run_voice_worker"]
