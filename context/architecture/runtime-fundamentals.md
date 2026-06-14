# Runtime Fundamentals

Correctness requirements that must be satisfied before any client goes live. These are
not optional features — they are safety and compliance requirements.

## Webhook idempotency

**Why this matters:** The debt collection scheduler sends WhatsApp templates and triggers
voice calls. Meta Cloud API and Telnyx both retry failed webhooks. Delivering a debt
collection message twice to the same contact on the same D+N stage is a compliance incident
under Spanish debt collection law (the contact may file a harassment complaint).

**Design:**
- Every inbound webhook (`/webhook/whatsapp`, `/trigger/debt`) includes a unique event ID
  in the request header or body.
- Before processing, the API checks a Redis key `idempotency:<event-id>` with a 24-hour TTL.
- If the key exists: return HTTP 200 immediately without processing (idempotent replay).
- If the key does not exist: set the key with NX + EX 86400, then process.

**Implementation:** `core/api/idempotency.py` — `check_and_claim(event_id, redis_client)`.

**Scope:**
- All inbound webhooks that trigger message sends or graph runs
- Debt trigger endpoint specifically: event ID must include `(client_id, case_id, stage)` to
  prevent duplicate staging even across retries with different event IDs

## LangGraph conversation checkpointing

**Why this matters:** WhatsApp users send multiple messages in quick succession. Without
checkpointing, two Celery workers can load the same `AgentState`, both complete a graph run,
and write conflicting replies. The last writer wins, and the conversation context is corrupted.

**Design:**
- LangGraph supports pluggable checkpointers. Use the **PostgreSQL checkpointer**
  (`langgraph-checkpoint-postgres`) keyed by `(client_id, conversation_id)`.
- Each worker acquires a row-level lock on the conversation row before invoking the graph.
- If the lock is held (another worker is processing this conversation), the new message
  is queued into a Redis list keyed by `queue:<client_id>:<phone>` and processed after
  the current turn completes.

**Implementation:** `core/agents/storageidol_agents/graphs/registry.py` — pass
`AsyncPostgresSaver` as the checkpointer when compiling the graph. The session factory
in `packages/db/storageidol_db/session.py` provides the connection.

**Configuration:** No additional config required — the main `DATABASE_URL` is used.

## Cost guardrails

**Why this matters:** A runaway graph, a misconfigured client, or a prompt injection
attack could trigger thousands of expensive LLM calls. Each client deployment must have a
per-conversation token spend cap to limit blast radius.

**Design:**
- `packages/llm/storageidol_llm/client.py` tracks cumulative tokens per `trace_id`.
- If tokens exceed `config.max_tokens_per_conversation` (default: 20,000), the Claude
  client raises `TokenBudgetExceeded`.
- The graph catches this exception in the entry node and routes to the `escalation/human_handoff`
  module with reason `"token_budget_exceeded"`.

**Configuration:** Add `max_tokens_per_conversation: 20000` to `clients/<id>/config.yaml`
(or omit to use the platform default).

## Knowledge-base freshness

**Why this matters:** A KB chunk with stale pricing or policy information will cause the
agent to give wrong answers confidently. RAG freshness is invisible until a client calls
to complain.

**Design:**
- KB documents in `clients/<id>/knowledge-base/` have a `last_updated` frontmatter date.
- A weekly Celery Beat job checks for documents where `last_updated` is older than 90 days
  and creates a GitHub issue tagged `kb-stale / <client-id>`.
- Re-ingestion is triggered by `POST /admin/kb/reingest` — this re-embeds all chunks and
  replaces them in the `knowledge_chunks` table (no in-place updates, full replacement).

## Secrets never in config

`clients/<id>/config.yaml` is committed to the repo and visible to anyone with repo access.
It must contain **zero secrets**. The rule:

- API keys, passwords, tokens → `.env` on the server only
- Thresholds, IDs, settings, names → `config.yaml`

If a value would be embarrassing or dangerous to leak in a GitHub breach, it is a secret.
`CRM_API_KEY` is a secret even though it looks like a config value.
