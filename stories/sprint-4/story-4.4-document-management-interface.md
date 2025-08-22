# Story 4.4: Document Management Interface with Role-Based Permissions

**Epic:** User Interface & Document Management Dashboard
**Story Points:** 8
**Priority:** Should Have (P1)
**Sprint:** 4

## User Story
**As a** user with different permission levels,  
**I want** advanced document management capabilities with role-based access controls and bulk operations,  
**so that** I can efficiently manage documents according to my permissions while maintaining security and proper access controls.

## Description
Implement a comprehensive document management system that combines backend role-based permissions with an enhanced frontend interface. This includes user roles, document permissions, bulk operations with permission checks, granular sharing controls, and a permission-aware UI that adapts based on user capabilities.

## Acceptance Criteria

### Backend Permission System
1. ⏳ User role system (Owner, Editor, Viewer, Admin)
2. ⏳ Document permission model with granular access controls
3. ⏳ Permission inheritance and sharing rules
4. ⏳ API endpoints with proper permission validation
5. ⏳ Bulk operation permissions and security checks

### Frontend Management Interface
6. ⏳ Permission-aware UI that shows/hides actions based on user roles
7. ⏳ Bulk selection and operations with permission validation
8. ⏳ Advanced search and filtering with access control awareness
9. ⏳ Enhanced sharing interface with granular permission controls
10. ⏳ Document organization features respecting user permissions

## Technical Requirements

### Backend
- FastAPI with dependency injection for permission checks
- SQLAlchemy models for roles, permissions, and document access
- Decorator-based permission validation for API endpoints
- Comprehensive audit logging for permission changes
- Database migrations for new permission tables

### Frontend
- Permission context provider for role-aware components
- TanStack Query with permission-based cache invalidation
- Conditional rendering based on user capabilities
- Enhanced error handling for permission-denied scenarios
- TypeScript interfaces for permission models

## Database Schema Additions

### User Roles and Permissions
```sql
-- User roles
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE, -- 'owner', 'editor', 'viewer', 'admin'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User role assignments
CREATE TABLE user_role_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES user_roles(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(user_id, role_id)
);

-- Document permissions
CREATE TABLE document_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permission_type VARCHAR(20) NOT NULL, -- 'read', 'write', 'share', 'delete', 'admin'
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(document_id, user_id, permission_type)
);

-- Permission groups for bulk sharing
CREATE TABLE permission_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permission_group_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES permission_groups(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, user_id)
);

-- Insert default roles
INSERT INTO user_roles (name, description) VALUES
    ('admin', 'Full system administration privileges'),
    ('owner', 'Document owner with full control'),
    ('editor', 'Can view, edit, and share documents'),
    ('viewer', 'Can only view documents');
```

## Backend Implementation

### Permission Models
```python
# app/models/permissions.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assignments = relationship("UserRoleAssignment", back_populates="role")

class UserRoleAssignment(Base):
    __tablename__ = "user_role_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("user_roles.id"), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("UserRole", back_populates="assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])

class DocumentPermission(Base):
    __tablename__ = "document_permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    permission_type = Column(String(20), nullable=False)  # read, write, share, delete, admin
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    document = relationship("Document")
    user = relationship("User", foreign_keys=[user_id])
    granter = relationship("User", foreign_keys=[granted_by])
```

