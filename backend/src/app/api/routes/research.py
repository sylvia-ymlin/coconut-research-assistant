"""Research workflow API routes."""

from __future__ import annotations

import json
from typing import Any, Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from app.agents.deep_research_agent import DeepResearchAgent
from app.api.schemas import ResearchRequest, ResearchResponse
from app.core.config import Configuration

router = APIRouter(tags=["research"])


def _build_config(payload: ResearchRequest) -> Configuration:
    overrides: dict[str, Any] = {}

    if payload.search_api is not None:
        overrides["search_api"] = payload.search_api

    return Configuration.from_env(overrides=overrides)


@router.get("/healthz")
def health_check() -> dict[str, str]:
    """Health-check endpoint."""

    return {"status": "ok"}


@router.post("/research", response_model=ResearchResponse)
def run_research(payload: ResearchRequest) -> ResearchResponse:
    """Run the full research workflow and return the final report."""

    try:
        config = _build_config(payload)
        agent = DeepResearchAgent(config=config)
        result = agent.run(payload.topic)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Research failed") from exc

    todo_payload = [
        {
            "id": item.id,
            "title": item.title,
            "intent": item.intent,
            "query": item.query,
            "status": item.status,
            "summary": item.summary,
            "sources_summary": item.sources_summary,
            "note_id": item.note_id,
            "note_path": item.note_path,
        }
        for item in result.todo_items
    ]

    return ResearchResponse(
        report_markdown=(result.report_markdown or result.running_summary or ""),
        todo_items=todo_payload,
    )


@router.post("/research/stream")
def stream_research(payload: ResearchRequest) -> StreamingResponse:
    """Run the research workflow with server-sent event streaming."""

    try:
        config = _build_config(payload)
        agent = DeepResearchAgent(config=config)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    def event_iterator() -> Iterator[str]:
        try:
            for event in agent.run_stream(payload.topic):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as exc:
            logger.exception("Streaming research failed")
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
