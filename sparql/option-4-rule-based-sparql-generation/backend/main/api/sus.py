"""POST /api/sus — validate, score, and store explicit SUS submissions."""

from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from backend.main.analytics import SUSSubmission, utc_now, validate_session_id
from backend.main.api.exploration import _analytics
from backend.main.schemas.requests import SUSSubmissionRequest
from backend.main.schemas.responses import SUSSubmissionResponse

logger = logging.getLogger(__name__)


class _SUSRoute(APIRoute):
    """Keep the survey's required 400 validation status local to this router."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def handle(request: Request) -> Response:
            try:
                return await handler(request)
            except RequestValidationError:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Supply questionnaire SUS, version brooke-1996, and "
                        "exactly ten integer answers from 1 through 5."
                    ),
                ) from None

        return handle


router = APIRouter(route_class=_SUSRoute)


@router.post(
    "/api/sus",
    status_code=201,
    response_model=SUSSubmissionResponse,
    responses={
        400: {"description": "Invalid questionnaire, answers, or session UUID"},
        500: {"description": "The submission could not be stored"},
        # Suppress FastAPI's default 422 documentation for this route.
        "4XX": {"description": "Invalid request"},
    },
)
def submit_sus(
    request: SUSSubmissionRequest,
    x_session_id: str | None = Header(default=None),
) -> SUSSubmissionResponse:
    """Store a submitted survey, independently of conversation analytics opt-in."""
    session_id = validate_session_id(x_session_id)
    if x_session_id is not None and session_id is None:
        raise HTTPException(status_code=400, detail="X-Session-Id must be a valid UUID.")

    submission = SUSSubmission(
        submission_id=str(uuid4()),
        questionnaire=request.questionnaire,
        version=request.version,
        answers=request.answers,
        sus_score=request.calculate_score(),
        session_id=session_id,
        submitted_at=utc_now(),
    )
    try:
        _analytics.record_sus(submission)
    except Exception:
        logger.exception("SUS submission storage failed")
        raise HTTPException(
            status_code=500, detail="The survey could not be stored. Please try again."
        ) from None

    return SUSSubmissionResponse(submission_id=submission.submission_id)
