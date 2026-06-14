"""
Composable LangGraph module subgraphs.

Each module:
  - Accepts AgentState (as a dict for LangGraph compatibility)
  - Returns a partial dict to merge into state
  - Has isolated tests that mock the LLM and MCP
  - Contains NO client-specific logic

Import individual modules in clients/<id>/graph.py to wire them together.
"""
