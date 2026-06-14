# Golden Scenarios

Human-authored conversation scenarios that form the ground truth for the simulate harness.

## Purpose

Agent-generated scenarios (from `.claude/agents/simulate-conversation.md`) test breadth but
cannot validate correctness — the same model that writes the scenario also evaluates it.
Golden scenarios are written by humans and reviewed before merging. They represent:

- The exact flows clients have signed off on
- Edge cases that were caught in production or staging
- Regulatory requirements (debt collection conduct, AI disclosure)

**Agent-generated scenarios supplement golden scenarios. They never replace them.**
No PR that touches `core/agents/modules/` or any client graph may be merged if the golden
scenario suite fails.

## Structure

Each scenario is a YAML file:

```yaml
# golden/retras/payment_query.yaml
client_id: retras
channel: whatsapp
description: "User asks about their outstanding payment"

turns:
  - user: "Hola, quiero saber cuánto debo"
    expected_intent: payment_query
    expected_reply_contains:
      - "importe"      # Must mention amount
      - "€"            # Must include currency
    expected_reply_excludes:
      - "ERROR"
      - "No sé"        # Agent must not say it doesn't know after CRM lookup

  - user: "¿Puedo pagar en dos plazos?"
    expected_intent: debt_negotiation
    should_escalate: false

final_state:
  auth_verified: true
  lead_qualified: false
```

## Running golden scenarios

```bash
uv run pytest core/agents/tests/golden/ -v
```

Each scenario file is discovered automatically. The harness mocks the MCP (CRM responses
come from fixtures in `clients/<id>/tests/fixtures/`) but uses the real graph and real LLM.

## Adding a scenario

1. Write the YAML following the structure above
2. Run it locally to confirm it passes
3. Get sign-off from the client contact or StorageIdol lead (not just the engineer)
4. Merge to `main`

## Review gate

Any PR that adds or modifies a golden scenario must have a human approval from someone who
is not the author. Automated approval is not sufficient — these scenarios represent
behavioural guarantees made to clients.
