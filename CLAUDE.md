# StorageIdol Core — Agent Entry Point

You are working inside **StorageIdol-core**, the company monorepo for StorageIdol.

## What is StorageIdol?

StorageIdol builds AI-powered agent systems for real estate and debt-collection companies. The product philosophy is **"Core + Configuration"**: a pre-built multi-agent framework (LangGraph, ElevenLabs, Twilio, WhatsApp Cloud API) that is deployed and configured per client — not rebuilt from scratch.

Three commercial modules:
1. **Customer Service 24/7** — Voice + WhatsApp agent, multilingual, human escalation
2. **Lead Management** — Capture → qualify → nurture → schedule → hand off to sales
3. **Debt Collection** — Staged scheduler (D+3/10/20/30), WhatsApp + AI calls, payment link integration

## Repo layout

```
apps/          # Deployable services (api, dashboard, backoffice, mcps, agents)
packages/      # Shared libraries reused across apps
infrastructure/ # Docker, cloud configs, CI/CD
scripts/       # Dev and ops utility scripts
context/       # AI-readable documentation (start here for any context)
clients/       # Per-client data: profile, requirements, meetings, decisions
.claude/       # Claude Code config (agents, hooks, skills, settings)
```

## Where to find context

**Always read `context/index.md` first** — it maps every topic to the right file.

Key files:
- `context/company/mission.md` — company goal and product philosophy
- `context/company/market-problems.md` — problems we solve
- `context/architecture/overview.md` — system design, agent topology
- `context/architecture/tech-stack.md` — languages, frameworks, services
- `context/operations/development.md` — how to run things locally
- `context/operations/deployment.md` — how deployments work

**Working on a specific client?** Go to `clients/<client-id>/` — not `context/`. Read `clients/README.md` first if unfamiliar with the structure.

## How to work in this repo

- Each app under `apps/` has its own README.md with local setup instructions.
- Shared code lives in `packages/` — prefer importing from there over duplicating logic.
- Never hardcode secrets; use environment variables documented in each app's `.env.example`.
- Before adding a new app or package, check `context/index.md` to avoid duplication.
