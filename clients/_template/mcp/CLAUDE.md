# MCP Agent Briefing

You are working on the MCP server for client `<CLIENT_ID>`. This is the integration layer between StorageIdol agents and the client's own CRM/PMS API.

## What you must know before editing

1. Read `clients/<CLIENT_ID>/requirements/integrations.md` — it lists all available endpoints
2. Read `clients/<CLIENT_ID>/profile.md` — it explains the client's business and auth model
3. Read `packages/mcp-base/README.md` — it defines the base class you extend

## Rules

- Only add tools for endpoints listed in `requirements/integrations.md`
- If an agent module needs data that doesn't have an endpoint yet, add a note in `requirements/integrations.md` under "Missing endpoints" — do not call non-existent endpoints
- Every tool needs a test. If you add a tool, add its test before finishing
- Run `npm test` before considering any change done

## Auth model for this client

See `clients/<CLIENT_ID>/profile.md` → Authentication section.
