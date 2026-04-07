from types import SimpleNamespace

from app.core.config import Configuration
from app.services.planner import PlanningService


def build_service() -> PlanningService:
    return PlanningService(
        planner_agent=SimpleNamespace(),
        config=Configuration(strip_thinking_tokens=True),
    )


def test_extract_tasks_from_json_object() -> None:
    service = build_service()
    raw = """
    <think>hidden</think>
    {
      "tasks": [
        {"title": "背景", "intent": "梳理背景", "query": "agent frameworks background"},
        {"title": "趋势", "intent": "分析趋势", "query": "agent frameworks trends"}
      ]
    }
    """

    tasks = service._extract_tasks(raw)

    assert len(tasks) == 2
    assert tasks[0]["title"] == "背景"
    assert tasks[1]["query"] == "agent frameworks trends"


def test_extract_tasks_from_tool_call_payload() -> None:
    service = build_service()
    raw = """
    Planner output:
    [TOOL_CALL:planner:{"tasks":[{"title":"市场格局","intent":"看竞品","query":"agent platform market map"}]}]
    """

    tasks = service._extract_tasks(raw)

    assert len(tasks) == 1
    assert tasks[0]["intent"] == "看竞品"
