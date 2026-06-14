# Packages — Shared Libraries

Shared code imported by `core/` services and client MCPs. Never import from `clients/` here.

| Package | Language | Purpose |
|---|---|---|
| `llm/` | Python | Claude API wrapper with prompt caching, retry logic, model routing |
| `whatsapp/` | Python | WhatsApp Cloud API client: send text, templates, media, reactions |
| `voice/` | Python | ElevenLabs TTS + Twilio telephony wrapper |
| `mcp-base/` | TypeScript | Base MCP server class extended by every client MCP |
| `db/` | Python | Shared SQLAlchemy models, session factory, migration helpers |

## Usage rule

Any piece of code that appears in more than one `core/` service belongs here. Any code that references a specific client's API, credentials, or behavior belongs in `clients/<id>/mcp/`.
