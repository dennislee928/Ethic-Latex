from fastapi import APIRouter

from ..config import get_settings


router = APIRouter()


@router.get("/", summary="Health check", tags=["health"])
def health_check() -> dict:
    """
    Simple health check endpoint.

    Returns basic status information so that monitoring systems
    (or humans) can verify that the API is alive.
    """
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
    }


