import pytest
from pydantic import ValidationError
from uuid import uuid4
from backend.src.schemas.topic import TopicRequest, TopicResponse
from backend.src.schemas.user import (
    UserCreate, UserResponse, VideoInfo,
    FriendInfo, FriendsListResponse, UserInterestsResponse,
    NotificationSettingUpdate, PublicUserProfile
)
from backend.src.schemas.userdata import UsernameData, EmailData, InterestData
from backend.src.schemas.search import UserSearchFilters, UserSearchResult
from backend.src.models.enums import (
    AppLang, AppTheme, OnboardingStatus, UserRole, SpeechVisibility
)


class TestTopicSchemas:
    """Unit tests for Topic-related schemas."""

    def test_topic_request_valid_english(self):
        """Test valid TopicRequest with English language."""
        data = {
            "interes": "technology",
            "lang": AppLang.EN
        }
        request = TopicRequest(**data)
        
        assert request.interes == "technology"
        assert request.lang == AppLang.EN

    def test_topic_request_valid_croatian(self):
        """Test valid TopicRequest with Croatian language."""
        data = {
            "interes": "glazba",
            "lang": AppLang.HR
        }
        request = TopicRequest(**data)
        
        assert request.interes == "glazba"
        assert request.lang == AppLang.HR

    def test_topic_request_default_language(self):
        """Test TopicRequest defaults to English when lang not provided."""
        data = {"interes": "sports"}
        request = TopicRequest(**data)  # type: ignore
        
        assert request.interes == "sports"
        assert request.lang == AppLang.EN

    def test_topic_request_min_length_validation(self):
        """Test TopicRequest rejects empty interest string."""
        data = {
            "interes": "",
            "lang": AppLang.EN
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TopicRequest(**data)
        
        errors = exc_info.value.errors()
        assert any("at least 1 character" in str(error) for error in errors)

    def test_topic_request_invalid_language(self):
        """Test TopicRequest rejects invalid language code."""
        data = {
            "interes": "technology",
            "lang": "invalid_lang"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TopicRequest(**data)  # type: ignore
        
        errors = exc_info.value.errors()
        assert any("lang" in str(error) for error in errors)

    def test_topic_response_valid(self):
        """Test valid TopicResponse."""
        data = {
            "tema": "The Future of Artificial Intelligence",
            "lang": AppLang.EN
        }
        response = TopicResponse(**data)
        
        assert response.tema == "The Future of Artificial Intelligence"
        assert response.lang == AppLang.EN

    def test_topic_response_missing_required_field(self):
        """Test TopicResponse requires both tema and lang."""
        data = {"tema": "Some topic"}
        
        with pytest.raises(ValidationError) as exc_info:
            TopicResponse(**data)  # type: ignore
        
        errors = exc_info.value.errors()
        assert any("lang" in str(error) for error in errors)


class TestUserSchemas:
    """Unit tests for User-related schemas."""

    def test_user_create_valid_email(self):
        """Test UserCreate with valid email."""
        data = {
            "email": "user@example.com",
            "name": "John Doe"
        }
        user = UserCreate(**data)
        
        assert user.email == "user@example.com"
        assert user.name == "John Doe"

    def test_user_create_without_name(self):
        """Test UserCreate allows optional name field."""
        data = {"email": "user@example.com"}
        user = UserCreate(**data)
        
        assert user.email == "user@example.com"
        assert user.name is None

    def test_user_create_invalid_email(self):
        """Test UserCreate rejects invalid email formats."""
        invalid_emails = [
            "not_an_email",
            "@example.com",
            "user@",
            "user@.com",
            "user @example.com",
            "",
        ]
        
        for invalid_email in invalid_emails:
            data = {"email": invalid_email}
            with pytest.raises(ValidationError):
                UserCreate(**data)

    def test_user_response_valid(self):
        """Test UserResponse with all valid fields."""
        data = {
            "role": UserRole.USER,
            "email": "user@example.com",
            "handle": "johndoe",
            "profile_picture_url": "https://example.com/pic.jpg",
            "onboarding_status": OnboardingStatus.COMPLETED,
            "preferred_lang": AppLang.EN,
            "preferred_theme": AppTheme.DARK,
            "preferred_tz_offset": -5.0,
            "email_notifications_enabled": True,
            "push_notifications_enabled": False,
            "streak_reminders_enabled": True,
            "friends_count": 42,
            "streak": 7
        }
        user = UserResponse(**data)
        
        assert user.role == UserRole.USER
        assert user.email == "user@example.com"
        assert user.handle == "johndoe"
        assert user.onboarding_status == OnboardingStatus.COMPLETED
        assert user.preferred_lang == AppLang.EN
        assert user.preferred_theme == AppTheme.DARK
        assert user.friends_count == 42
        assert user.streak == 7

    def test_user_response_invalid_role(self):
        """Test UserResponse rejects invalid role."""
        data = {
            "role": "invalid_role",
            "email": "user@example.com",
            "handle": "johndoe",
            "profile_picture_url": None,
            "onboarding_status": OnboardingStatus.COMPLETED,
            "preferred_lang": AppLang.EN,
            "preferred_theme": AppTheme.DARK,
            "preferred_tz_offset": 0.0,
            "email_notifications_enabled": True,
            "push_notifications_enabled": True,
            "streak_reminders_enabled": True,
            "friends_count": 0,
            "streak": 0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(**data)
        
        errors = exc_info.value.errors()
        assert any("role" in str(error) for error in errors)

    def test_video_info_valid(self):
        """Test VideoInfo with valid data."""
        video_id = uuid4()
        owner_id = uuid4()
        
        data = {
            "video_id": str(video_id),
            "owner_id": str(owner_id),
            "year": 2026,
            "month": 1,
            "day": 13,
            "caption": "My first speech",
            "url": "https://example.com/video.mp4",
            "visibility": SpeechVisibility.FRIENDS
        }
        video = VideoInfo(**data)
        
        assert video.video_id == video_id
        assert video.owner_id == owner_id
        assert video.year == 2026
        assert video.month == 1
        assert video.day == 13
        assert video.caption == "My first speech"
        assert video.visibility == SpeechVisibility.FRIENDS

    def test_video_info_optional_caption(self):
        """Test VideoInfo allows None caption."""
        data = {
            "video_id": str(uuid4()),
            "owner_id": str(uuid4()),
            "year": 2026,
            "month": 1,
            "day": 13,
            "caption": None,
            "url": "https://example.com/video.mp4",
            "visibility": SpeechVisibility.PRIVATE
        }
        video = VideoInfo(**data)
        
        assert video.caption is None
        assert video.visibility == SpeechVisibility.PRIVATE

    def test_friend_info_valid(self):
        """Test FriendInfo with valid data."""
        user_id = uuid4()
        data = {
            "user_id": user_id,
            "handle": "friend_user",
            "profile_picture_url": "https://example.com/pic.jpg"
        }
        friend = FriendInfo(**data)
        
        assert friend.user_id == user_id
        assert friend.handle == "friend_user"
        assert friend.profile_picture_url == "https://example.com/pic.jpg"

    def test_friends_list_response_empty(self):
        """Test FriendsListResponse with empty list."""
        data = {"friends": []}
        response = FriendsListResponse(**data)
        
        assert response.friends == []

    def test_friends_list_response_with_friends(self):
        """Test FriendsListResponse with multiple friends."""
        data = {
            "friends": [
                {
                    "user_id": str(uuid4()),
                    "handle": "friend1",
                    "profile_picture_url": None
                },
                {
                    "user_id": str(uuid4()),
                    "handle": "friend2",
                    "profile_picture_url": "https://example.com/pic.jpg"
                }
            ]
        }
        response = FriendsListResponse(**data)
        
        assert len(response.friends) == 2
        assert response.friends[0].handle == "friend1"
        assert response.friends[1].handle == "friend2"

    def test_user_interests_response_valid(self):
        """Test UserInterestsResponse with interest list."""
        data = {"interests": ["technology", "sports", "music"]}
        response = UserInterestsResponse(**data)
        
        assert len(response.interests) == 3
        assert "technology" in response.interests

    def test_notification_setting_update_valid(self):
        """Test NotificationSettingUpdate."""
        data = {"enabled": True}
        setting = NotificationSettingUpdate(**data)
        
        assert setting.enabled is True
        
        data = {"enabled": False}
        setting = NotificationSettingUpdate(**data)
        
        assert setting.enabled is False

    def test_public_user_profile_valid(self):
        """Test PublicUserProfile."""
        user_id = uuid4()
        data = {
            "id": str(user_id),
            "handle": "public_user",
            "profile_picture_url": "https://example.com/pic.jpg",
            "friend_count": 10,
            "current_streak": 5
        }
        profile = PublicUserProfile(**data)
        
        assert profile.id == user_id
        assert profile.handle == "public_user"
        assert profile.friend_count == 10
        assert profile.current_streak == 5


class TestUserdataSchemas:
    """Unit tests for Userdata schemas."""

    def test_username_data_valid(self):
        """Test UsernameData with valid username."""
        data = {"username": "newusername"}
        username = UsernameData(**data)
        
        assert username.username == "newusername"

    def test_username_data_missing(self):
        """Test UsernameData requires username field."""
        with pytest.raises(ValidationError) as exc_info:
            UsernameData(**{})
        
        errors = exc_info.value.errors()
        assert any("username" in str(error) for error in errors)

    def test_email_data_valid(self):
        """Test EmailData with valid email."""
        data = {"email": "newemail@example.com"}
        email = EmailData(**data)
        
        assert email.email == "newemail@example.com"

    def test_email_data_invalid(self):
        """Test EmailData rejects invalid email."""
        invalid_emails = ["not_an_email", "@example.com", ""]
        
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError):
                EmailData(email=invalid_email)

    def test_interest_data_valid(self):
        """Test InterestData with list of interests."""
        data = {"interests": ["tech", "sports", "music"]}
        interests = InterestData(**data)
        
        assert len(interests.interests) == 3
        assert "tech" in interests.interests

    def test_interest_data_empty_list(self):
        """Test InterestData allows empty list."""
        data = {"interests": []}
        interests = InterestData(**data)
        
        assert interests.interests == []

    def test_interest_data_missing(self):
        """Test InterestData requires interests field."""
        with pytest.raises(ValidationError):
            InterestData(**{})


class TestSearchSchemas:
    """Unit tests for Search schemas."""

    def test_user_search_filters_defaults(self):
        """Test UserSearchFilters with default values."""
        filters = UserSearchFilters()
        
        assert filters.include_friends is None
        assert filters.include_self is False
        assert filters.only_admins is None
        assert filters.only_mods is None
        assert filters.only_users is None

    def test_user_search_filters_custom(self):
        """Test UserSearchFilters with custom values."""
        data = {
            "include_friends": True,
            "include_self": True,
            "only_admins": False,
            "only_mods": True,
            "only_users": None
        }
        filters = UserSearchFilters(**data)
        
        assert filters.include_friends is True
        assert filters.include_self is True
        assert filters.only_admins is False
        assert filters.only_mods is True
        assert filters.only_users is None

    def test_user_search_result_minimal(self):
        """Test UserSearchResult with minimal required fields."""
        data = {
            "user_id": str(uuid4()),
            "handle": "searchuser",
            "profile_picture_url": None,
            "relationship_status": None,
            "friendship_id": None
        }
        result = UserSearchResult(**data)
        
        assert result.handle == "searchuser"
        assert result.email is None
        assert result.role is None

    def test_user_search_result_full(self):
        """Test UserSearchResult with all fields (admin view)."""
        user_id = uuid4()
        friendship_id = uuid4()
        
        data = {
            "user_id": str(user_id),
            "handle": "fulluser",
            "email": "user@example.com",
            "profile_picture_url": "https://example.com/pic.jpg",
            "relationship_status": "accepted",
            "friendship_id": str(friendship_id),
            "role": "mod",
            "created_at": "2026-01-13T12:00:00Z"
        }
        result = UserSearchResult(**data)
        
        assert result.handle == "fulluser"
        assert result.email == "user@example.com"
        assert result.relationship_status == "accepted"
        assert result.role == "mod"
        assert result.created_at == "2026-01-13T12:00:00Z"
