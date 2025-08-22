"""
Lifecycle management models for Briefcase application.
"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class LifecycleConfig(Base):
    """Configuration settings for document lifecycle management."""
    
    __tablename__ = "lifecycle_config"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    setting_name = Column(String(100), nullable=False, unique=True, index=True)
    setting_value = Column(Text, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LifecycleConfig(name={self.setting_name}, value={self.setting_value})>"


class DocumentLifecycleEvent(Base):
    """Lifecycle events for documents (expiration, cleanup, etc.)."""
    
    __tablename__ = "document_lifecycle_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # 'expired', 'cleanup_scheduled', 'permanently_deleted'
    event_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    automated = Column(Boolean, default=True, nullable=False)
    triggered_by = Column(String(36), ForeignKey("users.id"), nullable=True)  # null for automated events
    event_metadata = Column(JSONB, nullable=True)
    
    # Relationships
    document = relationship("Document", backref="lifecycle_events")
    triggered_by_user = relationship("User", foreign_keys=[triggered_by])
    
    def __repr__(self):
        return f"<DocumentLifecycleEvent(doc_id={self.document_id}, type={self.event_type})>"


class CleanupJob(Base):
    """Tracking for cleanup job executions."""
    
    __tablename__ = "cleanup_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String(50), nullable=False, index=True)  # 'document_expiration', 'file_cleanup', 'audit_cleanup'
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default='running', index=True)  # 'running', 'completed', 'failed'
    items_processed = Column(Integer, default=0, nullable=False)
    items_failed = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    event_metadata = Column(JSONB, nullable=True)
    
    def __repr__(self):
        return f"<CleanupJob(type={self.job_type}, status={self.status})>"