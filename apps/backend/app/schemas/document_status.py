"""
Document status API schemas for Briefcase application.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class LifecycleStage(str, Enum):
    """Document lifecycle stages."""
    active = "active"
    expiring_soon = "expiring_soon"
    expired = "expired"
    deleted = "deleted"


class StatusHealth(str, Enum):
    """Health status levels."""
    healthy = "healthy"
    warning = "warning"
    critical = "critical"


class AccessPattern(str, Enum):
    """Access pattern classifications."""
    never = "never"
    rare = "rare"
    occasional = "occasional"
    frequent = "frequent"


class DocumentStatusResponse(BaseModel):
    """Comprehensive document status information."""
    id: str
    title: str
    status: str
    lifecycle_stage: LifecycleStage
    
    # Access information
    access_count: int
    last_accessed: Optional[datetime] = None
    never_accessed: bool
    
    # Lifecycle information
    created_at: datetime
    expires_at: Optional[datetime] = None
    days_until_expiry: Optional[int] = None
    is_expired: bool
    
    # Limits and restrictions
    view_limit: Optional[int] = None
    remaining_views: Optional[int] = None
    view_limit_exceeded: bool
    
    # Size and storage
    file_size: int
    storage_location: str
    
    # Access control
    sender_email: Optional[str] = None
    recipient_email: Optional[str] = None
    is_accessible: bool
    
    # System information
    last_status_check: datetime
    status_health: StatusHealth


class DocumentStatusHistoryResponse(BaseModel):
    """Document status change history."""
    document_id: str
    title: str
    status_changes: List[Dict[str, Any]]
    lifecycle_events: List[Dict[str, Any]]


class DocumentAnalyticsResponse(BaseModel):
    """Detailed analytics for a document."""
    document_id: str
    title: str
    
    # Access patterns
    total_accesses: int
    unique_access_days: int
    last_access: Optional[datetime] = None
    access_frequency: float = Field(..., description="Accesses per day")
    
    # Time-based metrics
    time_since_creation: timedelta
    time_since_last_access: Optional[timedelta] = None
    average_time_between_accesses: Optional[timedelta] = None
    
    # Usage statistics
    peak_access_day: Optional[str] = None
    access_pattern: AccessPattern
    
    # Lifecycle metrics
    lifecycle_percentage: float = Field(..., ge=0, le=100, description="Percentage through lifecycle")
    predicted_deletion_date: Optional[datetime] = None
    
    # Audit trail summary
    audit_events_count: int
    security_events_count: int
    last_security_event: Optional[datetime] = None


class SystemStatusOverview(BaseModel):
    """System-wide status information."""
    total_documents: int
    active_documents: int
    expired_documents: int
    deleted_documents: int
    
    documents_expiring_soon: int = Field(..., description="Documents expiring within 7 days")
    documents_never_accessed: int
    documents_over_view_limit: int
    
    total_storage_used: int = Field(..., description="Total storage in bytes")
    average_document_size: float = Field(..., description="Average document size in bytes")
    
    last_cleanup_run: Optional[datetime] = None
    pending_cleanup_items: int
    
    system_health: StatusHealth
    active_users_24h: int
    status_breakdown: Dict[str, int] = Field(..., description="Document counts by status")


class SystemMetricsResponse(BaseModel):
    """System metrics for specified timeframe."""
    timeframe: str
    period_start: datetime
    period_end: datetime
    
    # Document metrics
    documents_created: int
    total_accesses: int
    failed_accesses: int
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    
    # User metrics
    unique_active_users: int
    average_accesses_per_user: float
    
    # Storage metrics
    storage_added_bytes: int
    average_document_size: float
    
    # System metrics
    lifecycle_events: int
    cleanup_jobs_successful: int
    cleanup_jobs_failed: int
    system_uptime_percentage: float = Field(..., ge=0, le=100)


class BulkStatusRequest(BaseModel):
    """Request for bulk document status check."""
    document_ids: List[str] = Field(..., max_items=100, description="List of document IDs (max 100)")
    include_analytics: bool = Field(False, description="Include analytics data")


class BulkStatusResponse(BaseModel):
    """Response for bulk document status check."""
    results: List[DocumentStatusResponse]
    total_requested: int
    total_found: int
    not_found_ids: List[str]
    processing_time_ms: int


class DocumentStatusFilters(BaseModel):
    """Filters for document status queries."""
    status: Optional[str] = None
    lifecycle_stage: Optional[LifecycleStage] = None
    sender_email: Optional[str] = None
    recipient_email: Optional[str] = None
    expires_before: Optional[datetime] = None
    expires_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    created_after: Optional[datetime] = None
    min_file_size: Optional[int] = None
    max_file_size: Optional[int] = None
    never_accessed: Optional[bool] = None
    over_view_limit: Optional[bool] = None
    health_status: Optional[StatusHealth] = None


class StatusWebhookPayload(BaseModel):
    """Webhook payload for status changes."""
    event: str = Field(..., description="Event type (status_changed, expired, etc.)")
    document_id: str
    timestamp: datetime
    data: Dict[str, Any] = Field(..., description="Status data")


class DocumentHealthCheck(BaseModel):
    """Health check for individual document."""
    document_id: str
    title: str
    health_status: StatusHealth
    issues: List[str] = Field(default_factory=list, description="List of identified issues")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions")


class SystemHealthCheck(BaseModel):
    """Comprehensive system health check."""
    overall_status: StatusHealth
    timestamp: datetime
    components: Dict[str, StatusHealth] = Field(..., description="Health status of system components")
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Component details
    database_status: StatusHealth
    storage_status: StatusHealth
    cleanup_status: StatusHealth
    api_status: StatusHealth


class StatusCacheInfo(BaseModel):
    """Information about status caching."""
    cache_enabled: bool
    cache_ttl_seconds: int
    cache_hit_rate: float = Field(..., ge=0, le=100, description="Cache hit rate percentage")
    total_cache_entries: int


class PerformanceMetrics(BaseModel):
    """API performance metrics."""
    endpoint: str
    average_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    total_requests: int
    error_rate: float = Field(..., ge=0, le=100)
    requests_per_minute: float