# Disaster Recovery

What to do when something is lost. The architecture is designed so that the container
server is **stateless and disposable** — all durable data lives in the external managed
database (see `database.md`). That single fact makes most "disasters" routine redeploys.

## Recovery targets

| | Target | Why achievable |
|---|---|---|
| **RPO** (data loss) | ≈ 0 for durable data | System of record is the managed DB with provider PITR; the server holds no durable state |
| **RTO** (time to restore) | < 30 min for a lost server | Redeploy stateless images + reconnect `DATABASE_URL` + repoint DNS |

## What must exist off-server (the only things you cannot regenerate)

1. **The client's `.env`** — holds `DATABASE_URL` and every API secret. Store a copy in
   StorageIdol's secret manager at provision time. **Without it, recovery is slow** (you
   must re-collect every credential). This is the single most important backup.
2. **The deploy artefact** — `deploy/clients/<client-id>/docker-compose.yml` is already in
   the repo. The image tags are pinned, so the exact running version is reproducible.
3. **Managed DB** — backups/PITR are the provider's responsibility (RDS/Supabase/Neon/etc.).
   Verify automated backups are enabled at onboarding; this is a go-live checklist item.

## Scenarios

### 1. A single container crashes
Auto-handled. `restart: unless-stopped` brings it back; the watchdog only escalates on a
crash-loop (>3 restarts / 5 min) or a stopped-and-not-restarting container. Usually no
human action — investigate the alert, roll back the image tag if a bad release.

### 2. The whole server is lost (hardware, provider outage, accidental deletion)
The durable data is safe in the managed DB. Recover the compute:
1. Provision a new server (or, for StorageIdol-hosted, `scripts/provision-vps.sh <client-id>`).
2. Install Docker; copy `deploy/clients/<client-id>/docker-compose.yml`.
3. Restore the client's `.env` from the secret manager (same `DATABASE_URL` → same data).
4. `docker login registry.storageidol.com` and `docker compose up -d`.
5. Repoint the client's DNS / reverse proxy to the new server IP.
6. Confirm `GET /health` is green and the watchdog heartbeat resumes at `ops.storageidol.com`.

No data restore step is needed — the new containers attach to the existing managed DB
with full history intact.

### 3. The managed database has a problem
This is the provider's domain, which is the point of externalizing it:
- **Corruption / bad migration / accidental delete** → restore via the provider's
  point-in-time recovery to just before the event. Because migrations are additive and
  backward-compatible (see `database.md`), the current image keeps working after a restore.
- **Instance outage** → provider failover (multi-AZ on RDS, Supabase HA, etc.). The app
  reconnects automatically once the endpoint is back; in-flight requests retry.
- Update `DATABASE_URL` only if the provider issues a new endpoint after restore.

### 4. Redis is lost
Recreated empty on restart automatically. The cost is bounded and acceptable:
- In-flight Celery tasks not yet processed (at most a few unprocessed inbound messages —
  WhatsApp/Meta will have the delivery; users can resend).
- Idempotency keys in their 24h window (worst case: a replayed webhook is processed twice;
  the debt-stage event ID `(client_id, case_id, stage)` and Postgres checkpoint locking
  still guard against duplicate debt sends).
- **No durable data is in Redis** — it is broker + ephemeral coordination only. This is
  exactly why it stays a local container rather than a managed service.

## Drill

Test scenario 2 against a staging deployment quarterly: destroy the server, rebuild from
`.env` + compose, confirm conversation history is intact from the managed DB. A recovery
path that has never been exercised is not a recovery path.