### Permission Service
```python
# app/services/permissions.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.permissions import UserRole, UserRoleAssignment, DocumentPermission
from app.models.documents import Document
from app.models.users import User

class PermissionService:
    @staticmethod
    async def check_document_permission(
        db: Session, 
        user_id: str, 
        document_id: str, 
        permission: str
    ) -> bool:
        """Check if user has specific permission on document."""
        # Check if user is document owner
        document = db.query(Document).filter(Document.id == document_id).first()
        if document and document.sender_id == user_id:
            return True
        
        # Check explicit permissions
        perm = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
            DocumentPermission.permission_type == permission,
            (DocumentPermission.expires_at.is_(None) | 
             (DocumentPermission.expires_at > datetime.utcnow()))
        ).first()
        
        return perm is not None
    
    @staticmethod
    async def get_user_roles(db: Session, user_id: str) -> List[str]:
        """Get all active roles for a user."""
        assignments = db.query(UserRoleAssignment).join(UserRole).filter(
            UserRoleAssignment.user_id == user_id,
            (UserRoleAssignment.expires_at.is_(None) | 
             (UserRoleAssignment.expires_at > datetime.utcnow()))
        ).all()
        
        return [assignment.role.name for assignment in assignments]
    
    @staticmethod
    async def grant_document_permission(
        db: Session,
        document_id: str,
        user_id: str,
        permission_type: str,
        granted_by: str,
        expires_at: Optional[datetime] = None
    ) -> DocumentPermission:
        """Grant permission to user for document."""
        permission = DocumentPermission(
            document_id=document_id,
            user_id=user_id,
            permission_type=permission_type,
            granted_by=granted_by,
            expires_at=expires_at
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    
    @staticmethod
    async def get_accessible_documents(
        db: Session, 
        user_id: str
    ) -> List[Document]:
        """Get all documents user has access to."""
        # Documents owned by user
        owned_docs = db.query(Document).filter(Document.sender_id == user_id)
        
        # Documents with explicit permissions
        permitted_doc_ids = db.query(DocumentPermission.document_id).filter(
            DocumentPermission.user_id == user_id,
            DocumentPermission.permission_type.in_(['read', 'write', 'admin']),
            (DocumentPermission.expires_at.is_(None) | 
             (DocumentPermission.expires_at > datetime.utcnow()))
        ).subquery()
        
        permitted_docs = db.query(Document).filter(
            Document.id.in_(permitted_doc_ids)
        )
        
        return owned_docs.union(permitted_docs).all()
```

### Permission Decorators
```python
# app/dependencies/permissions.py
from functools import wraps
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.services.permissions import PermissionService

def require_permission(permission_type: str):
    """Decorator to require specific permission on document."""
    def decorator(func):
        @wraps(func)
        async def wrapper(
            document_id: str,
            current_user: User = Depends(get_current_active_user),
            db: Session = Depends(get_db),
            *args,
            **kwargs
        ):
            has_permission = await PermissionService.check_document_permission(
                db, current_user.id, document_id, permission_type
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions: {permission_type} required"
                )
            
            return await func(document_id, current_user, db, *args, **kwargs)
        return wrapper
    return decorator

def require_role(required_role: str):
    """Decorator to require specific user role."""
    def decorator(func):
        @wraps(func)
        async def wrapper(
            current_user: User = Depends(get_current_active_user),
            db: Session = Depends(get_db),
            *args,
            **kwargs
        ):
            user_roles = await PermissionService.get_user_roles(db, current_user.id)
            
            if required_role not in user_roles and 'admin' not in user_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role required: {required_role}"
                )
            
            return await func(current_user, db, *args, **kwargs)
        return wrapper
    return decorator
```

### Enhanced Document APIs
```python
# app/api/v1/documents.py (enhanced)
from app.dependencies.permissions import require_permission, require_role

@router.delete("/documents/{document_id}")
@require_permission("delete")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete document (requires delete permission)."""
    pass

@router.post("/documents/bulk/delete")
async def bulk_delete_documents(
    request: BulkDeleteRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bulk delete documents (checks permissions for each)."""
    results = []
    for doc_id in request.document_ids:
        has_permission = await PermissionService.check_document_permission(
            db, current_user.id, doc_id, "delete"
        )
        if has_permission:
            # Delete document
            results.append({"id": doc_id, "status": "deleted"})
        else:
            results.append({"id": doc_id, "status": "permission_denied"})
    
    return {"results": results}

@router.post("/documents/{document_id}/share")
@require_permission("share")
async def share_document(
    document_id: str,
    request: ShareDocumentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Share document with users (requires share permission)."""
    pass

@router.get("/documents/accessible")
async def get_accessible_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents user has access to."""
    documents = await PermissionService.get_accessible_documents(db, current_user.id)
    return {"documents": documents}

# Permission management endpoints
@router.post("/documents/{document_id}/permissions")
@require_permission("admin")
async def grant_document_permission(
    document_id: str,
    request: GrantPermissionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Grant permission to user for document."""
    pass

@router.get("/documents/{document_id}/permissions")
@require_permission("admin")
async def get_document_permissions(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all permissions for document."""
    pass
```

