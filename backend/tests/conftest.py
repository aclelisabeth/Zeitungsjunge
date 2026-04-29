"""Test fixtures and setup for backend tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure we import models before creating tables
from backend.app.main import app
from backend.app.db.database import Base, get_db
from backend.app.models.models import User  # Important: Import all models
from backend.app.utils.security import hash_password

# Use in-memory SQLite for tests with proper pooling
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Use StaticPool for in-memory DB - all connections share same data
    echo=False
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables once at module load time
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def db():
    """Provide access to test database."""
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user_creds():
    """Create a test user via registration API with unique credentials."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    email = f"testuser_{unique_id}@example.com"
    username = f"testuser_{unique_id}"
    
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "full_name": "Test User",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200, f"Failed to register: {response.json()}"
    data = response.json()
    return {
        "username": username,
        "password": "TestPass123",
        "token": data["access_token"],
        "user": data["user"]  # Already have user info from response
    }


@pytest.fixture
def test_user_token(test_user_creds):
    """Get auth token for test user."""
    return test_user_creds["token"]


@pytest.fixture  
def test_user(test_user_creds):
    """Get test user object (from API response)."""
    # Create a simple object with the user data
    class UserObj:
        pass
    user = UserObj()
    for key, value in test_user_creds["user"].items():
        setattr(user, key, value)
    return user
