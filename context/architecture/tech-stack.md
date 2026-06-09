# Tech Stack

## Languages & runtimes

| Layer | Language | Runtime |
|---|---|---|
| AI agents | Python | 3.11+ |
| REST API | Python | FastAPI |
| Dashboard / Backoffice | TypeScript | Next.js 14 |
| MCP servers | TypeScript | Node.js 20+ |
| Infrastructure scripts | Bash / Python | — |

## Core frameworks & libraries

| Purpose | Library |
|---|---|
| Agent orchestration | LangGraph (Python) |
| LLM inference | Anthropic Claude (claude-sonnet-4-6 default) |
| Voice synthesis | ElevenLabs Python SDK |
| Telephony | Twilio Python / Node SDK |
| WhatsApp messaging | WhatsApp Cloud API (REST) |
| API framework | FastAPI + Pydantic v2 |
| Task queue | Celery + Redis |
| Database ORM | SQLAlchemy 2 (async) |
| Frontend framework | Next.js 14 + Tailwind CSS |

## Infrastructure

| Component | Service |
|---|---|
| Database | PostgreSQL (primary) |
| Cache / broker | Redis |
| File storage | S3-compatible (AWS S3 or MinIO) |
| Containerization | Docker + Docker Compose (dev), Kubernetes (prod) |
| CI/CD | GitHub Actions |
| Secrets | Environment variables (`.env` per service) |
| Monitoring | (TBD — see `operations/monitoring.md`) |

## Third-party services

| Service | Purpose | Docs |
|---|---|---|
| Anthropic Claude | LLM backbone for all agents | anthropic.com/docs |
| ElevenLabs | Voice synthesis | elevenlabs.io/docs |
| Twilio | Voice calls + SMS | twilio.com/docs |
| WhatsApp Cloud API | WhatsApp messaging | developers.facebook.com/docs/whatsapp |
| Stripe | Payment link generation | stripe.com/docs |

## Model policy

- Default model: `claude-sonnet-4-6`
- High-reasoning tasks (complex debt negotiation flows): `claude-opus-4-8`
- High-volume classification tasks: `claude-haiku-4-5-20251001`
- Always use the latest available model from each tier — see CLAUDE.md for current IDs.
