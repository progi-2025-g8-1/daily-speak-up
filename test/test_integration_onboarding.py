import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.src.db import Base, get_db
from backend.src.api.deps import get_session
from backend.src.models import User, Interest, UserInterest
from backend.src.models.enums import OnboardingStatus
from backend.src.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=None  # Disable connection pooling for tests
    )
    # Ensure all models are imported and registered
    import backend.src.models.user
    import backend.src.models.friendship
    import backend.src.models.interest
    import backend.src.models.user_interest
    import backend.src.models.user_streak
    import backend.src.models.speech
    import backend.src.models.rating
    import backend.src.models.ban
    import backend.src.models.report
    import backend.src.models.user_device
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a single database session for the entire test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def mock_session():
    """Create a mock SuperTokens session."""
    session = MagicMock()
    session.get_user_id.return_value = "test_user_123"
    return session


@pytest.fixture(scope="function")
def client(db_session, mock_session):
    """Create a test client with test database and mocked auth."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Don't close, managed by fixture
    
    def override_get_session():
        return mock_session
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def seed_interests(db_session):
    """Seed database with test interests."""
    interests = [
        Interest(name="technology", slug="technology"),
        Interest(name="sports", slug="sports"),
        Interest(name="music", slug="music"),
        Interest(name="cooking", slug="cooking"),
    ]
    db_session.add_all(interests)
    db_session.commit()


class TestUserRegistration:
    """Integration tests for user registration endpoint."""

    @patch('backend.src.services.email_service.EmailService.send_email')
    def test_register_new_user_success(self, mock_email, client, db_session):
        """Test successful user registration."""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "name": "New User"
        }
        
        # Act
        response = client.put("/api/v1/user/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "ok"
        
        # Verify user was created in database
        user = db_session.query(User).filter(User.email == "newuser@example.com").first()
        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.supertokens_user_id == "test_user_123"
        assert user.handle == "test_user_123"  # Default handle
        assert user.onboarding_status == OnboardingStatus.PENDING
        
        # Verify welcome email was sent
        mock_email.assert_called_once()

    @patch('backend.src.services.email_service.EmailService.send_email')
    def test_register_duplicate_user_fails(self, mock_email, client, db_session):
        """Test that registering an existing user fails."""
        # Arrange - create existing user
        existing_user = User(
            supertokens_user_id="test_user_123",
            email="existing@example.com",
            handle="existing_handle"
        )
        db_session.add(existing_user)
        db_session.commit()
        
        user_data = {
            "email": "newuser@example.com",
            "name": "New User"
        }
        
        # Act
        response = client.put("/api/v1/user/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"].lower()

    @patch('backend.src.services.email_service.EmailService.send_email')
    def test_register_without_name(self, mock_email, client, db_session):
        """Test user registration without optional name field."""
        # Arrange
        user_data = {
            "email": "noname@example.com"
        }
        
        # Act
        response = client.put("/api/v1/user/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Verify user was created
        user = db_session.query(User).filter(User.email == "noname@example.com").first()
        assert user is not None

    def test_register_invalid_email(self, client, db_session):
        """Test registration with invalid email format."""
        # Arrange
        user_data = {
            "email": "not_an_email",
            "name": "Test User"
        }
        
        # Act
        response = client.put("/api/v1/user/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestOnboardingFlow:
    """Integration tests for onboarding flow."""

    @pytest.fixture
    def registered_user(self, db_session):
        """Create a registered user for onboarding tests."""
        user = User(
            supertokens_user_id="test_user_123",
            email="onboarding@example.com",
            handle="test_user_123",
            onboarding_status=OnboardingStatus.PENDING
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_get_onboarding_state_pending(self, client, db_session, registered_user):
        """Test getting onboarding state for pending user."""
        # Act
        response = client.get("/api/v1/onboarding/state")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] is False
        assert data["phase"] == 1
        assert data["status"] == OnboardingStatus.PENDING

    def test_update_onboarding_profile(self, client, db_session, registered_user):
        """Test updating profile during onboarding (Phase 1)."""
        # Arrange
        profile_data = {
            "handle": "awesome_user"
        }
        
        # Act
        response = client.patch("/api/v1/onboarding/profile", json=profile_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Profile updated successfully"
        assert data["onboarding_status"] == OnboardingStatus.INTERESTS_SELECTION
        
        # Verify user in database
        user = db_session.query(User).filter(User.email == "onboarding@example.com").first()
        assert user.handle == "awesome_user"
        assert user.onboarding_status == OnboardingStatus.INTERESTS_SELECTION

    def test_update_onboarding_duplicate_handle_fails(self, client, db_session, registered_user):
        """Test that duplicate handle is rejected during onboarding."""
        # Arrange - create user with existing handle
        existing_user = User(
            supertokens_user_id="another_user",
            email="another@example.com",
            handle="taken_handle"
        )
        db_session.add(existing_user)
        db_session.commit()
        
        profile_data = {
            "handle": "taken_handle"
        }
        
        # Act
        response = client.patch("/api/v1/onboarding/profile", json=profile_data)
        
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already taken" in response.json()["detail"].lower()

    def test_update_onboarding_interests(self, client, db_session, registered_user, seed_interests):
        """Test updating interests during onboarding (Phase 2)."""
        # Arrange - advance user to interests phase
        user = db_session.query(User).filter(User.email == "onboarding@example.com").first()
        user.onboarding_status = OnboardingStatus.INTERESTS_SELECTION
        db_session.commit()
        
        interest_data = {
            "interests": ["technology", "sports"]
        }
        
        # Act
        response = client.patch("/api/v1/onboarding/interests", json=interest_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Onboarding completed successfully"
        assert data["onboarding_status"] == OnboardingStatus.COMPLETED
        
        # Verify user interests in database
        user = db_session.query(User).filter(User.email == "onboarding@example.com").first()
        assert user.onboarding_status == OnboardingStatus.COMPLETED
        
        user_interests = db_session.query(UserInterest).filter(
            UserInterest.user_id == user.id
        ).all()
        assert len(user_interests) == 2

    def test_get_onboarding_state_after_profile_update(self, client, db_session, registered_user):
        """Test onboarding state changes after profile update."""
        # Arrange - update profile first
        profile_data = {"handle": "test_handle"}
        client.patch("/api/v1/onboarding/profile", json=profile_data)
        
        # Act
        response = client.get("/api/v1/onboarding/state")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] is False
        assert data["phase"] == 2
        assert data["status"] == OnboardingStatus.INTERESTS_SELECTION

    def test_get_onboarding_state_completed(self, client, db_session, registered_user, seed_interests):
        """Test onboarding state when completed."""
        # Arrange - complete onboarding
        user = db_session.query(User).filter(User.email == "onboarding@example.com").first()
        user.handle = "completed_user"
        user.onboarding_status = OnboardingStatus.COMPLETED
        db_session.commit()
        
        # Act
        response = client.get("/api/v1/onboarding/state")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] is True
        assert data["phase"] is None
        assert data["status"] == OnboardingStatus.COMPLETED

    def test_onboarding_user_not_found(self, client, db_session):
        """Test onboarding endpoints when user doesn't exist."""
        # Override with different user ID that doesn't exist
        different_session = MagicMock()
        different_session.get_user_id.return_value = "non_existent_user"
        
        def override_get_session_not_found():
            return different_session
        
        app.dependency_overrides[get_session] = override_get_session_not_found
        
        # Act
        response = client.get("/api/v1/onboarding/state")
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


