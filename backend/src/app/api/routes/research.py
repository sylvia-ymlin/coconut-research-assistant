"""Research workflow API routes."""

from __future__ import annotations

import json
from typing import Any, Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from app.agents.deep_research_agent import DeepResearchAgent
from app.api.schemas import (
    ResearchRequest,
    ResearchResponse,
    ResearchSessionDetailResponse,
    ResearchSessionSummaryResponse,
    TodoItemResponse,
)
from app.core.config import Configuration
from app.models.domain import ResearchSessionDetail, ResearchSessionSummary, TodoItem
from app.services.sessions import SessionRepository

router = APIRouter(tags=["research"])


def _build_config(payload: ResearchRequest) -> Configuration:
    overrides: dict[str, Any] = {}

    if payload.search_api is not None:
        overrides["search_api"] = payload.search_api

    return Configuration.from_env(overrides=overrides)


def _get_session_repository(config: Configuration) -> SessionRepository:
    return SessionRepository(config.sessions_db_path)


def _serialize_task(item: TodoItem) -> TodoItemResponse:
    return TodoItemResponse(
        id=item.id,
        title=item.title,
        intent=item.intent,
        query=item.query,
        status=item.status,
        summary=item.summary,
        sources_summary=item.sources_summary,
        notices=list(item.notices or []),
        note_id=item.note_id,
        note_path=item.note_path,
    )


def _serialize_session_summary(item: ResearchSessionSummary) -> ResearchSessionSummaryResponse:
    return ResearchSessionSummaryResponse(
        session_id=item.session_id,
        topic=item.topic,
        status=item.status,
        search_api=item.search_api,
        created_at=item.created_at,
        updated_at=item.updated_at,
        task_count=item.task_count,
        completed_task_count=item.completed_task_count,
        report_available=item.report_available,
    )


def _serialize_session_detail(item: ResearchSessionDetail) -> ResearchSessionDetailResponse:
    return ResearchSessionDetailResponse(
        session_id=item.session_id,
        topic=item.topic,
        status=item.status,
        search_api=item.search_api,
        created_at=item.created_at,
        updated_at=item.updated_at,
        task_count=item.task_count,
        completed_task_count=item.completed_task_count,
        report_available=item.report_available,
        report_markdown=item.report_markdown,
        error_detail=item.error_detail,
        report_note_id=item.report_note_id,
        report_note_path=item.report_note_path,
        todo_items=[_serialize_task(task) for task in item.todo_items],
    )


@router.get("/healthz")
def health_check() -> dict[str, str]:
    """Health-check endpoint."""

    return {"status": "ok"}


@router.post("/research", response_model=ResearchResponse)
def run_research(payload: ResearchRequest) -> ResearchResponse:
    """Run the full research workflow and return the final report."""

    session_id: int | None = None
    try:
        config = _build_config(payload)
        repository = _get_session_repository(config)
        search_api = payload.search_api.value if payload.search_api is not None else config.search_api.value
        session_id = repository.create_session(
            topic=payload.topic,
            search_api=search_api,
        )
        agent = DeepResearchAgent(
            config=config,
            session_repository=repository,
            session_id=session_id,
        )
        result = agent.run(payload.topic)
        if session_id is not None:
            repository.replace_tasks(session_id, result.todo_items)
            existing_session = repository.get_session(session_id)
            if existing_session is None or existing_session.status == "running":
                repository.mark_completed(
                    session_id,
                    report_markdown=(result.report_markdown or result.running_summary or ""),
                )
    except ValueError as exc:
        if session_id is not None:
            repository.mark_failed(session_id, error_detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        if session_id is not None:
            repository.mark_failed(session_id, error_detail=str(exc))
        raise HTTPException(status_code=500, detail="Research failed") from exc

    todo_payload = [_serialize_task(item).model_dump() for item in result.todo_items]

    return ResearchResponse(
        session_id=result.session_id,
        report_markdown=(result.report_markdown or result.running_summary or ""),
        todo_items=todo_payload,
    )


@router.post("/research/stream")
def stream_research(payload: ResearchRequest) -> StreamingResponse:
    """Run the research workflow with server-sent event streaming."""

    session_id: int | None = None
    try:
        config = _build_config(payload)
        repository = _get_session_repository(config)
        search_api = payload.search_api.value if payload.search_api is not None else config.search_api.value
        session_id = repository.create_session(
            topic=payload.topic,
            search_api=search_api,
        )
        agent = DeepResearchAgent(
            config=config,
            session_repository=repository,
            session_id=session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    def event_iterator() -> Iterator[str]:
        try:
            for event in agent.run_stream(payload.topic):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as exc:
            logger.exception("Streaming research failed")
            if session_id is not None:
                repository.mark_failed(session_id, error_detail=str(exc))
            error_payload = {"type": "error", "detail": str(exc)}
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_iterator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/sessions", response_model=list[ResearchSessionSummaryResponse])
def list_sessions() -> list[ResearchSessionSummaryResponse]:
    """List persisted research sessions for the history sidebar."""

    config = Configuration.from_env()
    repository = _get_session_repository(config)
    return [_serialize_session_summary(item) for item in repository.list_sessions()]


@router.get("/sessions/{session_id}", response_model=ResearchSessionDetailResponse)
def get_session(session_id: int) -> ResearchSessionDetailResponse:
    """Return a single persisted session with its tasks and report."""

    config = Configuration.from_env()
    repository = _get_session_repository(config)
    session = repository.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return _serialize_session_detail(session)
