# StorageIdol Core — Agent Entry Point

You are working inside **StorageIdol-core**, the company monorepo for StorageIdol.

## What is StorageIdol?

StorageIdol builds AI-powered agent systems for companies with high-volume, repetitive client interactions — starting with self-storage operators (trasteros). The product is a **composable multi-agent platform** deployed per client via Docker images. Clients never receive source code — they receive running containers.

Three commercial modules:
1. **Customer Service 24/7** — WhatsApp + Voice agent, multilingual, human escalation
2. **Lead Management** — Capture → qualify → nurture → schedule → handoff to sales
3. **Debt Collection** — Staged D+N scheduler, WhatsApp + AI calls, payment link integration

## Critical architectural rules

**Rule 1 — Composable modules, not monolithic graphs.**
Agent behavior is built by wiring independent LangGraph subgraphs (`core/agents/modules/`). A client's graph is a composition of modules. Never put client-specific logic inside a module. Never assume all clients use all modules.

**Rule 2 — Clients never see other clients.**
Client configs live in `clients/<client-id>/`. Client MCPs are built into isolated Docker images. A bug in one client's MCP cannot affect another client. Data isolation is physical (separate servers, separate Postgres instances).

**Rule 3 — Context is documentation, not code.**
`context/` contains StorageIdol's own documentation (architecture, company, operations). Read it before making architectural decisions. Never put client-specific information in `context/`.

**Rule 4 — The deploy layer is what the client actually runs.**
`deploy/_template/` contains what a client server receives: a `docker-compose.yml` referencing registry images and a `.env.example`. The client fills in secrets. StorageIdol controls the images. The client never has source code.

## Repo layout

```
core/           # The platform framework — shared across all clients
  api/          # FastAPI: webhooks (WhatsApp, Voice), REST endpoints
  agents/       # LangGraph orchestration + composable module subgraphs
  dashboard/    # Next.js: client-facing conversation dashboard
  backoffice/   # Next.js: StorageIdol internal ops UI
  watchdog/     # Monitoring sidecar deployed alongside every client
packages/       # Shared libraries imported by core/ and client MCPs
  llm/          # Claude client wrapper (with prompt caching)
  whatsapp/     # WhatsApp Cloud API wrapper
  voice/        # ElevenLabs + Twilio wrapper
  mcp-base/     # Base MCP server (TypeScript) extended per client
  db/           # Shared SQLAlchemy models and migration helpers
clients/        # Per-client configs, MCPs, knowledge bases (INTERNAL ONLY)
  _template/    # Copy this when onboarding a new client
ops/            # StorageIdol internal ops platform (alert receiver, auto-remediation)
deploy/         # Templates for what gets deployed on client servers
  _template/    # docker-compose.yml + .env.example sent to client
infrastructure/ # Dev docker-compose, CI/CD pipelines
scripts/        # Provisioning and utility scripts
context/        # StorageIdol documentation — read before any architectural decision
.claude/        # Claude Code config: agents, hooks, skills
```

## Where to start for common tasks

| Task | Start here |
|---|---|
| Onboard a new client | `.claude/agents/provision-client.md` → run `/new-client` |
| Build an MCP for a client's API | `.claude/agents/build-mcp.md` → run `/build-mcp <client-id>` |
| Add a new agent behavior module | `core/agents/modules/README.md` |
| Understand client requirements | `clients/<client-id>/profile.md` + `requirements/` |
| Deploy to a client server | `deploy/_template/` + `scripts/build-image.sh` |
| Investigate a production alert | `ops/README.md` |
| Understand the full architecture | `context/architecture/overview.md` |
