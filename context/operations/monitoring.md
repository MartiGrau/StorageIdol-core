# Monitoring

> Status: To be defined as infrastructure is built out. Placeholder structure below.

## What to monitor

| Signal | Why it matters |
|---|---|
| API response time p95 | Agent latency directly affects UX |
| WhatsApp message delivery rate | Failed deliveries mean lost client interactions |
| Twilio call completion rate | Dropped calls = missed debt contacts |
| LangGraph session errors | Agent failures that surface as silent bugs |
| Debt scheduler job completion | Missed D+N triggers = missed collections |
| Escalation queue depth | Growing queue = human team overwhelmed |
| Payment link click-through rate | Business KPI for Module 3 |

## Alerting

Alerts should fire to the ops channel (Slack TBD) for:
- API health check failure
- Error rate > 1% over 5 minutes
- Debt scheduler job failure
- Escalation queue > 20 unhandled items

## Logging

- All services log to stdout in JSON format
- Logs are aggregated centrally (tool TBD)
- Each log entry includes: `service`, `client_id`, `conversation_id`, `level`, `message`, `timestamp`

## Audit log

A separate append-only audit log records every agent action for regulatory compliance:
- Message sent (channel, recipient, content hash)
- Call placed (number, duration, outcome)
- Escalation triggered (reason, agent context snapshot)
- Payment link generated and clicked
