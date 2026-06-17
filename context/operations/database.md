# Database

## Principle: durable data lives outside the container server

The primary application database is **external and managed by the client** — it is
**not** a container in the `deploy/_template/` stack. The client server runs only
**stateless** services (api, agents, voice, mcp, dashboard, watchdog, redis). All
durable data — conversations, transcripts, user PII, lead/debt records, LangGraph
checkpoints, and FAQ knowledge-base embeddings — lives in the managed database.

This separation is a hard requirement, not a preference. It is what makes the
container server disposable:

- **Server dies →** redeploy the same images on a new server, point `DATABASE_URL`
  at the same managed DB, and full history is intact (near-zero data loss).
- **Backups, point-in-time recovery, failover, patching** are handled by the managed
  provider, not by StorageIdol or the client's ops.
- **Container bugs cannot corrupt durable data** beyond what the schema allows — the
  data layer has its own lifecycle, isolation, and access controls.

## Requirement

Each client must provide a **managed PostgreSQL 16+ instance with the `pgvector`
extension available** (pgvector backs the FAQ RAG module — there is no separate
vector store).

| Compatible | Not compatible |
|---|---|
| AWS RDS for PostgreSQL | Astra DB (Cassandra — no Postgres wire protocol, no pgvector) |
| Supabase | Any Cassandra / DynamoDB / Mongo-style store |
| Neon | MySQL / MariaDB (no pgvector, dialect mismatch) |
| Hetzner managed Postgres | |
| Google Cloud SQL (Postgres) | |
| Azure Database for PostgreSQL | |

The platform connects with SQLAlchemy 2 async (`asyncpg`). The connection string must
use the `postgresql+asyncpg://` form and, for managed providers, request TLS
(`?ssl=require`).

## Two environments per client: DEV and PROD

Provision **two separate managed databases** per client:

| Environment | Purpose | `ENVIRONMENT` | Connection string lives in |
|---|---|---|---|
| **DEV / staging** | Integration tests, client demos, migration dry-runs | `development` / `staging` | the staging server's `.env` (or `.env.dev` locally) |
| **PROD** | Live client traffic | `production` | the production server's `.env` |

They are distinct databases (ideally distinct instances), never schemas in the same
database — this guarantees a migration or load test in DEV can never touch live data.
`DATABASE_URL` and `ENVIRONMENT` must always agree; the api refuses to start on a
mismatch (e.g. `ENVIRONMENT=production` pointed at a DB whose name contains `dev`).

## Migrations

- Run with Alembic against each environment independently: validate on DEV first,
  then PROD as part of the deploy workflow.
- Migrations must be **backward-compatible / additive** (add nullable columns, never
  drop-and-recreate in a single release). This keeps image rollback safe even after a
  migration has already run against the managed DB.

## What this changes about isolation and access

- The client **owns** the database and its credentials. The connection string lives
  only in the client's `.env` on their server. StorageIdol does **not** hold it as a
  standing credential — preserving zero-standing-access (see `monitoring.md`).
- Physical isolation between clients is now enforced at the managed-DB level: each
  client has their own instance, billed and access-controlled by them.
- Multi-brand clients (e.g. Retras + Citium) get one managed database per brand, same
  as today — routing is still by phone number.

## What stays local (and why)

| Service | Local? | Reason |
|---|---|---|
| Redis | Yes | Ephemeral Celery broker / cache; losing it costs only in-flight tasks |
| Langfuse Postgres | Yes | Reconstructable observability data, not the system of record. May be externalized for the StorageIdol-hosted tier. |
