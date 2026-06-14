# Package: voice

ElevenLabs TTS + Twilio telephony wrapper.

**Language:** Python | **Key dependencies:** `elevenlabs`, `twilio`

## What it provides

- `VoiceClient(elevenlabs_api_key, twilio_account_sid, twilio_auth_token)`
- `synthesize(text, voice_id, language) -> AudioStream` — Text → speech via ElevenLabs
- `place_call(to, from_, webhook_url) -> call_sid` — Outbound call via Twilio
- `stream_to_call(call_sid, audio_stream)` — Stream TTS audio to active call via WebSocket
- `transcribe(audio_stream) -> str` — STT via Twilio `<Gather>` or ElevenLabs STT

## Voice profile

Voice ID and language are client-specific. They live in `clients/<id>/config.yaml` under `voice.elevenlabs_voice_id` and `voice.language`. The `VoiceClient` does not hard-code any voice settings.
