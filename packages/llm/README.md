# Package: llm

Claude API wrapper used by all agent workers.

**Language:** Python | **Key dependency:** `anthropic`

## What it provides

- `ClaudeClient` — Configured client with prompt caching enabled by default, exponential retry on rate limits
- `model_for_task(task: TaskType) -> str` — Returns the right model ID given a task category:
  - `TaskType.CLASSIFICATION` → `claude-haiku-4-5-20251001` (high volume, cheap)
  - `TaskType.CONVERSATION` → `claude-sonnet-4-6` (default)
  - `TaskType.DEBT_NEGOTIATION` → `claude-opus-4-8` (complex reasoning)
- `count_tokens(messages)` — Token count helper for budget tracking

## Prompt caching

All system prompts are cached automatically. The client appends `cache_control: {"type": "ephemeral"}` to the last system message block. Cache TTL is 5 minutes — agents that run on a tight loop stay warm.
