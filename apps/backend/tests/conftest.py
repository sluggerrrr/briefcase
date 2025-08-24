"""
Test configuration and fixtures for Briefcase application.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

# Mock JSONB to use Text for SQLite compatibility before any imports
import sqlalchemy.dialects.postgresql

class MockJSONB(Text):
    """Mock JSONB that behaves like Text for SQLite compatibility."""
    def __init__(self, *args, **kwargs):
        super().__init__()
    
    def bind_processor(self, dialect):
        """Process values before binding to SQL."""
        import json
        def process(value):
            if value is None:
                return None
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            return str(value)
        return process
    
    def result_processor(self, dialect, coltype):
        """Process values after retrieving from SQL."""
        import json
        def process(value):
            if value is None:
                return None
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return process

sqlalchemy.dialects.postgresql.JSONB = MockJSONB

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with clean database."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data for registration/login."""
    return {
        "name": "Test User",
        "email": "test@briefcase.com",
        "password": "testpassword123"
    }


@pytest.fixture
def authenticated_client(client, test_user_data, db_session):
    """Create an authenticated client with a registered user."""
    # Register user
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 200
    
    # Login user
    response = client.post("/api/v1/auth/login", json=test_user_data)
    assert response.status_code == 200
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # Add auth header to client
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    return client, token_data