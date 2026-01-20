from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from supertokens_python.recipe.session import SessionContainer

from ..deps import get_session, get_current_user
from ...db import get_db
from ...models import User
from ...models.enums import OnboardingStatus
from ...schemas.userdata import UsernameData, InterestData
from .userdata import set_username, set_interests

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/state")
async def get_onboarding_state(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get the current onboarding state for the authenticated user."""
    
    # Map onboarding status to phase number
    phase_map = {
        OnboardingStatus.PENDING: 1,
        OnboardingStatus.PROFILE_CUSTOMIZATION: 1,
        OnboardingStatus.INTERESTS_SELECTION: 2,
        OnboardingStatus.COMPLETED: None,
    }
    
    return {
        "completed": user.onboarding_status == OnboardingStatus.COMPLETED,
        "phase": phase_map.get(user.onboarding_status, 1),
        "status": user.onboarding_status
    }


@router.patch("/profile")
async def update_onboarding_profile(
    profile_data: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update user profile during onboarding (Phase 1). Uses existing userdata endpoint."""
    # Use the existing set_username endpoint
    if 'handle' in profile_data:
        username_data = UsernameData(username=profile_data['handle'])
        await set_username(username_data, db, user)
    
    # Update onboarding status
    user.onboarding_status = OnboardingStatus.INTERESTS_SELECTION
    db.commit()
    
    return {
        "message": "Profile updated successfully",
        "onboarding_status": OnboardingStatus.INTERESTS_SELECTION
    }


@router.patch("/interests")
async def update_onboarding_interests(
    interest_data: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update user interests during onboarding (Phase 2). Uses existing userdata endpoint."""
    # Use the existing set_interests endpoint
    interests_list = interest_data.get('interests', [])
    interests = InterestData(interests=interests_list)
    result = await set_interests(interests, db, user)
    
    # Update onboarding status to completed
    user.onboarding_status = OnboardingStatus.COMPLETED
    db.commit()
    
    return {
        "message": "Onboarding completed successfully",
        "onboarding_status": OnboardingStatus.COMPLETED
    }
