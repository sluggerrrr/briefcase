# Story 3.3: Automated Lifecycle Management

**Epic:** Document Access Control & Lifecycle Management
**Story Points:** 5
**Priority:** Must Have (P0)
**Sprint:** 4

## User Story
**As a** system administrator and document owner,  
**I want** automated document lifecycle management with expiration and cleanup,  
**so that** documents are automatically managed according to security policies without manual intervention.

## Description
Implement automated background processes to manage document lifecycles including automatic expiration, cleanup of expired documents, notification systems, and scheduled maintenance tasks to ensure compliance with security policies and storage optimization.

## Acceptance Criteria
1. ⏳ Automated document expiration based on configured expiration dates
2. ⏳ Background cleanup process for expired documents with soft delete
3. ⏳ Scheduled cleanup of permanently deleted documents (hard delete after grace period)
4. ⏳ Notification system for document owners before expiration
5. ⏳ Cleanup of orphaned files and database records
6. ⏳ Automated audit log cleanup with configurable retention
7. ⏳ Storage optimization and file system cleanup
8. ⏳ Health monitoring and reporting for lifecycle processes
9. ⏳ Configurable grace periods and cleanup schedules
10. ⏳ Admin interface for monitoring and manual intervention

## Technical Requirements
- FastAPI background tasks and scheduler integration
- Database cleanup procedures with transaction safety
- File system cleanup with proper error handling
- Email/notification system integration
- Configurable scheduling (cron-like functionality)
- Monitoring and logging for all automated processes

## Background Processes

### Document Expiration Process
```python
# Scheduled task to run every hour
@scheduler.scheduled_job('interval', hours=1)
async def expire_documents():
    """Mark documents as expired when expiration date is reached."""
    expired_docs = await get_expired_documents()
    for doc in expired_docs:
        await mark_document_expired(doc.id)
        await log_expiration_event(doc.id)
        await notify_document_owner(doc)
```

### Cleanup Process
```python
# Scheduled task to run daily at 2 AM
@scheduler.scheduled_job('cron', hour=2)
async def cleanup_deleted_documents():
    """Permanently delete documents marked for deletion after grace period."""
    grace_period = timedelta(days=30)  # configurable
    old_deleted_docs = await get_documents_deleted_before(
        datetime.now() - grace_period
    )
    for doc in old_deleted_docs:
        await permanently_delete_document(doc.id)
        await cleanup_document_files(doc.encrypted_content_path)
```

## Database Schema Additions
```sql
-- Lifecycle management configuration
CREATE TABLE lifecycle_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_name VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document lifecycle events
CREATE TABLE document_lifecycle_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    event_type VARCHAR(50) NOT NULL, -- 'expired', 'cleanup_scheduled', 'permanently_deleted'
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    automated BOOLEAN DEFAULT TRUE,
    triggered_by UUID REFERENCES users(id), -- null for automated events
    metadata JSONB
);

-- Cleanup job tracking
CREATE TABLE cleanup_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL, -- 'document_expiration', 'file_cleanup', 'audit_cleanup'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL, -- 'running', 'completed', 'failed'
    items_processed INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB
);

-- Insert default configuration
INSERT INTO lifecycle_config (setting_name, setting_value, description) VALUES
    ('cleanup_grace_period_days', '30', 'Days to wait before permanent deletion'),
    ('notification_days_before_expiry', '7,1', 'Days before expiry to send notifications'),
    ('audit_log_retention_days', '2555', 'Days to retain audit logs (7 years)'),
    ('cleanup_batch_size', '100', 'Number of items to process per cleanup batch'),
    ('enable_expiration_notifications', 'true', 'Whether to send expiration notifications');
```

## API Endpoints
```python
# Admin endpoints for lifecycle management
@router.get("/admin/lifecycle/status")
async def get_lifecycle_status():
    """Get status of all lifecycle processes."""
    pass

@router.post("/admin/lifecycle/run-cleanup")
async def trigger_manual_cleanup():
    """Manually trigger cleanup processes."""
    pass

@router.get("/admin/lifecycle/config")
async def get_lifecycle_config():
    """Get lifecycle configuration settings."""
    pass

@router.put("/admin/lifecycle/config")
async def update_lifecycle_config():
    """Update lifecycle configuration settings."""
    pass

@router.get("/admin/lifecycle/jobs")
async def get_cleanup_job_history():
    """Get history of cleanup jobs."""
    pass
```

