# Component: Ops

StorageIdol internal monitoring and auto-remediation platform.

**Location:** `ops/`  
**Runs on:** StorageIdol infrastructure (not on client servers)

## Sub-components

### alert-receiver
FastAPI service. Receives structured JSON alerts from all client watchdogs via `POST /alerts`. Validates the `OPS_TOKEN` in each request. Stores alerts in the ops database. Triggers the remediation agent.

Also tracks heartbeats: every watchdog pings `POST /heartbeat` every 5 minutes. If a client goes silent for >10 minutes, the system generates an "offline" alert automatically.

### remediation-agent
LangGraph loop triggered on each new alert. Workflow:
1. Load alert context
2. Query `knowledge/` for matching error pattern
3. If match: send signed remediation command to the watchdog → verify recovery
4. If no match: open GitHub issue + notify on-call

Every successfully resolved incident gets a new entry in `knowledge/` so it self-heals next time.

### dashboard
Next.js internal UI. Shows:
- Real-time health status of all client deployments
- Alert history per client
- Heartbeat status (online/offline)
- Auto-remediation activity log
- On-call schedule

## What ops never does

- Query client conversation data or user PII
- Connect directly to any client's Postgres or Redis
- Store raw application logs from client servers
