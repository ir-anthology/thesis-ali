"""POST /api/exploration — main exploration endpoint."""

from __future__ import annotations

import logging
import json
import asyncio
from datetime import datetime
from collections.abc import AsyncIterator

from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse

from backend.main.analytics import (
    AnalyticsEvent,
    AnalyticsRepository,
    safe_record,
    utc_now,
    validate_session_id,
)
from backend.main.schemas.requests import CellQuestionRequest, ChatRequest
from backend.main.schemas.responses import CellQuestionResponse, ExplorationResponse
from backend.main.services.exploration import ExplorationService

logger = logging.getLogger(__name__)

router = APIRouter()

_service = ExplorationService()
_analytics = AnalyticsRepository()


def _outcome(response: ExplorationResponse) -> str:
    text = (response.interpretation or "").lower()
    if "invalid" in text:
        return "validation_error"
    if "execution failed" in text:
        return "sparql_error"
    if response.columns is not None or response.rows is not None:
        return "success"
    if "ambiguous" in text or "which one" in text:
        return "ambiguous"
    if "does not" in text or "cannot" in text or "not supported" in text:
        return "out_of_scope"
    return "success"


def _record_event(
    request: ChatRequest,
    response: ExplorationResponse,
    session_id: str | None,
    started_at: datetime,
    enabled: bool,
    error_category: str | None = None,
) -> None:
    if not enabled or session_id is None:
        return
    safe_record(
        _analytics,
        AnalyticsEvent(
            session_id=session_id,
            started_at=started_at,
            finished_at=utc_now(),
            message=request.message,
            history=[turn.model_dump(mode="json") for turn in request.history],
            response=response.model_dump(mode="json"),
            outcome=_outcome(response) if error_category is None else "backend_error",
            result_rows=len(response.rows or []),
            error_category=error_category,
        ),
    )


@router.post("/api/exploration", response_model=ExplorationResponse)
async def explore(
    request: ChatRequest,
    x_analytics_enabled: str | None = Header(default=None),
    x_session_id: str | None = Header(default=None),
) -> ExplorationResponse:
    """Process an exploration query."""
    started_at = utc_now()
    enabled = x_analytics_enabled == "true"
    session_id = validate_session_id(x_session_id)

    try:
        response = await _service.explore(request)
        if enabled:
            _record_event(request, response, session_id, started_at, enabled)
        logger.info("Exploration completed: outcome=%s rows=%d", _outcome(response), len(response.rows or []))
        return response
    except Exception:
        logger.exception("Pipeline failed")
        response = ExplorationResponse(
            interpretation="An error occurred while processing your query.",
            suggestions=[
                "Try rephrasing your question",
                "Ask about authors, publications, or venues",
                "Check if the entity names are correct",
            ],
        )
        if enabled:
            _record_event(request, response, session_id, started_at, enabled, "pipeline")
        return response


@router.post("/api/cell-question", response_model=CellQuestionResponse)
async def cell_question(request: CellQuestionRequest) -> CellQuestionResponse:
    """Generate one follow-up question for a clicked result cell."""
    logger.info("Generating cell question for column: %s", request.column)
    question = await _service.generate_cell_question(request)
    return CellQuestionResponse(question=question)


def _encode_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _stream_events(
    request: ChatRequest,
    analytics_enabled: bool,
    session_id: str | None,
) -> AsyncIterator[str]:
    started_at = utc_now()
    response_data: dict[str, object] = {}
    try:
        async for item in _service.explore_stream(request):
            event = item["event"]
            data = item["data"]
            if event == "interpretation":
                response_data["interpretation"] = data.get("text")
            elif event == "sparql":
                response_data["sparql_query"] = data.get("query")
            elif event == "result":
                response_data["columns"] = data.get("columns")
                response_data["rows"] = data.get("rows")
            elif event == "observations":
                response_data["observations"] = data.get("items")
            elif event == "suggestions":
                response_data["suggestions"] = data.get("items")
            elif event == "error":
                response_data["interpretation"] = data.get("message")
            yield _encode_sse(item["event"], item["data"])
    except Exception:
        logger.exception("Streaming pipeline failed")
        response_data["interpretation"] = "An error occurred while processing your query."
        yield _encode_sse(
            "error",
            {"message": "An error occurred while processing your query."},
        )
        error_category = "stream"
    else:
        error_category = None

    if analytics_enabled and session_id is not None:
        response = ExplorationResponse.model_validate(response_data)
        _record_event(request, response, session_id, started_at, True, error_category)


@router.post("/api/exploration/stream")
async def explore_stream(
    request: ChatRequest,
    x_analytics_enabled: str | None = Header(default=None),
    x_session_id: str | None = Header(default=None),
) -> StreamingResponse:
    """Stream exploration stages as Server-Sent Events."""
    enabled = x_analytics_enabled == "true"
    session_id = validate_session_id(x_session_id)
    return StreamingResponse(
        _stream_events(request, enabled, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
