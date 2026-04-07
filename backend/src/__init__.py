"""Coconut Research Assistant backend package."""

__version__ = "0.0.1"

from app.agents.deep_research_agent import DeepResearchAgent
from app.core.config import Configuration, SearchAPI
from app.models.domain import SummaryState, SummaryStateInput, SummaryStateOutput, TodoItem

__all__ = [
    "DeepResearchAgent",
    "Configuration",
    "SearchAPI",
    "SummaryState",
    "SummaryStateInput",
    "SummaryStateOutput",
    "TodoItem",
]
