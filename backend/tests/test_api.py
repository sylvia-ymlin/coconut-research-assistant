from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.models.domain import SummaryStateOutput, TodoItem


class StubDeepResearchAgent:
    should_fail = False

    def __init__(self, config=None, session_repository=None, session_id=None) -> None:
        self.session_id = session_id

    def run(self, topic: str) -> SummaryStateOutput:
        if self.should_fail:
            raise RuntimeError("boom")
        return SummaryStateOutput(
            running_summary="# Report",
            report_markdown="# Report",
            session_id=self.session_id,
            todo_items=[
                TodoItem(
                    id=1,
                    title="背景",
                    intent="梳理背景",
                    query="agent frameworks background",
                    status="completed",
                    summary="summary",
                    sources_summary="sources",
                )
            ],
        )

    def run_stream(self, topic: str):
        yield {
            "type": "session",
            "session_id": self.session_id,
            "status": "running",
            "topic": topic,
        }
        yield {
            "type": "todo_list",
            "tasks": [
                {
                    "id": 1,
                    "title": "背景",
                    "intent": "梳理背景",
                    "query": "agent frameworks background",
                    "status": "pending",
                }
            ],
        }
        if self.should_fail:
            raise RuntimeError("boom")
        yield {"type": "final_report", "report": "# Report", "session_id": self.session_id}
        yield {"type": "done"}


def build_client(monkeypatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("SESSIONS_DB_PATH", str(tmp_path / "sessions.sqlite3"))
    monkeypatch.setattr(
        "app.api.routes.research.DeepResearchAgent",
        StubDeepResearchAgent,
    )
    app = create_app()
    return TestClient(app)


def test_healthz() -> None:
    client = TestClient(create_app())

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_research_creates_session_and_lists_history(monkeypatch, tmp_path: Path) -> None:
    StubDeepResearchAgent.should_fail = False
    client = build_client(monkeypatch, tmp_path)

    response = client.post("/research", json={"topic": "Agent frameworks", "search_api": "tavily"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] is not None

    sessions_response = client.get("/sessions")
    assert sessions_response.status_code == 200
    sessions = sessions_response.json()
    assert len(sessions) == 1
    assert sessions[0]["status"] == "completed"

    detail_response = client.get(f"/sessions/{payload['session_id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["report_markdown"] == "# Report"
    assert detail["todo_items"][0]["summary"] == "summary"


def test_research_failure_marks_session_failed(monkeypatch, tmp_path: Path) -> None:
    StubDeepResearchAgent.should_fail = True
    client = build_client(monkeypatch, tmp_path)

    response = client.post("/research", json={"topic": "Failure case"})

    assert response.status_code == 500

    sessions_response = client.get("/sessions")
    sessions = sessions_response.json()
    assert len(sessions) == 1
    assert sessions[0]["status"] == "failed"
