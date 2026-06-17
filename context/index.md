# Context Index

StorageIdol documentation. Read the file most relevant to your current task before making decisions.

## Company

| Topic | File |
|---|---|
| Mission and product philosophy | `company/mission.md` |
| Market problems we solve | `company/market-problems.md` |
| Business model | `company/business-model.md` |
| Commercial modules (products) | `company/products.md` |

## Architecture

| Topic | File |
|---|---|
| System topology and data flows | `architecture/overview.md` |
| Tech stack and library choices | `architecture/tech-stack.md` |
| Core vs. Client Graph vs. Config (critical read) | `architecture/core-vs-config.md` |
| Idempotency, checkpointing, cost guardrails | `architecture/runtime-fundamentals.md` |

## Compliance

| Topic | File |
|---|---|
| EU AI Act Art. 50 — AI disclosure obligations | `compliance/eu-ai-act.md` |

## Components

| Component | File |
|---|---|
| AI agents and composable modules | `components/agents/README.md` |
| FastAPI and webhooks | `components/api/README.md` |
| Client MCP servers | `components/mcp/README.md` |
| Monitoring, ops, auto-remediation | `components/ops/README.md` |
| Client dashboard | `components/dashboard/README.md` |
| Internal backoffice | `components/backoffice/README.md` |

## Operations

| Topic | File |
|---|---|
| Local development setup | `operations/development.md` |
| Deploying to a client server | `operations/deployment.md` |
| Database (external managed Postgres, DEV+PROD) | `operations/database.md` |
| Disaster recovery (lost server / DB / Redis) | `operations/disaster-recovery.md` |
| Onboarding a new client (process) | `operations/client-onboarding.md` |
| Environment variables reference | `operations/env-vars.md` |
| Monitoring, alerts, incident response | `operations/monitoring.md` |

## Clients

Client data lives outside `context/` — company-wide docs and per-client work are strictly separated.

| Topic | Location |
|---|---|
| All active clients (status, modules) | `clients/index.md` |
| Per-client profile, requirements, meetings | `clients/<client-id>/` |
| New client template | `clients/_template/` |
| What gets deployed to client server | `deploy/clients/<client-id>/` |

**When working on a specific client**, read in this order:
1. `clients/<client-id>/profile.md`
2. `clients/<client-id>/requirements/` (all files)
3. `clients/<client-id>/decisions.md`
4. Meetings only if the above leave gaps

## Rules

- `architecture/core-vs-config.md` is the most important file in this directory. Read it before any structural decision.
- `clients/<client-id>/decisions.md` records why the config is the way it is. Do not override without explicit instruction.
- Never put client-specific information inside `context/`.
