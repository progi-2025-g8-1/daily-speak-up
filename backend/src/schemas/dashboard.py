from uuid import UUID
from pydantic import BaseModel
from typing import Optional

class UserDashboardResponse(BaseModel):
    user_id: UUID
    email: str
    handle: str
    profile_picture_url: Optional[str]

class BanInfo(BaseModel):
    ban_reason: Optional[str]
    banned_by: UUID
    ban_id: UUID
    user_info: UserDashboardResponse

class ReportedVideoResponse(BaseModel):
    video_id: UUID
    year: int
    month: int
    day: int
    caption: str | None
    report_reasons: list[str]
    user_info: UserDashboardResponse
    video_url: str