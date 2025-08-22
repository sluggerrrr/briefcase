"""
Permission management API endpoints.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.dependencies import get_current_active_user
from app.dependencies.permissions import get_admin_user, require_permission, require_document_access
from app.models.user import User
from app.services.permission_service import PermissionService
from app.schemas.permissions import (
    UserPermissionSummary,
    DocumentPermissionSummary,
    GrantPermissionRequest,
    RevokePermissionRequest,
    BulkPermissionRequest,
    AssignRoleRequest,
    CreatePermissionGroupRequest,
    UpdatePermissionGroupRequest,
    AddGroupMembersRequest,
    PermissionCheckRequest,
    PermissionCheckResponse,
    PermissionCheckResult,
    SystemPermissionOverview,
    UserRoleSchema,
    DocumentPermissionSchema,
    PermissionGroupSchema
)

router = APIRouter()


# User Permission Management
@router.get("/users/me/permissions", response_model=UserPermissionSummary)
async def get_my_permissions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's permissions summary."""
    roles = PermissionService.get_user_roles(db, current_user.id)
    document_permissions = PermissionService.get_user_permissions_summary(db, current_user.id)
    
    return UserPermissionSummary(
        user_id=current_user.id,
        roles=roles,
        document_permissions=document_permissions
    )


@router.get("/users/{user_id}/permissions", response_model=UserPermissionSummary)
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user's permissions summary (admin only)."""
    roles = PermissionService.get_user_roles(db, user_id)
    document_permissions = PermissionService.get_user_permissions_summary(db, user_id)
    
    return UserPermissionSummary(
        user_id=user_id,
        roles=roles,
        document_permissions=document_permissions
    )


