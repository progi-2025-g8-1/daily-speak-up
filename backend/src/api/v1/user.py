import logging
import datetime
from uuid import UUID 
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import extract, and_, or_, func
from sqlalchemy.orm import Session
from typing import List

from ..deps import get_session, get_s3_service, get_current_user
from ...db import get_db
from ...schemas import UserResponse, UserCreate, MonthlyUserVideosResponse, VideoInfo, FriendsListResponse, FriendInfo, UserInterestsResponse, NotificationSettingUpdate, LanguageUpdate, ThemeUpdate, PublicUserProfile
from ...models import User, Friendship, UserStreak, Speech, UserDevice, UserInterest, Interest, Rating, Ban, Report, UserRole, RequestStatus, SpeechVisibility, AppLang, AppTheme
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.asyncio import delete_user

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
        preferred_lang=user_data.preferred_lang if user_data.preferred_lang else AppLang.EN,
        preferred_theme=user_data.preferred_theme if user_data.preferred_theme else AppTheme.LIGHT,
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
    user: User = Depends(get_current_user),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    friends_count = db.query(Friendship).filter(
        and_(
            or_(Friendship.user_id1 == user.id, Friendship.user_id2 == user.id),
            Friendship.status == RequestStatus.ACCEPTED,
            Friendship.deleted_at.is_(None)
        )
    ).count()

    streak = db.query(UserStreak).filter(
        UserStreak.user_id == user.id
    ).order_by(UserStreak.created_at.desc()).first()

    # Display streak as the inclusive count from `start_date` to the last
    # recorded day (`end_date`). If `end_date` is None (brand new/ongoing),
    # treat it as a one-day streak at `start_date`.
    if streak is None:
        streak_days = 0
    else:
        end_date: datetime.date = streak.end_date if streak.end_date is not None else streak.start_date
        start_date: datetime.date = streak.start_date

        days_delta = (end_date - start_date).days
        streak_days = max(0, int(days_delta) + 1)

    # Generate presigned URL for profile picture
    profile_pic_url = None
    try:
        photo_data = s3_service.get_photo_read_url(str(user.id))
        profile_pic_url = photo_data.get('download_url')
    except Exception:
        profile_pic_url = None

    return UserResponse(
        id=user.id,
        role=user.role,
        email=user.email,
        handle=user.handle,
        profile_picture_url=profile_pic_url,
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
    requesting_user: User = Depends(get_current_user)
):
    # Check if viewing own profile or if admin/moderator
    is_own_profile = requesting_user.id == user_id
    is_admin = requesting_user.role in [UserRole.ADMIN, UserRole.ROOT, UserRole.MOD]
    
    # If not own profile and not admin, check if friends
    are_friends = False
    if not is_own_profile and not is_admin:
        user_id1 = min(requesting_user.id, user_id)
        user_id2 = max(requesting_user.id, user_id)
        
        friendship = db.query(Friendship).filter(
            and_(
                Friendship.user_id1 == user_id1,
                Friendship.user_id2 == user_id2,
                Friendship.status == RequestStatus.ACCEPTED,
                Friendship.deleted_at.is_(None)
            )
        ).first()
        
        are_friends = friendship is not None
        
        # If not friends and not admin, deny access
        if not are_friends:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Access denied'
            )
    
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid month'
        )
    
    # Fetch speeches - filter by visibility based on relationship
    query = db.query(Speech).filter(
        Speech.user_id == user_id,
        extract('year', Speech.created_at) == year,
        extract('month', Speech.created_at) == month
    )
    
    # Apply visibility filters
    if is_own_profile or is_admin:
        # Own profile or admin - show all videos
        pass
    elif are_friends:
        # Friends - only show videos marked as for friends
        query = query.filter(Speech.visibility_level == SpeechVisibility.FRIENDS)
    
    speeches = query.all()

    # Bulk fetch all ratings for speeches in one query
    speech_ids = [speech.id for speech in speeches]
    rating_stats = {}
    if speech_ids:
        stats_query = db.query(
            Rating.speech_id,
            func.avg(Rating.score).label('avg_rating'),
            func.count(Rating.id).label('total_ratings')
        ).filter(
            Rating.speech_id.in_(speech_ids),
            Rating.removed_at.is_(None)
        ).group_by(Rating.speech_id).all()
        
        rating_stats = {
            stat.speech_id: (
                float(stat.avg_rating) if stat.avg_rating else None,
                int(stat.total_ratings)
            ) for stat in stats_query
        }

    videos = []

    for speech in speeches:
        # Get rating info from bulk query
        avg_rating, total_ratings = rating_stats.get(speech.id, (None, 0))

        # Get interest name if available
        interest_name = None
        if speech.interest:
            interest_name = speech.interest.slug

        # If the video is hosted on YouTube, use the existing URL directly
        if 'youtube' in str(speech.s3_url):
            videos.append(
                VideoInfo(
                    video_id=speech.id,
                    year=speech.created_at.year,
                    month=speech.created_at.month,
                    day=speech.created_at.day,
                    caption=speech.caption,
                    url=speech.s3_url,
                    owner_id=speech.user_id,
                    visibility=speech.visibility_level,
                    average_rating=avg_rating,
                    total_ratings=total_ratings,
                    topic=speech.task,
                    interest=interest_name
                )
            )
            continue

        if speech.s3_url is None or speech.is_cancelled:
            continue

        # Check if file exists in S3 before returning
        if not s3_service.check_file_exists(speech.s3_url):
            logger.warning(f"Video file missing for speech {speech.id}, key: {speech.s3_url}")
            continue

        download_url = None

        # Pre sign the S3 URL
        try:
            rd = s3_service.get_read_url(str(requesting_user.id), str(speech.id), str(speech.user_id))
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
                visibility=speech.visibility_level,
                average_rating=avg_rating,
                total_ratings=total_ratings,
                topic=speech.task,
                interest=interest_name
            )
        )

    return MonthlyUserVideosResponse(videos=videos)

