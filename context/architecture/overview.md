# Architecture Overview

## System topology

```
                    ┌──────────────────────────────────────┐
                    │  Client Server (per deployment)       │
                    │                                       │
  WhatsApp ────────►│  core/api  ──► Celery task ──► LangGraph
  Voice ───────────►│                               (client graph)
  Debt trigger ────►│                                    │
                    │                         ┌──────────┴──────────┐
                    │                    modules/*            mcp/<client>
                    │                    (Core layer)    (client CRM adapter)
                    │                                               │
                    │  core/watchdog ──────────────► ops.storageidol.com
                    └──────────────────────────────────────────────┘
```

## Layer definitions

### Core (`core/`)
Shared platform code. Deployed as Docker images. Same image runs for every client.

| Component | Role |
|---|---|
| `core/api` | FastAPI — inbound webhooks (WhatsApp, Voice, Debt triggers), internal REST |
| `core/agents` | LangGraph orchestrator + composable module subgraphs |
| `core/dashboard` | Next.js — client-facing analytics and conversation history |
| `core/backoffice` | Next.js — StorageIdol internal ops UI |
| `core/watchdog` | Python monitoring sidecar — health checks, alert shipping, heartbeat |

### Composable modules (`core/agents/modules/`)
Independent LangGraph subgraphs. Each has a single responsibility and its own tests. A client graph wires selected modules together. No module contains client-specific logic.

| Module | Purpose |
|---|---|
| `auth/phone_dni` | Identity validation |
| `intent/storage` | Storage domain intent classifier |
| `intent/financial` | Financial domain intent classifier |
| `conversation/faq_rag` | Knowledge base RAG answering |
| `conversation/crm_lookup` | CRM data retrieval via MCP |
| `debt/soft` | Debt recovery: negotiate, extend, recover possession |
| `debt/hard` | Debt recovery: escalate to legal |
| `lead/qualify_storage` | Storage lead qualification |
| `escalation/human_handoff` | Human escalation with context |
| `voice/bridge` | Real-time voice STT/TTS bridge |

### Client configuration (`clients/<id>/`)
Per-client data. Never deployed to other clients. Contains:
- `profile.md` — Business context and requirements
- `config.yaml` — Non-sensitive settings (modules, thresholds, voice ID)
- `graph.py` — The client's LangGraph composition (which modules, how wired)
- `knowledge-base/` — RAG documents
- `debt-templates.yaml` — WhatsApp templates for Meta
- `mcp/` — TypeScript MCP server for this client's CRM API

### Client deployment (`deploy/clients/<id>/`)
What gets sent to the client's server:
- `docker-compose.yml` — References registry images, no source code
- `.env.example` — Template for the client to fill in their secrets

### Ops (`ops/`)
StorageIdol internal monitoring. Receives alerts from all client watchdogs. Auto-remediates known failures. Never contains client data.

## Data flow — WhatsApp Customer Service

1. User sends WhatsApp → Meta webhook → `core/api` `/webhook/whatsapp`
2. API validates signature, extracts `phone_number_id` → determines `client_id`
3. API enqueues Celery task with message payload
4. Celery worker loads client graph from `clients/<id>/graph.py`
5. Orchestrator classifies intent → routes to correct module chain
6. Module chain may call MCP tools (CRM lookup, auth validation)
7. Agent generates reply → `packages/whatsapp` sends it
8. Interaction summary POSTed back to client CRM via MCP `post_interaction_summary`

## Data flow — Debt collection trigger

1. Client CRM detects overdue payment → POST `core/api` `/trigger/debt`
2. API validates request signature, extracts `case_id`, `contact_phone`, `stage`
3. Debt collection agent loads correct stage template from `clients/<id>/debt-templates.yaml`
4. Sends WhatsApp template message via `packages/whatsapp`
5. If voice stage: `packages/voice` places outbound Twilio call
6. Client response (if any) resumes the LangGraph session

## Multi-brand isolation

Each brand (e.g. Retras and Citium) is treated as a separate client with a separate deployment, separate Docker stack, and separate Postgres instance. Routing is by phone number — each brand's WhatsApp number maps to one deployment.
