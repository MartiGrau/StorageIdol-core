# Component: AI Agents

The LangGraph multi-agent system. This is the Core layer — the intelligence of the platform.

**App location:** `apps/agents/`

**Agent types:**
- **Orchestrator** — entry point, classifies intent, routes to the right specialist agent
- **Conversation agent** — handles FAQ, scheduling, general queries (Module 1)
- **Lead nurturing agent** — runs qualification and follow-up sequences (Module 2)
- **Debt collection agent** — executes staged debt outreach with tone escalation (Module 3)
- **Escalation agent** — detects triggers, pauses session, prepares handoff context

**Key dependencies:** LangGraph, Anthropic Claude, ElevenLabs SDK, Twilio SDK, WhatsApp Cloud API client

**Important:** Agent prompts and graph definitions are Core. Client-specific scripts and thresholds are Configuration (injected at runtime from client config). See `context/architecture/core-vs-config.md`.

**Owned by:** AI team
