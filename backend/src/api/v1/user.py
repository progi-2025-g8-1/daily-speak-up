import logging
import datetime
from uuid import UUID 
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import extract
from sqlalchemy.orm import Session

from ..deps import get_session, get_s3_service
from ...db import get_db
from ...schemas import UserResponse, UserCreate, MonthlyUserVideosResponse, VideoInfo, FriendsListResponse, FriendInfo, UserInterestsResponse, NotificationSettingUpdate
from ...models import User, Friendship, UserStreak, Speech, UserInterest, Interest
from supertokens_python.recipe.session import SessionContainer

from ...services import EmailService, S3SecureService

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
        # `end_date` is nullable in the model. If it's missing, treat the
        # current date (UTC) as the effective end date for the ongoing streak.
        # Ensure we operate on `date` objects when subtracting.
        end_date: datetime.date = (
            streak.end_date if streak.end_date is not None else datetime.datetime.now(datetime.timezone.utc).date()
        )
        start_date: datetime.date = streak.start_date

        # Use inclusive day count: a streak that starts and ends the same day counts as 1.
        days_delta = (end_date - start_date).days
        streak_days = max(0, int(days_delta) + 1)

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
    s3_service: S3SecureService = Depends(get_s3_service),
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
    
    # Fetch speeches and generate presigned read URLs for each available video
    speeches = db.query(Speech).filter(
        Speech.user_id == requesting_user.id,
        extract('year', Speech.created_at) == year,
        extract('month', Speech.created_at) == month
    ).all()

    videos = []

    for speech in speeches:

        if speech.s3_url is None or speech.is_cancelled:
            continue

        download_url = None

        # Pre sign the S3 URL
        try:
            rd = s3_service.get_read_url(str(requesting_user.id), str(speech.id))
            if isinstance(rd, dict):
                download_url = rd.get('download_url')
            elif hasattr(rd, 'get'):
                download_url = rd.get('download_url')
            else:
                download_url = getattr(rd, 'download_url', None)
        except Exception as exc:
            logger.debug("Failed to generate presigned URL for speech %s: %s", speech.id, exc)
            download_url = None

        videos.append(
            VideoInfo(
                video_id=speech.id,
                year=speech.created_at.year,
                month=speech.created_at.month,
                day=speech.created_at.day,
                caption=speech.caption,
                url=download_url if download_url is not None else speech.s3_url,
                owner_id=speech.user_id,
                visibility=speech.visibility_level
            )
        )
    
    return MonthlyUserVideosResponse(videos=videos)

@router.get('/{user_id}/friends', response_model=FriendsListResponse)
async def get_friends_list(
    user_id: UUID,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    supertokens_user_id = session.get_user_id()

    requesting_user: User | None = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()

    if requesting_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be logged in to view friends list'
        )

    target_user: User | None = db.query(User).filter(
        User.supertokens_user_id == str(user_id)
    ).first()

    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Target user not found'
        )
    
    friendships = db.query(Friendship).filter(
        (Friendship.user_id1 == target_user.id) | (Friendship.user_id2 == target_user.id)
    ).all()

    friend_infos = []
    for friendship in friendships:
        friend_id = friendship.user_id2 if friendship.user_id1 == target_user.id else friendship.user_id1
        friend: User | None = db.query(User).filter(User.id == friend_id).first()
        if friend:
            friend_infos.append(
                FriendInfo(
                    user_id=friend.id,
                    handle=friend.handle,
                    profile_picture_url=friend.profile_picture_url
                )
            )

    return FriendsListResponse(friends=friend_infos)

@router.get('/interests', response_model=UserInterestsResponse)
async def get_user_interests(
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
    
    interests = db.query(Interest).all()
    user_interests_db = db.query(UserInterest).filter(UserInterest.user_id == user.id).all()

    user_interests_return = []

    for user_interest in user_interests_db:
        for interest in interests:
            if user_interest.interest_id == interest.id:
                user_interests_return.append(interest.slug)
                break
    
    return UserInterestsResponse(interests=user_interests_return)

@router.put('/email-notifications', response_class=JSONResponse)
async def update_email_notifications(
    data: NotificationSettingUpdate,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    print(data)
    supertokens_user_id = session.get_user_id()

    user: User | None = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    user.email_notifications_enabled = data.enabled
    db.commit()
    db.refresh(user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'ok'
        }
    )

@router.put('/push-notifications', response_class=JSONResponse)
async def update_push_notifications(
    data: NotificationSettingUpdate,
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
    
    user.push_notifications_enabled = data.enabled
    db.commit()
    db.refresh(user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'ok'
        }
    )

@router.put('/streak-reminders', response_class=JSONResponse)
async def update_streak_reminders(
    data: NotificationSettingUpdate,
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
    
    user.streak_reminders_enabled = data.enabled
    db.commit()
    db.refresh(user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'ok'
        }
    )