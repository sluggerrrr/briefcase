"""
User management endpoints for Briefcase application.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse, MessageResponse
from app.schemas.user import PasswordUpdate
from app.api.dependencies import get_current_user
from app.core.security import verify_password, get_password_hash

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
    return [UserResponse.model_validate(user) for user in users]

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    """
    return UserResponse.model_validate(current_user)

@router.put("/me/password", response_model=MessageResponse)
def update_password(
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's password.
    Requires current password verification.
    """
    # Verify current password
    if not verify_password(password_update.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_update.new_password)
    db.commit()
    
    return MessageResponse(message="Password updated successfully")