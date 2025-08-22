"""
Permission service for role-based access control.
"""
from typing import List, Optional, Dict, Set
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.permissions import (
    UserRole, UserRoleAssignment, DocumentPermission, 
    PermissionGroup, PermissionGroupMember, PermissionType
)
from app.models.document import Document
from app.models.user import User


class PermissionService:
    """Service for managing user permissions and roles."""
    
    @staticmethod
    def check_document_permission(
        db: Session, 
        user_id: str, 
        document_id: str, 
        permission: str
    ) -> bool:
        """
        Check if user has specific permission on document.
        
        Args:
            db: Database session
            user_id: ID of the user
            document_id: ID of the document
            permission: Permission type to check (read, write, share, delete, admin)
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Check if user is document owner (owners have all permissions)
        document = db.query(Document).filter(Document.id == document_id).first()
        if document and document.sender_id == user_id:
            return True
        
        # Check if user is recipient (recipients have read permission by default)
        if document and document.recipient_id == user_id and permission == "read":
            return True
        
        # Check explicit permissions
        perm = db.query(DocumentPermission).filter(
            and_(
                DocumentPermission.document_id == document_id,
                DocumentPermission.user_id == user_id,
                DocumentPermission.permission_type == permission,
                or_(
                    DocumentPermission.expires_at.is_(None),
                    DocumentPermission.expires_at > datetime.now()
                )
            )
        ).first()
        
        return perm is not None
    
    @staticmethod
    def get_user_roles(db: Session, user_id: str) -> List[str]:
        """
        Get all active roles for a user.
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            List[str]: List of role names
        """
        assignments = db.query(UserRoleAssignment).join(UserRole).filter(
            and_(
                UserRoleAssignment.user_id == user_id,
                or_(
                    UserRoleAssignment.expires_at.is_(None),
                    UserRoleAssignment.expires_at > datetime.now()
                )
            )
        ).all()
        
        return [assignment.role.name for assignment in assignments]
    
    @staticmethod
    def has_role(db: Session, user_id: str, role_name: str) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            db: Database session
            user_id: ID of the user
            role_name: Name of the role to check
            
        Returns:
            bool: True if user has role, False otherwise
        """
        user_roles = PermissionService.get_user_roles(db, user_id)
        return role_name in user_roles or 'admin' in user_roles
    
    @staticmethod
    def grant_document_permission(
        db: Session,
        document_id: str,
        user_id: str,
        permission_type: str,
        granted_by: str,
        expires_at: Optional[datetime] = None
    ) -> DocumentPermission:
        """
        Grant permission to user for document.
        
        Args:
            db: Database session
            document_id: ID of the document
            user_id: ID of the user to grant permission to
            permission_type: Type of permission (read, write, share, delete, admin)
            granted_by: ID of the user granting the permission
            expires_at: Optional expiration datetime
            
        Returns:
            DocumentPermission: The created permission record
            
        Raises:
            ValueError: If permission already exists or invalid permission type
        """
        # Validate permission type
        valid_permissions = [p.value for p in PermissionType]
        if permission_type not in valid_permissions:
            raise ValueError(f"Invalid permission type: {permission_type}")
        
        # Check if permission already exists
        existing = db.query(DocumentPermission).filter(
            and_(
                DocumentPermission.document_id == document_id,
                DocumentPermission.user_id == user_id,
                DocumentPermission.permission_type == permission_type
            )
        ).first()
        
        if existing:
            # Update existing permission
            existing.granted_by = granted_by
            existing.granted_at = datetime.now()
            existing.expires_at = expires_at
            db.commit()
            return existing
        
        # Create new permission
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
    def revoke_document_permission(
        db: Session,
        document_id: str,
        user_id: str,
        permission_type: str
    ) -> bool:
        """
        Revoke permission from user for document.
        
        Args:
            db: Database session
            document_id: ID of the document
            user_id: ID of the user
            permission_type: Type of permission to revoke
            
        Returns:
            bool: True if permission was revoked, False if not found
        """
        permission = db.query(DocumentPermission).filter(
            and_(
                DocumentPermission.document_id == document_id,
                DocumentPermission.user_id == user_id,
                DocumentPermission.permission_type == permission_type
            )
        ).first()
        
        if permission:
            db.delete(permission)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_accessible_documents(db: Session, user_id: str) -> List[Document]:
        """
        Get all documents user has access to.
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            List[Document]: List of accessible documents
        """
        # Documents owned by user
        owned_docs = db.query(Document).filter(Document.sender_id == user_id)
        
        # Documents where user is recipient
        recipient_docs = db.query(Document).filter(Document.recipient_id == user_id)
        
        # Documents with explicit permissions
        permitted_doc_ids = db.query(DocumentPermission.document_id).filter(
            and_(
                DocumentPermission.user_id == user_id,
                DocumentPermission.permission_type.in_(['read', 'write', 'admin']),
                or_(
                    DocumentPermission.expires_at.is_(None),
                    DocumentPermission.expires_at > datetime.now()
                )
            )
        ).distinct()
        
        permitted_docs = db.query(Document).filter(
            Document.id.in_(permitted_doc_ids)
        )
        
        # Combine all queries
        all_docs = owned_docs.union(recipient_docs, permitted_docs).all()
        
        # Remove duplicates and return
        seen = set()
        unique_docs = []
        for doc in all_docs:
            if doc.id not in seen:
                seen.add(doc.id)
                unique_docs.append(doc)
        
        return unique_docs
    
    @staticmethod
    def get_document_permissions(db: Session, document_id: str) -> List[DocumentPermission]:
        """
        Get all permissions for a document.
        
        Args:
            db: Database session
            document_id: ID of the document
            
        Returns:
            List[DocumentPermission]: List of permissions
        """
        return db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id
        ).all()
    
    @staticmethod
    def get_user_permissions_summary(db: Session, user_id: str) -> Dict[str, List[str]]:
        """
        Get summary of user's permissions across all documents.
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            Dict[str, List[str]]: Document ID -> list of permissions
        """
        permissions = db.query(DocumentPermission).filter(
            and_(
                DocumentPermission.user_id == user_id,
                or_(
                    DocumentPermission.expires_at.is_(None),
                    DocumentPermission.expires_at > datetime.now()
                )
            )
        ).all()
        
        summary = {}
        for perm in permissions:
            if perm.document_id not in summary:
                summary[perm.document_id] = []
            summary[perm.document_id].append(perm.permission_type)
        
        # Add owned documents (owners have all permissions)
        owned_docs = db.query(Document).filter(Document.sender_id == user_id).all()
        for doc in owned_docs:
            summary[doc.id] = ['read', 'write', 'share', 'delete', 'admin']
        
        # Add recipient documents (recipients have read permission)
        recipient_docs = db.query(Document).filter(Document.recipient_id == user_id).all()
        for doc in recipient_docs:
            if doc.id not in summary:
                summary[doc.id] = []
            if 'read' not in summary[doc.id]:
                summary[doc.id].append('read')
        
        return summary
    
    @staticmethod
    def assign_user_role(
        db: Session,
        user_id: str,
        role_name: str,
        assigned_by: str,
        expires_at: Optional[datetime] = None
    ) -> UserRoleAssignment:
        """
        Assign role to user.
        
        Args:
            db: Database session
            user_id: ID of the user
            role_name: Name of the role
            assigned_by: ID of the user assigning the role
            expires_at: Optional expiration datetime
            
        Returns:
            UserRoleAssignment: The created assignment
            
        Raises:
            ValueError: If role doesn't exist or assignment already exists
        """
        # Get role
        role = db.query(UserRole).filter(UserRole.name == role_name).first()
        if not role:
            raise ValueError(f"Role not found: {role_name}")
        
        # Check if assignment already exists
        existing = db.query(UserRoleAssignment).filter(
            and_(
                UserRoleAssignment.user_id == user_id,
                UserRoleAssignment.role_id == role.id
            )
        ).first()
        
        if existing:
            # Update existing assignment
            existing.assigned_by = assigned_by
            existing.assigned_at = datetime.now()
            existing.expires_at = expires_at
            db.commit()
            return existing
        
        # Create new assignment
        assignment = UserRoleAssignment(
            user_id=user_id,
            role_id=role.id,
            assigned_by=assigned_by,
            expires_at=expires_at
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment
    
    @staticmethod
    def can_perform_bulk_operation(
        db: Session,
        user_id: str,
        document_ids: List[str],
        operation: str
    ) -> Dict[str, bool]:
        """
        Check if user can perform bulk operation on documents.
        
        Args:
            db: Database session
            user_id: ID of the user
            document_ids: List of document IDs
            operation: Operation type (read, write, share, delete, admin)
            
        Returns:
            Dict[str, bool]: Document ID -> can perform operation
        """
        result = {}
        for doc_id in document_ids:
            result[doc_id] = PermissionService.check_document_permission(
                db, user_id, doc_id, operation
            )
        return result
    
    @staticmethod
    def initialize_default_roles(db: Session) -> None:
        """
        Initialize default system roles.
        
        Args:
            db: Database session
        """
        default_roles = [
            {
                "name": "admin",
                "description": "Full system administration privileges"
            },
            {
                "name": "owner",
                "description": "Document owner with full control"
            },
            {
                "name": "editor",
                "description": "Can view, edit, and share documents"
            },
            {
                "name": "viewer",
                "description": "Can only view documents"
            }
        ]
        
        for role_data in default_roles:
            existing = db.query(UserRole).filter(UserRole.name == role_data["name"]).first()
            if not existing:
                role = UserRole(**role_data)
                db.add(role)
        
        db.commit()