"""POST /api/exploration — main exploration endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from backend.main.schemas.requests import ChatRequest
from backend.main.schemas.responses import ExplorationResponse
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