@router.get('/{user_id}/friends', response_model=FriendsListResponse)
async def get_friends_list(
    user_id: UUID,
    db: Session = Depends(get_db),
    requesting_user: User = Depends(get_current_user),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    target_user: User | None = db.query(User).filter(User.id == user_id).first()

    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Target user not found')

    friendships = db.query(Friendship).filter(
        and_(
            or_(Friendship.user_id1 == target_user.id, Friendship.user_id2 == target_user.id),
            Friendship.status == RequestStatus.ACCEPTED,
            Friendship.deleted_at.is_(None)
        )
    ).all()

    # Bulk fetch all friend users in one query
    friend_ids = [
        friendship.user_id2 if friendship.user_id1 == target_user.id else friendship.user_id1
        for friendship in friendships
    ]
    
    friends = {}
    if friend_ids:
        friends = {user.id: user for user in db.query(User).filter(User.id.in_(friend_ids)).all()}

    friend_infos = []
    for friend_id in friend_ids:
        friend = friends.get(friend_id)
        if friend:
            # Generate presigned URL for profile picture
            profile_pic_url = None
            try:
                photo_data = s3_service.get_photo_read_url(str(friend.id))
                profile_pic_url = photo_data.get('download_url')
            except Exception:
                profile_pic_url = None

            friend_infos.append(
                FriendInfo(
                    user_id=friend.id,
                    handle=friend.handle,
                    profile_picture_url=profile_pic_url
                )
            )

    return FriendsListResponse(friends=friend_infos)

@router.delete('/delete', response_class=JSONResponse)
async def delete_account(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    session: SessionContainer = Depends(get_session),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    supertokens_user_id = user.supertokens_user_id
    
    if user.role == UserRole.ROOT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Root admin account cannot be deleted'
        )
    
    speeches = db.query(Speech).filter(Speech.user_id == user.id)
    speeches_ids = [speech.id for speech in speeches.all()]
    speech_ids_str = [str(sid) for sid in speeches_ids]

    # Delete from S3
    try:
        s3_service.delete_videos(str(user.id), speech_ids_str)
        s3_service.delete_profile_photo(str(user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to delete user files on S3'
        )   

    # Delete user-related data here (e.g., speeches, friendships, etc.)
    try:
        db.query(Ban).filter(Ban.user_id == user.id).delete(synchronize_session=False)

        db.query(Rating).filter(Rating.speech_id.in_(speeches_ids)).delete(synchronize_session=False)
        db.query(Rating).filter(Rating.rated_by == user.id).delete(synchronize_session=False)

        db.query(Report).filter(Report.speech_id.in_(speeches_ids)).delete(synchronize_session=False)
        db.query(Report).filter(Report.reported_by == user.id).delete(synchronize_session=False)


        db.query(Friendship).filter(
            (Friendship.user_id1 == user.id) | (Friendship.user_id2 == user.id)
        ).delete(synchronize_session=False)

        db.query(UserStreak).filter(UserStreak.user_id == user.id).delete(synchronize_session=False)

        db.query(UserDevice).filter(UserDevice.user_id == user.id).delete(synchronize_session=False)

        db.query(UserInterest).filter(UserInterest.user_id == user.id).delete(synchronize_session=False)

        speeches.delete(synchronize_session=False)

        try:
            await delete_user(supertokens_user_id)
            await session.revoke_session()
        except Exception as exc:
            logger.error("Failed to delete SuperTokens user %s: %s", supertokens_user_id, exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to delete user account'
            )

        email = user.email

        # Soft delete for admins/moderators, hard delete for regular users
        # Admins and moderators should remain for moderation purposes in Bans and Reports
        if user.role == UserRole.USER:
            db.delete(user)

        else:
            user.email = f"deleted_{user.id}@deleted.local"
            user.supertokens_user_id = f"deleted_{user.supertokens_user_id}"
            user.handle = f"deleted_{user.id}"
            user.profile_picture_url = None
            user.deleted_at = datetime.datetime.now(datetime.timezone.utc)
            user.anonymized_at = datetime.datetime.now(datetime.timezone.utc)

        db.commit()

        EmailService.send_email(    
            to_mail=email,
            subject="Your DailySpeakUp account has been deleted",
            template="confirm_account_deletion",
            message=""
        )

        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'message': 'User account deleted successfully'
            }
        )
        return response
    
    except Exception as exc:
        logger.error("Error deleting user data for user %s: %s", user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to delete user data'
        )
        
