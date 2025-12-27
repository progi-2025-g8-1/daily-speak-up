from typing import Optional
from pydantic import BaseModel, EmailStr

from ..models import (
    AppLang,
    AppTheme,
    OnboardingStatus,
    UserRole
)

class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None

class UserResponse(BaseModel):
    role: UserRole
    email: str
    handle: str
    profile_picture_url: Optional[str]
    onboarding_status: OnboardingStatus
    preferred_lang: AppLang
    preferred_theme: AppTheme
    preferred_tz_offset: float
    email_notifications_enabled: bool
    push_notifications_enabled: bool
    streak_reminders_enabled: bool
    friends_count: int
    streak: int
