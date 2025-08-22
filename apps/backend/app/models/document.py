"""
Document model for Briefcase application.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DocumentStatus(enum.Enum):
    """Document status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    VIEW_EXHAUSTED = "view_exhausted"
    DELETED = "deleted"


class Document(Base):
    """Document model for secure document sharing."""
    
    __tablename__ = "documents"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Document metadata
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    
    # Ownership and recipients
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Security parameters
    encrypted_content = Column(Text, nullable=False)  # Base64 encoded encrypted content
    encryption_iv = Column(String(100), nullable=False)  # Base64 encoded initialization vector
    encryption_key_id = Column(String(100), nullable=True)  # Reference to key used for encryption
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    view_limit = Column(Integer, nullable=True, default=None)  # None means unlimited
    access_count = Column(Integer, default=0, nullable=False)
    
    # Status tracking
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.ACTIVE, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete timestamp
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_documents")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_documents")
    
    def calculate_status(self) -> DocumentStatus:
        """
        Calculate the current status of the document based on security parameters.
        
        Returns:
            DocumentStatus: The calculated status of the document
        """
        # If already deleted, return deleted status
        if self.status == DocumentStatus.DELETED or self.deleted_at:
            return DocumentStatus.DELETED
        
        # Check if expired
        if self.expires_at and datetime.now(self.expires_at.tzinfo) > self.expires_at:
            return DocumentStatus.EXPIRED
        
        # Check if view limit exhausted
        if self.view_limit is not None and self.access_count >= self.view_limit:
            return DocumentStatus.VIEW_EXHAUSTED
        
        # Otherwise, document is active
        return DocumentStatus.ACTIVE
    
    def update_status(self):
        """Update the document status based on current state."""
        self.status = self.calculate_status()
    
    def is_accessible_by(self, user_id: str) -> bool:
        """
        Check if a user can access this document.
        
        Args:
            user_id: The ID of the user to check
            
        Returns:
            bool: True if the user can access the document, False otherwise
        """
        # Check if user is sender or recipient
        if user_id not in [self.sender_id, self.recipient_id]:
            return False
        
        # Check if document is still active
        self.update_status()
        return self.status == DocumentStatus.ACTIVE
    
    def increment_access_count(self):
        """Increment the access count and update status."""
        self.access_count += 1
        self.update_status()
    
    def soft_delete(self):
        """Soft delete the document."""
        self.deleted_at = datetime.now(self.created_at.tzinfo)
        self.status = DocumentStatus.DELETED
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, status={self.status.value})>"