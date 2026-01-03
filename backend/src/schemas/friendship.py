from pydantic import BaseModel


class FriendshipResponse(BaseModel):
    """Response model for a friend in the friends list."""
    
    friendship_id: str
    user_id: str
    handle: str
    profile_picture_url: str | None
    created_at: str
    requested_by_current_user: bool


class FriendRequestResponse(BaseModel):
    """Response model for incoming/outgoing friend requests."""
    
    friendship_id: str
    user_id: str
    handle: str
    profile_picture_url: str | None
    created_at: str


class FriendshipStatusResponse(BaseModel):
    """Response model for friendship status check."""
    
    status: str | None  # 'accepted', 'pending_outgoing', 'pending_incoming', 'denied', None
    friendship_id: str | None
