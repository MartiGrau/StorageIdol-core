# Agent: provision-client

Triggered by the `/new-client <client-id>` skill. Onboards a new client from scratch.

## Prerequisites before running

The following file must exist and be filled in:
```
clients/<client-id>/profile.md
```

If it doesn't exist, copy from `clients/_template/profile.md` and fill it in first.

## What this agent does

Read `clients/<client-id>/profile.md` in full before doing anything else.

### Step 1 — Scaffold directory structure

Copy `clients/_template/` to `clients/<client-id>/` (skip files that already exist).

### Step 2 — Write config.yaml

From `profile.md`, extract:
- Modules required (customer_service, debt_collection, lead_management, voice)
- CRM type and authentication method
- WhatsApp Business Account info
- Voice language and preferred tone
- D+N thresholds if debt_collection is enabled
- Escalation contacts

Write `clients/<client-id>/config.yaml` with all known values. Leave placeholder comments for values the client must provide.

### Step 3 — Generate the client graph

Read `core/agents/modules/README.md` to understand available modules.

Based on the modules listed in profile.md, generate `clients/<client-id>/graph.py`:
- Import only the modules that this client needs
- Wire the graph with correct routing conditions
- Add a comment block at the top explaining why each module was included

Run: `pytest clients/<client-id>/tests/test_graph.py` — if the file doesn't exist yet, create a basic smoke test first.

### Step 4 — Build the MCP

Call the `build-mcp` agent: read `.claude/agents/build-mcp.md` and execute it for this client.

### Step 5 — Generate WhatsApp templates

If debt_collection is enabled:
- Read `clients/<client-id>/requirements/flows.md` for tone and content guidelines
- Generate `clients/<client-id>/debt-templates.yaml` with 4 templates (D+3, D+10, D+20, D+30)
- Each template must comply with Meta's template policy (no threats, clear opt-out)

If customer_service is enabled:
- Generate any proactive template messages (e.g. post-visit follow-up)

### Step 6 — Generate deploy config

Run: `scripts/provision-client.sh <client-id>`

This generates `deploy/clients/<client-id>/docker-compose.yml` from the template, substituting CLIENT_ID and pinning the current image VERSION.

### Step 7 — Open PR

Stage all generated files. Write a PR description that lists:
- Which modules were included and why
- What the client must still provide (credentials, approved templates)
- Estimated go-live dependencies (template approval timeline, CRM endpoint availability)

## What this agent must NOT do

- Commit secrets or real API keys
- Access any other client's directory
- Modify anything in `core/` or `packages/`