@router.get('/interests', response_model=UserInterestsResponse)
async def get_user_interests(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Fetch user interests with joined interest data
    user_interests = db.query(UserInterest, Interest).join(
        Interest, UserInterest.interest_id == Interest.id
    ).filter(UserInterest.user_id == user.id).all()

    return UserInterestsResponse(interests=[interest.slug for _, interest in user_interests])

@router.put('/email-notifications', response_class=JSONResponse)
async def update_email_notifications(
    data: NotificationSettingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
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
    user: User = Depends(get_current_user)
):
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
    user: User = Depends(get_current_user)
):
    user.streak_reminders_enabled = data.enabled
    db.commit()
    db.refresh(user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'ok'
        }
    )

@router.put('/preferred-language', response_class=JSONResponse)
async def update_preferred_language(
    data: LanguageUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update the user's preferred application language."""
    user.preferred_lang = data.lang
    db.commit()
    db.refresh(user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'ok'
        }
    )

@router.put('/preferred-theme', response_class=JSONResponse)
async def update_preferred_theme(
    data: ThemeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update the user's preferred application theme."""
    user.preferred_theme = data.theme
    db.commit()
    db.refresh(user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'ok'
        }
    )

@router.delete('/profile-picture', response_class=JSONResponse)
async def delete_profile_picture(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    """Delete the user's profile picture."""
    try:
        # Delete from S3 if it exists
        if user.profile_picture_url:
            s3_service.delete_profile_photo(str(user.id))
        
        # Update database
        user.profile_picture_url = None
        db.commit()
        db.refresh(user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'message': 'Profile picture deleted successfully'
            }
        )
    except Exception as e:
        logger.error(f"Error deleting profile picture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to delete profile picture'
        )

