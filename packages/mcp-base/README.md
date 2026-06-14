# Package: mcp-base

Base MCP (Model Context Protocol) server class that every client MCP extends.

**Language:** TypeScript | **Key dependency:** `@modelcontextprotocol/sdk`

## What it provides

- `BaseMCPServer` — Abstract class with:
  - Auth middleware (validates that requests come from StorageIdol agents)
  - Standard error handling and logging
  - Health endpoint
  - Tool registration helpers
- `createTool(name, description, inputSchema, handler)` — Type-safe tool factory
- `MCPClient` (Python) — Used by agents to call MCP tools

## How client MCPs extend this

```typescript
// clients/retras/mcp/index.ts
import { BaseMCPServer, createTool } from '@storageidol/mcp-base';

const server = new BaseMCPServer({ clientId: 'retras' });

server.registerTool(createTool(
  'get_client_by_phone',
  'Look up a Retras client by phone number',
  { phone: { type: 'string' } },
  async ({ phone }) => { /* call Retras REST API */ }
));

server.start();
```

Client MCPs never import from `core/` or from other clients.
