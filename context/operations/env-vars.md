# Environment Variables Reference

Variables shared across services. Each service also has its own `.env.example` with service-specific vars.

## Core / shared

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude (all LLM calls) |
| `OPENAI_API_KEY` | Yes | OpenAI API key for embeddings (`text-embedding-3-small`) |
| `CLIENT_ID` | Yes | Which client graph to load (e.g. `retras`) |
| `ENVIRONMENT` | Yes | `development`, `staging`, or `production` |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` (default: `INFO`) |

## Database

The primary database is **external and managed by the client** — never a container in
the deploy stack. It must be managed PostgreSQL 16+ with `pgvector`. Provision two
separate databases per client (DEV and PROD). See `context/operations/database.md`.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | External managed-Postgres asyncpg string (`postgresql+asyncpg://...?ssl=require`). DEV and PROD use different databases. |
| `REDIS_URL` | Yes | Redis connection string (local ephemeral broker/cache) |

## Messaging

| Variable | Required | Description |
|---|---|---|
| `WHATSAPP_ACCESS_TOKEN` | Yes | Meta WhatsApp Cloud API access token |
| `WHATSAPP_PHONE_NUMBER_ID` | Yes | Sending phone number ID |
| `WHATSAPP_WEBHOOK_VERIFY_TOKEN` | Yes | Token for webhook verification |

## Voice (LiveKit + Telnyx SIP)

LiveKit handles the real-time STT→LLM→TTS pipeline. Telnyx provides Spanish (+34) phone
numbers and routes PSTN calls to LiveKit via SIP (LiveKit does not provision ES DIDs directly).

| Variable | Required | Description |
|---|---|---|
| `LIVEKIT_URL` | Yes | LiveKit server WebSocket URL (`wss://...`) |
| `LIVEKIT_API_KEY` | Yes | LiveKit API key |
| `LIVEKIT_API_SECRET` | Yes | LiveKit API secret |
| `TELNYX_API_KEY` | Yes | Telnyx API key (Spanish +34 SIP numbers) |
| `TELNYX_SIP_CONNECTION_ID` | Yes | Telnyx SIP connection ID for inbound call routing |
| `DEEPGRAM_API_KEY` | Yes | Deepgram API key (speech-to-text) |
| `ELEVENLABS_API_KEY` | Yes | ElevenLabs API key (text-to-speech, per-client voice ID) |

## Observability (Langfuse)

| Variable | Required | Description |
|---|---|---|
| `LANGFUSE_PUBLIC_KEY` | Yes | Langfuse project public key |
| `LANGFUSE_SECRET_KEY` | Yes | Langfuse project secret key |
| `LANGFUSE_HOST` | Yes | Langfuse server URL (e.g. `http://langfuse:3000`) |

## Payments (optional — debt collection module)

| Variable | Required | Description |
|---|---|---|
| `STRIPE_SECRET_KEY` | No | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | No | Stripe webhook signing secret |
| `REDSYS_MERCHANT_CODE` | No | Redsys merchant code (Spanish payment gateway) |
| `REDSYS_SECRET_KEY` | No | Redsys secret key |

## Client-specific

Each client's non-secret settings are loaded from `clients/<id>/config.yaml` at startup
(modules enabled, voice ID, thresholds). Secrets stay in `.env`.
See `context/architecture/core-vs-config.md`.