class TestCompleteOnboardingFlow:
    """Integration test for complete registration to onboarding flow."""

    @patch('backend.src.services.email_service.EmailService.send_email')
    def test_full_user_journey_registration_to_completion(self, mock_email, client, db_session, seed_interests):
        """Test complete user journey from registration to onboarding completion."""
        # Step 1: Register new user
        user_data = {
            "email": "journey@example.com",
            "name": "Journey User"
        }
        response = client.put("/api/v1/user/register", json=user_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Step 2: Check initial onboarding state
        response = client.get("/api/v1/onboarding/state")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["phase"] == 1
        assert response.json()["completed"] is False
        
        # Step 3: Update profile (Phase 1)
        profile_data = {"handle": "journey_user"}
        response = client.patch("/api/v1/onboarding/profile", json=profile_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["onboarding_status"] == OnboardingStatus.INTERESTS_SELECTION
        
        # Step 4: Check onboarding state after profile update
        response = client.get("/api/v1/onboarding/state")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["phase"] == 2
        assert response.json()["completed"] is False
        
        # Step 5: Update interests (Phase 2)
        interest_data = {"interests": ["technology", "music"]}
        response = client.patch("/api/v1/onboarding/interests", json=interest_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["onboarding_status"] == OnboardingStatus.COMPLETED
        
        # Step 6: Check final onboarding state
        response = client.get("/api/v1/onboarding/state")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["completed"] is True
        assert response.json()["phase"] is None
        
        # Step 7: Verify final database state
        user = db_session.query(User).filter(User.email == "journey@example.com").first()
        assert user is not None
        assert user.handle == "journey_user"
        assert user.onboarding_status == OnboardingStatus.COMPLETED
        
        user_interests = db_session.query(UserInterest).filter(
            UserInterest.user_id == user.id
        ).all()
        assert len(user_interests) == 2
        
        # Verify welcome email was sent
        mock_email.assert_called_once()
