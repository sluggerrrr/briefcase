# Story 3.4: Document Status API

**Epic:** Document Access Control & Lifecycle Management
**Story Points:** 3
**Priority:** Must Have (P0)
**Sprint:** 4

## User Story
**As a** user and system administrator,  
**I want** real-time document status information and tracking,  
**so that** I can monitor document lifecycle, access patterns, and system health with up-to-date status information.

## Description
Create comprehensive API endpoints and services to provide real-time document status information, including lifecycle status, access statistics, system health, and detailed status tracking for both individual documents and system-wide monitoring.

## Acceptance Criteria
1. ⏳ Real-time document status API with lifecycle information
2. ⏳ Document access statistics and usage analytics
3. ⏳ System-wide status dashboard API for administrators
4. ⏳ Document status change tracking and history
5. ⏳ Health check endpoints for document system monitoring
6. ⏳ Status notification webhooks for external integrations
7. ⏳ Bulk status checking for multiple documents
8. ⏳ Status caching and performance optimization
9. ⏳ Real-time status updates via WebSocket (optional)
10. ⏳ Status-based filtering and search capabilities

## Technical Requirements
- FastAPI endpoints with proper authentication and authorization
- Real-time status calculation and caching strategies
- Efficient database queries with proper indexing
- WebSocket support for real-time updates (optional)
- Integration with existing audit logging system
- Comprehensive error handling and validation

## API Endpoints

### Document Status Endpoints
```python
@router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive status information for a document."""
    pass

@router.get("/documents/status/bulk", response_model=List[DocumentStatusResponse])
async def get_bulk_document_status(
    document_ids: List[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get status for multiple documents in a single request."""
    pass

@router.get("/documents/{document_id}/status/history")
async def get_document_status_history(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get status change history for a document."""
    pass

@router.get("/documents/{document_id}/analytics")
async def get_document_analytics(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a document."""
    pass
```

### System Status Endpoints
```python
@router.get("/admin/status/overview")
async def get_system_status_overview(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system-wide document status overview."""
    pass

@router.get("/admin/status/health")
async def get_document_system_health():
    """Health check for document management system."""
    pass

@router.get("/admin/status/metrics")
async def get_system_metrics(
    timeframe: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system metrics for specified timeframe."""
    pass
```

## Response Schemas
```python
class DocumentStatusResponse(BaseModel):
    """Comprehensive document status information."""
    id: str
    title: str
    status: DocumentStatus
    lifecycle_stage: str  # 'active', 'expiring_soon', 'expired', 'deleted'
    
    # Access information
    access_count: int
    last_accessed: Optional[datetime]
    never_accessed: bool
    
    # Lifecycle information
    created_at: datetime
    expires_at: Optional[datetime]
    days_until_expiry: Optional[int]
    is_expired: bool
    
    # Limits and restrictions
    view_limit: Optional[int]
    remaining_views: Optional[int]
    view_limit_exceeded: bool
    
    # Size and storage
    file_size: int
    storage_location: str
    
    # Access control
    sender_email: str
    recipient_email: str
    is_accessible: bool
    
    # System information
    last_status_check: datetime
    status_health: str  # 'healthy', 'warning', 'critical'

class SystemStatusOverview(BaseModel):
    """System-wide status information."""
    total_documents: int
    active_documents: int
    expired_documents: int
    deleted_documents: int
    
    documents_expiring_soon: int  # within 7 days
    documents_never_accessed: int
    documents_over_view_limit: int
    
    total_storage_used: int
    average_document_size: float
    
    last_cleanup_run: Optional[datetime]
    pending_cleanup_items: int
    
    system_health: str  # 'healthy', 'warning', 'critical'
    active_users_24h: int

class DocumentAnalytics(BaseModel):
    """Detailed analytics for a document."""
    document_id: str
    title: str
    
    # Access patterns
    total_accesses: int
    unique_access_days: int
    last_access: Optional[datetime]
    access_frequency: float  # accesses per day
    
    # Time-based metrics
    time_since_creation: timedelta
    time_since_last_access: Optional[timedelta]
    average_time_between_accesses: Optional[timedelta]
    
    # Usage statistics
    peak_access_day: Optional[str]
    access_pattern: str  # 'frequent', 'occasional', 'rare', 'never'
    
    # Lifecycle metrics
    lifecycle_percentage: float  # 0-100% through lifecycle
    predicted_deletion_date: Optional[datetime]
    
    # Audit trail summary
    audit_events_count: int
    security_events_count: int
    last_security_event: Optional[datetime]
```

