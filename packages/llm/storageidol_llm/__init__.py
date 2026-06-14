"""
storageidol-llm — Claude API wrapper with prompt caching, model routing, Langfuse tracing.

Usage:
    from storageidol_llm import ClaudeClient, Task

    client = ClaudeClient(client_id="retras", trace_id="conv-123")
    response = await client.complete(
        messages=[{"role": "user", "content": "Hola"}],
        task=Task.CONVERSATION,
        system="You are a helpful storage assistant.",
    )
"""

from .client import ClaudeClient
from .routing import Task, model_for_task

__all__ = ["ClaudeClient", "Task", "model_for_task"]
