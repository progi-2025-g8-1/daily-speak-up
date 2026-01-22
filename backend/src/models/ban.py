from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import datetime
import uuid

from ..db import Base

if TYPE_CHECKING:
    from .user import User
    from .report import Report

class Ban(Base):
    __tablename__ = 'bans'
    __table_args__ = (
        Index(
            'idx_bans_user_id',
            'user_id',
        ),
        Index(
            'idx_bans_banned_by',
            'banned_by',
        ),
        Index(
            'idx_bans_report_id',
            'report_id',
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
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        unique=True,
    )
    ends_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    banned_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False,
    )
    report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('reports.id'),
        nullable=True
    )

    # Relationships
    banned_user: Mapped[User] = relationship(
        'User',
        foreign_keys=[user_id],
        back_populates='bans_received',
    )
    banner: Mapped[User] = relationship(
        'User',
        foreign_keys=[banned_by],
        back_populates='bans_issued',
    )
    report: Mapped[Optional[Report]] = relationship(
        'Report',
        back_populates='bans',
    )
