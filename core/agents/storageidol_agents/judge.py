"""
LLM-as-a-judge conversation evaluator.

Runs as a post-conversation Celery task (asynchronously after each conversation ends).
Scores the conversation and writes results to:
  - JudgeScore table (client's Postgres)
  - Langfuse as an evaluation score on the trace

Scoring rubric (0.0 - 1.0):
  1.0  Perfect: intent correctly resolved, accurate info, no hallucination, appropriate escalation if needed
  0.7  Good: mostly correct, minor issues (slightly verbose, one unclear turn)
  0.5  Partial: intent eventually resolved but took too long or had some errors
  0.3  Poor: incorrect info provided OR failed to escalate when needed
  0.0  Failure: hallucinated data, wrong client brand referenced, infinite loop detected

Threshold: score >= 0.7 → success = True
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from python_ulid import ULID

from storageidol_db import Conversation, ConversationStatus, JudgeScore, get_session
from storageidol_llm import ClaudeClient, Task

logger = logging.getLogger(__name__)

_SUCCESS_THRESHOLD = 0.7

_JUDGE_SYSTEM = """You are evaluating a customer service conversation for quality assurance.

Client brand: {brand_name}
Channel: {channel}
Detected intent: {intent}

Evaluate the conversation on these criteria:
1. Intent correctly identified and resolved (or appropriately escalated)
2. Information accuracy (no hallucinated data, no invented facts)
3. Brand consistency (mentions only {brand_name}, never another company's name)
4. Tone appropriateness for the channel and situation
5. Efficiency (resolved in a reasonable number of turns)

Output ONLY valid JSON:
{{
  "score": 0.0-1.0,
  "success": true/false,
  "reason": "Brief explanation (2-3 sentences)",
  "flags": ["list of specific issues, or empty array"]
}}

Score >= 0.7 means success=true.
"""


async def evaluate_conversation(
    conversation_id: str,
    client_id: str,
    brand_name: str,
) -> JudgeScore | None:
    """
    Evaluate a conversation and persist the score.

    Called by the post-conversation Celery task (tasks.evaluate_conversation_task).
    Returns None if the conversation cannot be loaded or evaluation fails.
    """
    async with get_session(client_id) as session:
        from sqlalchemy import select
        from storageidol_db import Message

        # Load conversation + messages
        conv_result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.client_id == client_id,
            )
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            logger.warning("Conversation %s not found for client %s", conversation_id, client_id)
            return None

        msgs_result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = list(msgs_result.scalars().all())

    if not messages:
        logger.warning("No messages for conversation %s", conversation_id)
        return None

    # Format messages for judge
    formatted = [{"role": m.role.value, "content": m.content} for m in messages]

    llm = ClaudeClient(client_id=client_id, trace_id=conversation.langfuse_trace_id)
    system = _JUDGE_SYSTEM.format(
        brand_name=brand_name,
        channel=conversation.channel.value,
        intent=conversation.detected_intent or "unknown",
    )

    try:
        response = await llm.complete(
            messages=formatted,
            task=Task.JUDGE,
            model=None,  # Uses Sonnet (sufficient for evaluation)
            system=system,
            cache_system=False,
            max_tokens=512,
        )
        data = json.loads(response.content)
    except (json.JSONDecodeError, ValueError, Exception) as e:
        logger.exception("Judge evaluation failed for conversation %s: %s", conversation_id, e)
        return None

    score = float(data.get("score", 0.0))
    success = score >= _SUCCESS_THRESHOLD

    judge_score = JudgeScore(
        id=str(ULID()),
        conversation_id=conversation_id,
        score=score,
        success=success,
        reason=data.get("reason", ""),
        model="claude-sonnet-4-6",  # From Task.JUDGE routing
        evaluated_at=datetime.now(timezone.utc),
    )

    async with get_session(client_id) as session:
        session.add(judge_score)
        # Also update conversation status
        from sqlalchemy import select
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = result.scalar_one_or_none()
        if conv and conv.status == ConversationStatus.ACTIVE:
            conv.status = ConversationStatus.RESOLVED if success else ConversationStatus.RESOLVED
            conv.ended_at = datetime.now(timezone.utc)

    logger.info(
        "Judge evaluated conversation %s: score=%.2f success=%s",
        conversation_id, score, success
    )
    return judge_score
