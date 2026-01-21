from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from uuid import UUID
import datetime

from ..deps import get_current_user
from ...models import User, Speech, Rating
from ...schemas import RatingCreateRequest, RatingResponse, SpeechRatingInfo, RatingDeleteResponse
from ...db import get_db

router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post('', response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_rating(
    rating_request: RatingCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create or update a rating for a speech."""
    speech = db.query(Speech).filter(Speech.id == rating_request.speech_id).first()
    if not speech:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speech not found")
    
    # Find or create rating
    rating = db.query(Rating).filter(
        Rating.speech_id == rating_request.speech_id,
        Rating.rated_by == user.id,
        Rating.removed_at.is_(None)
    ).first()
    
    if rating:
        rating.score = rating_request.rating
        rating.created_at = datetime.datetime.now(datetime.timezone.utc)
    else:
        rating = Rating(speech_id=rating_request.speech_id, rated_by=user.id, score=rating_request.rating)
        db.add(rating)
    
    db.commit()
    db.refresh(rating)
    
    return RatingResponse(
        id=rating.id,
        speech_id=rating.speech_id,
        rated_by=rating.rated_by,
        rating=rating.score,
        created_at=rating.created_at
    )


@router.get('/speech/{speech_id}', response_model=SpeechRatingInfo)
async def get_speech_rating_info(
    speech_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get rating info for a speech."""
    speech = db.query(Speech).filter(Speech.id == speech_id).first()
    if not speech:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speech not found")
    
    # Get stats and user rating in one query
    stats = db.query(
        func.avg(Rating.score).label('avg'),
        func.count(Rating.id).label('total')
    ).filter(Rating.speech_id == speech_id, Rating.removed_at.is_(None)).first()
    
    user_rating = db.query(Rating.score).filter(
        Rating.speech_id == speech_id,
        Rating.rated_by == user.id,
        Rating.removed_at.is_(None)
    ).scalar()
    
    return SpeechRatingInfo(
        speech_id=speech_id,
        average_rating=round(float(stats.avg), 2) if stats.avg else None,
        total_ratings=int(stats.total),
        user_rating=float(user_rating) if user_rating else None
    )


@router.delete('/{speech_id}', response_model=RatingDeleteResponse)
async def delete_rating(
    speech_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a user's rating for a speech."""
    rating = db.query(Rating).filter(
        Rating.speech_id == speech_id,
        Rating.rated_by == user.id,
        Rating.removed_at.is_(None)
    ).first()
    
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    
    rating.removed_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    
    return RatingDeleteResponse(message="Rating deleted successfully", speech_id=speech_id)


@router.get('/my-ratings', response_model=list[RatingResponse])
async def get_my_ratings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get all ratings by current user."""
    ratings = db.query(Rating).filter(
        Rating.rated_by == user.id,
        Rating.removed_at.is_(None)
    ).order_by(Rating.created_at.desc()).all()
    
    return [
        RatingResponse(
            id=r.id,
            speech_id=r.speech_id,
            rated_by=r.rated_by,
            rating=r.score,
            created_at=r.created_at
        )
        for r in ratings
    ]

