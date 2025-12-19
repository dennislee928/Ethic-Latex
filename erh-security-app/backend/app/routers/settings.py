"""
API routes for user settings management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.schemas import UserSettingsRead, UserPreferences
from ..core.models import UserSettings
from ..deps import get_db

router = APIRouter()


@router.get("/", response_model=UserSettingsRead, tags=["settings"])
def get_settings(db: Session = Depends(get_db)):
    """
    Get user settings.
    
    Note: In a production system, you'd get the user_id from authentication.
    For now, we'll use a default user_id of 1.
    """
    # TODO: Get user_id from authenticated user
    user_id = 1

    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        # Create default settings
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
):
    """Update user settings."""
    # TODO: Get user_id from authenticated user
    user_id = 1

    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(
            user_id=user_id,
            preferences=preferences.dict(exclude_unset=True),
        )
        db.add(settings)
    else:
        # Update preferences
        current_prefs = settings.preferences or {}
        current_prefs.update(preferences.dict(exclude_unset=True))
        settings.preferences = current_prefs

    db.commit()
    db.refresh(settings)
    return settings

