# Conversational Flow Specs: [Company Name]

Specific conversational flows requested by this client. Each flow should map to a LangGraph node or subgraph.

## Format

```
### Flow name

**Trigger:** What starts this flow (inbound message keyword, intent, scheduler event)
**Goal:** What the agent is trying to achieve
**Steps:** numbered list of what the agent does/says
**Success condition:** how we know the flow completed successfully
**Fallback:** what happens if the flow fails or the user goes off-script
**Human escalation trigger:** what causes this flow to hand off to a human
```

---

_(No flows documented yet. Add one after each discovery call where a specific flow is discussed.)_
