"""
Client graph registry — loads and compiles a client's LangGraph.

Each client has a graph.py in clients/<id>/graph.py that defines:
    def build_graph(config: ClientConfig) -> CompiledGraph: ...

This registry imports that module and caches the compiled graph.
The graph is compiled ONCE per (client_id, config hash) and reused
for all subsequent invocations (Celery workers keep it in memory).
"""

from __future__ import annotations

import hashlib
import importlib
import logging
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langgraph.graph import CompiledStateGraph

from ..state import ClientConfig

logger = logging.getLogger(__name__)


def load_graph(client_id: str, config: ClientConfig) -> "CompiledStateGraph":
    """
    Import and compile the LangGraph for a given client.

    The compiled graph is cached — calling this multiple times with the same
    config is cheap (LRU cache keyed on client_id + config hash).

    Args:
        client_id: The client identifier (e.g. "retras").
        config:    The ClientConfig loaded from clients/<id>/config.yaml.

    Returns:
        A compiled LangGraph CompiledStateGraph ready for .invoke() or .astream().

    Raises:
        ModuleNotFoundError: If clients/<id>/graph.py does not exist.
        AttributeError:      If graph.py does not define build_graph().
    """
    config_hash = _config_hash(config)
    return _cached_graph(client_id, config_hash, config)


def _config_hash(config: ClientConfig) -> str:
    """Stable hash of config for cache key."""
    return hashlib.md5(config.model_dump_json().encode(), usedforsecurity=False).hexdigest()[:8]


@lru_cache(maxsize=32)
def _cached_graph(
    client_id: str,
    config_hash: str,  # noqa: ARG001 — used only as cache discriminator
    config: ClientConfig,
) -> "CompiledStateGraph":
    """LRU-cached graph compilation."""
    module_path = f"clients.{client_id}.graph"
    logger.info("Loading graph for client=%s from %s", client_id, module_path)

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            f"Graph not found for client '{client_id}'. "
            f"Expected module at '{module_path}'. "
            f"Run /new-client {client_id} to generate it."
        ) from e

    if not hasattr(module, "build_graph"):
        raise AttributeError(
            f"clients/{client_id}/graph.py must define: "
            "def build_graph(config: ClientConfig) -> CompiledStateGraph"
        )

    compiled = module.build_graph(config)
    logger.info("Graph compiled for client=%s", client_id)
    return compiled


def invalidate_cache(client_id: str | None = None) -> None:
    """
    Invalidate the compiled graph cache.

    Called after a client config or graph.py update (e.g. after /new-client).
    Pass client_id=None to invalidate all clients.
    """
    _cached_graph.cache_clear()
    logger.info("Graph cache cleared for client=%s", client_id or "ALL")
