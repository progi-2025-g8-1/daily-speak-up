from uuid import UUID
from pydantic import BaseModel
from typing import Optional

from ..models import UserRole

class UserDashboardResponse(BaseModel):
    user_id: UUID
    email: str
    handle: str
    profile_picture_url: Optional[str]
    user_role: Optional[UserRole]

class BanInfo(BaseModel):
    ban_reason: Optional[str]
    banned_by: UserDashboardResponse
    banned_user: UserDashboardResponse
    ban_id: UUID

class ReportedVideoResponse(BaseModel):
    video_id: UUID
    year: int
    month: int
    day: int
    caption: str | None
    report_reasons: list[str]
    user_info: UserDashboardResponse
    video_url: str

class StatsResponse(BaseModel):
    labels: list[str]
    counts: list[int]

class StatsSummaryResponse(BaseModel):
    total_users: int
    total_speeches: int
    total_bans: int
    pending_reports: int