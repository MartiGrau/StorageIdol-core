# Component: MCP Servers

Model Context Protocol servers that expose StorageIdol data and actions to Claude agents (both internal and client-facing).

**App location:** `apps/mcps/`

**MCP servers planned:**
- `storage-crm` — read/write contacts, conversations, and deal stages
- `storage-scheduler` — trigger and inspect debt collection scheduler jobs
- `storage-knowledge` — query per-client knowledge base
- `storage-analytics` — pull conversation metrics and KPIs

**Key dependencies:** `@anthropic-ai/sdk`, MCP SDK (TypeScript)

**Note:** MCP servers are the bridge that allows Claude Code agent loops to operate directly on live StorageIdol data without a REST API call. This enables the automated agent workflows described in `CLAUDE.md`.

**Owned by:** Platform team
