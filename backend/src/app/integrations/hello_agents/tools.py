"""Tool adapters for HelloAgents."""

from hello_agents.tools import SearchTool, ToolRegistry
from hello_agents.tools.builtin.note_tool import NoteTool

ToolRegistryAdapter = ToolRegistry
NoteToolAdapter = NoteTool
SearchToolAdapter = SearchTool


def create_tool_registry() -> ToolRegistryAdapter:
    """Create a tool registry instance."""

    return ToolRegistry()


def create_note_tool(**kwargs) -> NoteToolAdapter:
    """Create the note tool used by the application."""

    return NoteTool(**kwargs)


def create_search_tool(**kwargs) -> SearchToolAdapter:
    """Create the search tool used by the application."""

    return SearchTool(**kwargs)
