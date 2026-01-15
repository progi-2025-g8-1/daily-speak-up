import uuid
import datetime
import asyncio
from uuid import UUID
from typing import List
from supertokens_python.recipe.session import SessionContainer
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from ..deps import get_session, get_s3_service
from ...schemas import FriendshipResponse, FriendRequestResponse, FriendshipStatusResponse
from ...db import get_db
from ...models import User, Friendship, RequestStatus,Speech, SpeechVisibility
from ...services import S3SecureService

router = APIRouter(prefix='/friend', tags=['friend'])

@router.post('/request')
async def send_friend_request(
    target_user_id: uuid.UUID = Body(..., embed=True),
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
    
    # Check if target user exists
    target_user: User | None = db.query(User).filter(
        User.id == target_user_id
    ).first()
    
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Target user not found'
        )
    
    # Check if user is trying to befriend themselves
    if user.id == target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot send friend request to yourself'
        )
    
    # Ensure user_id1 < user_id2 for database constraint
    user_id1 = min(user.id, target_user_id)
    user_id2 = max(user.id, target_user_id)
    
    # Check if friendship already exists (any status)
    existing_friendship = db.query(Friendship).filter(
        and_(
            Friendship.user_id1 == user_id1,
            Friendship.user_id2 == user_id2,
            Friendship.deleted_at.is_(None)
        )
    ).first()
    
    if existing_friendship:
        if existing_friendship.status == RequestStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Users are already friends'
            )
        elif existing_friendship.status == RequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Friend request already pending'
            )
        elif existing_friendship.status == RequestStatus.DENIED:
            # Allow resending request after denial - delete old and create new
            db.delete(existing_friendship)
            db.commit()
    
    # Create new friend request
    new_friendship = Friendship(
        user_id1=user_id1,
        user_id2=user_id2,
        requested_by_id=user.id,
        status=RequestStatus.PENDING
    )
    
    db.add(new_friendship)
    db.commit()
    db.refresh(new_friendship)
    
    # TODO: Send notification to target_user about incoming friend request
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'message': 'Friend request sent successfully',
            'friendship_id': str(new_friendship.id)
        }
    )

@router.post('/request/{friendship_id}/respond')
async def respond_to_friend_request(
    friendship_id: uuid.UUID,
    accept: bool = Body(..., embed=True),
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
    
    # Find the friendship request
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id
    ).first()
    
    if friendship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Friend request not found'
        )
    
    # Check if request is still pending
    if friendship.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Friend request is not pending (current status: {friendship.status.value})'
        )
    
    # Check if the current user is the recipient (not the requester)
    if friendship.requested_by_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Cannot respond to your own friend request'
        )
    
    # Verify that the current user is one of the users in the friendship
    if user.id != friendship.user_id1 and user.id != friendship.user_id2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to respond to this friend request'
        )
    
    # Update the friendship status
    friendship.status = RequestStatus.ACCEPTED if accept else RequestStatus.DENIED
    friendship.answered_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.commit()
    db.refresh(friendship)
    
    action = 'accepted' if accept else 'rejected'
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': f'Friend request {action} successfully',
            'friendship_id': str(friendship.id),
            'status': friendship.status.value
        }
    )

@router.delete('/{friend_user_id}')
async def remove_friend(
    friend_user_id: uuid.UUID,
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
    
    # Check if friend user exists
    friend_user: User | None = db.query(User).filter(
        User.id == friend_user_id
    ).first()
    
    if friend_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Friend user not found'
        )
    
    # Ensure user_id1 < user_id2 for database constraint
    user_id1 = min(user.id, friend_user_id)
    user_id2 = max(user.id, friend_user_id)
    
    # Find the friendship
    friendship = db.query(Friendship).filter(
        and_(
            Friendship.user_id1 == user_id1,
            Friendship.user_id2 == user_id2,
            Friendship.deleted_at.is_(None)
        )
    ).first()
    
    if friendship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Friendship not found'
        )
    
    # Check if friendship is accepted (can only remove accepted friendships)
    if friendship.status != RequestStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Cannot remove friendship with status: {friendship.status.value}'
        )
    
    # Soft delete the friendship
    friendship.deleted_at = datetime.datetime.now(datetime.timezone.utc)
    friendship.deleted_by = user.id
    friendship.status = RequestStatus.DELETED
    
    db.commit()
    
    # TODO: Send notification to the other user about friendship removal
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'Friend removed successfully',
            'friendship_id': str(friendship.id)
        }
    )

