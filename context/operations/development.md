# Local Development

## Prerequisites

- Docker + Docker Compose
- Python 3.11+ with [uv](https://docs.astral.sh/uv/)
- Node.js 20+ with [pnpm](https://pnpm.io/)
- `gh` CLI (authenticated)

## First-time setup

```bash
# 1. Copy the root environment file and fill in the required keys
cp .env.example .env
# Minimum for local dev: ANTHROPIC_API_KEY, OPENAI_API_KEY, CLIENT_ID

# 2. Start all infrastructure (Postgres+pgvector, Redis, Langfuse, LiveKit dev server)
docker compose -f infrastructure/docker/docker-compose.dev.yml up -d

# 3. Install all Python dependencies (uv workspace — run from repo root)
uv sync

# 4. Install all TypeScript dependencies (pnpm workspace — run from repo root)
pnpm install

# 5. Run DB migrations
uv run alembic -c core/api/alembic.ini upgrade head
```

## Running services locally

Each service has its own start command documented in its `README.md`. The typical dev stack:

| Service | Command | Port |
|---|---|---|
| API | `uv run uvicorn core.api.main:app --reload` | 8000 |
| Agents (worker) | `uv run celery -A core.agents.storageidol_agents.tasks worker --loglevel=info` | — |
| Dashboard | `pnpm --filter=dashboard dev` | 3000 |
| Backoffice | `pnpm --filter=backoffice dev` | 3001 |
| Langfuse (observability) | via docker compose | 3002 |
| LiveKit (voice dev) | via docker compose | 7880 |

Set `CLIENT_ID=retras` (or any client directory under `clients/`) in `.env` to route local traffic to a specific client graph.

## Environment variables

Copy `.env.example` at the repo root to `.env` and fill in values. Never commit `.env` files.

Key variables to configure for local dev:
- `ANTHROPIC_API_KEY` — required by all agent services (Claude)
- `OPENAI_API_KEY` — required for knowledge-base embeddings (`text-embedding-3-small`)
- `CLIENT_ID` — which client graph to load (e.g. `retras`)
- `ELEVENLABS_API_KEY` — required for voice synthesis
- `DEEPGRAM_API_KEY` — required for voice STT
- `LIVEKIT_URL` / `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` — voice runtime (dev defaults: `ws://localhost:7880`, key=`devkey`, secret=`devsecret`)
- `TELNYX_*` — required for PSTN calls (skip for WhatsApp-only dev)
- `WHATSAPP_*` — required for WhatsApp messaging (use Meta test number)
- `DATABASE_URL` — `postgresql+asyncpg://storageidol:storageidol@localhost:5432/storageidol_dev`
- `REDIS_URL` — `redis://localhost:6379`
- `LANGFUSE_*` — auto-configured by the dev docker-compose; see `infrastructure/docker/docker-compose.dev.yml`

Full variable reference: `context/operations/env-vars.md`.

## Running tests

```bash
# Python — all packages and core services
uv run pytest core/ packages/

# Python — specific service or package
uv run pytest core/agents/

# TypeScript — all packages
pnpm test

# TypeScript — specific package
pnpm --filter=mcp-base test
```
