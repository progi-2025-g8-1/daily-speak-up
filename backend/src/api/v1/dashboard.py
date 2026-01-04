from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import extract, select
from sqlalchemy.orm import Session

from ..deps import get_session, get_s3_service
from ...db import get_db
from ...schemas import UserResponse, ReportedVideoResponse
from ...models import User, Friendship, UserStreak, Speech, UserDevice, UserInterest, Interest, Rating, Ban, Report, UserRole
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.asyncio import delete_user

from ...services import S3SecureService

router = APIRouter(tags=['dashboard'], prefix='/dashboard')

@router.get("/users", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get all users for dashboard."""
    
    supertokens_user_id = session.get_user_id()

    user = db.query(User).filter(User.supertokens_user_id == supertokens_user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    users = db.query(User).all()
    return [UserResponse(
                role=u.role,
                email=u.email,
                handle=u.handle,
                profile_picture_url=u.profile_picture_url,
                onboarding_status=u.onboarding_status,
                preferred_lang=u.preferred_lang,
                preferred_theme=u.preferred_theme,
                preferred_tz_offset=u.preferred_tz_offset,
                email_notifications_enabled=u.email_notifications_enabled,
                push_notifications_enabled=u.push_notifications_enabled,
                streak_reminders_enabled=u.streak_reminders_enabled,
                friends_count=0,
                streak=0
            ) 
            for u in users
            if u.role != UserRole.ADMIN
           ]

@router.get("/reported-videos", response_model=list[ReportedVideoResponse], status_code=status.HTTP_200_OK)
async def get_reported_videos(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    """Get reported videos for dashboard."""
    
    supertokens_user_id = session.get_user_id()

    user = db.query(User).filter(User.supertokens_user_id == supertokens_user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if user.role not in (UserRole.ADMIN, UserRole.MOD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    reported_video_ids = db.scalars(select(Report.speech_id).distinct()).all()
    
    response_list = []

    for video_id in reported_video_ids:
        speech = db.scalar(select(Speech).where(Speech.id == video_id))
        if not speech:
            continue

        report_reasons_query = db.scalars(select(Report.reason).where(Report.speech_id == video_id)).all()
        report_reasons = [str(reason) for reason in report_reasons_query if reason is not None]

        video_url = ''

        if 'youtube' not in str(speech.s3_url):
            # Generate a presigned URL for the video
            pass
        elif speech.s3_url:
            video_url = speech.s3_url

        response_list.append(ReportedVideoResponse(
            video_id=speech.id,
            owner_id=speech.user_id,
            year=speech.created_at.year,
            month=speech.created_at.month,
            day=speech.created_at.day,
            caption=speech.caption,
            report_reasons=report_reasons,
            video_url=video_url
        ))

    return response_list