# Agent Modules — Composable Subgraphs

Each subdirectory is an independent LangGraph subgraph with a single responsibility.
Modules are the building blocks that client graphs (`clients/<id>/graph.py`) assemble.

**Implementation source:** `core/agents/storageidol_agents/modules/`

## Module contract

Every module:
1. Is a **factory function** `<name>_node(config: ClientConfig)` that returns the actual async node.
2. Accepts `AgentState` (as a dict) and returns a **partial dict** of updated keys only.
3. Has isolated tests that use a mocked LLM + mocked MCP (no real credentials needed).
4. Contains **no client-specific logic** — all client values come from `config`.

```python
def my_module_node(config: ClientConfig):
    async def _node(state: dict) -> dict:
        s = AgentState(**state)
        # read from s, produce updates
        return {"reply": "...", "some_state_key": value}
    return _node
```

## Available modules

| Module | Path | Purpose | Required state inputs |
|---|---|---|---|
| `auth/phone_dni` | `auth/phone_dni.py` | Verify identity via phone + DNI (calls MCP `verify_identity`) | `user_message`, `messages` |
| `intent/storage` | `intent/storage.py` | Classify self-storage intents → routing | `user_message` |
| `intent/generic` | `intent/generic.py` | Classify generic multi-domain intents | `user_message` |
| `conversation/faq_rag` | `conversation/faq_rag.py` | Answer FAQ via pgvector KB | `user_message`, `client_id` |
| `conversation/crm_lookup` | `conversation/crm_lookup.py` | Personalised answer from CRM via MCP | `contact_crm_id`, `auth_verified` |
| `debt/soft` | `debt/soft.py` | Soft debt collection dialogue (D+3, D+10) | `debt_case_id`, `auth_verified` |
| `debt/hard` | `debt/hard.py` | Hard debt collection dialogue (D+20, D+30) | `debt_case_id`, `auth_verified` |
| `lead/qualify_storage` | `lead/qualify_storage.py` | Storage lead qualification (size/duration/budget) | `user_message`, `messages` |
| `escalation/human_handoff` | `escalation/human_handoff.py` | Human escalation + Slack/Teams webhook | `should_escalate`, `messages` |
| `channel/formatter` | `channel/formatter.py` | **Channel-specific response reformatter** (always last) | `reply`, `channel` |
| `channel/prompt_adapter` | `channel/prompt_adapter.py` | Utility: inject channel instructions into any system prompt | (not a node) |

## Channel architecture — shared reasoning, channel-specific UX

**WhatsApp and voice use the same reasoning graph** (intent, auth, CRM, debt).
What differs is **how the answer is expressed** — not what it says, but its form.

| | Voice | WhatsApp |
|---|---|---|
| Format | Spoken sentences only | `*bold*`, `-` lists, emoji, links |
| Length | 2-3 sentences max | Up to 6 lines |
| URLs | Say "le enviaré el enlace por WhatsApp" | Clickable link on its own line |
| Numbers | "cuarenta y cinco euros" | "45 €" |
| Images/docs | Not applicable | Can receive/send media |

**Implementation pattern:**

1. Every module can use `channel_instructions(state.channel)` from `channel/prompt_adapter.py`
   to append channel-specific constraints to its system prompt.
2. **`channel/formatter`** is always the LAST node in the graph — it reformats
   the `reply` produced by the preceding module for the current channel.

```
entry → intent → [auth] → [faq_rag | crm_lookup | debt | lead] → escalation? → formatter → END
```

## Client graph wiring

`build_graph(config)` in `clients/<id>/graph.py` creates and compiles a LangGraph `StateGraph`
by wiring the subset of modules the client uses. The `channel/formatter` node is always included.

See `core/agents/modules/README.md#client-graph-wiring-example` or run `/new-client <id>` to
generate a complete graph for a new client.

## Adding a new module

1. Create `core/agents/storageidol_agents/modules/<category>/<name>.py` with the factory function.
2. Add tests in `core/agents/storageidol_agents/modules/<category>/test_<name>.py`.
3. Add an entry to the table above.
4. The provisioning agent discovers modules by scanning this directory.
