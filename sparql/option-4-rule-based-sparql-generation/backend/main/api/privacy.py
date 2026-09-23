"""Public data-collection policy used by the frontend notice."""

from fastapi import APIRouter

from backend.main.config import ANALYTICS_RETENTION_DAYS

router = APIRouter()


@router.get("/api/privacy")
async def privacy_policy() -> dict[str, object]:
    """Describe the analytics collection policy without exposing stored data."""
    return {
        "analytics_enabled_by_default": True,
        "anonymous": True,
        "stores_full_conversations": True,
        "retention_days": ANALYTICS_RETENTION_DAYS,
        "inactivity_timeout_minutes": 30,
        "opt_out_supported": True,
        "purpose": "Improve the service",
    }