@router.get('/list', response_model=List[FriendshipResponse])
async def get_friends_list(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session),
    s3_service: S3SecureService = Depends(get_s3_service)
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
    
    # Get all accepted friendships where user is either user1 or user2
    friendships = db.query(Friendship).filter(
        and_(
            or_(
                Friendship.user_id1 == user.id,
                Friendship.user_id2 == user.id
            ),
            Friendship.status == RequestStatus.ACCEPTED,
            Friendship.deleted_at.is_(None)
        )
    ).all()
    
    # Build response with friend details
    friends_list = []
    friend_ids = []
    for friendship in friendships:
        # Determine which user is the friend
        friend_id = friendship.user_id2 if friendship.user_id1 == user.id else friendship.user_id1
        friend = db.query(User).filter(User.id == friend_id).first()
        
        if friend:
            friends_list.append({
                'friendship': friendship,
                'friend': friend
            })
            friend_ids.append(str(friend.id))
    
    # Fetch all profile picture URLs concurrently
    async def get_photo_url(user_id: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, s3_service.get_photo_read_url, user_id)
    
    photo_results = await asyncio.gather(*[get_photo_url(fid) for fid in friend_ids])
    
    # Build final response
    response = []
    for i, item in enumerate(friends_list):
        response.append({
            'friendship_id': str(item['friendship'].id),
            'user_id': str(item['friend'].id),
            'handle': item['friend'].handle,
            'profile_picture_url': photo_results[i].get('download_url'),
            'created_at': item['friendship'].created_at.isoformat(),
            'requested_by_current_user': item['friendship'].requested_by_id == user.id
        })
    
    return response

@router.get('/requests/incoming', response_model=List[FriendRequestResponse])
async def get_incoming_friend_requests(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session),
    s3_service: S3SecureService = Depends(get_s3_service)
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
    
    # Get pending friendships where user is NOT the requester
    friendships = db.query(Friendship).filter(
        and_(
            or_(
                Friendship.user_id1 == user.id,
                Friendship.user_id2 == user.id
            ),
            Friendship.requested_by_id != user.id,
            Friendship.status == RequestStatus.PENDING,
            Friendship.deleted_at.is_(None)
        )
    ).all()
    
    # Build response with requester details
    requests_list = []
    requester_ids = []
    for friendship in friendships:
        requester = db.query(User).filter(User.id == friendship.requested_by_id).first()
        
        if requester:
            requests_list.append({
                'friendship': friendship,
                'requester': requester
            })
            requester_ids.append(str(requester.id))
    
    # Fetch all profile picture URLs concurrently
    async def get_photo_url(user_id: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, s3_service.get_photo_read_url, user_id)
    
    photo_results = await asyncio.gather(*[get_photo_url(rid) for rid in requester_ids])
    
    # Build final response
    response = []
    for i, item in enumerate(requests_list):
        response.append({
            'friendship_id': str(item['friendship'].id),
            'user_id': str(item['requester'].id),
            'handle': item['requester'].handle,
            'profile_picture_url': photo_results[i].get('download_url'),
            'created_at': item['friendship'].created_at.isoformat()
        })
    
    return response

