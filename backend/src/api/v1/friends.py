import logging
import uuid
import datetime
from typing import List
from supertokens_python.recipe.session import SessionContainer
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from ..deps import get_session
from ...schemas import FriendshipResponse, FriendRequestResponse, FriendshipStatusResponse
from ...db import get_db
from ...models import User, Friendship, RequestStatus

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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Friend request was previously denied'
            )
    
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
    
    # TODO: Send notification to requester about the response
    
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
    for friendship in friendships:
        # Determine which user is the friend
        friend_id = friendship.user_id2 if friendship.user_id1 == user.id else friendship.user_id1
        friend = db.query(User).filter(User.id == friend_id).first()
        
        if friend:
            friends_list.append({
                'friendship_id': str(friendship.id),
                'user_id': str(friend.id),
                'handle': friend.handle,
                'profile_picture_url': friend.profile_picture_url,
                'created_at': friendship.created_at.isoformat(),
                'requested_by_current_user': friendship.requested_by_id == user.id
            })
    
    return friends_list

@router.get('/requests/incoming', response_model=List[FriendRequestResponse])
async def get_incoming_friend_requests(
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
    for friendship in friendships:
        requester = db.query(User).filter(User.id == friendship.requested_by_id).first()
        
        if requester:
            requests_list.append({
                'friendship_id': str(friendship.id),
                'user_id': str(requester.id),
                'handle': requester.handle,
                'profile_picture_url': requester.profile_picture_url,
                'created_at': friendship.created_at.isoformat()
            })
    
    return requests_list

@router.get('/requests/outgoing', response_model=List[FriendRequestResponse])
async def get_outgoing_friend_requests(
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
    for friendship in friendships:
        # Determine which user is the target (not the requester)
        target_id = friendship.user_id2 if friendship.user_id1 == user.id else friendship.user_id1
        target_user = db.query(User).filter(User.id == target_id).first()
        
        if target_user:
            requests_list.append({
                'friendship_id': str(friendship.id),
                'user_id': str(target_user.id),
                'handle': target_user.handle,
                'profile_picture_url': target_user.profile_picture_url,
                'created_at': friendship.created_at.isoformat()
            })
    
    return requests_list

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
