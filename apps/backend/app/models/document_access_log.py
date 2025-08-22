"""
Document access log model for Briefcase application.
"""
import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AccessAction(enum.Enum):
    """Document access action types."""
    VIEW = "view"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    DELETE = "delete"
    UPDATE = "update"
    ACCESS_DENIED = "access_denied"


class DocumentAccessLog(Base):
    """Log model for tracking all document access attempts."""
    
    __tablename__ = "document_access_logs"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Document and user references
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Access details
    action = Column(SQLEnum(AccessAction), nullable=False, index=True)
    success = Column(String(5), nullable=False, default="true")  # "true" or "false" as string for compatibility
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Error details (if access was denied)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    accessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    document = relationship("Document", backref="access_logs")
    user = relationship("User", backref="document_access_logs")
    
    def __repr__(self):
        return f"<DocumentAccessLog(id={self.id}, action={self.action.value}, success={self.success})>"