## Frontend Implementation

### Permission Context
```typescript
// app/contexts/PermissionContext.tsx
import { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

interface UserPermissions {
  roles: string[];
  documentPermissions: Record<string, string[]>; // document_id -> permissions
}

interface PermissionContextType {
  permissions: UserPermissions | null;
  hasRole: (role: string) => boolean;
  hasDocumentPermission: (documentId: string, permission: string) => boolean;
  canPerformBulkOperation: (operation: string, documentIds: string[]) => boolean;
  refreshPermissions: () => Promise<void>;
}

const PermissionContext = createContext<PermissionContextType | undefined>(undefined);

export function PermissionProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [permissions, setPermissions] = useState<UserPermissions | null>(null);

  const hasRole = (role: string) => {
    return permissions?.roles.includes(role) || permissions?.roles.includes('admin') || false;
  };

  const hasDocumentPermission = (documentId: string, permission: string) => {
    return permissions?.documentPermissions[documentId]?.includes(permission) || false;
  };

  const canPerformBulkOperation = (operation: string, documentIds: string[]) => {
    return documentIds.every(id => hasDocumentPermission(id, operation));
  };

  const refreshPermissions = async () => {
    if (!user) return;
    
    try {
      // Fetch user permissions from API
      const response = await fetch('/api/v1/users/me/permissions');
      const data = await response.json();
      setPermissions(data);
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
    }
  };

  useEffect(() => {
    if (user) {
      refreshPermissions();
    }
  }, [user]);

  return (
    <PermissionContext.Provider value={{
      permissions,
      hasRole,
      hasDocumentPermission,
      canPerformBulkOperation,
      refreshPermissions
    }}>
      {children}
    </PermissionContext.Provider>
  );
}

export const usePermissions = () => {
  const context = useContext(PermissionContext);
  if (!context) {
    throw new Error('usePermissions must be used within PermissionProvider');
  }
  return context;
};
```

### Enhanced Document List with Permissions
```typescript
// app/components/dashboard/DocumentList.tsx (enhanced)
import { usePermissions } from '@/contexts/PermissionContext';

export function DocumentList() {
  const { hasDocumentPermission, canPerformBulkOperation } = usePermissions();
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);

  const handleBulkDelete = () => {
    if (!canPerformBulkOperation('delete', selectedDocuments)) {
      toast.error('You do not have permission to delete some selected documents');
      return;
    }
    
    // Proceed with bulk delete
    bulkDeleteMutation.mutate({ document_ids: selectedDocuments });
  };

  return (
    <div className="space-y-4">
      {/* Bulk Actions Toolbar */}
      {selectedDocuments.length > 0 && (
        <BulkActionsToolbar
          selectedCount={selectedDocuments.length}
          onDelete={handleBulkDelete}
          onShare={() => canPerformBulkOperation('share', selectedDocuments)}
          onDownload={() => canPerformBulkOperation('read', selectedDocuments)}
          canDelete={canPerformBulkOperation('delete', selectedDocuments)}
          canShare={canPerformBulkOperation('share', selectedDocuments)}
          canDownload={canPerformBulkOperation('read', selectedDocuments)}
        />
      )}

      {/* Document Cards with Permission-Aware Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {documents?.map((document) => (
          <DocumentCard
            key={document.id}
            document={document}
            isSelected={selectedDocuments.includes(document.id)}
            onSelectionChange={(selected) => {
              if (selected) {
                setSelectedDocuments([...selectedDocuments, document.id]);
              } else {
                setSelectedDocuments(selectedDocuments.filter(id => id !== document.id));
              }
            }}
            canView={hasDocumentPermission(document.id, 'read')}
            canEdit={hasDocumentPermission(document.id, 'write')}
            canShare={hasDocumentPermission(document.id, 'share')}
            canDelete={hasDocumentPermission(document.id, 'delete')}
            canManagePermissions={hasDocumentPermission(document.id, 'admin')}
          />
        ))}
      </div>
    </div>
  );
}
```

