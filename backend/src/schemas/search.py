from pydantic import BaseModel, Field
from typing import Optional
from ..models import UserRole


class UserSearchFilters(BaseModel):
    """Filters for user search."""
    
    include_friends: Optional[bool] = Field(
        default=None,
        description="If True, only include friends. If False, exclude friends. If None, include all."
    )
    include_self: bool = Field(
        default=False,
        description="Whether to include the current user in results"
    )
    only_admins: Optional[bool] = Field(
        default=None,
        description="If True, only admins. If False, exclude admins. If None, include all."
    )
    only_mods: Optional[bool] = Field(
        default=None,
        description="If True, only mods. If False, exclude mods. If None, include all."
    )
    only_users: Optional[bool] = Field(
        default=None,
        description="If True, only regular users. If False, exclude regular users. If None, include all."
    )


class UserSearchResult(BaseModel):
    """Search result for a single user."""
    
    user_id: str
    handle: str
    email: str | None = None  # Only visible to admins
    profile_picture_url: str | None
    relationship_status: str | None  # 'accepted', 'pending_outgoing', 'pending_incoming', 'denied', None
    friendship_id: str | None
    role: str | None = None  # Only visible to admins
    created_at: str | None = None  # Only visible to admins
