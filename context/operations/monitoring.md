# Monitoring and Incident Response

## Overview

Every client deployment includes two monitoring containers:
- **watchdog** — Observes other containers, ships health alerts, sends heartbeats
- **watchtower** — Polls Docker registry for new images, auto-updates on new releases

StorageIdol runs its own ops platform (`ops/`) that receives alerts from all client watchdogs.

## Alert flow

```
Client server watchdog
  → POST https://ops.storageidol.com/alerts
  → Remediation agent classifies
  → Auto-fix (if known pattern) or GitHub issue + on-call page (if unknown)
```

## What triggers an alert

| Event | Threshold | Severity |
|---|---|---|
| Container crash-loop | >3 restarts in 5 min | High |
| Container stopped and not restarting | immediate | Critical |
| Memory usage | >90% for >5 min | Medium |
| API error rate | >10% 5xx over 2 min | High |
| Heartbeat missing | >10 min silence | Critical |
| Watchtower pull failure | 3 consecutive fails | Medium |

## Heartbeat

The watchdog sends `POST /heartbeat` to StorageIdol ops every 5 minutes. If ops does not receive a heartbeat for >10 minutes, the deployment is marked **offline** and a Critical alert fires — even with no error reported. This catches server shutdowns, network outages, and watchdog failures.

## Auto-remediation (known patterns)

The remediation agent in `ops/remediation-agent/` maintains a knowledge base of known error → fix mappings in `ops/remediation-agent/knowledge/`. When an alert matches a known pattern:

1. Agent sends a signed remediation command to the watchdog
2. Watchdog executes: restart container / clear cache / pull new image
3. Agent polls for healthy status over 60s
4. If healthy: closes alert, logs resolution
5. If still failing after 60s: escalates to on-call

## On-call escalation

When auto-remediation fails or the pattern is unknown:
1. GitHub issue opened with full alert context
2. Webhook notification sent (Slack or PagerDuty — configured in ops env vars)
3. Issue assigned to on-call engineer

## Adding a new known fix

Create `ops/remediation-agent/knowledge/<error-signature>.md` following the template in `ops/CLAUDE.md`.

## Debugging policy

StorageIdol engineers never have SSH access to client servers by default. All debugging goes through the watchdog's remote command channel. If a client grants temporary SSH for an incident, it must be revoked immediately after resolution.