### Permission-Aware Document Card
```typescript
// app/components/dashboard/DocumentCard.tsx (enhanced)
interface DocumentCardProps {
  document: Document;
  isSelected: boolean;
  onSelectionChange: (selected: boolean) => void;
  canView: boolean;
  canEdit: boolean;
  canShare: boolean;
  canDelete: boolean;
  canManagePermissions: boolean;
}

export function DocumentCard({
  document,
  isSelected,
  onSelectionChange,
  canView,
  canEdit,
  canShare,
  canDelete,
  canManagePermissions
}: DocumentCardProps) {
  return (
    <Card className={`relative ${isSelected ? 'ring-2 ring-primary' : ''}`}>
      {/* Selection Checkbox */}
      <div className="absolute top-2 left-2 z-10">
        <Checkbox
          checked={isSelected}
          onCheckedChange={onSelectionChange}
          className="bg-background"
        />
      </div>

      <CardContent className="p-4">
        {/* Document Info */}
        <div className="space-y-2">
          <h3 className="font-semibold truncate">{document.title}</h3>
          <p className="text-sm text-muted-foreground">{document.file_name}</p>
          
          {/* Permission Indicators */}
          <div className="flex gap-1">
            {canView && <Badge variant="secondary" className="text-xs">View</Badge>}
            {canEdit && <Badge variant="secondary" className="text-xs">Edit</Badge>}
            {canShare && <Badge variant="secondary" className="text-xs">Share</Badge>}
            {canDelete && <Badge variant="destructive" className="text-xs">Delete</Badge>}
            {canManagePermissions && <Badge variant="default" className="text-xs">Admin</Badge>}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-4">
          {canView && (
            <Button size="sm" variant="outline">
              <Eye className="h-3 w-3 mr-1" />
              View
            </Button>
          )}
          
          {canShare && (
            <Button size="sm" variant="outline">
              <Share className="h-3 w-3 mr-1" />
              Share
            </Button>
          )}

          {canManagePermissions && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button size="sm" variant="outline">
                  <MoreHorizontal className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {canEdit && (
                  <DropdownMenuItem>
                    <Edit className="h-3 w-3 mr-2" />
                    Edit Details
                  </DropdownMenuItem>
                )}
                <DropdownMenuItem>
                  <Settings className="h-3 w-3 mr-2" />
                  Manage Permissions
                </DropdownMenuItem>
                {canDelete && (
                  <DropdownMenuItem className="text-destructive">
                    <Trash className="h-3 w-3 mr-2" />
                    Delete
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

## Definition of Done
- [ ] Backend permission system with roles and document permissions implemented
- [ ] Permission decorators and middleware working correctly
- [ ] Database migrations for permission tables completed
- [ ] Frontend permission context and hooks implemented
- [ ] Permission-aware UI components render correctly based on user capabilities
- [ ] Bulk operations respect permission constraints
- [ ] Enhanced sharing interface with granular permission controls
- [ ] Comprehensive error handling for permission-denied scenarios
- [ ] API endpoints properly validate permissions before operations
- [ ] Audit logging captures all permission changes and access attempts

## Blockers/Dependencies
- Story 4.1 (Authentication UI) - Completed
- Story 4.2 (Document Dashboard) - Completed  
- Story 4.3 (Document Upload Interface) - Completed
- Database migration system for permission tables
- Backend audit logging system enhancement
- Frontend state management for complex permission scenarios

## Future Enhancements
- Advanced role hierarchy and inheritance
- Time-based permissions with automatic expiration
- API rate limiting based on user roles
- Advanced audit dashboard for administrators
- Integration with external identity providers (SSO)
- Fine-grained field-level permissions for document metadata

## Notes
- Permission checks should be performed on both frontend (UX) and backend (security)
- Consider performance implications of permission queries on large datasets
- Plan for permission migration and role assignment workflows
- Design permission UI to be intuitive for non-technical users
- Consider offline permission caching strategies for mobile clients