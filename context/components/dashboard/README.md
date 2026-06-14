# Component: Client Dashboard

The client-facing web application. Each client accesses their own instance via their dedicated subdomain.

**App location:** `core/dashboard/` (built into each client's Docker stack; reads only that client's data)

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
