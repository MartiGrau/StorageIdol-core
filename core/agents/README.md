# Agents

LangGraph multi-agent system. Runs as Celery workers, invoked by the API.

**Language:** Python 3.11 | **Frameworks:** LangGraph, Anthropic Claude, Celery

## Structure

```
agents/
├── tasks.py              # Celery task definitions — entry points from API
├── graphs/               # Per-client graph compositions (wiring of modules)
│   └── _base.py          # Base graph builder utility
├── modules/              # Composable LangGraph subgraphs (Core layer)
│   ├── README.md
│   ├── auth/             # Identity validation (phone + DNI, etc.)
│   ├── intent/           # Domain-specific intent classifiers
│   ├── conversation/     # FAQ RAG + CRM lookup
│   ├── debt/             # Debt collection (soft and hard variants)
│   ├── lead/             # Lead qualification flows
│   ├── escalation/       # Human handoff
│   └── voice/            # Voice-specific nodes (STT/TTS bridge)
├── scheduler/            # D+N debt staging engine
└── tests/
```

## How client graphs work

A client graph is a Python file that imports modules and wires them into a LangGraph `StateGraph`. It is NOT generated at runtime from config — it is code, committed under `clients/<id>/graph.py` and referenced here via a registry.

**Canonical location:** `clients/<id>/graph.py` — client-owned, not inside `core/`.

**Registry:** `core/agents/graphs/registry.py` discovers and loads client graphs by `client_id`:

```python
# core/agents/graphs/registry.py  (this is Core — lives here)
from importlib import import_module
from storageidol_agents.state import AgentState, ClientConfig

def load_graph(client_id: str, config: ClientConfig):
    """Import and compile the graph for a given client."""
    module = import_module(f"clients.{client_id}.graph")
    return module.build_graph(config)
```

```python
# clients/retras/graph.py  (Client-layer code — lives in clients/, not here)
from core.agents.modules.auth.phone_dni import phone_dni_node
from core.agents.modules.intent.storage import storage_intent_node
from core.agents.modules.conversation.faq_rag import faq_rag_node
from core.agents.modules.conversation.crm_lookup import crm_lookup_node
from core.agents.modules.debt.soft import debt_soft_node
from core.agents.modules.escalation.human_handoff import escalation_node

def build_graph(config: ClientConfig) -> CompiledGraph:
    graph = StateGraph(AgentState)
    graph.add_node("intent", storage_intent_node(config))
    graph.add_node("auth", phone_dni_node(config))
    # ... wire edges and conditions
    return graph.compile()
```

The provisioning agent (`.claude/agents/provision-client.md`) generates `clients/<id>/graph.py` when onboarding a new client.

## Local setup

```bash
cp .env.example .env
pip install -r requirements.txt
celery -A tasks worker --loglevel=info
```
