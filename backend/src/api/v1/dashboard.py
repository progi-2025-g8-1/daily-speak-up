import datetime
import calendar
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import extract, func, select, or_, delete
from sqlalchemy.orm import Session

from ..deps import get_session, get_s3_service
from ...db import get_db
from ...schemas import UserDashboardResponse, ReportedVideoResponse, BanInfo, StatsResponse, StatsSummaryResponse
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

    if user.role not in (UserRole.ROOT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    users = db.query(User).all()
    return [UserDashboardResponse(
                user_id=u.id,
                email=u.email,
                handle=u.handle,
                profile_picture_url=u.profile_picture_url,
                user_role=u.role
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

    if admin_user.role not in (UserRole.ROOT, UserRole.ADMIN, UserRole.MOD):
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

    if user.role not in (UserRole.ROOT, UserRole.ADMIN, UserRole.MOD):
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
                profile_picture_url=user.profile_picture_url,
                user_role=user.role
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

    if admin_user.role not in (UserRole.ROOT, UserRole.ADMIN, UserRole.MOD):
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

    if admin_user.role not in (UserRole.ROOT, UserRole.ADMIN, UserRole.MOD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    active_bans = db.execute(select(Ban.id, Ban.user_id, Ban.reason, Ban.banned_by)
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
                        user_role=banned_by_user.role
                    ),
                    banned_user=UserDashboardResponse(
                        user_id=banned_user.id,
                        email=banned_user.email,
                        handle=banned_user.handle,
                        profile_picture_url=banned_user.profile_picture_url,
                        user_role=banned_user.role
                    )
                )
            )

    return banned_users_list

@router.post("/unban-user", status_code=status.HTTP_200_OK)
async def unban_user(
    user_id: UUID = Body(..., embed=True),
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Unban a user by admin/mod."""
    
    supertokens_user_id = session.get_user_id()

    admin_user = db.scalar(select(User).where(User.supertokens_user_id == supertokens_user_id))

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ROOT, UserRole.ADMIN, UserRole.MOD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    try:
        db.execute(delete(Ban).where(Ban.user_id == user_id))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unban user: {str(e)}"
        )

    return JSONResponse(content={"detail": "User unbanned successfully"}, status_code=status.HTTP_200_OK)

@router.get("/stats/users-by-month", response_model=StatsResponse, status_code=status.HTTP_200_OK)
async def get_user_stats_by_month(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get user registration stats by month for dashboard."""
    
    supertokens_user_id = session.get_user_id()

    admin_user = db.scalar(select(User).where(User.supertokens_user_id == supertokens_user_id))

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ROOT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    current_year = datetime.datetime.now().year
    current_year_month = datetime.datetime.now().month
    current_day = datetime.datetime.now().day

    labels = []
    user_counts = []

    for i in range(11, -1, -1):
        if current_year_month - i <= 0:
            month = current_year_month - i + 12
            year = current_year - 1
        else:
            month = current_year_month - i
            year = current_year
        
        users = db.execute(
            select(User).where(
                extract('month', User.created_at) == month,
                extract('year', User.created_at) == year
            )
        ).all()

        labels.append(calendar.month_abbr[month])
        user_counts.append(len(users))

    return StatsResponse(labels=labels, counts=user_counts)


@router.get("/stats/counts-by-topic", response_model=StatsResponse, status_code=status.HTTP_200_OK)
async def get_speech_stats_by_month(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get speech counts by topic for dashboard."""
    
    supertokens_user_id = session.get_user_id()

    admin_user = db.scalar(select(User).where(User.supertokens_user_id == supertokens_user_id))

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ROOT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )

    labels = []
    counts = []

    interests = db.execute(select(Interest.id, Interest.name)).all()

    for interest_id, interest_name in interests:
        speech_count = db.execute(
            select(func.count(Speech.id)).where(Speech.interest_id == interest_id)
        ).scalar_one()
        labels.append(interest_name)
        counts.append(speech_count)

    return StatsResponse(labels=labels, counts=counts)

@router.get("/stats/speeches-this-week", response_model=StatsResponse, status_code=status.HTTP_200_OK)
async def get_speech_stats_by_day(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get speech creation stats by day for the last week for dashboard."""
    
    supertokens_user_id = session.get_user_id()

    admin_user = db.scalar(select(User).where(User.supertokens_user_id == supertokens_user_id))

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ROOT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    labels = []
    speech_counts = []

    today = datetime.datetime.now().date()

    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        speeches = db.execute(
            select(Speech).where(
                extract('day', Speech.created_at) == day.day,
                extract('month', Speech.created_at) == day.month,
                extract('year', Speech.created_at) == day.year
            )
        ).all()

        labels.append(day.strftime('%a'))
        speech_counts.append(len(speeches))

    return StatsResponse(labels=labels, counts=speech_counts)

@router.get("/stats/summary", response_model=StatsSummaryResponse, status_code=status.HTTP_200_OK)
async def get_user_count(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    """Get total user count for dashboard."""
    
    supertokens_user_id = session.get_user_id()

    admin_user = db.scalar(select(User).where(User.supertokens_user_id == supertokens_user_id))

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ROOT, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    user_count = db.execute(select(func.count(User.id)).where(User.role != UserRole.ROOT)).scalar_one()
    speech_count = db.execute(select(func.count(Speech.id))).scalar_one()
    ban_count = db.execute(
        select(func.count(Ban.id)).where(
            or_(Ban.ends_at == None, Ban.ends_at > datetime.datetime.now(datetime.timezone.utc))
        )
    ).scalar_one()
    pending_report_count = db.execute(
        select(func.count(Report.id)).where(
            Report.resolved_by.is_(None)
        )
    ).scalar_one()

    return StatsSummaryResponse(
        total_users=user_count,
        total_speeches=speech_count,
        total_bans=ban_count,
        pending_reports=pending_report_count
    )


@router.put("/user-role", status_code=status.HTTP_200_OK)
async def change_user_role(
    user_id: UUID = Body(..., embed=True),
    db: Session = Depends(get_db),
    session: Session = Depends(get_session)
):
    """Update (toggle) user role to MOD/USER by admin."""
    
    supertokens_user_id = session.get_user_id()

    admin_user = db.scalar(select(User).where(User.supertokens_user_id == supertokens_user_id))

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ADMIN, UserRole.ROOT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    user_to_update = db.scalar(select(User).where(User.id == user_id))

    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User to update not found"
        )
    
    try:
        user_to_update.role = UserRole.MOD if user_to_update.role == UserRole.USER else UserRole.USER
        db.commit()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified"
        )

    return JSONResponse(content={"detail": "User role updated successfully"}, status_code=status.HTTP_200_OK)

@router.delete("/dismiss-reports/{speech_id}", status_code=status.HTTP_200_OK)
async def dismiss_reports_for_speech(
    speech_id: UUID,
    db: Session = Depends(get_db),
    session: Session = Depends(get_session)
):
    """Dismiss all reports for a specific speech by admin/mod."""
    
    supertokens_user_id = session.get_user_id()

    admin_user = db.scalar(select(User).where(User.supertokens_user_id == supertokens_user_id))

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if admin_user.role not in (UserRole.ROOT, UserRole.ADMIN, UserRole.MOD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this resource"
        )
    
    try:
        db.execute(delete(Report).where(Report.speech_id == speech_id))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete reports: {str(e)}"
        )

    return JSONResponse(content={"detail": "Reports deleted successfully"}, status_code=status.HTTP_200_OK)