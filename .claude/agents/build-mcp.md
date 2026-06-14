# Agent: build-mcp

Generates a fully functional MCP server for a client from their API specification.

## Input

Either:
- An OpenAPI/Swagger spec file path (e.g. `clients/<client-id>/requirements/api-spec.json`)
- A Postman collection file path
- A plain-text endpoint list in `clients/<client-id>/requirements/integrations.md`

## What this agent does

### Step 1 — Read the integration requirements

Read `clients/<client-id>/requirements/integrations.md`. Identify:
- All available endpoints
- Authentication method (API key, OAuth, phone+DNI, etc.)
- Which endpoints are relevant for each enabled module (auth, CRM lookup, debt trigger, etc.)

### Step 2 — Read the base MCP package

Read `packages/mcp-base/README.md` to understand the base class and `createTool` factory.

### Step 3 — Generate MCP tools

For each relevant endpoint, generate a tool in `clients/<client-id>/mcp/tools/`:

```
clients/<client-id>/mcp/tools/
├── auth.ts          # validate_client(phone, dni) → ClientRecord | null
├── contracts.ts     # get_contracts(client_id) → Contract[]
├── invoices.ts      # get_invoices(client_id) → Invoice[], get_payment_link(invoice_id) → string
├── debt.ts          # get_open_cases(client_id) → DebtCase[], update_case_note(case_id, note)
└── crm.ts           # post_interaction_summary(client_id, summary)
```

Each tool must:
- Have a clear description that the LLM will use to decide when to call it
- Validate its inputs (Zod schema)
- Return typed output
- Handle API errors gracefully (return null or empty array, never throw to the agent)

### Step 4 — Generate the MCP index

Write `clients/<client-id>/mcp/index.ts` that imports all tools and registers them on `BaseMCPServer`.

### Step 5 — Generate tests

For each tool, write a test in `clients/<client-id>/mcp/tests/` using mock HTTP responses. Tests must:
- Cover the happy path
- Cover auth failure (401)
- Cover not-found (404)
- Cover timeout/network error

Run: `cd clients/<client-id>/mcp && npm test`

Iterate until all tests pass.

### Step 6 — Generate Dockerfile

Write `clients/<client-id>/mcp/Dockerfile`:
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist/ ./dist/
EXPOSE 3100
CMD ["node", "dist/index.js"]
```

## Output

A fully tested MCP server at `clients/<client-id>/mcp/` ready to be built into a Docker image.
