import logging
import datetime
from uuid import UUID 
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import extract
from sqlalchemy.orm import Session

from ..deps import get_session
from ...db import get_db
from ...schemas import UserResponse, UserCreate, MonthlyUserVideosResponse, VideoInfo
from ...models import User, Friendship, UserStreak, Speech
from supertokens_python.recipe.session import SessionContainer

from ...services import EmailService

logger = logging.getLogger(__name__)
router = APIRouter(tags=['user'], prefix='/user')

@router.put('/register', response_class=JSONResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    # Get user_id from SuperTokens session
    supertokens_user_id = session.get_user_id()
    
    existing_user: User | None = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User already exists'
        )

    user = User(
        supertokens_user_id=supertokens_user_id,
        email=user_data.email,
        handle=supertokens_user_id,  # Default handle
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    EmailService.send_email(    
        to_mail=user_data.email,
        subject="Welcome to DailySpeakUp!"
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'ok'
        }
    )

@router.get('/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    supertokens_user_id = session.get_user_id()

    user: User | None = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    friends_count = db.query(Friendship).filter(
        (Friendship.user_id1 == user.id) | (Friendship.user_id2 == user.id)
    ).count()

    streak = db.query(UserStreak).filter(
        UserStreak.user_id == user.id 
    ).order_by(UserStreak.created_at.desc()).first()

    if streak is None or streak.ends_at < datetime.datetime.now(datetime.timezone.utc):
        streak_days = 0
    else:
        streak_days = (streak.ends_at.date() - streak.starts_at.date()).days + 1 

    return UserResponse(
        role=user.role,
        email=user.email,
        handle=user.handle,
        profile_picture_url=user.profile_picture_url,
        onboarding_status=user.onboarding_status,
        preferred_lang=user.preferred_lang,
        preferred_theme=user.preferred_theme,
        preferred_tz_offset=user.preferred_tz_offset,
        email_notifications_enabled=user.email_notifications_enabled,
        push_notifications_enabled=user.push_notifications_enabled,
        streak_reminders_enabled=user.streak_reminders_enabled,
        friends_count=friends_count,
        streak=streak_days
    )

@router.get('/{user_id}/{year}/{month}/videos', response_model=MonthlyUserVideosResponse)
async def get_monthly_user_videos(
    user_id: UUID,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    supertokens_user_id = session.get_user_id()

    requesting_user: User | None = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()

    if requesting_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Requesting user not found'
        )
    
    # Ovdje će kasnije vjerojatno trebati proći po friendship pravilima,
    # Ako su prijatelji, vratiti listu videa koji imaju FRIENDS vidljivost (ili praznu listu ako takvih nema),
    # inače vratiti FORBIDDEN ako nisu prijatelji
    elif str(requesting_user.supertokens_user_id) != str(user_id):
        print(str(requesting_user.supertokens_user_id) != str(user_id))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )
    
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid month'
        )
    
    speeches = db.query(Speech).filter(
        Speech.user_id == requesting_user.id,
        extract('year', Speech.created_at) == year,
        extract('month', Speech.created_at) == month
    ).all()

    videos = { 
        int(speech.created_at.date().day): VideoInfo(
            id=speech.id, 
            url=speech.s3_url
        ) 
        for speech in speeches 
        if speech.s3_url is not None and not speech.is_cancelled 
    }
    
    return MonthlyUserVideosResponse(videos=videos)