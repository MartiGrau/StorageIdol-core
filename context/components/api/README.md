# Component: API

The central REST API that receives all inbound webhooks (WhatsApp, Voice) and exposes endpoints for the dashboard and backoffice.

**App location:** `core/api/`

**Responsibilities:**
- Receive and validate WhatsApp Cloud API webhooks
- Receive and validate LiveKit voice session webhooks
- Create and resume LangGraph agent sessions
- Expose REST endpoints for dashboard (conversation history, client config, analytics)
- Expose REST endpoints for backoffice (client management, provisioning)
- Write to the audit log

**Key dependencies:** FastAPI, LangGraph, SQLAlchemy, Celery, Redis

**Owned by:** Backend team
