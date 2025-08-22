"""
Lifecycle management schemas for Briefcase application.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobType(str, Enum):
    """Available cleanup job types."""
    expire_documents = "expire_documents"
    cleanup_deleted_documents = "cleanup_deleted_documents"
    cleanup_audit_logs = "cleanup_audit_logs"


class JobStatus(str, Enum):
    """Cleanup job status options."""
    running = "running"
    completed = "completed"
    failed = "failed"


class ScheduledJobInfo(BaseModel):
    """Information about a scheduled job."""
    id: str
    name: str
    next_run: Optional[str] = None
    trigger: str


class CleanupJobResponse(BaseModel):
    """Response schema for cleanup job information."""
    id: str
    job_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    items_processed: int
    items_failed: int
    error_message: Optional[str] = None


class LifecycleConfigResponse(BaseModel):
    """Response schema for lifecycle configuration."""
    id: str
    setting_name: str
    setting_value: str
    description: Optional[str] = None
    updated_at: datetime


class LifecycleConfigUpdate(BaseModel):
    """Request schema for updating lifecycle configuration."""
    setting_value: str = Field(..., description="New configuration value")
    description: Optional[str] = Field(None, description="Optional description of the setting")


class LifecycleStatusResponse(BaseModel):
    """Comprehensive lifecycle system status."""
    scheduler_running: bool
    scheduled_jobs: List[ScheduledJobInfo]
    recent_jobs: List[CleanupJobResponse]
    statistics: Dict[str, Any]


class ManualCleanupRequest(BaseModel):
    """Request schema for manually triggering cleanup jobs."""
    job_type: JobType = Field(..., description="Type of cleanup job to run")


class ManualCleanupResponse(BaseModel):
    """Response schema for manual cleanup trigger."""
    job_type: str
    triggered_at: datetime
    items_processed: int
    success: bool


class DocumentLifecycleEventResponse(BaseModel):
    """Response schema for document lifecycle events."""
    id: str
    document_id: str
    event_type: str
    event_timestamp: datetime
    automated: bool
    triggered_by: Optional[str] = None
    event_metadata: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


class LifecycleStatistics(BaseModel):
    """Statistics about document lifecycle."""
    documents_by_status: Dict[str, int]
    expiring_soon: int
    recent_jobs: Dict[str, int]