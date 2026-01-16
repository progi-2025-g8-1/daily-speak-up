from enum import Enum

class AppLang(str, Enum):
    """Application language options."""
    EN = 'en'
    HR = 'hr'

class UserRole(str, Enum):
    """User role options"""
    USER = 'user'
    MOD = 'mod'
    ADMIN = 'admin'
    ROOT = 'root'

class OnboardingStatus(str, Enum):
    """Onboarding status options."""
    PENDING = 'pending'
    PROFILE_CUSTOMIZATION = 'profile_customization'
    INTERESTS_SELECTION = 'interests_selection'
    COMPLETED = 'completed'

class RequestStatus(str, Enum):
    """Friendship request status options."""
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    DENIED = 'denied'
    DELETED = 'deleted'

class SpeechVisibility(str, Enum):
    """Speech visibility options."""
    PRIVATE = 'private'
    FRIENDS = 'friends'

class ResolutionAction(str, Enum):
    """Report resolution action options."""
    PENDING = 'pending'
    IGNORED = 'ignored'
    VIDEO_DELETED = 'video_deleted'
    USER_BANNED = 'user_banned'
