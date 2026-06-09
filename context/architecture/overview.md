# Architecture Overview

## System topology

StorageIdol runs a **multi-agent system** built with LangGraph. Three specialized agents collaborate within a shared state graph:

```
                         ┌─────────────────┐
                         │  Orchestrator   │  ← routes intent, manages state
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
   ┌──────────▼──────┐  ┌─────────▼──────┐  ┌────────▼────────┐
   │  Conversation   │  │    Scheduler   │  │  Escalation     │
   │     Agent       │  │    Agent       │  │    Agent        │
   └──────────┬──────┘  └─────────┬──────┘  └────────┬────────┘
              │                   │                   │
       WhatsApp / Voice      CRM triggers        Human queue
        (ElevenLabs,          (D+N staging)      (handoff + log)
         Twilio)
```

## Core layer (shared across all clients)

| Component | Role |
|---|---|
| LangGraph state machine | Agent orchestration, state persistence, conditional routing |
| ElevenLabs | Voice synthesis (text-to-speech, custom voice profiles) |
| Twilio | Telephony (inbound/outbound calls, call routing, recording) |
| WhatsApp Cloud API | Messaging (template messages, session messages, media) |
| Debt scheduler | Cron-based D+N stage engine, reads CRM, triggers agents |
| Human escalation | Detects triggers, pauses agent, routes to human queue with context |
| Payment integration | Generates payment links, embeds in messages, tracks completion |

## Configuration layer (per-client)

| Configuration | Examples |
|---|---|
| Conversational flows | Scripts, decision trees, tone per stage |
| WhatsApp templates | Approved templates per use case per client |
| Knowledge base | FAQs, property listings, policy documents |
| CRM connector | REST/webhook adapter per CRM (Salesforce, HubSpot, custom) |
| Voice profile | Language, accent, speed, ElevenLabs voice ID |
| Debt thresholds | D+N values, amounts, escalation conditions |
| Infrastructure slice | Dedicated subdomain, isolated env vars, separate DB schema |

## Data flow (Customer Service example)

1. Client sends WhatsApp message → WhatsApp Cloud API webhook → API server
2. API server creates/resumes LangGraph session for that contact
3. Orchestrator agent classifies intent → routes to Conversation agent
4. Conversation agent queries knowledge base → generates reply
5. Reply sent via WhatsApp Cloud API
6. If escalation trigger detected → Escalation agent pauses session, notifies human queue
7. Human agent takes over; on resolution, session is closed and logged

## Key design decisions

- **Stateful sessions**: LangGraph persists the full conversation state between turns — no context loss on re-entry.
- **Agent isolation**: Each client runs in an isolated configuration namespace; no data bleed between clients.
- **Async-first**: All agent invocations are async; long-running tasks (calls, scheduling) do not block the API.
- **Audit log**: Every agent action (message sent, call placed, escalation triggered) is written to an append-only log for compliance.
