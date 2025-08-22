"""
Permission models for role-based access control in Briefcase application.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PermissionType(enum.Enum):
    """Document permission types."""
    READ = "read"
    WRITE = "write"
    SHARE = "share"
    DELETE = "delete"
    ADMIN = "admin"


class UserRole(Base):
    """User roles for system-wide permissions."""
    
    __tablename__ = "user_roles"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Role details
    name = Column(String(50), unique=True, nullable=False, index=True)  # 'owner', 'editor', 'viewer', 'admin'
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    assignments = relationship("UserRoleAssignment", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserRole(id={self.id}, name={self.name})>"


class UserRoleAssignment(Base):
    """Assignment of roles to users."""
    
    __tablename__ = "user_role_assignments"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("user_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Assignment details
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("UserRole", back_populates="assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='uq_user_role'),)
    
    def is_active(self) -> bool:
        """Check if role assignment is currently active."""
        if self.expires_at is None:
            return True
        return datetime.now(self.expires_at.tzinfo) < self.expires_at
    
    def __repr__(self):
        return f"<UserRoleAssignment(user_id={self.user_id}, role={self.role.name if self.role else 'Unknown'})>"


class DocumentPermission(Base):
    """Granular permissions for documents."""
    
    __tablename__ = "document_permissions"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Foreign keys
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    granted_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Permission details
    permission_type = Column(String(20), nullable=False, index=True)  # read, write, share, delete, admin
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document = relationship("Document")
    user = relationship("User", foreign_keys=[user_id])
    granter = relationship("User", foreign_keys=[granted_by])
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('document_id', 'user_id', 'permission_type', name='uq_document_user_permission'),)
    
    def is_active(self) -> bool:
        """Check if permission is currently active."""
        if self.expires_at is None:
            return True
        return datetime.now(self.expires_at.tzinfo) < self.expires_at
    
    def __repr__(self):
        return f"<DocumentPermission(document_id={self.document_id}, user_id={self.user_id}, permission={self.permission_type})>"


class PermissionGroup(Base):
    """Permission groups for bulk sharing and management."""
    
    __tablename__ = "permission_groups"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Group details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    owner = relationship("User")
    members = relationship("PermissionGroupMember", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PermissionGroup(id={self.id}, name={self.name}, owner_id={self.owner_id})>"


class PermissionGroupMember(Base):
    """Members of permission groups."""
    
    __tablename__ = "permission_group_members"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Foreign keys
    group_id = Column(String(36), ForeignKey("permission_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Member details
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    added_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    group = relationship("PermissionGroup", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    adder = relationship("User", foreign_keys=[added_by])
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('group_id', 'user_id', name='uq_group_user'),)
    
    def __repr__(self):
        return f"<PermissionGroupMember(group_id={self.group_id}, user_id={self.user_id})>"