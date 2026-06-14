# Component: AI Agents

The LangGraph multi-agent system. This is the Core layer — the intelligence of the platform.

**App location:** `core/agents/`

**Agent types:**
- **Orchestrator** (`core/agents/graphs/_base.py`) — entry point, classifies intent, routes to the right specialist agent
- **Conversation agent** — handles FAQ, scheduling, general queries (Module 1)
- **Lead nurturing agent** — runs qualification and follow-up sequences (Module 2)
- **Debt collection agent** — executes staged debt outreach with tone escalation (Module 3)
- **Escalation agent** — detects triggers, pauses session, prepares handoff context

**Key dependencies:** LangGraph, Anthropic Claude, LiveKit Agents SDK (voice), ElevenLabs TTS, Deepgram STT, WhatsApp Cloud API client

**Important:** Agent prompts and graph definitions are Core. Client-specific wiring lives in `clients/<id>/graph.py` (registered via `core/agents/graphs/registry.py`). Client-specific thresholds and values are Configuration (injected at runtime from client config). See `context/architecture/core-vs-config.md`.

**Owned by:** AI team
