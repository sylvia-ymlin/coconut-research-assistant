from pathlib import Path

from app.models.domain import TodoItem
from app.services.sessions import SessionRepository


def test_session_repository_round_trip(tmp_path: Path) -> None:
    repository = SessionRepository(str(tmp_path / "sessions.sqlite3"))

    session_id = repository.create_session(
        topic="Agent frameworks",
        search_api="tavily",
    )
    repository.replace_tasks(
        session_id,
        [
            TodoItem(
                id=1,
                title="背景",
                intent="梳理背景",
                query="agent frameworks background",
                status="in_progress",
            )
        ],
    )

    repository.upsert_task(
        session_id,
        TodoItem(
            id=1,
            title="背景",
            intent="梳理背景",
            query="agent frameworks background",
            status="completed",
            summary="summary",
            sources_summary="sources",
            notices=["notice"],
            note_id="note-1",
            note_path="./notes/note-1.md",
        ),
    )
    repository.mark_completed(
        session_id,
        report_markdown="# Report",
        report_note_id="report-note",
        report_note_path="./notes/report-note.md",
    )

    summaries = repository.list_sessions()
    detail = repository.get_session(session_id)

    assert len(summaries) == 1
    assert summaries[0].status == "completed"
    assert summaries[0].report_available is True
    assert detail is not None
    assert detail.report_markdown == "# Report"
    assert detail.todo_items[0].summary == "summary"
    assert detail.todo_items[0].notices == ["notice"]
