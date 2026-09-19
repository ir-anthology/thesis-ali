"""POST /api/exploration — main exploration endpoint."""

from __future__ import annotations

import logging
import json
import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.main.schemas.requests import CellQuestionRequest, ChatRequest
from backend.main.schemas.responses import CellQuestionResponse, ExplorationResponse
from backend.main.services.exploration import ExplorationService

logger = logging.getLogger(__name__)

router = APIRouter()

_service = ExplorationService()


@router.post("/api/exploration", response_model=ExplorationResponse)
async def explore(request: ChatRequest) -> ExplorationResponse:
    """Process an exploration query."""
    logger.info("Received exploration request: %s", request.message)

    try:
        return await _service.explore(request)
    except Exception:
        logger.exception("Pipeline failed")
        return ExplorationResponse(
            interpretation="An error occurred while processing your query.",
            suggestions=[
                "Try rephrasing your question",
                "Ask about authors, publications, or venues",
                "Check if the entity names are correct",
            ],
        )


@router.post("/api/cell-question", response_model=CellQuestionResponse)
async def cell_question(request: CellQuestionRequest) -> CellQuestionResponse:
    """Generate one follow-up question for a clicked result cell."""
    logger.info("Generating cell question for column: %s", request.column)
    question = await _service.generate_cell_question(request)
    return CellQuestionResponse(question=question)


def _encode_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _stream_events(request: ChatRequest) -> AsyncIterator[str]:
    try:
        async for item in _service.explore_stream(request):
            yield _encode_sse(item["event"], item["data"])
    except Exception:
        logger.exception("Streaming pipeline failed")
        yield _encode_sse(
            "error",
            {"message": "An error occurred while processing your query."},
        )


@router.post("/api/exploration/stream")
async def explore_stream(request: ChatRequest) -> StreamingResponse:
    """Stream exploration stages as Server-Sent Events."""
    return StreamingResponse(
        _stream_events(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
