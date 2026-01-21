from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
import datetime


class RatingCreateRequest(BaseModel):
    """Request schema for creating/updating a rating"""
    speech_id: UUID
    rating: float = Field(..., ge=0, le=5, description="Rating score between 0 and 5")

    @field_validator('rating')
    @classmethod
    def validate_score(cls, v: float) -> float:
        if v < 0 or v > 5:
            raise ValueError('Rating must be between 0 and 5')
        return round(v, 2)


class RatingResponse(BaseModel):
    """Response schema for a rating"""
    id: UUID
    speech_id: UUID
    rated_by: UUID
    rating: float
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class SpeechRatingInfo(BaseModel):
    """Rating information for a speech"""
    speech_id: UUID
    average_rating: Optional[float] = Field(None, description="Average rating of the speech")
    total_ratings: int = Field(0, description="Total number of ratings")
    user_rating: Optional[float] = Field(None, description="Current user's rating if exists")


class RatingDeleteResponse(BaseModel):
    """Response schema for deleting a rating"""
    message: str
    speech_id: UUID
