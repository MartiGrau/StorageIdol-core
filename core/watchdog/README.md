# Watchdog

Lightweight monitoring sidecar deployed alongside every client's Docker Compose stack.

**Language:** Python 3.11 | **Image:** `registry.storageidol.com/watchdog:<version>`

## What it does

1. **Health monitoring** — Polls other containers via the Docker socket every 30s. Detects crash-loops, OOM kills, and failed health checks.
2. **Metric aggregation** — Collects CPU, memory, restart counts, and HTTP error rates. No application logs, no PII.
3. **Alert shipping** — When a threshold is breached, sends a structured JSON alert to `ops.storageidol.com/alerts`. Never sends raw logs or user data.
4. **Heartbeat** — Sends a ping to StorageIdol ops every 5 minutes. If the ping stops arriving, StorageIdol detects the deployment as offline.
5. **Remediation commands** — Listens for signed remediation commands from StorageIdol ops. Can restart a specific container, clear Redis cache, or trigger a `docker pull` + redeploy.

## Alert payload (what gets sent to StorageIdol)

```json
{
  "client_id": "retras",
  "timestamp": "2026-06-12T10:00:00Z",
  "container": "platform-api",
  "event": "crash_loop",
  "restart_count": 7,
  "last_exit_code": 1,
  "cpu_percent": 12.4,
  "memory_mb": 245
}
```

No message content, no user identifiers, no conversation data — ever.

## Structure

```
watchdog/
├── Dockerfile
├── requirements.txt
├── main.py           # Entry point
├── monitor.py        # Docker socket polling
├── shipper.py        # Alert HTTP client
├── heartbeat.py      # Periodic ping
├── remediation.py    # Inbound command handler
└── tests/
```

## Configuration (via environment variables)

```
CLIENT_ID            # Identifier sent in every alert
OPS_WEBHOOK_URL      # https://ops.storageidol.com/alerts
OPS_TOKEN            # Signed token for authentication
HEARTBEAT_INTERVAL   # Default: 300 (seconds)
POLL_INTERVAL        # Default: 30 (seconds)
```
