from uuid import UUID
from pydantic import BaseModel

class ReportedVideoResponse(BaseModel):
    video_id: UUID
    owner_id: UUID
    year: int
    month: int
    day: int
    caption: str | None
    report_reasons: list[str]
    video_url: str