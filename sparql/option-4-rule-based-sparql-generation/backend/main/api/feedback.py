"""POST /api/feedback — anonymous answer feedback endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Header

from backend.main.analytics import (
    FeedbackEvent,
    safe_record_feedback,
    utc_now,
    validate_session_id,
)
from backend.main.api.exploration import _analytics
from backend.main.schemas.requests import FeedbackRequest

router = APIRouter()


@router.post("/api/feedback", status_code=204)
async def feedback(
    request: FeedbackRequest,
    x_analytics_enabled: str | None = Header(default=None),
    x_session_id: str | None = Header(default=None),
) -> None:
    """Record one feedback click when anonymous analytics is enabled."""
    if x_analytics_enabled != "true":
        return

    session_id = validate_session_id(x_session_id)
    if session_id is None:
        return

    safe_record_feedback(
        _analytics,
        FeedbackEvent(
            session_id=session_id,
            answer_turn_id=request.answer_turn_id,
            feedback=request.feedback,
            created_at=utc_now(),
        ),
    )
