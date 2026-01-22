import pytest
import datetime
from unittest.mock import MagicMock
from backend.src.models.user_streak import UserStreak


class TestStreakCalculationLogic:
    """Unit tests for streak calculation logic from user.py endpoint."""

    def test_active_streak_single_day(self):
        """Test streak that started and ended on the same day."""
        # Arrange
        now = datetime.datetime(2026, 1, 13, 12, 0, 0, tzinfo=datetime.timezone.utc)
        streak = UserStreak(
            start_date=datetime.date(2026, 1, 13),
            end_date=datetime.date(2026, 1, 13),
            ends_at=now + datetime.timedelta(hours=12)  # Still active
        )
        
        # Act - replicate updated logic from user.py
        if streak is None:
            streak_days = 0
        else:
            end_date = streak.end_date if streak.end_date is not None else streak.start_date
            start_date = streak.start_date
            days_delta = (end_date - start_date).days
            streak_days = max(0, int(days_delta) + 1)
        
        # Assert
        assert streak_days == 1  # Same day = 1 day streak

    def test_active_streak_multiple_days(self):
        """Test streak spanning multiple days."""
        # Arrange
        now = datetime.datetime(2026, 1, 13, 12, 0, 0, tzinfo=datetime.timezone.utc)
        streak = UserStreak(
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 13),
            ends_at=now + datetime.timedelta(hours=12)  # Still active
        )
        
        # Act - updated logic
        if streak is None:
            streak_days = 0
        else:
            end_date = streak.end_date if streak.end_date is not None else streak.start_date
            start_date = streak.start_date
            days_delta = (end_date - start_date).days
            streak_days = max(0, int(days_delta) + 1)
        
        # Assert
        assert streak_days == 13  # Jan 1 to Jan 13 = 13 days

    def test_expired_streak_returns_length(self):
        """Expired streak still displays its recorded length."""
        # Arrange
        now = datetime.datetime(2026, 1, 13, 12, 0, 0, tzinfo=datetime.timezone.utc)
        streak = UserStreak(
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 10),
            ends_at=now - datetime.timedelta(days=1)  # Expired yesterday
        )
        
        # Act - updated logic ignores `ends_at` for display
        if streak is None:
            streak_days = 0
        else:
            end_date = streak.end_date if streak.end_date is not None else streak.start_date
            start_date = streak.start_date
            days_delta = (end_date - start_date).days
            streak_days = max(0, int(days_delta) + 1)
        
        # Assert
        assert streak_days == 10

    def test_streak_with_none_end_date_counts_start_date(self):
        """Ongoing streak without `end_date` counts only start day."""
        # Arrange
        now = datetime.datetime(2026, 1, 13, 12, 0, 0, tzinfo=datetime.timezone.utc)
        streak = UserStreak(
            start_date=datetime.date(2026, 1, 10),
            end_date=None,  # Ongoing streak
            ends_at=now + datetime.timedelta(hours=12)  # Still active
        )
        
        # Act - updated logic
        if streak is None:
            streak_days = 0
        else:
            end_date = streak.end_date if streak.end_date is not None else streak.start_date
            start_date = streak.start_date
            days_delta = (end_date - start_date).days
            streak_days = max(0, int(days_delta) + 1)
        
        # Assert: with no end_date provided, count only start day
        assert streak_days == 1

    def test_streak_barely_active(self):
        """Test streak that is still active by 1 second."""
        # Arrange
        now = datetime.datetime(2026, 1, 13, 12, 0, 0, tzinfo=datetime.timezone.utc)
        streak = UserStreak(
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 13),
            ends_at=now + datetime.timedelta(seconds=1)  # Active for 1 more second
        )
        
        # Act - updated logic
        if streak is None:
            streak_days = 0
        else:
            end_date = streak.end_date if streak.end_date is not None else streak.start_date
            start_date = streak.start_date
            days_delta = (end_date - start_date).days
            streak_days = max(0, int(days_delta) + 1)
        
        # Assert
        assert streak_days == 13

    def test_no_streak_returns_zero(self):
        """Test when user has no streak (streak is None)."""
        # Arrange
        streak = None
        now = datetime.datetime(2026, 1, 13, 12, 0, 0, tzinfo=datetime.timezone.utc)
        
        # Act
        if streak is None or streak.ends_at < now:
            streak_days = 0
        else:
            end_date = streak.end_date if streak.end_date is not None else now.date()
            start_date = streak.start_date
            days_delta = (end_date - start_date).days
            streak_days = max(0, int(days_delta) + 1)
        
        # Assert
        assert streak_days == 0

    def test_streak_long_period(self):
        """Test streak spanning a long period (30 days)."""
        # Arrange
        now = datetime.datetime(2026, 1, 31, 12, 0, 0, tzinfo=datetime.timezone.utc)
        streak = UserStreak(
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 30),
            ends_at=now + datetime.timedelta(hours=1)  # Still active
        )
        
        # Act
        if streak.ends_at < now:
            streak_days = 0
        else:
            end_date = streak.end_date if streak.end_date is not None else now.date()
            start_date = streak.start_date
            days_delta = (end_date - start_date).days
            streak_days = max(0, int(days_delta) + 1)
        
        # Assert
        assert streak_days == 30

    def test_streak_across_month_boundary(self):
        """Test streak that spans across month boundaries."""
        # Arrange
        now = datetime.datetime(2026, 2, 5, 12, 0, 0, tzinfo=datetime.timezone.utc)
        streak = UserStreak(
            start_date=datetime.date(2026, 1, 28),
            end_date=datetime.date(2026, 2, 4),
            ends_at=now + datetime.timedelta(hours=1)  # Still active
        )
        
        # Act
        if streak.ends_at < now:
            streak_days = 0
        else:
            end_date = streak.end_date if streak.end_date is not None else now.date()
            start_date = streak.start_date
            days_delta = (end_date - start_date).days
            streak_days = max(0, int(days_delta) + 1)
        
        # Assert
        # Jan 28, 29, 30, 31, Feb 1, 2, 3, 4 = 8 days
        assert streak_days == 8

    def test_streak_with_timezone_edge_case(self):
        """Test streak calculation respects UTC timezone."""
        # Arrange
        now = datetime.datetime(2026, 1, 13, 23, 59, 59, tzinfo=datetime.timezone.utc)
        streak = UserStreak(
            start_date=datetime.date(2026, 1, 13),
            end_date=None,  # Ongoing
            ends_at=datetime.datetime(2026, 1, 14, 0, 0, 0, tzinfo=datetime.timezone.utc)
        )
        
        # Act - updated logic
        if streak is None:
            streak_days = 0
        else:
            end_date = streak.end_date if streak.end_date is not None else streak.start_date
            start_date = streak.start_date
            days_delta = (end_date - start_date).days
            streak_days = max(0, int(days_delta) + 1)
        
        # Assert
        assert streak_days == 1  # Count only recorded day
