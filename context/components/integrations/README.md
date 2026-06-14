# Component: Integrations (Shared Packages)

Adapters for third-party services. Each integration is a thin wrapper that normalizes external APIs into internal interfaces.

**Package locations** (under `packages/`, imported by `core/agents/` and `core/api/`):
- `packages/whatsapp/` — WhatsApp Cloud API client (Python)
- `packages/voice/` — LiveKit Agents wrapper: Deepgram STT → Claude → ElevenLabs TTS pipeline (Python)
- `packages/llm/` — Claude API wrapper with prompt caching, model routing, Langfuse instrumentation (Python)
- `packages/db/` — SQLAlchemy 2 async models, session factory, Alembic migrations (Python)
- `packages/mcp-base/` — Base MCP server + `createTool` factory (TypeScript)

## Included integrations

### WhatsApp Cloud API (`packages/whatsapp/`)
- Send template messages (outbound)
- Send session messages (reply within 24h window)
- Parse inbound message webhooks
- Status callbacks (delivered, read, failed)

### Voice: LiveKit Agents (`packages/voice/`)
- **STT:** Deepgram (streaming, real-time)
- **TTS:** ElevenLabs (voice ID per client, streaming)
- **PSTN telephony:** Telnyx SIP trunk — provides Spanish (+34) phone numbers and routes PSTN calls to LiveKit
- Built-in turn detection, interruption handling, noise cancellation
- Target latency: <500ms end-to-end
- `bridge.py` connects LiveKit session → client's LangGraph for reasoning (no business logic duplicated between WhatsApp and voice)

### Stripe (`packages/whatsapp/` — payment link helper)
- Generate payment links with prefilled amount and metadata
- Webhook listener for payment completion events

### CRM adapters
- Generic interface lives in the per-client MCP (`clients/<id>/mcp/tools/`)
- Implementations: custom REST per client (via `mcp-base`'s `createTool`)

**Owned by:** Backend / Platform team
