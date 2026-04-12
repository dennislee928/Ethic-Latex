"""
API routes for user settings management.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.schemas import UserSettingsRead, UserPreferences
from ..core.models import UserSettings
from ..deps import get_db, get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=UserSettingsRead, tags=["settings"])
def get_settings(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get user settings for the authenticated user.

    VUL-003: user_id is resolved from the authenticated user via
    get_current_user_id(). Full JWT validation is pending (see deps.py).
    """
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        # Create default settings for new users
        settings = UserSettings(
            user_id=user_id,
            preferences={
                "theme": "light",
                "default_judge_type": "COMBINED",
                "auto_save": True,
            },
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.put("/", response_model=UserSettingsRead, tags=["settings"])
def update_settings(
    preferences: UserPreferences,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update settings for the authenticated user."""
    # VUL-003: Scoped to the authenticated user's record.
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(
            user_id=user_id,
            preferences=preferences.dict(exclude_unset=True),
        )
        db.add(settings)
    else:
        # Merge preferences
        current_prefs = settings.preferences or {}
        current_prefs.update(preferences.dict(exclude_unset=True))
        settings.preferences = current_prefs

    db.commit()
    db.refresh(settings)
    logger.info("Updated settings for user_id=%d", user_id)
    return settings