@router.get("/profile/{handle}")
async def get_user_profile_by_handle(
    handle: str,
    db: Session = Depends(get_db),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    """Get public user profile by handle - returns user_id and basic info"""
    
    target_user = db.query(User).filter(
        User.handle == handle,
        User.deleted_at.is_(None),
        User.anonymized_at.is_(None)
    ).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Bulk query for friend count, streak, and interests in parallel
    friend_count = db.query(func.count(Friendship.id)).filter(
        and_(
            or_(Friendship.user_id1 == target_user.id, Friendship.user_id2 == target_user.id),
            Friendship.status == RequestStatus.ACCEPTED,
            Friendship.deleted_at.is_(None)
        )
    ).scalar() or 0
    
    latest_streak = db.query(UserStreak).filter(
        UserStreak.user_id == target_user.id
    ).order_by(UserStreak.created_at.desc()).first()
    
    # Display streak as the inclusive count from `start_date` to the last
    # recorded day (`end_date`). If `end_date` is None (brand new/ongoing),
    # treat it as a one-day streak at `start_date`.
    if latest_streak is None:
        streak_days = 0
    else:
        end_date: datetime.date = latest_streak.end_date if latest_streak.end_date is not None else latest_streak.start_date
        start_date: datetime.date = latest_streak.start_date
        days_delta = (end_date - start_date).days
        streak_days = max(0, int(days_delta) + 1)
    
    # Get user interests with join
    user_interests = [
        interest.slug for _, interest in 
        db.query(UserInterest, Interest).join(
            Interest, UserInterest.interest_id == Interest.id
        ).filter(UserInterest.user_id == target_user.id).all()
    ]
    
    # Get presigned profile picture URL
    profile_picture_url = None
    try:
        photo_result = s3_service.get_photo_read_url(str(target_user.id))
        profile_picture_url = photo_result.get('download_url')
    except Exception as e:
        logger.debug(f"Failed to get profile picture URL: {e}")
    
    return {
        "id": str(target_user.id),  
        "handle": target_user.handle,
        "profile_picture_url": profile_picture_url,
        "friend_count": friend_count,
        "current_streak": streak_days,
        "interests": user_interests  
    }

@router.get("/{user_id}/videos", response_model=List[dict])
async def get_friend_videos(
    user_id: UUID,
    year:int | None  = None,
    month:int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    """Get target user's friends-only videos - requires friendship"""
    
    target_user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    # Verify friendship
    user_id1 = min(current_user.id, target_user.id)
    user_id2 = max(current_user.id, target_user.id)
    
    friendship = db.query(Friendship).filter(
        and_(
            Friendship.user_id1 == user_id1,
            Friendship.user_id2 == user_id2,
            Friendship.status == RequestStatus.ACCEPTED,
            Friendship.deleted_at.is_(None)
        )
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=403, detail="Not friends with this user")
    
    # Get friends-only videos
    query = db.query(Speech).filter(
        Speech.user_id == target_user.id,
        Speech.visibility_level == SpeechVisibility.FRIENDS,
        Speech.is_cancelled == False,
        Speech.s3_url.isnot(None)
    )
    
    if year and month:
        query = query.filter(
            extract('year', Speech.created_at) == year,
            extract('month', Speech.created_at) == month
        )
    
    videos = query.order_by(Speech.created_at.desc()).limit(20).all()
    
    # Generate presigned URLs and build response
    response = []
    for video in videos:
        download_url = None
        try:
            rd = s3_service.get_read_url(str(target_user.id), str(video.id))
            if isinstance(rd, dict):
                download_url = rd.get('download_url')
        except Exception as e:
            logger.debug(f"Failed to generate presigned URL for video {video.id}: {e}")
        
        response.append({
            "id": str(video.id),
            "caption": video.caption,
            "created_at": video.created_at.isoformat(),
            "url": download_url or video.s3_url
        })
    
    return response

@router.get('/amibanned', response_model=dict)
async def am_i_banned(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    now = datetime.datetime.now(datetime.timezone.utc)
    
    active_ban: Ban | None = db.query(Ban).filter(
        Ban.user_id == user.id,
        or_(Ban.ends_at > now, Ban.ends_at.is_(None))
    ).first()

    if active_ban is None:
        return {
            'banned': False
        }
    
    return {
        'banned': True,
        'reason': active_ban.reason,
        'expires_at': active_ban.ends_at.isoformat() if active_ban.ends_at else None
    }
