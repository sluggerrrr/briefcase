"""
Permission dependencies for FastAPI routes.
"""
from functools import wraps
from typing import Any, Callable
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_active_user
from app.api.dependencies import get_db
from app.models.user import User
from app.services.permission_service import PermissionService


def require_permission(permission_type: str):
    """
    Decorator to require specific permission on document.
    
    Args:
        permission_type: The permission type required (read, write, share, delete, admin)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            document_id: str,
            current_user: User = Depends(get_current_active_user),
            db: Session = Depends(get_db),
            *args,
            **kwargs
        ) -> Any:
            has_permission = PermissionService.check_document_permission(
                db, current_user.id, document_id, permission_type
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {permission_type} permission required for this document"
                )
            
            return await func(document_id, current_user, db, *args, **kwargs)
        return wrapper
    return decorator


def require_role(required_role: str):
    """
    Decorator to require specific user role.
    
    Args:
        required_role: The role name required
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            current_user: User = Depends(get_current_active_user),
            db: Session = Depends(get_db),
            *args,
            **kwargs
        ) -> Any:
            if not PermissionService.has_role(db, current_user.id, required_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {required_role}"
                )
            
            return await func(current_user, db, *args, **kwargs)
        return wrapper
    return decorator


async def get_admin_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current user and verify admin role.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User: The current user (verified as admin)
        
    Raises:
        HTTPException: If user is not admin
    """
    if not PermissionService.has_role(db, current_user.id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required"
        )
    return current_user


async def check_document_permission_dependency(
    document_id: str,
    permission_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> bool:
    """
    Dependency to check document permission.
    
    Args:
        document_id: ID of the document
        permission_type: Permission type to check
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        bool: True if user has permission
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    has_permission = PermissionService.check_document_permission(
        db, current_user.id, document_id, permission_type
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions: {permission_type} permission required"
        )
    
    return True


def require_document_access(permission_type: str = "read"):
    """
    FastAPI dependency factory for document access checks.
    
    Args:
        permission_type: Permission type required (default: read)
        
    Returns:
        FastAPI dependency function
    """
    def dependency(
        document_id: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> tuple[str, User, Session]:
        """Check permission and return validated parameters."""
        has_permission = PermissionService.check_document_permission(
            db, current_user.id, document_id, permission_type
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission_type} permission required"
            )
        
        return document_id, current_user, db
    
    return dependency


def require_bulk_permission(permission_type: str):
    """
    Dependency factory for bulk operations with permission checks.
    
    Args:
        permission_type: Permission type required for each document
        
    Returns:
        FastAPI dependency function
    """
    def dependency(
        document_ids: list[str],
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> tuple[list[str], User, Session]:
        """Check permissions for all documents."""
        permission_results = PermissionService.can_perform_bulk_operation(
            db, current_user.id, document_ids, permission_type
        )
        
        # Check if user has permission for all documents
        denied_documents = [
            doc_id for doc_id, has_perm in permission_results.items() 
            if not has_perm
        ]
        
        if denied_documents:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for documents: {', '.join(denied_documents)}"
            )
        
        return document_ids, current_user, db
    
    return dependency