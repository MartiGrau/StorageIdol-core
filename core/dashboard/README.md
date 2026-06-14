# Dashboard

Client-facing Next.js application. Each client deployment gets their own instance.

**Language:** TypeScript | **Framework:** Next.js 14 + Tailwind CSS | **Port:** 3000

## What clients can see here

- **Conversations** — Full history of WhatsApp and voice interactions, searchable by contact, date, intent
- **Debt cases** — Status of all open debt collection expedients, stage, last contact, outcome
- **Analytics** — Conversation volume, resolution rate, escalation rate, top intents, geographic breakdown by location
- **Alerts** — Pattern detection: recurring complaint categories, anomalous contact volume, unresolved escalations

## What it does NOT expose

- Other clients' data (impossible — this instance only connects to this client's API)
- Raw system logs or infrastructure metrics (those go to `ops/`)

## Structure

```
dashboard/
├── package.json
├── .env.example
├── app/
│   ├── conversations/
│   ├── debt/
│   ├── analytics/
│   └── alerts/
├── components/
└── lib/
    └── api.ts    # Typed client for core/api internal endpoints
```

## Local setup

```bash
cp .env.example .env
npm install
npm run dev  # Port 3000
```
