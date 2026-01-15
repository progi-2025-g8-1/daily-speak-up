from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr

from ..models import (
    AppLang,
    AppTheme,
    OnboardingStatus,
    UserRole,
    SpeechVisibility
)

class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None

class UserResponse(BaseModel):
    id: UUID
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

class VideoInfo(BaseModel):
    video_id: UUID
    owner_id: UUID
    year: int
    month: int
    day: int
    caption: Optional[str]
    url: str
    visibility: SpeechVisibility

class MonthlyUserVideosResponse(BaseModel):
    videos: List[VideoInfo]  

class FriendInfo(BaseModel):
    user_id: UUID
    handle: str
    profile_picture_url: Optional[str]
class FriendsListResponse(BaseModel):
    friends: List[FriendInfo]

class UserInterestsResponse(BaseModel):
    interests: List[str]

class NotificationSettingUpdate(BaseModel):
    enabled: bool

class PublicUserProfile(BaseModel):
    id: UUID
    handle: str
    profile_picture_url: str | None
    friend_count: int
    current_streak: int
