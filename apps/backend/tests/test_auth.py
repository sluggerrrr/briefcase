"""
Authentication tests for Briefcase application.
"""
import pytest
from fastapi import status
from app.core.security import verify_password, get_password_hash, create_access_token, verify_token


class TestPasswordSecurity:
    """Test password hashing and verification."""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed and verified."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Should verify correctly
        assert verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed) is False


class TestJWTTokens:
    """Test JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["type"] == "access"
    
    def test_invalid_token_verification(self):
        """Test that invalid tokens return None."""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)
        assert payload is None


class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_register_new_user(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User registered successfully"
    
    def test_register_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email fails."""
        # Register first user
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Try to register same email again
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "already registered" in data["detail"]
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails."""
        invalid_data = {
            "email": "invalid-email",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_valid_credentials(self, client, test_user_data):
        """Test login with valid credentials."""
        # First register the user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Then login
        response = client.post("/api/v1/auth/login", json=test_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        
        # Check user data
        user_data = data["user"]
        assert user_data["email"] == test_user_data["email"]
        assert user_data["is_active"] is True
        assert "id" in user_data
        assert "password" not in user_data  # Should not include password
        
        # Check token data
        assert data["token_type"] == "bearer"
        assert isinstance(data["expires_in"], int)
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        invalid_data = {
            "email": "nonexistent@briefcase.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=invalid_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Incorrect email or password" in data["detail"]
    
    def test_login_invalid_password(self, client, test_user_data):
        """Test login with wrong password."""
        # First register the user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to login with wrong password
        invalid_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=invalid_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Incorrect email or password" in data["detail"]


class TestProtectedEndpoints:
    """Test protected endpoint access."""
    
    def test_access_protected_endpoint_with_token(self, authenticated_client):
        """Test accessing protected endpoint with valid token."""
        client, token_data = authenticated_client
        
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "email" in data
        assert "id" in data
        assert "is_active" in data
        assert data["is_active"] is True
    
    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token fails."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_access_protected_endpoint_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token fails."""
        client.headers.update({"Authorization": "Bearer invalid.token.here"})
        
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefresh:
    """Test token refresh functionality."""
    
    def test_refresh_valid_token(self, authenticated_client):
        """Test refreshing with valid refresh token."""
        client, token_data = authenticated_client
        
        refresh_data = {"refresh_token": token_data["refresh_token"]}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token fails."""
        refresh_data = {"refresh_token": "invalid.refresh.token"}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    """Test logout functionality."""
    
    def test_logout_authenticated_user(self, authenticated_client):
        """Test logout for authenticated user."""
        client, _ = authenticated_client
        
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully logged out"
    
    def test_logout_unauthenticated_user(self, client):
        """Test logout without authentication fails."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN