# Local Development

## Prerequisites

- Docker + Docker Compose
- Python 3.11+
- Node.js 20+
- `gh` CLI (authenticated)

## First-time setup

```bash
# 1. Copy environment files
cp apps/api/.env.example apps/api/.env
cp apps/dashboard/.env.example apps/dashboard/.env

# 2. Start infrastructure (Postgres, Redis)
docker compose -f infrastructure/docker/docker-compose.dev.yml up -d

# 3. Install Python dependencies (api + agents)
cd apps/api && pip install -r requirements.txt
cd apps/agents && pip install -r requirements.txt

# 4. Install JS dependencies (dashboard + mcps)
cd apps/dashboard && npm install
cd apps/mcps && npm install

# 5. Run DB migrations
cd apps/api && alembic upgrade head
```

## Running services locally

Each service has its own start command documented in its `README.md`. The typical dev stack:

| Service | Command | Port |
|---|---|---|
| API | `uvicorn main:app --reload` | 8000 |
| Agents (worker) | `celery -A tasks worker --loglevel=info` | — |
| Dashboard | `npm run dev` | 3000 |
| Backoffice | `npm run dev` | 3001 |
| MCP servers | `npm run dev` | varies |

## Environment variables

Each app has a `.env.example` — copy to `.env` and fill in values. Never commit `.env` files.

Key variables to configure for local dev:
- `ANTHROPIC_API_KEY` — required by all agent services
- `ELEVENLABS_API_KEY` — required for voice synthesis
- `TWILIO_*` — required for telephony (use Twilio dev credentials)
- `WHATSAPP_*` — required for WhatsApp messaging (use Meta test number)
- `DATABASE_URL` — points to local Postgres
- `REDIS_URL` — points to local Redis

## Running tests

```bash
# Python (api + agents)
pytest apps/api/tests/
pytest apps/agents/tests/

# TypeScript (dashboard + mcps)
npm test --workspace=apps/dashboard
npm test --workspace=apps/mcps
```
