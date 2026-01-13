import pytest
import uuid
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from backend.src.db import Base
from backend.src.models.friendship import Friendship
from backend.src.models.rating import Rating
from backend.src.models.user import User
from backend.src.models.speech import Speech
from backend.src.models.interest import Interest
from backend.src.models.enums import RequestStatus


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    # Use SQLite in-memory for fast tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_users(db_session):
    """Create test users for constraint testing."""
    user1 = User(
        id=uuid.uuid4(),
        supertokens_user_id="test_user_1",
        email="user1@example.com",
        handle="user1"
    )
    user2 = User(
        id=uuid.uuid4(),
        supertokens_user_id="test_user_2",
        email="user2@example.com",
        handle="user2"
    )
    user3 = User(
        id=uuid.uuid4(),
        supertokens_user_id="test_user_3",
        email="user3@example.com",
        handle="user3"
    )
    db_session.add_all([user1, user2, user3])
    db_session.commit()
    return user1, user2, user3


class TestFriendshipConstraints:
    """Test database constraints on Friendship model."""

    def test_friendship_user_ids_must_be_ordered(self, db_session, test_users):
        """Test that user_id1 < user_id2 constraint is enforced."""
        user1, user2, _ = test_users
        
        # Get IDs and ensure user1 > user2 for this test
        if user1.id < user2.id:
            user1, user2 = user2, user1
        
        # Try to create friendship with user_id1 > user_id2 (should fail)
        friendship = Friendship(
            user_id1=user1.id,  # Larger ID
            user_id2=user2.id,  # Smaller ID
            requested_by_id=user1.id,
            status=RequestStatus.PENDING
        )
        db_session.add(friendship)
        
        # Assert - SQLite may not enforce this, but test the intent
        # In PostgreSQL this would raise IntegrityError
        # For SQLite, we just document the expected behavior
        try:
            db_session.commit()
            # If commit succeeds, manually check the constraint
            assert friendship.user_id1 < friendship.user_id2, \
                "Constraint should enforce user_id1 < user_id2"
        except IntegrityError:
            # Expected in PostgreSQL
            db_session.rollback()

    def test_friendship_users_must_be_different(self, db_session, test_users):
        """Test that user_id1 != user_id2 constraint is enforced."""
        user1, _, _ = test_users
        
        # Try to create friendship with same user (should fail)
        friendship = Friendship(
            user_id1=user1.id,
            user_id2=user1.id,  # Same as user_id1
            requested_by_id=user1.id,
            status=RequestStatus.PENDING
        )
        db_session.add(friendship)
        
        # Assert - should raise IntegrityError
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_friendship_unique_pair_constraint(self, db_session, test_users):
        """Test that user pair must be unique."""
        user1, user2, _ = test_users
        
        # Ensure proper ordering
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        # Create first friendship
        friendship1 = Friendship(
            user_id1=user1.id,
            user_id2=user2.id,
            requested_by_id=user1.id,
            status=RequestStatus.PENDING
        )
        db_session.add(friendship1)
        db_session.commit()
        
        # Try to create duplicate friendship (should fail)
        friendship2 = Friendship(
            user_id1=user1.id,
            user_id2=user2.id,
            requested_by_id=user2.id,
            status=RequestStatus.ACCEPTED
        )
        db_session.add(friendship2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_friendship_valid_creation(self, db_session, test_users):
        """Test that valid friendship can be created."""
        user1, user2, _ = test_users
        
        # Ensure proper ordering
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        # Create valid friendship
        friendship = Friendship(
            user_id1=user1.id,
            user_id2=user2.id,
            requested_by_id=user1.id,
            status=RequestStatus.PENDING
        )
        db_session.add(friendship)
        db_session.commit()
        
        # Assert
        assert friendship.id is not None
        assert friendship.user_id1 == user1.id
        assert friendship.user_id2 == user2.id
        assert friendship.status == RequestStatus.PENDING


class TestRatingConstraints:
    """Test database constraints on Rating model."""

    @pytest.fixture
    def test_speech(self, db_session, test_users):
        """Create a test speech for rating tests."""
        user1, _, _ = test_users
        interest = Interest(name="technology", slug="technology")
        db_session.add(interest)
        db_session.commit()
        
        speech = Speech(
            id=uuid.uuid4(),
            user_id=user1.id,
            interest_id=interest.id,
            task="Test topic"
        )
        db_session.add(speech)
        db_session.commit()
        return speech

    def test_rating_score_minimum_constraint(self, db_session, test_users, test_speech):
        """Test that rating score cannot be below 0."""
        user1, _, _ = test_users
        
        # Try to create rating with score < 0 (should fail)
        rating = Rating(
            speech_id=test_speech.id,
            rated_by=user1.id,
            score=-0.5  # Invalid: below 0
        )
        db_session.add(rating)
        
        # SQLite may not enforce this, but PostgreSQL will
        try:
            db_session.commit()
            # If it succeeds, check manually
            assert rating.score >= 0, "Score should not be negative"
        except IntegrityError:
            db_session.rollback()

    def test_rating_score_maximum_constraint(self, db_session, test_users, test_speech):
        """Test that rating score cannot be above 5."""
        user1, _, _ = test_users
        
        # Try to create rating with score > 5 (should fail)
        rating = Rating(
            speech_id=test_speech.id,
            rated_by=user1.id,
            score=5.5  # Invalid: above 5
        )
        db_session.add(rating)
        
        # SQLite may not enforce this, but PostgreSQL will
        try:
            db_session.commit()
            # If it succeeds, check manually
            assert rating.score <= 5, "Score should not exceed 5"
        except IntegrityError:
            db_session.rollback()

    def test_rating_valid_scores(self, db_session, test_users, test_speech):
        """Test that valid rating scores are accepted."""
        _, user2, user3 = test_users
        
        valid_scores = [0.0, 1.0, 2.5, 3.75, 4.5, 5.0]
        
        for idx, score in enumerate(valid_scores):
            # Use different users to avoid unique constraint issues
            rated_by = user2.id if idx % 2 == 0 else user3.id
            
            # Create a new speech for each rating
            interest = Interest(name=f"interest_{idx}", slug=f"interest-{idx}")
            db_session.add(interest)
            db_session.commit()
            
            speech = Speech(
                id=uuid.uuid4(),
                user_id=test_users[0].id,
                interest_id=interest.id,
                task=f"Test topic {idx}"
            )
            db_session.add(speech)
            db_session.commit()
            
            rating = Rating(
                speech_id=speech.id,
                rated_by=rated_by,
                score=score
            )
            db_session.add(rating)
            db_session.commit()
            
            # Assert
            assert rating.id is not None
            assert rating.score == score

    def test_rating_boundary_values(self, db_session, test_users, test_speech):
        """Test rating with exact boundary values."""
        user1, user2, _ = test_users
        
        # Create two speeches for two boundary ratings
        interest1 = Interest(name="boundary_test_1", slug="boundary-test-1")
        interest2 = Interest(name="boundary_test_2", slug="boundary-test-2")
        db_session.add_all([interest1, interest2])
        db_session.commit()
        
        speech1 = Speech(
            id=uuid.uuid4(),
            user_id=user1.id,
            interest_id=interest1.id,
            task="Boundary test 1"
        )
        speech2 = Speech(
            id=uuid.uuid4(),
            user_id=user1.id,
            interest_id=interest2.id,
            task="Boundary test 2"
        )
        db_session.add_all([speech1, speech2])
        db_session.commit()
        
        # Test minimum boundary (0)
        rating_min = Rating(
            speech_id=speech1.id,
            rated_by=user2.id,
            score=0.0
        )
        db_session.add(rating_min)
        db_session.commit()
        assert rating_min.score == 0.0
        
        # Test maximum boundary (5)
        rating_max = Rating(
            speech_id=speech2.id,
            rated_by=user2.id,
            score=5.0
        )
        db_session.add(rating_max)
        db_session.commit()
        assert rating_max.score == 5.0


class TestUserConstraints:
    """Test database constraints on User model."""

    def test_user_unique_email_constraint(self, db_session):
        """Test that email must be unique."""
        user1 = User(
            supertokens_user_id="user_unique_1",
            email="duplicate@example.com",
            handle="user1"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create another user with same email
        user2 = User(
            supertokens_user_id="user_unique_2",
            email="duplicate@example.com",  # Duplicate
            handle="user2"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_unique_handle_constraint(self, db_session):
        """Test that handle must be unique."""
        user1 = User(
            supertokens_user_id="user_handle_1",
            email="email1@example.com",
            handle="duplicate_handle"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create another user with same handle
        user2 = User(
            supertokens_user_id="user_handle_2",
            email="email2@example.com",
            handle="duplicate_handle"  # Duplicate
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_unique_supertokens_id_constraint(self, db_session):
        """Test that supertokens_user_id must be unique."""
        user1 = User(
            supertokens_user_id="duplicate_supertokens",
            email="email3@example.com",
            handle="handle3"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create another user with same supertokens_user_id
        user2 = User(
            supertokens_user_id="duplicate_supertokens",  # Duplicate
            email="email4@example.com",
            handle="handle4"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_valid_creation(self, db_session):
        """Test that user with valid unique fields can be created."""
        user = User(
            supertokens_user_id="valid_user",
            email="valid@example.com",
            handle="valid_handle"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "valid@example.com"
        assert user.handle == "valid_handle"
