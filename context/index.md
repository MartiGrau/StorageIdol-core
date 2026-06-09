# Context Index

Quick navigation map for any AI agent or developer. Find the topic below and jump directly to the right file.

## Company & Product
| Topic | File |
|---|---|
| Mission, vision, product philosophy | `company/mission.md` |
| Market problems we solve | `company/market-problems.md` |
| The three commercial modules | `company/products.md` |
| Business model and pricing logic | `company/business-model.md` |

## Architecture & Tech
| Topic | File |
|---|---|
| System design, agent topology, data flow | `architecture/overview.md` |
| Languages, frameworks, third-party services | `architecture/tech-stack.md` |
| Core vs Configuration layer explained | `architecture/core-vs-config.md` |

## Components (per app)
| App | Context folder |
|---|---|
| REST API (core backend) | `components/api/` |
| AI Agents (LangGraph) | `components/agents/` |
| MCP servers | `components/mcp/` |
| Client Dashboard | `components/dashboard/` |
| Internal Backoffice | `components/backoffice/` |
| WhatsApp / Voice integrations | `components/integrations/` |

## Operations
| Topic | File |
|---|---|
| Local development setup | `operations/development.md` |
| Deployment process | `operations/deployment.md` |
| New client onboarding | `operations/client-onboarding.md` |
| Environment variables reference | `operations/env-vars.md` |
| Monitoring and alerts | `operations/monitoring.md` |

## Clients

Client data lives outside `context/` to keep company-wide docs separate from per-client work.

| Topic | Location |
|---|---|
| All clients at a glance (status, modules) | `clients/index.md` |
| How to use the client folder system | `clients/README.md` |
| Per-client profile, requirements, meetings | `clients/<client-id>/` |
| Template for a new client | `clients/_template/` |
| Deployed client configuration | `infrastructure/clients/<client-id>/config.yaml` |

**When doing any work for a specific client**, read in this order:
1. `clients/<client-id>/profile.md`
2. `clients/<client-id>/requirements/` (all files)
3. `clients/<client-id>/decisions.md`
4. Raw meetings/emails only if the above leave gaps

## Rules
- Always check this index before searching the repo for context.
- Each component folder contains a `README.md` explaining that component only.
- `architecture/overview.md` is the single source of truth for system design decisions.
- `clients/<client-id>/decisions.md` is the source of truth for why a client's config is the way it is — do not override decisions recorded there without explicit instruction.
