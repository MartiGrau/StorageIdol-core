# Agent: simulate-conversation

Validates that a client's agent graph responds correctly to a set of conversation scenarios.

## When to run

- After generating a new client graph (`provision-client` calls this automatically)
- After modifying any module used by an existing client
- Before a go-live deployment

## What this agent does

### Step 1 — Load the client config

Read `clients/<client-id>/config.yaml` and `clients/<client-id>/graph.py`.

### Step 2 — Load the scenario suite

Read `clients/<client-id>/requirements/flows.md`. Extract the key flows defined there. If no scenario file exists, generate one from the flows document at `clients/<client-id>/tests/scenarios.yaml`.

Each scenario has:
```yaml
- name: "Customer asks for last invoice"
  channel: whatsapp
  messages:
    - role: user
      content: "Hola, quiero saber cuánto es mi última factura"
  expected:
    - intent: crm_lookup
    - asks_for_auth: true
    - after_auth_mentions: invoice
    - does_not_mention: competitor_brand
```

### Step 3 — Run simulations

For each scenario:
1. Instantiate the client graph with a mock MCP (returns fixture data)
2. Feed the conversation turn by turn
3. Check that the actual agent behavior matches `expected`
4. Record pass/fail with the actual agent response

### Step 4 — Report

Print a table: scenario name | result | failing assertion (if any) | actual response excerpt.

If any scenario fails, do NOT open a PR. Fix the graph or prompt and re-run.

## What counts as a failure

- Wrong intent classification
- Agent asks for authentication when it shouldn't (or doesn't when it should)
- Agent mentions another client's brand name
- Agent makes up information not in the knowledge base or MCP response
- Agent fails to escalate when the scenario requires it
- Agent enters an infinite loop (>10 turns without resolution)
