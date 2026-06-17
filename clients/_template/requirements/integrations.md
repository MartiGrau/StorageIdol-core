# Integration Specs: [Company Name]

Technical details for all third-party integrations required by this client.

## Database (external, managed — required)

Managed PostgreSQL 16+ with `pgvector`, owned by the client. Two separate databases.
Not Astra DB. See `context/operations/database.md`.

| Field | DEV | PROD |
|---|---|---|
| Provider (RDS/Supabase/Neon/Hetzner/Cloud SQL/Azure) | — | — |
| Host / region | — | — |
| pgvector available | yes/no | yes/no |
| Connection string location | DEV server `.env` | PROD server `.env` |

## CRM

| Field | Value |
|---|---|
| CRM name | e.g. HubSpot, Salesforce, custom |
| Integration method | REST API / Webhook / File export |
| API base URL | — |
| Auth method | API key / OAuth / Basic |
| Key objects | e.g. "Contact, Deal, Activity" |
| Contacts to sync | e.g. "all contacts with tag 'tenant'" |
| Fields to read | list the fields the agent needs |
| Fields to write | list the fields the agent will update |
| Unpaid invoice endpoint | (Module 3) URL or query to get overdue invoices |

## Calendar (Module 1 / 2 — visit scheduling)

| Field | Value |
|---|---|
| Calendar system | Google Calendar / Outlook / Calendly / Other |
| Integration method | — |
| Available slot source | — |
| Booking confirmation method | — |

## Payment gateway (Module 3)

| Field | Value |
|---|---|
| Provider | Stripe / Other |
| Link format | — |
| Prefilled fields | amount, client name, reference |
| Confirmation webhook | URL where payment events are sent |

## WhatsApp

| Field | Value |
|---|---|
| Business Account ID | — |
| Phone number | — |
| Approved templates | list names and use cases |
| Template submission status | pending / approved / rejected |

## Other integrations

_(Add any client-specific integrations not covered above.)_
