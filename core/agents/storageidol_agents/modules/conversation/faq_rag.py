"""
Module: conversation/faq_rag

FAQ answering via Retrieval-Augmented Generation using pgvector.

Pipeline:
  1. Embed the user's question with text-embedding-3-small (via Anthropic/OpenAI API).
  2. Query the `knowledge_chunks` table for the top-k most similar chunks
     (cosine similarity via pgvector).
  3. Feed retrieved chunks as context into Claude Sonnet to generate the answer.
  4. If no relevant chunks found (max similarity < threshold), acknowledge and escalate.

State inputs:
    user_message, client_id, conversation_id
    (config.knowledge_base_path is used for the embedding model name)

State outputs:
    kb_answer: the generated answer (or None if nothing relevant found)
    reply: the final reply to send (may include escalation suggestion)
    should_escalate: True if no KB match found
"""

from __future__ import annotations

import logging

from sqlalchemy import select, text

from storageidol_db import KnowledgeChunk, get_session
from storageidol_llm import ClaudeClient, Task

from ...state import AgentState, ClientConfig

logger = logging.getLogger(__name__)

_TOP_K = 5
_MIN_SIMILARITY = 0.75   # Below this, answer is probably hallucinated

_ANSWER_SYSTEM = """You are a helpful customer service assistant for {brand_name}.

Answer the customer's question using ONLY the provided context.
If the context does not contain enough information to answer accurately, say so politely.
Do NOT invent information. Keep the answer concise (2-4 sentences max).
Language: {language}.

Context:
{context}
"""

_NO_ANSWER_REPLY = (
    "Lo siento, no tengo información específica sobre eso. "
    "¿Le gustaría que le ponga en contacto con uno de nuestros agentes?"
)


def faq_rag_node(config: ClientConfig):
    """Returns a LangGraph node for FAQ RAG answering."""

    async def _node(state: dict) -> dict:
        s = AgentState(**state)
        llm = ClaudeClient(client_id=s.client_id, trace_id=s.langfuse_trace_id)

        # 1. Embed user question
        embedding = await _embed(s.user_message)
        if embedding is None:
            return {
                "reply": _NO_ANSWER_REPLY,
                "should_escalate": True,
                "escalation_reason": "Embedding failed",
            }

        # 2. Retrieve relevant chunks from pgvector
        chunks = await _retrieve(s.client_id, embedding)
        if not chunks:
            return {
                "reply": _NO_ANSWER_REPLY,
                "should_escalate": True,
                "escalation_reason": "No KB match found",
            }

        # 3. Generate answer
        context = "\n\n---\n\n".join(c.content for c in chunks)
        system = _ANSWER_SYSTEM.format(
            brand_name=config.brand_name,
            language=config.language,
            context=context,
        )
        response = await llm.complete(
            messages=[{"role": "user", "content": s.user_message}],
            task=Task.CONVERSATION,
            system=system,
            cache_system=False,  # Context changes per query
            max_tokens=512,
        )

        return {
            "kb_answer": response.content,
            "reply": response.content,
        }

    return _node


async def _embed(text_input: str) -> list[float] | None:
    """
    Generate a text embedding via the Anthropic/OpenAI embeddings API.

    Returns None on failure (non-fatal — caller handles gracefully).
    """
    try:
        import openai
        client = openai.AsyncOpenAI()
        resp = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text_input,
        )
        return resp.data[0].embedding
    except Exception:
        logger.exception("Embedding API call failed")
        return None


async def _retrieve(
    client_id: str, embedding: list[float]
) -> list[KnowledgeChunk]:
    """
    Retrieve the top-k most similar knowledge chunks from pgvector.

    Uses cosine similarity. Filters by client_id (each client has isolated KB).
    """
    try:
        async with get_session(client_id) as session:
            # pgvector cosine similarity via <=> operator (lower = more similar)
            result = await session.execute(
                select(KnowledgeChunk)
                .where(KnowledgeChunk.client_id == client_id)
                .order_by(
                    KnowledgeChunk.embedding.op("<=>")(embedding)
                )
                .limit(_TOP_K)
            )
            return list(result.scalars().all())
    except Exception:
        logger.exception("KB retrieval query failed")
        return []
