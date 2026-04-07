"""SQLite-backed persistence for research sessions and tasks."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Iterable

from app.models.domain import ResearchSessionDetail, ResearchSessionSummary, TodoItem


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value)


class SessionRepository:
    """Persist research sessions locally using SQLite."""

    def __init__(self, database_path: str) -> None:
        self._path = Path(database_path).expanduser()
        self._lock = Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, timeout=30, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS research_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    status TEXT NOT NULL,
                    search_api TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    report_markdown TEXT DEFAULT '',
                    error_detail TEXT,
                    report_note_id TEXT,
                    report_note_path TEXT
                );

                CREATE TABLE IF NOT EXISTS research_tasks (
                    session_id INTEGER NOT NULL,
                    task_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    query TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary TEXT,
                    sources_summary TEXT,
                    notices_json TEXT DEFAULT '[]',
                    note_id TEXT,
                    note_path TEXT,
                    PRIMARY KEY (session_id, task_id),
                    FOREIGN KEY (session_id) REFERENCES research_sessions(session_id) ON DELETE CASCADE
                );
                """
            )

    def create_session(self, *, topic: str, search_api: str | None) -> int:
        timestamp = _utc_now()
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO research_sessions (
                    topic, status, search_api, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (topic, "running", search_api, timestamp, timestamp),
            )
            return int(cursor.lastrowid)

    def mark_running(self, session_id: int) -> None:
        self._update_session_fields(session_id, status="running")

    def mark_completed(
        self,
        session_id: int,
        *,
        report_markdown: str,
        report_note_id: str | None = None,
        report_note_path: str | None = None,
    ) -> None:
        self._update_session_fields(
            session_id,
            status="completed",
            report_markdown=report_markdown,
            error_detail=None,
            report_note_id=report_note_id,
            report_note_path=report_note_path,
        )

    def mark_failed(self, session_id: int, *, error_detail: str) -> None:
        self._update_session_fields(
            session_id,
            status="failed",
            error_detail=error_detail,
        )

    def replace_tasks(self, session_id: int, tasks: Iterable[TodoItem]) -> None:
        task_list = list(tasks)
        timestamp = _utc_now()
        with self._lock, self._connect() as connection:
            connection.execute(
                "DELETE FROM research_tasks WHERE session_id = ?",
                (session_id,),
            )
            for task in task_list:
                connection.execute(
                    """
                    INSERT INTO research_tasks (
                        session_id, task_id, title, intent, query, status,
                        summary, sources_summary, notices_json, note_id, note_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        task.id,
                        task.title,
                        task.intent,
                        task.query,
                        task.status,
                        task.summary,
                        task.sources_summary,
                        json.dumps(task.notices, ensure_ascii=False),
                        task.note_id,
                        task.note_path,
                    ),
                )
            connection.execute(
                "UPDATE research_sessions SET updated_at = ? WHERE session_id = ?",
                (timestamp, session_id),
            )

    def upsert_task(self, session_id: int, task: TodoItem) -> None:
        timestamp = _utc_now()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO research_tasks (
                    session_id, task_id, title, intent, query, status,
                    summary, sources_summary, notices_json, note_id, note_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, task_id) DO UPDATE SET
                    title=excluded.title,
                    intent=excluded.intent,
                    query=excluded.query,
                    status=excluded.status,
                    summary=excluded.summary,
                    sources_summary=excluded.sources_summary,
                    notices_json=excluded.notices_json,
                    note_id=excluded.note_id,
                    note_path=excluded.note_path
                """,
                (
                    session_id,
                    task.id,
                    task.title,
                    task.intent,
                    task.query,
                    task.status,
                    task.summary,
                    task.sources_summary,
                    json.dumps(task.notices, ensure_ascii=False),
                    task.note_id,
                    task.note_path,
                ),
            )
            connection.execute(
                "UPDATE research_sessions SET updated_at = ? WHERE session_id = ?",
                (timestamp, session_id),
            )

    def list_sessions(self) -> list[ResearchSessionSummary]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    s.session_id,
                    s.topic,
                    s.status,
                    s.search_api,
                    s.created_at,
                    s.updated_at,
                    CASE
                        WHEN COALESCE(s.report_markdown, '') <> '' THEN 1
                        ELSE 0
                    END AS report_available,
                    COUNT(t.task_id) AS task_count,
                    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) AS completed_task_count
                FROM research_sessions s
                LEFT JOIN research_tasks t ON t.session_id = s.session_id
                GROUP BY s.session_id
                ORDER BY s.updated_at DESC
                """
            ).fetchall()

        summaries: list[ResearchSessionSummary] = []
        for row in rows:
            summaries.append(
                ResearchSessionSummary(
                    session_id=int(row["session_id"]),
                    topic=str(row["topic"]),
                    status=str(row["status"]),
                    search_api=row["search_api"],
                    created_at=_parse_datetime(row["created_at"]),
                    updated_at=_parse_datetime(row["updated_at"]),
                    task_count=int(row["task_count"] or 0),
                    completed_task_count=int(row["completed_task_count"] or 0),
                    report_available=bool(row["report_available"]),
                )
            )
        return summaries

    def get_session(self, session_id: int) -> ResearchSessionDetail | None:
        with self._connect() as connection:
            session_row = connection.execute(
                """
                SELECT
                    session_id,
                    topic,
                    status,
                    search_api,
                    created_at,
                    updated_at,
                    report_markdown,
                    error_detail,
                    report_note_id,
                    report_note_path
                FROM research_sessions
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
            if session_row is None:
                return None

            task_rows = connection.execute(
                """
                SELECT
                    task_id,
                    title,
                    intent,
                    query,
                    status,
                    summary,
                    sources_summary,
                    notices_json,
                    note_id,
                    note_path
                FROM research_tasks
                WHERE session_id = ?
                ORDER BY task_id ASC
                """,
                (session_id,),
            ).fetchall()

        tasks = [
            TodoItem(
                id=int(row["task_id"]),
                title=str(row["title"]),
                intent=str(row["intent"]),
                query=str(row["query"]),
                status=str(row["status"]),
                summary=row["summary"],
                sources_summary=row["sources_summary"],
                notices=list(json.loads(row["notices_json"] or "[]")),
                note_id=row["note_id"],
                note_path=row["note_path"],
            )
            for row in task_rows
        ]

        completed_count = sum(1 for task in tasks if task.status == "completed")
        report_markdown = str(session_row["report_markdown"] or "")

        return ResearchSessionDetail(
            session_id=int(session_row["session_id"]),
            topic=str(session_row["topic"]),
            status=str(session_row["status"]),
            search_api=session_row["search_api"],
            created_at=_parse_datetime(session_row["created_at"]),
            updated_at=_parse_datetime(session_row["updated_at"]),
            task_count=len(tasks),
            completed_task_count=completed_count,
            report_available=bool(report_markdown.strip()),
            report_markdown=report_markdown,
            error_detail=session_row["error_detail"],
            report_note_id=session_row["report_note_id"],
            report_note_path=session_row["report_note_path"],
            todo_items=tasks,
        )

    def _update_session_fields(self, session_id: int, **fields: object) -> None:
        values = {key: value for key, value in fields.items()}
        values["updated_at"] = _utc_now()
        assignments = ", ".join(f"{key} = ?" for key in values.keys())
        parameters = [*values.values(), session_id]

        with self._lock, self._connect() as connection:
            connection.execute(
                f"UPDATE research_sessions SET {assignments} WHERE session_id = ?",
                parameters,
            )
