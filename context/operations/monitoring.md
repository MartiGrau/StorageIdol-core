# Monitoring and Incident Response

## Overview

Every client deployment includes a **watchdog** monitoring sidecar that observes other containers, sends heartbeats, and ships alerts to StorageIdol ops.

**No remote command channel exists today.** The watchdog is an alert-shipper only — it cannot accept commands or modify the deployment. StorageIdol engineers diagnose and fix incidents through the GitHub issue + on-call flow below. A secure remote-command channel may be added in a future version after a proper security design review.

## Alert flow

```
Client server watchdog
  → POST https://ops.storageidol.com/alerts
  → ops/alert-receiver classifies alert
  → GitHub issue opened with full context
  → On-call engineer notified (Slack / PagerDuty)
  → Engineer fixes manually (SSH if client grants access, or instructs client)
```

## What triggers an alert

| Event | Threshold | Severity |
|---|---|---|
| Container crash-loop | >3 restarts in 5 min | High |
| Container stopped and not restarting | immediate | Critical |
| Memory usage | >90% for >5 min | Medium |
| API error rate | >10% 5xx over 2 min | High |
| Heartbeat missing | >10 min silence | Critical |

## Heartbeat

The watchdog sends `POST /heartbeat` to StorageIdol ops every 5 minutes. If ops does not receive a heartbeat for >10 minutes, the deployment is marked **offline** and a Critical alert fires — even with no error reported. This catches server shutdowns, network outages, and watchdog failures.

## On-call escalation

All alerts escalate to the on-call engineer:
1. GitHub issue opened with full alert context and recommended fix steps
2. Webhook notification sent (Slack or PagerDuty — configured in ops env vars)
3. Engineer accesses the server only if the client grants temporary SSH access; access must be revoked immediately after resolution
4. Issue closed with post-mortem note

## Debugging policy

StorageIdol engineers have no standing access to client servers. All access requires explicit, time-limited permission from the client. Zero-standing-access is a contractual requirement for client-hosted deployments. For StorageIdol-hosted deployments, engineers may access the VPS directly.
