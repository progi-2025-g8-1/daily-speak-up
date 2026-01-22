import datetime
import random
import uuid
from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from uuid import UUID
from ..deps import get_session, get_s3_service, get_gemini_service, get_current_user
from ...models import User, Speech, Report, SpeechVisibility, Rating, UserStreak
from ...models.enums import UserRole
from ...schemas import UploadRequestResponse, VideoReadResponse
from sqlalchemy.orm import Session
from ...db import get_db
from supertokens_python.recipe.session import SessionContainer 
from ...services import S3SecureService, GeminiService

router = APIRouter(prefix="/video", tags=["Video"])

@router.get('/start', response_model=UploadRequestResponse)
async def get_upload_token(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    s3_service: S3SecureService = Depends(get_s3_service),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    # Check if user has already recorded a video today
    today = datetime.date.today()
    today_start = datetime.datetime.combine(today, datetime.time.min, tzinfo=datetime.timezone.utc)
    today_end = datetime.datetime.combine(today, datetime.time.max, tzinfo=datetime.timezone.utc)
    
    existing_video_today = db.query(Speech).filter(
        Speech.user_id == user.id,
        Speech.created_at >= today_start,
        Speech.created_at <= today_end,
        Speech.is_cancelled == False
    ).first()
    
    if existing_video_today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already recorded a video today. You can only record one video per day."
        )
    
    # Ensure the user has at least a single interest and choose one
    if not user.user_interests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no interests selected"
        )
    
    chosen_interest = random.choice([ui.interest for ui in user.user_interests])

    # Generate a topic based on the chosen interest - don't hard fail on Gemini errors
    topic = None
    try:
        topic = await gemini_service.generate_topic(chosen_interest.name, user.preferred_lang)
        print(f"[/start] Gemini topic generated successfully: {topic}")
    except Exception as e:
        print(f"[/start] Gemini error (using fallback): {e}")
        # Use a more user-friendly fallback topic
        topic = f"Share your thoughts about {chosen_interest.name}"
    
    # Generate a temporary speech ID first (before DB operations)
    import uuid
    temp_speech_id = uuid.uuid4()
    
    # Try to generate S3 upload URL BEFORE creating the speech in DB
    try:
        upload_data = s3_service.get_upload_url(str(user.id), str(temp_speech_id))
    except Exception as e:
        print(f"[/start] S3 service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service temporarily unavailable. Please try again."
        )
    
    # Now create the speech object with the pre-generated ID and all data ready
    speech = Speech(
        id=temp_speech_id,
        user_id=user.id,
        interest_id=chosen_interest.id,
        task=topic,
        s3_url=upload_data['key']
    )
    db.add(speech)
    
    # Check if user has an active streak for today, if not create one
    existing_streak = db.query(UserStreak).filter(
        UserStreak.user_id == user.id,
        UserStreak.start_date <= today,
        UserStreak.end_date >= today
    ).first()
    
    if not existing_streak:
        # Check if there's a streak that can be extended (ended yesterday)
        latest_streak = db.query(UserStreak).filter(
            UserStreak.user_id == user.id
        ).order_by(UserStreak.created_at.desc()).first()
        
        yesterday = today - datetime.timedelta(days=1)
        if latest_streak and latest_streak.end_date == yesterday:
            # Extend the existing streak (consecutive day)
            latest_streak.end_date = today
            latest_streak.ends_at = datetime.datetime.combine(
                today + datetime.timedelta(days=1),
                datetime.time.min,
                tzinfo=datetime.timezone.utc
            )
        else:
            # Create a new streak starting today (gap detected or first streak)
            new_streak = UserStreak(
                user_id=user.id,
                start_date=today,
                end_date=today,
                ends_at=datetime.datetime.combine(
                    today + datetime.timedelta(days=1),
                    datetime.time.min,
                    tzinfo=datetime.timezone.utc
                )
            )
            db.add(new_streak)
    
    # Commit everything at once - if this fails, nothing is persisted
    try:
        db.commit()
        db.refresh(speech)
    except Exception as e:
        db.rollback()
        print(f"[/start] Database commit error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize recording session. Please try again."
        )

    return UploadRequestResponse(
        interest=chosen_interest.name,
        topic=topic,
        user_id=str(user.id),
        upload_url=upload_data['upload_url'],
        upload_method=upload_data.get('method', 'PUT'),
        upload_fields=upload_data.get('fields'),
        video_path=upload_data['key']
    )

