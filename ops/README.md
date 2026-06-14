# Ops — StorageIdol Internal Operations Platform

This is StorageIdol's own monitoring and auto-remediation system. It runs on StorageIdol infrastructure — never on client servers.

## What lives here

```
ops/
├── alert-receiver/        # FastAPI webhook endpoint that receives alerts from all client watchdogs
├── remediation-agent/     # LangGraph agent that classifies alerts and auto-fixes known issues
│   └── knowledge/         # Known error → fix mappings (grows over time)
└── dashboard/             # Internal view of all client deployment health
```

## How it works

```
Client server (watchdog) ──── POST /alerts ────► alert-receiver
                                                        │
                                                        ▼
                                               remediation-agent
                                              /                 \
                                    Known issue?              Unknown issue?
                                         │                          │
                               Send remediation command       Open GitHub issue
                               to watchdog on client           + page on-call
                                         │
                               Verify container healthy
                               in 60s → close alert
```

## Heartbeat monitor

Every client watchdog sends a ping every 5 minutes. The `alert-receiver` tracks last-seen timestamps. If a client goes silent for >10 minutes, it is marked "offline" and an alert is created — even if no error was reported.

## Remediation agent

The agent in `remediation-agent/` is a LangGraph loop that:
1. Receives structured alert JSON
2. Queries `knowledge/` for known error patterns (container name + exit code + restart count)
3. If match found: sends a signed remediation command to the client's watchdog
4. Waits 60s and polls for healthy status
5. If no match: creates a GitHub issue with full context + notifies on-call via webhook

Over time, every resolved incident adds an entry to `knowledge/` so the same issue never requires human intervention twice.
