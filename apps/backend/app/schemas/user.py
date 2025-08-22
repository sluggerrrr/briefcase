"""
User management schemas for Briefcase application.
"""
from pydantic import BaseModel, field_validator
from typing import Optional


class PasswordUpdate(BaseModel):
    """Schema for password update request."""
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password meets minimum requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserStatusUpdate(BaseModel):
    """Schema for updating user account status."""
    is_active: bool