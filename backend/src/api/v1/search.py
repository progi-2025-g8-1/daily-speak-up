import uuid
import asyncio
from typing import List
from supertokens_python.recipe.session import SessionContainer
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from ..deps import get_session, get_s3_service, get_current_user
from ...schemas import UserSearchResult
from ...db import get_db
from ...models import User, Friendship, RequestStatus, UserRole
from ...services import S3SecureService

router = APIRouter(prefix='/search', tags=['search'])


@router.get('/users', response_model=List[UserSearchResult])
async def search_users(
    query: str = Query(..., min_length=1, description="Search query for username or handle"),
    include_friends: bool | None = Query(default=None, description="Filter by friendship status"),
    include_self: bool = Query(default=False, description="Include current user in results"),
    only_admins: bool | None = Query(default=None, description="Filter by admin role"),
    only_mods: bool | None = Query(default=None, description="Filter by moderator role"),
    only_users: bool | None = Query(default=None, description="Filter by regular user role"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    """
    Search for users by handle or email with comprehensive filtering options.
    
    Filters:
    - include_friends: True (only friends), False (exclude friends), None (all)
    - include_self: Whether to include the current user
    - only_admins: True (only admins), False (exclude admins), None (all)
    - only_mods: True (only mods), False (exclude mods), None (all)
    - only_users: True (only regular users), False (exclude regular users), None (all)
    
    Admins will see additional fields: email, role, created_at
    """
    is_admin = current_user.role == UserRole.ADMIN
    
    # Build base query - search by handle or email (case-insensitive)
    search_filter = or_(
        func.lower(User.handle).contains(func.lower(query)),
        func.lower(User.email).contains(func.lower(query))
    )
    
    # Start with base filters
    filters = [
        search_filter,
        User.deleted_at.is_(None),
        User.anonymized_at.is_(None)
    ]
    
    # Filter by self
    if not include_self:
        filters.append(User.id != current_user.id)
    
    # Filter by role
    role_filters = []
    if only_admins is True:
        role_filters.append(User.role == UserRole.ADMIN)
    elif only_admins is False:
        role_filters.append(User.role != UserRole.ADMIN)
    
    if only_mods is True:
        role_filters.append(User.role == UserRole.MOD)
    elif only_mods is False:
        role_filters.append(User.role != UserRole.MOD)
    
    if only_users is True:
        role_filters.append(User.role == UserRole.USER)
    elif only_users is False:
        role_filters.append(User.role != UserRole.USER)
    
    # Combine role filters with OR if multiple specified
    if role_filters:
        if len(role_filters) == 1:
            filters.append(role_filters[0])
        else:
            filters.append(or_(*role_filters))
    
    # Execute initial query
    users_query = db.query(User).filter(and_(*filters))
    
    # Get all matching users first
    all_users = users_query.limit(limit * 2).all()  # Get extra to filter by friendship
    
    # Get all friendships for the current user
    friendships = db.query(Friendship).filter(
        and_(
            or_(
                Friendship.user_id1 == current_user.id,
                Friendship.user_id2 == current_user.id
            ),
            Friendship.deleted_at.is_(None)
        )
    ).all()
    
    # Build friendship lookup
    friendship_map = {}
    for friendship in friendships:
        other_id = friendship.user_id2 if friendship.user_id1 == current_user.id else friendship.user_id1
        friendship_map[other_id] = {
            'friendship_id': friendship.id,
            'status': friendship.status,
            'requested_by_id': friendship.requested_by_id
        }
    
    # Filter by friendship status
    filtered_users = []
    for user in all_users:
        is_friend = user.id in friendship_map and friendship_map[user.id]['status'] == RequestStatus.ACCEPTED
        
        if include_friends is True and not is_friend:
            continue
        elif include_friends is False and is_friend:
            continue
        
        filtered_users.append(user)
        
        if len(filtered_users) >= limit:
            break
    
    # Fetch profile pictures concurrently
    user_ids = [str(user.id) for user in filtered_users]
    
    async def get_photo_url(user_id: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, s3_service.get_photo_read_url, user_id)
    
    photo_results = await asyncio.gather(*[get_photo_url(uid) for uid in user_ids])
    
    # Build response
    results = []
    for i, user in enumerate(filtered_users):
        # Determine relationship status
        relationship_status = None
        friendship_id = None
        
        if user.id in friendship_map:
            friend_info = friendship_map[user.id]
            friendship_id = str(friend_info['friendship_id'])
            
            if friend_info['status'] == RequestStatus.ACCEPTED:
                relationship_status = 'accepted'
            elif friend_info['status'] == RequestStatus.PENDING:
                if friend_info['requested_by_id'] == current_user.id:
                    relationship_status = 'pending_outgoing'
                else:
                    relationship_status = 'pending_incoming'
            elif friend_info['status'] == RequestStatus.DENIED:
                relationship_status = 'denied'
        
        result = {
            'user_id': str(user.id),
            'handle': user.handle,
            'profile_picture_url': photo_results[i].get('download_url'),
            'relationship_status': relationship_status,
            'friendship_id': friendship_id
        }
        
        # Add admin-only fields
        if is_admin:
            result['email'] = user.email
            result['role'] = user.role.value
            result['created_at'] = user.created_at.isoformat()
        
        results.append(result)
    
    return results
