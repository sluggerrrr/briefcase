"""
Authentication schemas for Briefcase application.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    """Schema for user registration request."""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None

class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str

class UserResponse(BaseModel):
    """Schema for user response (excludes sensitive data)."""
    id: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class LoginResponse(BaseModel):
    """Schema for login response including user and token."""
    user: UserResponse
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None

class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str