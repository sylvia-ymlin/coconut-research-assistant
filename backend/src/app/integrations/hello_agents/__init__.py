"""HelloAgents integration boundary for the application."""

from app.integrations.hello_agents.agents import ToolAwareAgent, create_tool_aware_agent
from app.integrations.hello_agents.llm import LLMClient, create_llm_client
from app.integrations.hello_agents.tools import (
    NoteToolAdapter,
    SearchToolAdapter,
    ToolRegistryAdapter,
    create_note_tool,
    create_search_tool,
    create_tool_registry,
)

__all__ = [
    "LLMClient",
    "NoteToolAdapter",
    "SearchToolAdapter",
    "ToolAwareAgent",
    "ToolRegistryAdapter",
    "create_llm_client",
    "create_note_tool",
    "create_search_tool",
    "create_tool_aware_agent",
    "create_tool_registry",
]
