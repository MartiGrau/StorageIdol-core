"""
storageidol-agents — LangGraph multi-agent system.

Exports:
  AgentState, ClientConfig — the typed state shared by all modules
  load_graph               — registry to compile a client's graph
  run_graph                — run a compiled graph on a new message (Celery-called)
"""

from .state import AgentState, Channel, ClientConfig
from .graphs.registry import load_graph

__all__ = ["AgentState", "Channel", "ClientConfig", "load_graph"]
