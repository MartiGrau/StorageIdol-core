# StorageIdol Core

AI agent platform for companies with high-volume, repetitive client interactions — starting with self-storage operators. Clients receive running Docker containers, not source code.

```
  WhatsApp ──┐                    ┌─── reply
  Voice ─────┤  core/api          │
  Debt cron ─┘  (FastAPI)         │
               │                  │
               ▼                  │
           Celery task             │
               │                  │
               ▼                  │
         LangGraph graph ──────────┘
         (clients/<id>/graph.py)
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
    intent   auth    debt / lead / faq
    module  module   modules (core)
               │
               ▼
         MCP tool calls
         (clients/<id>/mcp/)
               │
               ▼
         client CRM / API
```

## Three commercial modules

| Module | What it does |
|---|---|
| **Customer Service 24/7** | WhatsApp + voice agent; FAQ, CRM lookup, human escalation |
| **Lead Management** | Capture → qualify → nurture → handoff to sales |
| **Debt Collection** | Staged D+N scheduler; WhatsApp + AI calls; payment link |

## Repo layout

```
core/           ← platform framework (shared across all clients)
  api/          ← FastAPI webhooks + REST
  agents/       ← LangGraph modules + graph registry
  dashboard/    ← client-facing conversation dashboard (Next.js)
  backoffice/   ← StorageIdol internal ops UI (Next.js)
  watchdog/     ← monitoring sidecar

packages/       ← shared libraries
  llm/          ← Claude client (caching, routing, Langfuse)
  whatsapp/     ← WhatsApp Cloud API wrapper
  voice/        ← LiveKit Agents (Deepgram STT + ElevenLabs TTS)
  mcp-base/     ← base MCP server (TypeScript)
  db/           ← SQLAlchemy models + migrations

clients/        ← per-client configs, MCPs, knowledge bases (private)
  _template/    ← copy this when onboarding a new client
  redtras/      ← Retras self-storage (first client)

deploy/         ← what gets deployed on client servers
  _template/    ← docker-compose.yml + .env.example

context/        ← StorageIdol documentation (read before any decision)
.claude/        ← Claude Code agents, skills, hooks
```

## Key architecture rules

1. **Client graphs are code, not config** — `clients/<id>/graph.py` wires Core modules; `config.yaml` holds values only; secrets go in `.env` on the server
2. **Clients never see other clients** — separate Docker stacks, separate Postgres instances
3. **Same agent for WhatsApp and voice** — shared LangGraph reasoning; `channel/formatter` adapts the reply at the end of every graph
4. **EU AI Act Art. 50** — AI identity disclosure is baked into Core and fires on every first turn; wording is client-configurable

## Quick start

```bash
cp .env.example .env          # fill in ANTHROPIC_API_KEY, OPENAI_API_KEY, CLIENT_ID
docker compose -f infrastructure/docker/docker-compose.dev.yml up -d
uv sync && pnpm install
uv run alembic -c core/api/alembic.ini upgrade head
```

Full setup: `context/operations/development.md`

## Common tasks

| Task | Where to start |
|---|---|
| Onboard a new client | `/new-client <id>` → `.claude/agents/provision-client.md` |
| Build a client MCP | `/build-mcp <id>` → `.claude/agents/build-mcp.md` |
| Add a new agent module | `core/agents/modules/README.md` |
| Understand the architecture | `context/architecture/overview.md` |
| Investigate a production alert | `ops/README.md` |
