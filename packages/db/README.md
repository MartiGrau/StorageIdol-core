# Package: db

Shared SQLAlchemy models and database utilities used by `core/api/` and `core/agents/`.

**Language:** Python | **Key dependencies:** `sqlalchemy[asyncio]`, `alembic`, `asyncpg`

## What it provides

- `Base` — Declarative base for all ORM models
- `get_session()` — Async session factory
- Shared models:
  - `Contact` — phone, client_id, brand_id, metadata
  - `Conversation` — thread_id, channel (whatsapp/voice), state, client_id
  - `Message` — direction (inbound/outbound), body, timestamp, conversation_id
  - `DebtCase` — case_id, contact_id, stage (D+N), amount, status, last_action_at
  - `Lead` — contact_id, qualification_state, assigned_to, created_at

## Multi-tenant isolation

Every model includes `client_id`. All queries in `core/api/` and `core/agents/` are scoped by `client_id` extracted from the inbound request context. There is no cross-client query path.

Since each client deployment has its own Postgres instance (separate Docker container), the `client_id` column is a safety net — not the primary isolation mechanism.
