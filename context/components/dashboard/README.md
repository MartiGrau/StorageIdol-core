# Component: Client Dashboard

The client-facing web application. Each client accesses their own instance via their dedicated subdomain.

**App location:** `core/dashboard/` (built into each client's Docker stack, runs **on the client server**)

**How it reads data:** It is a presentation layer only — it never connects to Postgres
directly. It calls `core/api` over localhost, and the API owns the managed-DB
connection. This is why the dashboard stays on the client server rather than being
hosted centrally: keeping it local means no public API exposure, no CORS/cross-origin
auth, and StorageIdol holds zero client DB credentials (zero-standing-access). With the
database external and managed, a lost server is just redeployed — data is safe — so the
old "centralize for availability" argument no longer applies. StorageIdol's central
views (`backoffice`, `ops`) consume only non-PII aggregates, never raw conversations.

**Features:**
- Conversation history and transcripts (WhatsApp + calls)
- Live escalation queue (pending human handoffs)
- Lead pipeline view (Module 2)
- Debt portfolio status and collection funnel (Module 3)
- Basic config UI (knowledge base upload, template preview)
- Analytics: response rate, conversion rate, collection rate

**Key dependencies:** Next.js 14, Tailwind CSS, ShadCN UI, React Query

**Authentication:** Per-client credentials; each client can only see their own data.

**Owned by:** Frontend team