# Document Permission Management
@router.get("/documents/{document_id}/permissions", response_model=DocumentPermissionSummary)
async def get_document_permissions(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get document's permissions (requires admin permission on document)."""
    # Check if user has admin permission on document
    if not PermissionService.check_document_permission(db, current_user.id, document_id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required to view document permissions"
        )
    
    from app.models.document import Document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    permissions = PermissionService.get_document_permissions(db, document_id)
    
    return DocumentPermissionSummary(
        document_id=document_id,
        owner_id=document.sender_id,
        recipient_id=document.recipient_id,
        permissions=[DocumentPermissionSchema.from_orm(p) for p in permissions]
    )


@router.post("/documents/{document_id}/permissions")
async def grant_document_permission(
    document_id: str,
    request: GrantPermissionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Grant permission to user for document (requires admin permission)."""
    # Check if user has admin permission on document
    if not PermissionService.check_document_permission(db, current_user.id, document_id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required to grant document permissions"
        )
    
    try:
        permission = PermissionService.grant_document_permission(
            db=db,
            document_id=document_id,
            user_id=request.user_id,
            permission_type=request.permission_type,
            granted_by=current_user.id,
            expires_at=request.expires_at
        )
        
        return {"message": "Permission granted successfully", "permission_id": permission.id}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/documents/{document_id}/permissions")
async def revoke_document_permission(
    document_id: str,
    request: RevokePermissionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Revoke permission from user for document (requires admin permission)."""
    # Check if user has admin permission on document
    if not PermissionService.check_document_permission(db, current_user.id, document_id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required to revoke document permissions"
        )
    
    success = PermissionService.revoke_document_permission(
        db=db,
        document_id=document_id,
        user_id=request.user_id,
        permission_type=request.permission_type
    )
    
    if success:
        return {"message": "Permission revoked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )


# Bulk Permission Operations
@router.post("/documents/bulk/permissions/grant")
async def bulk_grant_permissions(
    request: BulkPermissionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Grant permission to user for multiple documents."""
    results = []
    
    for doc_id in request.document_ids:
        try:
            # Check if user has admin permission on document
            if not PermissionService.check_document_permission(db, current_user.id, doc_id, "admin"):
                results.append({
                    "document_id": doc_id,
                    "status": "permission_denied",
                    "error": "Admin permission required"
                })
                continue
            
            permission = PermissionService.grant_document_permission(
                db=db,
                document_id=doc_id,
                user_id=request.user_id,
                permission_type=request.permission_type,
                granted_by=current_user.id,
                expires_at=request.expires_at
            )
            
            results.append({
                "document_id": doc_id,
                "status": "success",
                "permission_id": permission.id
            })
            
        except Exception as e:
            results.append({
                "document_id": doc_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {"results": results}


@router.post("/permissions/check", response_model=PermissionCheckResponse)
async def check_permissions(
    request: PermissionCheckRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check permissions for multiple documents."""
    results = []
    
    for doc_id in request.document_ids:
        has_permission = PermissionService.check_document_permission(
            db, current_user.id, doc_id, request.permission_type
        )
        
        result = PermissionCheckResult(
            document_id=doc_id,
            has_permission=has_permission,
            reason=None if has_permission else f"User lacks {request.permission_type} permission"
        )
        results.append(result)
    
    return PermissionCheckResponse(
        user_id=current_user.id,
        permission_type=request.permission_type,
        results=results
    )


# Role Management
@router.get("/roles", response_model=List[UserRoleSchema])
async def list_roles(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all available roles (admin only)."""
    from app.models.permissions import UserRole
    roles = db.query(UserRole).all()
    return [UserRoleSchema.from_orm(role) for role in roles]


@router.post("/users/{user_id}/roles")
async def assign_role(
    user_id: str,
    request: AssignRoleRequest,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Assign role to user (admin only)."""
    try:
        assignment = PermissionService.assign_user_role(
            db=db,
            user_id=request.user_id,
            role_name=request.role_name,
            assigned_by=current_user.id,
            expires_at=request.expires_at
        )
        
        return {"message": "Role assigned successfully", "assignment_id": assignment.id}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Permission Groups
@router.get("/groups", response_model=List[PermissionGroupSchema])
async def list_permission_groups(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List permission groups owned by current user."""
    from app.models.permissions import PermissionGroup
    groups = db.query(PermissionGroup).filter(
        PermissionGroup.owner_id == current_user.id
    ).all()
    return [PermissionGroupSchema.from_orm(group) for group in groups]


@router.post("/groups", response_model=PermissionGroupSchema)
async def create_permission_group(
    request: CreatePermissionGroupRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new permission group."""
    from app.models.permissions import PermissionGroup, PermissionGroupMember
    
    # Create group
    group = PermissionGroup(
        name=request.name,
        description=request.description,
        owner_id=current_user.id
    )
    db.add(group)
    db.flush()  # Get the ID
    
    # Add members
    for user_id in request.member_user_ids:
        member = PermissionGroupMember(
            group_id=group.id,
            user_id=user_id,
            added_by=current_user.id
        )
        db.add(member)
    
    db.commit()
    db.refresh(group)
    
    return PermissionGroupSchema.from_orm(group)


# System Overview (Admin only)
@router.get("/admin/overview", response_model=SystemPermissionOverview)
async def get_system_permission_overview(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system-wide permission overview (admin only)."""
    from app.models.permissions import UserRole, UserRoleAssignment, DocumentPermission, PermissionGroup
    from app.models.user import User
    from app.models.document import Document
    from datetime import datetime, timedelta
    
    # Basic counts
    total_users = db.query(User).count()
    total_documents = db.query(Document).count()
    total_permissions = db.query(DocumentPermission).count()
    active_permission_groups = db.query(PermissionGroup).count()
    
    # Users by role
    users_by_role = {}
    roles = db.query(UserRole).all()
    for role in roles:
        count = db.query(UserRoleAssignment).filter(
            UserRoleAssignment.role_id == role.id
        ).count()
        users_by_role[role.name] = count
    
    # Permissions by type
    permissions_by_type = {}
    permission_types = ["read", "write", "share", "delete", "admin"]
    for perm_type in permission_types:
        count = db.query(DocumentPermission).filter(
            DocumentPermission.permission_type == perm_type
        ).count()
        permissions_by_type[perm_type] = count
    
    # Recent permission changes (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    recent_permission_changes = db.query(DocumentPermission).filter(
        DocumentPermission.granted_at >= yesterday
    ).count()
    
    return SystemPermissionOverview(
        total_users=total_users,
        total_documents=total_documents,
        total_permissions=total_permissions,
        users_by_role=users_by_role,
        permissions_by_type=permissions_by_type,
        active_permission_groups=active_permission_groups,
        recent_permission_changes=recent_permission_changes
    )