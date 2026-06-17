# Client Profile: [Company Name]

## Identity

| Field | Value |
|---|---|
| Client ID | `<client-id>` |
| Company | — |
| Industry | Real estate / Financial / Other |
| Company size | e.g. "120 rental units", "€2M debt portfolio" |
| Region / language | e.g. "Spain — Spanish + Catalan" |
| CRM | e.g. HubSpot, Salesforce, custom |
| Status | prospect / onboarding / live / churned |
| Go-live date | YYYY-MM-DD (or "TBD") |

## Key contacts

| Name | Role | Email | Phone | Notes |
|---|---|---|---|---|
| — | Main contact | — | — | — |
| — | Technical contact | — | — | — |
| — | Billing contact | — | — | — |

## Contracted modules

- [ ] Module 1 — Customer Service 24/7
- [ ] Module 2 — Lead Management & Nurturing
- [ ] Module 3 — Debt Collection & Recovery

## Infrastructure pointers

- Config file: `infrastructure/clients/<client-id>/config.yaml`
- Subdomain: `<client-id>.storageidol.com` (when live)
- Hosting tier: `client` | `storageidol`
- Database: external managed PostgreSQL 16+ (pgvector), client-owned — **two instances: DEV + PROD**. Provider and connection details in `requirements/integrations.md`. See `context/operations/database.md`.

## Quick summary

_(2–3 sentences: who they are, what problem they hired StorageIdol to solve, any important context an agent should know before doing any work for this client.)_
