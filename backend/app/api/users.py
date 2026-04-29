"""User profile and preferences API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.schemas.schemas import (
    UserResponse, UserUpdate, UserPreferenceResponse, UserPreferenceCreate
)
from backend.app.services.user_service import UserService
from backend.app.models.models import UserPreference
from backend.app.utils.security import get_current_user
from backend.app.db.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user profile."""
    user = UserService.get_user_by_id(db, current_user["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update user profile."""
    user = UserService.update_user(db, current_user["user_id"], user_data)
    return user


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete user account (deactivate)."""
    UserService.delete_user(db, current_user["user_id"])


@router.get("/preferences", response_model=UserPreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user preferences."""
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user["user_id"]
    ).first()
    
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    
    return preferences


@router.put("/preferences", response_model=UserPreferenceResponse)
def update_preferences(
    pref_data: UserPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences."""
    preferences = db.query(UserPreference).filter(
        UserPreference.user_id == current_user["user_id"]
    ).first()
    
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    
    # Update preferences
    for key, value in pref_data.dict().items():
        if hasattr(preferences, key):
            setattr(preferences, key, value)
    
    db.commit()
    db.refresh(preferences)
    return preferences
