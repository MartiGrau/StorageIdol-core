# Dashboard

Next.js 14 client-facing web application.

See `context/components/dashboard/README.md` for full component documentation.

## Local setup

```bash
cp .env.example .env
npm install
npm run dev
# Runs on http://localhost:3000
```

## Structure (to be defined as development starts)

```
apps/dashboard/
├── package.json
├── .env.example
├── app/              # Next.js App Router
│   ├── (auth)/
│   ├── conversations/
│   ├── leads/
│   ├── debt/
│   └── settings/
├── components/
├── lib/
└── public/
```
