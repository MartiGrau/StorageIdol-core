# Package: voice

LiveKit Agents voice runtime: Deepgram STT → shared LangGraph → ElevenLabs TTS.

**Language:** Python | **Key dependencies:** `livekit-agents`, `livekit-plugins` (deepgram, elevenlabs, silero)

## Architecture

LiveKit is the **sole voice runtime**. The pipeline wires audio I/O around the same
LangGraph graph used for WhatsApp — the graph does all reasoning, this package only
handles audio in/out:

```
SIP inbound/outbound → LiveKit room
  → Silero VAD → Deepgram STT
  → _GraphLLMAdapter (invokes the client's compiled LangGraph)
  → ElevenLabs TTS → caller
```

See `storageidol_voice/agent.py` for the implementation.

## Telephony (PSTN connectivity)

Phone numbers reach LiveKit through a **SIP trunk**. The trunk provider is a
connectivity choice only — it does not change the runtime above.

| Provider | `config.yaml` value | Notes |
|---|---|---|
| Telnyx | `telnyx` | Default. Provisions Spanish +34 DIDs (LiveKit does not provision ES DIDs directly). |
| Twilio | `twilio_sip` | For clients who already own Twilio numbers — point their Twilio SIP trunk at LiveKit. |
| Sinch | `sinch` | Alternative SIP trunk. |

**A Twilio-native runtime (Twilio Media Streams / ConversationRelay) is explicitly out
of scope.** Twilio is supported only as a SIP trunk into the LiveKit pipeline. We reuse
a client's existing Twilio numbers and ElevenLabs voice, not their voice-agent code.

## Voice profile

Voice ID, language, and SIP trunk are client-specific and live in
`clients/<id>/config.yaml` under `voice.*`. This package hard-codes no voice settings.
