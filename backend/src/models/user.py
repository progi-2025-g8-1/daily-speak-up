from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    DateTime,
    Text,
    Index,
    Numeric,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import datetime
import uuid

from ..db import Base
from .enums import UserRole, OnboardingStatus, AppTheme, AppLang

if TYPE_CHECKING:
    from .user_device import UserDevice
    from .friendship import Friendship
    from .user_streak import UserStreak
    from .user_interest import UserInterest
    from .speech import Speech
    from .report import Report
    from .rating import Rating
    from .ban import Ban

class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        Index(
            'idx_users_supertokens_user_id',
            'supertokens_user_id',
            unique=True,
        ),
        Index(
            'idx_users_email',
            'email',
            unique=True,
        ),
        Index(
            'idx_users_handle',
            'handle',
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name='user_role', create_type=True),
        default=UserRole.USER,
        nullable=False,
    )

    supertokens_user_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )

    email: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )
    email_changed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    handle: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )
    handle_changed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    profile_picture_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    profile_picture_changed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    onboarding_status: Mapped[OnboardingStatus] = mapped_column(
        SQLEnum(OnboardingStatus, name='onboarding_status', create_type=True),
        default=OnboardingStatus.PENDING,
        nullable=False,
    )

    preferred_lang: Mapped[AppLang] = mapped_column(
        SQLEnum(AppLang, name='app_lang', create_type=True),
        default=AppLang.EN,
        nullable=False,
    )
    preferred_theme: Mapped[AppTheme] = mapped_column(
        SQLEnum(AppTheme, name='app_theme', create_type=True),
        default=AppTheme.SYSTEM,
        nullable=False,
    )
    preferred_tz_offset: Mapped[float] = mapped_column(
        Numeric(3, 1),
        default=0.0,
        nullable=False,
    )

    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    anonymized_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    email_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    push_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    streak_reminders_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    devices: Mapped[List[UserDevice]] = relationship(
        'UserDevice',
        back_populates='user',
    )

    # Friendships where this user is user_id1
    friendships_as_user1: Mapped[List[Friendship]] = relationship(
        'Friendship',
        foreign_keys='Friendship.user_id1',
        back_populates='user1',
    )

    # Friendships where this user is user_id2
    friendships_as_user2: Mapped[List[Friendship]] = relationship(
        'Friendship',
        foreign_keys='Friendship.user_id2',
        back_populates='user2',
    )

    # Friend requests initiated by this user
    requested_friendships: Mapped[List[Friendship]] = relationship(
        'Friendship',
        foreign_keys='Friendship.requested_by_id',
        back_populates='requester',
    )

    # Friendships deleted by this user
    deleted_friendships: Mapped[List[Friendship]] = relationship(
        'Friendship',
        foreign_keys='Friendship.deleted_by',
        back_populates='deleter',
    )

    streaks: Mapped[List[UserStreak]] = relationship(
        'UserStreak',
        back_populates='user',
    )

    user_interests: Mapped[List[UserInterest]] = relationship(
        'UserInterest',
        back_populates='user',
    )

    speeches: Mapped[List[Speech]] = relationship(
        'Speech',
        foreign_keys='Speech.user_id',
        back_populates='user',
    )

    deleted_speeches: Mapped[List[Speech]] = relationship(
        'Speech',
        foreign_keys='Speech.deleted_by',
        back_populates='deleter',
    )

    reports: Mapped[List[Report]] = relationship(
        'Report',
        foreign_keys='Report.reported_by',
        back_populates='reporter',
    )

    resolved_reports: Mapped[List[Report]] = relationship(
        'Report',
        foreign_keys='Report.resolved_by',
        back_populates='resolver',
    )

    ratings: Mapped[List[Rating]] = relationship(
        'Rating',
        back_populates='rater',
    )

    bans_received: Mapped[List[Ban]] = relationship(
        'Ban',
        foreign_keys='Ban.user_id',
        back_populates='banned_user',
    )

    bans_issued: Mapped[List[Ban]] = relationship(
        'Ban',
        foreign_keys='Ban.banned_by',
        back_populates='banner',
    )
