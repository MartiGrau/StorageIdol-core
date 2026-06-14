# Component: Internal Backoffice

StorageIdol internal tool for managing all clients, monitoring system health, and triggering provisioning operations.

**App location:** `core/backoffice/`

**Features:**
- Client list and status overview
- Per-client configuration editor (read/write `config.yaml` equivalents)
- Client provisioning and deprovisioning triggers
- System-wide health and error dashboard
- Audit log viewer
- WhatsApp template submission status
- Billing overview (setup fees, monthly recurring, usage)

**Key dependencies:** Next.js 14, Tailwind CSS, ShadCN UI

**Authentication:** StorageIdol team only. Separate auth from client dashboard.

**Owned by:** Platform / Ops team