## Status Calculation Service
```python
class DocumentStatusService:
    @staticmethod
    async def calculate_document_status(document: Document) -> DocumentStatusResponse:
        """Calculate comprehensive status for a document."""
        now = datetime.now()
        
        # Determine lifecycle stage
        lifecycle_stage = DocumentStatusService._get_lifecycle_stage(document, now)
        
        # Calculate access metrics
        access_metrics = await DocumentStatusService._get_access_metrics(document.id)
        
        # Calculate expiry information
        expiry_info = DocumentStatusService._calculate_expiry_info(document, now)
        
        # Determine system health
        health_status = DocumentStatusService._assess_document_health(document, access_metrics)
        
        return DocumentStatusResponse(
            id=document.id,
            title=document.title,
            status=document.status,
            lifecycle_stage=lifecycle_stage,
            **access_metrics,
            **expiry_info,
            file_size=document.file_size,
            storage_location=f"encrypted/{document.id[:2]}/{document.id}",
            sender_email=document.sender.email,
            recipient_email=document.recipient.email,
            is_accessible=document.is_accessible_by_current_time(),
            last_status_check=now,
            status_health=health_status
        )
    
    @staticmethod
    def _get_lifecycle_stage(document: Document, now: datetime) -> str:
        """Determine the current lifecycle stage."""
        if document.status == DocumentStatus.DELETED:
            return 'deleted'
        elif document.status == DocumentStatus.EXPIRED:
            return 'expired'
        elif document.expires_at and (document.expires_at - now).days <= 7:
            return 'expiring_soon'
        else:
            return 'active'
    
    @staticmethod
    async def _get_access_metrics(document_id: str) -> dict:
        """Calculate access-related metrics."""
        access_logs = await db.query(DocumentAccessLog).filter(
            DocumentAccessLog.document_id == document_id,
            DocumentAccessLog.success == "true"
        ).all()
        
        return {
            'access_count': len(access_logs),
            'last_accessed': max([log.accessed_at for log in access_logs], default=None),
            'never_accessed': len(access_logs) == 0
        }
```

## Caching Strategy
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

class DocumentStatusCache:
    CACHE_TTL = 300  # 5 minutes
    
    @staticmethod
    @cache(expire=CACHE_TTL)
    async def get_cached_document_status(document_id: str) -> DocumentStatusResponse:
        """Get cached document status or calculate if not cached."""
        document = await get_document_by_id(document_id)
        return await DocumentStatusService.calculate_document_status(document)
    
    @staticmethod
    async def invalidate_document_cache(document_id: str):
        """Invalidate cache when document is accessed or modified."""
        cache_key = f"document_status:{document_id}"
        await FastAPICache.clear(cache_key)
```

## Real-time Updates (Optional)
```python
from fastapi import WebSocket

class DocumentStatusWebSocket:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast_status_update(self, document_id: str, status_data: dict):
        """Broadcast status updates to connected clients."""
        message = {
            "type": "document_status_update",
            "document_id": document_id,
            "data": status_data
        }
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                await self.disconnect(connection)

@router.websocket("/ws/document-status")
async def document_status_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time status updates."""
    await document_status_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
    except WebSocketDisconnect:
        await document_status_manager.disconnect(websocket)
```

## Webhook System
```python
class StatusWebhookService:
    @staticmethod
    async def trigger_status_webhook(document_id: str, event_type: str, status_data: dict):
        """Trigger webhook for status changes."""
        webhook_url = await get_webhook_url_for_document(document_id)
        if webhook_url:
            payload = {
                "event": event_type,
                "document_id": document_id,
                "timestamp": datetime.now().isoformat(),
                "data": status_data
            }
            
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(webhook_url, json=payload, timeout=10)
                except httpx.TimeoutException:
                    await log_webhook_failure(document_id, "timeout")
```

## Performance Optimization
```python
# Database indexes for efficient status queries
CREATE INDEX idx_documents_status_expires ON documents(status, expires_at);
CREATE INDEX idx_documents_created_status ON documents(created_at, status);
CREATE INDEX idx_access_logs_document_success ON document_access_logs(document_id, success);
CREATE INDEX idx_access_logs_timestamp ON document_access_logs(accessed_at);

# Materialized view for system metrics
CREATE MATERIALIZED VIEW system_metrics_daily AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as documents_created,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_count,
    COUNT(CASE WHEN status = 'expired' THEN 1 END) as expired_count,
    AVG(file_size) as avg_file_size,
    SUM(file_size) as total_storage
FROM documents 
GROUP BY DATE(created_at);
```

## Error Handling
```python
class DocumentStatusError(Exception):
    """Base exception for document status operations."""
    pass

class DocumentNotFoundError(DocumentStatusError):
    """Document not found error."""
    pass

class StatusCalculationError(DocumentStatusError):
    """Error during status calculation."""
    pass

@router.get("/documents/{document_id}/status")
async def get_document_status(document_id: str):
    try:
        status = await DocumentStatusService.get_status(document_id)
        return status
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except StatusCalculationError as e:
        raise HTTPException(status_code=500, detail=f"Status calculation failed: {str(e)}")
```

## Definition of Done
- [ ] All document status API endpoints implemented and tested
- [ ] System-wide status overview provides accurate metrics
- [ ] Status calculation includes all required lifecycle information
- [ ] Caching improves performance for frequently accessed status
- [ ] Bulk status operations handle large requests efficiently
- [ ] Error handling covers all edge cases gracefully
- [ ] Database queries are optimized with proper indexing
- [ ] WebSocket support provides real-time updates (if implemented)
- [ ] Webhook system notifies external services of status changes
- [ ] Admin endpoints provide comprehensive system monitoring

## Blockers/Dependencies
- Story 2.1 (Document Data Models) - Completed
- Story 3.2 (Access Tracking & Audit) - Completed
- Story 3.3 (Automated Lifecycle Management) - Pending
- Redis or similar caching system for performance
- WebSocket support configuration (optional)

## Notes
- Consider rate limiting for status API endpoints
- Plan for monitoring of API performance and usage
- Design status responses for easy frontend consumption
- Consider batch processing for bulk status operations
- Plan for future integration with monitoring systems
- Ensure status calculations remain performant at scale