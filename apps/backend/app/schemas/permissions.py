"""
Permission schemas for API request/response models.
"""
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class UserRoleSchema(BaseModel):
    """Schema for user role."""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserRoleAssignmentSchema(BaseModel):
    """Schema for user role assignment."""
    id: str
    user_id: str
    role_id: str
    assigned_by: Optional[str] = None
    assigned_at: datetime
    expires_at: Optional[datetime] = None
    role: Optional[UserRoleSchema] = None
    
    class Config:
        from_attributes = True


class DocumentPermissionSchema(BaseModel):
    """Schema for document permission."""
    id: str
    document_id: str
    user_id: str
    permission_type: str
    granted_by: Optional[str] = None
    granted_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PermissionGroupSchema(BaseModel):
    """Schema for permission group."""
    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PermissionGroupMemberSchema(BaseModel):
    """Schema for permission group member."""
    id: str
    group_id: str
    user_id: str
    added_at: datetime
    added_by: Optional[str] = None
    
    class Config:
        from_attributes = True


# Request schemas
class GrantPermissionRequest(BaseModel):
    """Request to grant document permission."""
    user_id: str = Field(..., description="ID of user to grant permission to")
    permission_type: str = Field(..., description="Type of permission (read, write, share, delete, admin)")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration datetime")


class RevokePermissionRequest(BaseModel):
    """Request to revoke document permission."""
    user_id: str = Field(..., description="ID of user to revoke permission from")
    permission_type: str = Field(..., description="Type of permission to revoke")


class BulkPermissionRequest(BaseModel):
    """Request for bulk permission operations."""
    document_ids: List[str] = Field(..., description="List of document IDs")
    user_id: str = Field(..., description="ID of user for permission operation")
    permission_type: str = Field(..., description="Type of permission")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration datetime")


class AssignRoleRequest(BaseModel):
    """Request to assign role to user."""
    user_id: str = Field(..., description="ID of user to assign role to")
    role_name: str = Field(..., description="Name of role to assign")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration datetime")


class CreatePermissionGroupRequest(BaseModel):
    """Request to create permission group."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    member_user_ids: List[str] = Field(default=[], description="Initial members of the group")


class UpdatePermissionGroupRequest(BaseModel):
    """Request to update permission group."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="New name for the group")
    description: Optional[str] = Field(None, max_length=500, description="New description")


class AddGroupMembersRequest(BaseModel):
    """Request to add members to permission group."""
    user_ids: List[str] = Field(..., description="List of user IDs to add to group")


class BulkDeleteRequest(BaseModel):
    """Request for bulk document deletion."""
    document_ids: List[str] = Field(..., description="List of document IDs to delete")


class BulkShareRequest(BaseModel):
    """Request for bulk document sharing."""
    document_ids: List[str] = Field(..., description="List of document IDs to share")
    recipient_ids: List[str] = Field(..., description="List of recipient user IDs")
    permission_type: str = Field(default="read", description="Permission type to grant")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration datetime")


class BulkDownloadRequest(BaseModel):
    """Request for bulk document download."""
    document_ids: List[str] = Field(..., description="List of document IDs to download")


# Response schemas
class UserPermissionSummary(BaseModel):
    """Summary of user's permissions."""
    user_id: str
    roles: List[str] = Field(description="List of user's role names")
    document_permissions: Dict[str, List[str]] = Field(description="Document ID -> list of permissions")


class DocumentPermissionSummary(BaseModel):
    """Summary of document's permissions."""
    document_id: str
    owner_id: str
    recipient_id: str
    permissions: List[DocumentPermissionSchema] = Field(description="List of explicit permissions")


class BulkOperationResult(BaseModel):
    """Result of bulk operation."""
    document_id: str
    status: str = Field(description="Operation status: success, failed, permission_denied")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class BulkOperationResponse(BaseModel):
    """Response for bulk operations."""
    total_documents: int = Field(description="Total number of documents in request")
    successful: int = Field(description="Number of successful operations")
    failed: int = Field(description="Number of failed operations")
    results: List[BulkOperationResult] = Field(description="Detailed results for each document")


class PermissionCheckRequest(BaseModel):
    """Request to check permissions."""
    document_ids: List[str] = Field(..., description="List of document IDs to check")
    permission_type: str = Field(..., description="Permission type to check")


class PermissionCheckResult(BaseModel):
    """Result of permission check."""
    document_id: str
    has_permission: bool
    reason: Optional[str] = Field(None, description="Reason if permission denied")


class PermissionCheckResponse(BaseModel):
    """Response for permission checks."""
    user_id: str
    permission_type: str
    results: List[PermissionCheckResult] = Field(description="Results for each document")


class SystemPermissionOverview(BaseModel):
    """System-wide permission overview for administrators."""
    total_users: int
    total_documents: int
    total_permissions: int
    users_by_role: Dict[str, int] = Field(description="Role name -> user count")
    permissions_by_type: Dict[str, int] = Field(description="Permission type -> count")
    active_permission_groups: int
    recent_permission_changes: int = Field(description="Permission changes in last 24 hours")