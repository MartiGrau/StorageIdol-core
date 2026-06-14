"""
Base graph builder utilities.

Provides helpers for building client graphs from composable modules.
Client graphs (clients/<id>/graph.py) import from here, not from each module directly.
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from ..state import AgentState, ClientConfig


def make_entry_node(config: ClientConfig):
    """
    Returns the entry node function for a client graph.

    The entry node:
      1. Extracts the latest user message text.
      2. Increments the turn counter.
      3. Sets the Langfuse trace ID (conversation_id).
      4. Routes to the intent classifier.
    """
    def entry_node(state: dict) -> dict:
        s = AgentState(**state)
        latest = next(
            (m["content"] for m in reversed(s.messages) if m["role"] == "user"),
            "",
        )
        return {
            "user_message": latest,
            "turn_count": s.turn_count + 1,
            "langfuse_trace_id": s.conversation_id,
        }
    return entry_node


def route_after_intent(state: dict) -> str:
    """
    Edge function: route to the correct module after intent classification.

    Reads `next_node` from state (set by the intent module) and falls back
    to "faq_rag" if not set.
    """
    s = AgentState(**state)
    if s.should_escalate:
        return "escalation"
    return s.next_node or "faq_rag"


def route_after_auth(state: dict) -> str:
    """
    Edge function: if auth failed, send a reply and end; otherwise continue.
    """
    s = AgentState(**state)
    if not s.auth_verified:
        return END
    return s.next_node or "faq_rag"


def build_base_graph() -> StateGraph:
    """
    Returns an empty StateGraph with AgentState.

    Client graphs call this, then add_node() and add_edge() for their modules.
    """
    return StateGraph(dict)  # Use dict for LangGraph compatibility; AgentState validates on use
