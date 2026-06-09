# Backoffice

Next.js 14 internal tool for StorageIdol team.

See `context/components/backoffice/README.md` for full component documentation.

## Local setup

```bash
cp .env.example .env
npm install
npm run dev
# Runs on http://localhost:3001
```

## Structure (to be defined as development starts)

```
apps/backoffice/
├── package.json
├── .env.example
├── app/
│   ├── clients/
│   ├── health/
│   ├── audit/
│   └── billing/
├── components/
└── lib/
```
