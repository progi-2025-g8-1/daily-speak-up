import datetime
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import extract, select, or_
from sqlalchemy.orm import Session

from ..deps import get_session, get_s3_service
from ...db import get_db
from ...schemas import UserDashboardResponse, ReportedVideoResponse, BanInfo
from ...models import User, Friendship, UserStreak, Speech, UserDevice, UserInterest, Interest, Rating, Ban, Report, UserRole
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.asyncio import delete_user

from ...services import S3SecureService

router = APIRouter(tags=['dashboard'], prefix='/dashboard')

@router.get("/users", response_model=list[UserDashboardResponse], status_code=status.HTTP_200_OK)
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
    return [UserDashboardResponse(
                user_id=u.id,
                email=u.email,
                handle=u.handle,
                profile_picture_url=u.profile_picture_url
            ) 
            for u in users
            if u.role != UserRole.ADMIN
           ]

@router.get("/report-reasons/{user_id}", response_model=list[str], status_code=status.HTTP_200_OK)
async def get_report_reasons(
    user_id: UUID,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    
    """Get report reasons for dashboard."""
    
    supertokens_user_id = session.get_user_id()

    print(user_id)

    admin_user = db.scalar(select(User).where(User.supertokens_user_id == supertokens_user_id))

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ADMIN, UserRole.MOD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    user_speech_ids = db.scalars(select(Speech.id).where(Speech.user_id == user_id)).all()
    
    user_reports = db.scalars(select(Report.reason).where(Report.speech_id.in_(user_speech_ids))).all()

    report_reasons = [str(reason) for reason in user_reports if reason is not None]

    return report_reasons

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
        user = db.scalar(select(User).where(User.id == speech.user_id)) if speech else None
        if not speech or not user:
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
            user_info=UserDashboardResponse(
                user_id=user.id,
                email=user.email,
                handle=user.handle,
                profile_picture_url=user.profile_picture_url
            ),
            year=speech.created_at.year,
            month=speech.created_at.month,
            day=speech.created_at.day,
            caption=speech.caption,
            report_reasons=report_reasons,
            video_url=video_url
        ))

    return response_list

@router.post("/ban-user", status_code=status.HTTP_200_OK)
async def ban_user(
    user_id: UUID = Body(...),
    reason: str = Body(...),
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Ban a user by admin/mod."""
    
    supertokens_user_id = session.get_user_id()

    admin_user = db.query(User).filter(User.supertokens_user_id == supertokens_user_id).first()

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ADMIN, UserRole.MOD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    user_to_ban = db.scalar(select(User).where(User.id == user_id))

    if not user_to_ban:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User to ban not found"
        )
    
    existing_ban = db.scalar(select(Ban)
                            .where(
                                Ban.user_id == user_id and 
                                (Ban.ends_at == None or Ban.ends_at > datetime.datetime.now(datetime.timezone.utc))
                            ))

    if existing_ban:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User is already banned"
        )
    
    ban_entry = Ban(
                    user_id=user_id,
                    banned_by=admin_user.id,
                    reason=reason if reason else None,
                )
    db.add(ban_entry)
    db.commit()

    return JSONResponse(content={"detail": "User banned successfully"}, status_code=status.HTTP_200_OK)

@router.get("/bans", response_model=list[BanInfo], status_code=status.HTTP_200_OK)
async def get_banned_users(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get all banned users for dashboard."""
    
    supertokens_user_id = session.get_user_id()

    admin_user = db.scalar(select(User).where(User.supertokens_user_id == supertokens_user_id))

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ADMIN, UserRole.MOD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    active_bans = db.scalars(select(Ban.id, Ban.user_id, Ban.reason, Ban.banned_by)
                                .where(
                                    or_(Ban.ends_at == None, Ban.ends_at > datetime.datetime.now(datetime.timezone.utc))
                                )).all()

    banned_users_list = []

    for ban_id, banned_user_id, reason, banned_by_id in active_bans:
        banned_user = db.scalar(select(User).where(User.id == banned_user_id))
        banned_by_user = db.scalar(select(User).where(User.id == banned_by_id))
        if banned_user and banned_by_user:
            banned_users_list.append(
                BanInfo(
                    ban_id=ban_id,
                    ban_reason=reason,
                    banned_by=UserDashboardResponse(
                        user_id=banned_by_user.id,
                        email=banned_by_user.email,
                        handle=banned_by_user.handle,
                        profile_picture_url=banned_by_user.profile_picture_url,
                    ),
                    banned_user=UserDashboardResponse(
                        user_id=banned_user.id,
                        email=banned_user.email,
                        handle=banned_user.handle,
                        profile_picture_url=banned_user.profile_picture_url,
                    )
                )
            )

    return banned_users_list