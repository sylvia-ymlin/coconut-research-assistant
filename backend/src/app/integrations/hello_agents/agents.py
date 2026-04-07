"""Agent adapters for HelloAgents."""

from hello_agents import ToolAwareSimpleAgent

ToolAwareAgent = ToolAwareSimpleAgent


def create_tool_aware_agent(**kwargs) -> ToolAwareAgent:
    """Create a tool-aware agent instance."""

    return ToolAwareSimpleAgent(**kwargs)
