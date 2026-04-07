from app.core.config import Configuration
from app.models.domain import SummaryState, TodoItem
from app.services.reporter import ReportingService
from app.services.summarizer import SummarizationService


class StubAgent:
    def __init__(self, response: str) -> None:
        self._response = response
        self.cleared = False

    def run(self, prompt: str) -> str:
        return self._response

    def clear_history(self) -> None:
        self.cleared = True

    def stream_run(self, prompt: str):
        yield self._response


def test_reporting_service_strips_thinking_and_tool_calls() -> None:
    agent = StubAgent(
        "<think>internal</think>\n[TOOL_CALL:note:{\"action\":\"read\"}]\n# Final\nUseful report"
    )
    state = SummaryState(
        research_topic="Agent frameworks",
        todo_items=[
            TodoItem(
                id=1,
                title="背景",
                intent="看背景",
                query="agent frameworks background",
                status="completed",
                summary="summary",
                sources_summary="source",
            )
        ],
    )

    service = ReportingService(agent, Configuration(strip_thinking_tokens=True))
    report = service.generate_report(state)

    assert "<think>" not in report
    assert "TOOL_CALL" not in report
    assert "Useful report" in report
    assert agent.cleared is True


def test_summarization_service_strips_thinking_and_tool_calls() -> None:
    service = SummarizationService(
        summarizer_factory=lambda: StubAgent(
            "<think>internal</think>\n[TOOL_CALL:note:{\"action\":\"update\"}]\nVisible summary"
        ),
        config=Configuration(strip_thinking_tokens=True),
    )

    summary = service.summarize_task(
        SummaryState(research_topic="Agent frameworks"),
        TodoItem(
            id=1,
            title="背景",
            intent="梳理背景",
            query="agent frameworks background",
        ),
        "context",
    )

    assert "<think>" not in summary
    assert "TOOL_CALL" not in summary
    assert summary == "Visible summary"
