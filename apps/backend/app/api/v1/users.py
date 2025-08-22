"""
User management endpoints for Briefcase application.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all active users for recipient selection.
    Only returns basic user information (no sensitive data).
    """
    users = db.query(User).filter(User.is_active == True).all()
    return [UserResponse.from_orm(user) for user in users]

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    """
    return UserResponse.from_orm(current_user)