## Notification System
```python
class DocumentNotificationService:
    async def send_expiration_warnings(self):
        """Send warnings before document expiration."""
        warning_days = await get_notification_days()
        for days in warning_days:
            docs_expiring = await get_documents_expiring_in_days(days)
            for doc in docs_expiring:
                await send_expiration_warning(doc, days)
    
    async def send_expiration_notification(self, document):
        """Send notification when document expires."""
        await send_email(
            to=document.sender.email,
            subject=f"Document '{document.title}' has expired",
            template="document_expired",
            context={"document": document}
        )
```

## Scheduler Configuration
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# Job store configuration
jobstores = {
    'default': SQLAlchemyJobStore(url=database_url)
}

scheduler = AsyncIOScheduler(jobstores=jobstores)

# Scheduled jobs
@scheduler.scheduled_job('interval', minutes=30, id='expire_documents')
async def expire_documents_job():
    await DocumentLifecycleService.expire_documents()

@scheduler.scheduled_job('cron', hour=2, id='cleanup_deleted_documents')
async def cleanup_deleted_documents_job():
    await DocumentLifecycleService.cleanup_deleted_documents()

@scheduler.scheduled_job('cron', hour=1, id='send_expiration_warnings')
async def send_expiration_warnings_job():
    await DocumentNotificationService.send_expiration_warnings()

@scheduler.scheduled_job('cron', hour=3, day_of_week=0, id='cleanup_audit_logs')
async def cleanup_audit_logs_job():
    await DocumentLifecycleService.cleanup_old_audit_logs()
```

## Services Implementation
```python
class DocumentLifecycleService:
    @staticmethod
    async def expire_documents():
        """Mark expired documents and update status."""
        now = datetime.now()
        expired_docs = await db.query(Document).filter(
            Document.expires_at <= now,
            Document.status == DocumentStatus.ACTIVE
        ).all()
        
        for doc in expired_docs:
            doc.status = DocumentStatus.EXPIRED
            await DocumentLifecycleService.log_lifecycle_event(
                doc.id, 'expired', automated=True
            )
        
        await db.commit()
        return len(expired_docs)
    
    @staticmethod
    async def cleanup_deleted_documents():
        """Permanently delete documents after grace period."""
        grace_period = await get_config_value('cleanup_grace_period_days', 30)
        cutoff_date = datetime.now() - timedelta(days=grace_period)
        
        docs_to_delete = await db.query(Document).filter(
            Document.status == DocumentStatus.DELETED,
            Document.updated_at <= cutoff_date
        ).all()
        
        for doc in docs_to_delete:
            await DocumentLifecycleService.permanently_delete_document(doc)
        
        return len(docs_to_delete)
```

## Monitoring and Health Checks
```python
@router.get("/health/lifecycle")
async def lifecycle_health_check():
    """Health check for lifecycle processes."""
    last_expiration_job = await get_last_cleanup_job('document_expiration')
    last_cleanup_job = await get_last_cleanup_job('file_cleanup')
    
    return {
        "status": "healthy",
        "last_expiration_check": last_expiration_job.completed_at if last_expiration_job else None,
        "last_cleanup_run": last_cleanup_job.completed_at if last_cleanup_job else None,
        "pending_expirations": await count_documents_expiring_soon(),
        "pending_cleanup": await count_documents_pending_cleanup()
    }
```

## Configuration Management
- Environment variables for scheduling intervals
- Database configuration for grace periods and thresholds
- Feature flags for enabling/disabling specific lifecycle processes
- Admin interface for real-time configuration updates

## Error Handling and Recovery
- Transactional cleanup operations to prevent partial failures
- Retry logic for failed operations with exponential backoff
- Dead letter queues for permanently failed operations
- Comprehensive logging for troubleshooting and auditing

## Performance Considerations
- Batch processing for large cleanup operations
- Database indexing on expiration and deletion dates
- Async processing to avoid blocking the main application
- Configurable batch sizes to manage database load

## Definition of Done
- [ ] Document expiration process runs automatically
- [ ] Cleanup processes safely remove expired documents
- [ ] Notification system sends timely expiration warnings
- [ ] Admin interface allows monitoring and configuration
- [ ] All processes have comprehensive error handling
- [ ] Health checks monitor lifecycle process status
- [ ] Database cleanup maintains referential integrity
- [ ] File system cleanup removes orphaned files
- [ ] Performance remains good with large document volumes
- [ ] All lifecycle events are properly audited

## Blockers/Dependencies
- Story 2.1 (Document Data Models) - Completed
- Story 2.2 (AES Encryption Implementation) - Completed
- Story 3.2 (Access Tracking & Audit) - Completed
- Email/notification service configuration
- Task scheduler setup (APScheduler or similar)

## Notes
- Consider using Celery for more complex job scheduling needs
- Plan for monitoring integration (Prometheus, etc.)
- Ensure compliance with data retention regulations
- Design for horizontal scaling of background processes
- Consider timezone handling for scheduled operations