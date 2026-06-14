"""
Model routing policy — maps task types to the appropriate Claude tier.

Keep model IDs here, not scattered across the codebase.
Update this file when new Claude versions are released.
"""

from __future__ import annotations

import enum


class Task(str, enum.Enum):
    """
    Task categories used to route to the right Claude model tier.

    Match the cost/capability to the task:
      - High-volume classification → Haiku (cheap, fast)
      - Standard conversation     → Sonnet (balanced)
      - Complex reasoning         → Opus  (expensive, best quality)
    """

    # Intent classification, auth check, template selection
    CLASSIFICATION = "classification"

    # Regular FAQ/CRM conversation, lead qualification, soft debt follow-up
    CONVERSATION = "conversation"

    # Complex debt negotiation, dispute resolution, legal-escalation detection
    REASONING = "reasoning"

    # LLM-as-a-judge conversation evaluation (post-conversation async)
    JUDGE = "judge"

    # Knowledge-base embedding queries (does not call Claude)
    EMBEDDING = "embedding"


# ── Model IDs ─────────────────────────────────────────────────────────────────
# Keep in sync with CLAUDE.md and context/architecture/tech-stack.md.
_MODEL_ROUTING: dict[Task, str] = {
    Task.CLASSIFICATION: "claude-haiku-4-5-20251001",
    Task.CONVERSATION:   "claude-sonnet-4-6",
    Task.REASONING:      "claude-opus-4-8",
    Task.JUDGE:          "claude-sonnet-4-6",    # Sonnet is sufficient for evaluation
    Task.EMBEDDING:      "text-embedding-3-small",
}


def model_for_task(task: Task, overrides: dict[str, str] | None = None) -> str:
    """Return the model ID for a given task, respecting per-client config overrides.

    Pass `config.model_overrides` to allow clients to downgrade or change models
    without touching platform code. Unknown task keys in overrides are ignored.
    """
    if overrides:
        override = overrides.get(task.value)
        if override:
            return override
    return _MODEL_ROUTING[task]
