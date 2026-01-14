import datetime
from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from ..deps import get_session, get_s3_service, get_gemini_service, get_current_user
from ..deps import get_session, get_s3_service, get_gemini_service, get_current_user
from ...models import User, Speech, Report, SpeechVisibility, Rating, UserStreak
from ...models.enums import UserRole
from ...schemas import UploadRequestResponse, VideoReadResponse
from sqlalchemy.orm import Session
from ...db import get_db
from supertokens_python.recipe.session import SessionContainer 
from ...services import S3SecureService, GeminiService
import random
from uuid import UUID

router = APIRouter(prefix="/video", tags=["Video"])

@router.get('/start', response_model=UploadRequestResponse)
async def get_upload_token(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    s3_service: S3SecureService = Depends(get_s3_service),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    # Ensure the user has at least a single interest and choose one
    if not user.user_interests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no interests selected"
        )
    
    chosen_interest = random.choice([ui.interest for ui in user.user_interests])

    # Generate a topic based on the chosen interest
    try:
        topic = await gemini_service.generate_topic(chosen_interest.name, user.preferred_lang)
    except Exception as e:
        print(f"Error generating topic: {e}")
        topic = f"Talk about {chosen_interest.name} (Fallback Topic)"

    # Create a speech object - commit first to get the ID
    speech = Speech(
        user_id=user.id,
        interest_id=chosen_interest.id,
        task=topic
    )
    db.add(speech)
    db.commit()
    db.refresh(speech)
    
    # Check if user has an active streak for today, if not create one
    today = datetime.date.today()
    existing_streak = db.query(UserStreak).filter(
        UserStreak.user_id == user.id,
        UserStreak.start_date == today,
        UserStreak.end_date == None
    ).first()
    
    if not existing_streak:
        # Check if there's a streak that expired
        latest_streak = db.query(UserStreak).filter(
            UserStreak.user_id == user.id
        ).order_by(UserStreak.created_at.desc()).first()
        
        if latest_streak and latest_streak.ends_at >= datetime.datetime.now(datetime.timezone.utc):
            # Extend the existing streak
            latest_streak.end_date = today
            latest_streak.ends_at = datetime.datetime.combine(
                today,
                datetime.time.max,
                tzinfo=datetime.timezone.utc
            )
        else:
            # Create a new streak starting today
            new_streak = UserStreak(
                user_id=user.id,
                start_date=today,
                end_date=None,
                ends_at=datetime.datetime.combine(
                    today + datetime.timedelta(days=1),
                    datetime.time.min,
                    tzinfo=datetime.timezone.utc
                )
            )
            db.add(new_streak)
    
    db.commit()
    
    # Now generate presigned upload URL using the committed speech ID
    upload_data = s3_service.get_upload_url(str(user.id), str(speech.id))
    speech.s3_url = upload_data['key']
    
    db.commit()
    db.refresh(speech)

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
    
    if str(user.id) != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )
    
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

    streak = db.query(UserStreak).filter(
        UserStreak.user_id == user.id 
    ).order_by(UserStreak.created_at.desc()).first()

    if streak:
        if streak.start_date == streak.end_date:
            db.delete(streak)
            db.commit()
        elif speech.created_at.date() == streak.end_date:
            streak.end_date = streak.end_date - datetime.timedelta(days=1)
            streak.ends_at = datetime.datetime.combine(
                streak.end_date,
                datetime.time.max,
                tzinfo=datetime.timezone.utc
            )
            db.commit()
        elif speech.created_at.date() == streak.start_date:
            streak.start_date = streak.start_date + datetime.timedelta(days=1)
            db.commit()
        elif streak.start_date < speech.created_at.date() < streak.end_date:
            original_end_date = streak.end_date
            streak.end_date = speech.created_at.date() - datetime.timedelta(days=1)
            streak.ends_at = datetime.datetime.combine(
                streak.end_date,
                datetime.time.max,
                tzinfo=datetime.timezone.utc
            )

            new_streak = UserStreak(
                user_id=user.id,
                start_date=speech.created_at.date() + datetime.timedelta(days=1),
                end_date=original_end_date,
                ends_at=datetime.datetime.combine(
                    original_end_date,
                    datetime.time.max,
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
