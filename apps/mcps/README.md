# MCP Servers

Model Context Protocol servers that expose StorageIdol data and actions to Claude agent loops.

See `context/components/mcp/README.md` for full component documentation.

## Local setup

```bash
cp .env.example .env
npm install
npm run dev
```

## Structure (to be defined as development starts)

```
apps/mcps/
├── package.json
├── .env.example
├── servers/
│   ├── storage-crm/
│   ├── storage-scheduler/
│   ├── storage-knowledge/
│   └── storage-analytics/
└── shared/
```
