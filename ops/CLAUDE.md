# Ops — Agent Briefing

This directory is StorageIdol's internal ops platform. It monitors all client deployments.

## What you are working with

- `alert-receiver/` — FastAPI app. Receives POSTs from client watchdogs. Stores alerts in DB. Triggers remediation agent.
- `remediation-agent/` — LangGraph agent. Runs on every new alert. Looks up known fixes. Either auto-remediates or escalates.
- `remediation-agent/knowledge/` — Markdown files, one per known error pattern. File name = error signature. Content = diagnosis + fix steps.
- `dashboard/` — Next.js app showing real-time health of all client deployments.

## When adding a new known fix to the knowledge base

Create a file `knowledge/<error-signature>.md` with:
```
# Error: <container> exits with code <N>

## Pattern
restart_count > 5, exit_code = 1, last_error contains "ConnectionRefused"

## Diagnosis
Database container started after API container. API failed to connect on boot.

## Automated fix
Send remediation command: restart api container with 10s delay

## Verification
Check api container status after 30s. Should be healthy.
```

## What you must never do here

- Query or access client conversation data
- Store any PII from client deployments
- Connect to a client's Postgres or Redis directly
