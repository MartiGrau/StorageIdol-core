# Backoffice

StorageIdol internal operations UI. Not deployed to client servers — runs on StorageIdol infrastructure only.

**Language:** TypeScript | **Framework:** Next.js 14 + Tailwind CSS | **Port:** 3001

## What it exposes

- **Client registry** — All active deployments, their status, go-live date, modules enabled
- **Deployment health** — Aggregated view from `ops/` alert receiver (mirrors what the ops dashboard shows)
- **Onboarding pipeline** — Track new client onboarding steps: config ready → templates submitted → staging tested → live
- **Usage and billing** — Token consumption, conversation counts, cost per client
- **Knowledge base editor** — Upload and manage FAQ documents for any client

## Local setup

```bash
cp .env.example .env
npm install
npm run dev  # Port 3001
```
