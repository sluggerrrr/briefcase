"""
User management tests for Briefcase application.
"""
import pytest
from fastapi import status
from app.core.security import get_password_hash


class TestUserProfile:
    """Test user profile endpoints."""
    
    def test_get_current_user_profile(self, authenticated_client):
        """Test getting current user profile."""
        client, token_data = authenticated_client
        
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert "id" in data
        assert "is_active" in data
        assert data["email"] == "test@briefcase.com"
    
    def test_get_profile_unauthenticated(self, client):
        """Test getting profile without authentication fails."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserListing:
    """Test user listing endpoint."""
    
    def test_list_users_authenticated(self, authenticated_client, db_session):
        """Test listing users when authenticated."""
        client, _ = authenticated_client
        
        # Create additional test users
        from app.models.user import User
        test_users = [
            User(email="user1@test.com", password_hash=get_password_hash("pass1"), is_active=True),
            User(email="user2@test.com", password_hash=get_password_hash("pass2"), is_active=True),
            User(email="inactive@test.com", password_hash=get_password_hash("pass3"), is_active=False)
        ]
        for user in test_users:
            db_session.add(user)
        db_session.commit()
        
        response = client.get("/api/v1/users/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # Should return only active users
        emails = [user["email"] for user in data]
        assert "test@briefcase.com" in emails
        assert "user1@test.com" in emails
        assert "user2@test.com" in emails
        assert "inactive@test.com" not in emails  # Inactive user should not be included
    
    def test_list_users_unauthenticated(self, client):
        """Test listing users without authentication fails."""
        response = client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPasswordUpdate:
    """Test password update functionality."""
    
    def test_update_password_success(self, authenticated_client, db_session):
        """Test successful password update."""
        client, _ = authenticated_client
        
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword456"
        }
        
        response = client.put("/api/v1/users/me/password", json=password_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password updated successfully"
        
        # Verify can log in with new password
        login_data = {
            "email": "test@briefcase.com",
            "password": "newpassword456"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
    
    def test_update_password_wrong_current(self, authenticated_client):
        """Test password update with wrong current password fails."""
        client, _ = authenticated_client
        
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword456"
        }
        
        response = client.put("/api/v1/users/me/password", json=password_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Current password is incorrect" in data["detail"]
    
    def test_update_password_weak_new(self, authenticated_client):
        """Test password update with weak new password fails."""
        client, _ = authenticated_client
        
        password_data = {
            "current_password": "testpassword123",
            "new_password": "short"
        }
        
        response = client.put("/api/v1/users/me/password", json=password_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert any("at least 8 characters" in str(error) for error in data["detail"])
    
    def test_update_password_unauthenticated(self, client):
        """Test password update without authentication fails."""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword456"
        }
        
        response = client.put("/api/v1/users/me/password", json=password_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserRegistrationValidation:
    """Test user registration validation (already tested in test_auth.py, but adding specific cases)."""
    
    def test_register_with_weak_password(self, client):
        """Test registration with password validation."""
        user_data = {
            "email": "newuser@briefcase.com",
            "password": "123"  # Too short
        }
        
        # Currently no password strength validation on registration
        # This could be added as an enhancement
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # For now, this will succeed as we don't have password strength validation on registration
        # Adding a note that this could be enhanced
        assert response.status_code == status.HTTP_200_OK
        
    def test_register_with_valid_email_formats(self, client):
        """Test registration with various valid email formats."""
        valid_emails = [
            "user+tag@briefcase.com",
            "first.last@briefcase.com",
            "user123@briefcase.com"
        ]
        
        for idx, email in enumerate(valid_emails):
            user_data = {
                "email": email,
                "password": f"testpassword{idx}"
            }
            
            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == status.HTTP_200_OK