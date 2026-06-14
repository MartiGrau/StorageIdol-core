# Core — The Platform Framework

This directory contains the shared platform code. It is StorageIdol's intellectual property and is reused across every client deployment.

## What lives here

| Directory | Purpose |
|---|---|
| `api/` | FastAPI application — all inbound webhooks and internal REST endpoints |
| `agents/` | LangGraph agent system — orchestrator + composable behavior modules |
| `dashboard/` | Next.js app — client-facing conversation and analytics dashboard |
| `backoffice/` | Next.js app — StorageIdol internal ops and client management |
| `watchdog/` | Lightweight monitoring sidecar — deployed alongside every client |

## What does NOT live here

- Client-specific prompts, thresholds, or routing logic → `clients/<id>/`
- Client CRM connectors (MCPs) → `clients/<id>/mcp/`
- Deployment configuration for a specific client → `deploy/clients/<id>/`

## The module contract

`agents/modules/` contains independent subgraphs. Each module:
- Has a single, well-defined responsibility
- Accepts a typed `AgentState` input and returns a typed output
- Has its own tests that can run in isolation without a full client config
- Documents which inputs it requires and which state keys it sets

A client graph lives at **`clients/<id>/graph.py`** (client-owned code, not here). The Core layer only provides `agents/graphs/registry.py` — a registry that discovers and imports client graphs by `client_id` at runtime. The registry lives here; the graph definitions do not.