@router.get('/{target_user_id}/{video_id}/play-token', response_model=VideoReadResponse)
async def get_video_play_token(
    target_user_id: UUID,
    video_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    # Get the speech to check visibility
    speech = db.query(Speech).filter(Speech.id == video_id).first()
    if not speech:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Video not found'
        )
    
    # Check ownership
    is_owner = str(user.id) == str(target_user_id)
    is_admin = user.role in [UserRole.ADMIN, UserRole.ROOT, UserRole.MOD]
    
    # Check if video is private and user is not owner/admin
    if speech.visibility_level == SpeechVisibility.PRIVATE and not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='This video is private'
        )
    
    # For friends-only videos, check friendship
    if speech.visibility_level == SpeechVisibility.FRIENDS and not is_owner and not is_admin:
        from ...models import Friendship, RequestStatus
        from sqlalchemy import and_, or_
        
        user_id1 = min(user.id, speech.user_id)
        user_id2 = max(user.id, speech.user_id)
        
        friendship = db.query(Friendship).filter(
            and_(
                Friendship.user_id1 == user_id1,
                Friendship.user_id2 == user_id2,
                Friendship.status == RequestStatus.ACCEPTED,
                Friendship.deleted_at.is_(None)
            )
        ).first()
        
        if not friendship:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Access denied - not friends with video owner'
            )
    
    if str(user.id) != str(target_user_id) and not is_admin:
        # Allow viewing if visibility checks passed but wrong target_user_id parameter
        # Just use the actual owner's ID
        target_user_id = speech.user_id
    
    try:
        read_data = s3_service.get_read_url(str(target_user_id), video_id)
        return VideoReadResponse(
            user_id=str(target_user_id),
            video_path=read_data['key'],
            download_url=read_data['download_url']
        )
    except Exception as _:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Video not found or access error'
        )

@router.put('/{video_id}/cancel', status_code=status.HTTP_200_OK, response_model=None)
async def cancel_video(
    video_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    speech: Speech | None = db.query(Speech).filter(
        Speech.id == video_id,
        Speech.user_id == user.id
    ).first()

    if speech is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Speech not found'
        )
    
    speech.is_cancelled = True
    db.commit()

    return

@router.put('/{video_id}/visibility', status_code=status.HTTP_200_OK, response_model=None)
async def set_video_visibility(
    video_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    speech: Speech | None = db.query(Speech).filter(
        Speech.id == video_id,
        Speech.user_id == user.id
    ).first()

    if speech is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Speech not found'
        )
    
    if speech.visibility_level == SpeechVisibility.PRIVATE:
        speech.visibility_level = SpeechVisibility.FRIENDS
    else:
        speech.visibility_level = SpeechVisibility.PRIVATE
    db.commit()
    db.refresh(speech)

    return

@router.delete('/{video_id}', status_code=status.HTTP_200_OK, response_model=None)
async def delete_video(
    video_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    speech: Speech | None = db.query(Speech).filter(
        Speech.id == video_id
    ).first()

    if speech is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Speech not found'
        )

    if speech.user_id != user.id and user.role not in (UserRole.ROOT, UserRole.ADMIN, UserRole.MOD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )

    ratings: list[Rating] | None = db.query(Rating).filter(
        Rating.speech_id == video_id
    ).all()

    reports: list[Report] | None = db.query(Report).filter(
        Report.speech_id == video_id
    ).all()

    # Find the streak that contains this video's date
    video_date = speech.created_at.date()
    streak = db.query(UserStreak).filter(
        UserStreak.user_id == speech.user_id,
        UserStreak.start_date <= video_date,
        UserStreak.end_date >= video_date
    ).first()

    if streak:
        if streak.start_date == streak.end_date:
            db.delete(streak)
            db.commit()
        elif speech.created_at.date() == streak.end_date:
            streak.end_date = streak.end_date - datetime.timedelta(days=1)
            streak.ends_at = datetime.datetime.combine(
                streak.end_date + datetime.timedelta(days=1),
                datetime.time.min,
                tzinfo=datetime.timezone.utc
            )
            db.commit()
        elif speech.created_at.date() == streak.start_date:
            streak.start_date = streak.start_date + datetime.timedelta(days=1)
            # ends_at stays the same since the end didn't change
            db.commit()
        elif streak.start_date < speech.created_at.date() < streak.end_date:
            original_end_date = streak.end_date
            streak.end_date = speech.created_at.date() - datetime.timedelta(days=1)
            streak.ends_at = datetime.datetime.combine(
                streak.end_date + datetime.timedelta(days=1),
                datetime.time.min,
                tzinfo=datetime.timezone.utc
            )

            new_streak = UserStreak(
                user_id=speech.user_id,
                start_date=speech.created_at.date() + datetime.timedelta(days=1),
                end_date=original_end_date,
                ends_at=datetime.datetime.combine(
                    original_end_date + datetime.timedelta(days=1),
                    datetime.time.min,
                    tzinfo=datetime.timezone.utc
                )
            )
            db.add(new_streak)
            db.commit()
    
    if ratings:
        for rating in ratings:
            db.delete(rating)
        db.commit()
    
    if reports:
        for report in reports:
            db.delete(report)
        db.commit()

    # Tu negdje dodati brisanje iz S3

    db.delete(speech)
    db.commit()

    return