@router.get('/requests/outgoing', response_model=List[FriendRequestResponse])
async def get_outgoing_friend_requests(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session),
    s3_service: S3SecureService = Depends(get_s3_service)
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
    
    # Get pending friendships where user IS the requester
    friendships = db.query(Friendship).filter(
        and_(
            Friendship.requested_by_id == user.id,
            Friendship.status == RequestStatus.PENDING,
            Friendship.deleted_at.is_(None)
        )
    ).all()
    
    # Build response with target user details
    requests_list = []
    target_ids = []
    for friendship in friendships:
        # Determine which user is the target (not the requester)
        target_id = friendship.user_id2 if friendship.user_id1 == user.id else friendship.user_id1
        target_user = db.query(User).filter(User.id == target_id).first()
        
        if target_user:
            requests_list.append({
                'friendship': friendship,
                'target_user': target_user
            })
            target_ids.append(str(target_user.id))
    
    # Fetch all profile picture URLs concurrently
    async def get_photo_url(user_id: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, s3_service.get_photo_read_url, user_id)
    
    photo_results = await asyncio.gather(*[get_photo_url(tid) for tid in target_ids])
    
    # Build final response
    response = []
    for i, item in enumerate(requests_list):
        response.append({
            'friendship_id': str(item['friendship'].id),
            'user_id': str(item['target_user'].id),
            'handle': item['target_user'].handle,
            'profile_picture_url': photo_results[i].get('download_url'),
            'created_at': item['friendship'].created_at.isoformat()
        })
    
    return response

@router.get('/check/{user_id}', response_model=FriendshipStatusResponse)
async def check_friendship_status(
    user_id: uuid.UUID,
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
    
    # Check if target user exists
    target_user: User | None = db.query(User).filter(
        User.id == user_id
    ).first()
    
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Target user not found'
        )
    
    # Can't check friendship with yourself
    if user.id == user_id:
        return {
            'status': None,
            'friendship_id': None
        }
    
    # Ensure user_id1 < user_id2 for database constraint
    user_id1 = min(user.id, user_id)
    user_id2 = max(user.id, user_id)
    
    # Find any existing friendship
    friendship = db.query(Friendship).filter(
        and_(
            Friendship.user_id1 == user_id1,
            Friendship.user_id2 == user_id2,
            Friendship.deleted_at.is_(None)
        )
    ).first()
    
    if friendship is None:
        return {
            'status': None,
            'friendship_id': None
        }
    
    # Determine status from current user's perspective
    if friendship.status == RequestStatus.ACCEPTED:
        status_value = 'accepted'
    elif friendship.status == RequestStatus.PENDING:
        if friendship.requested_by_id == user.id:
            status_value = 'pending_outgoing'
        else:
            status_value = 'pending_incoming'
    elif friendship.status == RequestStatus.DENIED:
        status_value = 'denied'
    else:
        status_value = None
    
    return {
        'status': status_value,
        'friendship_id': str(friendship.id) if friendship else None
    }


@router.get("/{user_id}/friends", response_model=List[dict])
async def get_user_friends_list(
    user_id: UUID,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    """Get target user's friends list - requires friendship"""
    
    # Current user
    supertokens_user_id = session.get_user_id()
    current_user = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()
    
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    # Target user
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
    
    # Get target user's friends
    friendships = db.query(Friendship).filter(
        and_(
            or_(
                Friendship.user_id1 == target_user.id,
                Friendship.user_id2 == target_user.id
            ),
            Friendship.status == RequestStatus.ACCEPTED,
            Friendship.deleted_at.is_(None)
        )
    ).limit(limit).offset(offset).all()
    
    # Build friends list
    friends_list = []
    friend_ids = []
    for f in friendships:
        friend_id = f.user_id2 if f.user_id1 == target_user.id else f.user_id1
        friend = db.query(User).filter(User.id == friend_id).first()
        if friend:
            friends_list.append(friend)
            friend_ids.append(str(friend.id))
    
    # Fetch profile pictures
    async def get_photo_url(user_id: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, s3_service.get_photo_read_url, user_id)
    
    photo_results = await asyncio.gather(*[get_photo_url(fid) for fid in friend_ids])
    
    # Build response
    response = []
    for i, friend in enumerate(friends_list):
        response.append({
            "id": str(friend.id),
            "handle": friend.handle,
            "profile_picture_url": photo_results[i].get('download_url') if photo_results[i] else None
        })
    
    return response
