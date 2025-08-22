"""
Document lifecycle management service.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.lifecycle import LifecycleConfig, DocumentLifecycleEvent, CleanupJob
from app.models.document_access_log import DocumentAccessLog
import os
import logging

logger = logging.getLogger(__name__)


class LifecycleConfigService:
    """Service for managing lifecycle configuration."""
    
    @staticmethod
    async def get_config_value(setting_name: str, default: str = None) -> str:
        """Get a configuration value by name."""
        db = next(get_db())
        try:
            config = db.query(LifecycleConfig).filter(
                LifecycleConfig.setting_name == setting_name
            ).first()
            return config.setting_value if config else default
        finally:
            db.close()
    
    @staticmethod
    async def get_config_int(setting_name: str, default: int = 0) -> int:
        """Get a configuration value as integer."""
        value = await LifecycleConfigService.get_config_value(setting_name, str(default))
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    async def get_config_bool(setting_name: str, default: bool = False) -> bool:
        """Get a configuration value as boolean."""
        value = await LifecycleConfigService.get_config_value(setting_name, str(default))
        return value.lower() in ('true', '1', 'yes', 'on')
    
    @staticmethod
    async def set_config_value(setting_name: str, value: str, description: str = None):
        """Set a configuration value."""
        db = next(get_db())
        try:
            config = db.query(LifecycleConfig).filter(
                LifecycleConfig.setting_name == setting_name
            ).first()
            
            if config:
                config.setting_value = value
                if description:
                    config.description = description
            else:
                config = LifecycleConfig(
                    setting_name=setting_name,
                    setting_value=value,
                    description=description
                )
                db.add(config)
            
            db.commit()
        finally:
            db.close()


class DocumentLifecycleService:
    """Service for automated document lifecycle management."""
    
    @staticmethod
    async def expire_documents() -> int:
        """Mark expired documents and update their status."""
        job = await DocumentLifecycleService._start_cleanup_job('document_expiration')
        
        try:
            db = next(get_db())
            now = datetime.now()
            expired_count = 0
            
            # Find documents that have passed their expiration date and are still active
            expired_docs = db.query(Document).filter(
                and_(
                    Document.expires_at <= now,
                    Document.status == DocumentStatus.ACTIVE
                )
            ).all()
            
            for doc in expired_docs:
                try:
                    # Update document status
                    doc.status = DocumentStatus.EXPIRED
                    
                    # Log lifecycle event
                    event = DocumentLifecycleEvent(
                        document_id=doc.id,
                        event_type='expired',
                        automated=True,
                        event_metadata={'expiration_date': doc.expires_at.isoformat()}
                    )
                    db.add(event)
                    expired_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to expire document {doc.id}: {e}")
                    job.items_failed += 1
            
            db.commit()
            job.items_processed = expired_count
            await DocumentLifecycleService._complete_cleanup_job(job, 'completed')
            
            logger.info(f"Expired {expired_count} documents")
            return expired_count
            
        except Exception as e:
            await DocumentLifecycleService._complete_cleanup_job(job, 'failed', str(e))
            logger.error(f"Document expiration job failed: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    async def cleanup_deleted_documents() -> int:
        """Permanently delete documents that have been soft-deleted past grace period."""
        job = await DocumentLifecycleService._start_cleanup_job('document_cleanup')
        
        try:
            db = next(get_db())
            grace_period_days = await LifecycleConfigService.get_config_int('cleanup_grace_period_days', 30)
            batch_size = await LifecycleConfigService.get_config_int('cleanup_batch_size', 100)
            
            cutoff_date = datetime.now() - timedelta(days=grace_period_days)
            deleted_count = 0
            
            # Find documents marked as deleted past the grace period
            docs_to_delete = db.query(Document).filter(
                and_(
                    Document.status == DocumentStatus.DELETED,
                    Document.updated_at <= cutoff_date
                )
            ).limit(batch_size).all()
            
            for doc in docs_to_delete:
                try:
                    await DocumentLifecycleService._permanently_delete_document(doc, db)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to permanently delete document {doc.id}: {e}")
                    job.items_failed += 1
            
            db.commit()
            job.items_processed = deleted_count
            await DocumentLifecycleService._complete_cleanup_job(job, 'completed')
            
            logger.info(f"Permanently deleted {deleted_count} documents")
            return deleted_count
            
        except Exception as e:
            await DocumentLifecycleService._complete_cleanup_job(job, 'failed', str(e))
            logger.error(f"Document cleanup job failed: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    async def cleanup_old_audit_logs() -> int:
        """Clean up old audit logs based on retention policy."""
        job = await DocumentLifecycleService._start_cleanup_job('audit_cleanup')
        
        try:
            db = next(get_db())
            retention_days = await LifecycleConfigService.get_config_int('audit_log_retention_days', 2555)  # ~7 years
            batch_size = await LifecycleConfigService.get_config_int('cleanup_batch_size', 100)
            
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0
            
            # Delete old access logs
            old_logs = db.query(DocumentAccessLog).filter(
                DocumentAccessLog.accessed_at <= cutoff_date
            ).limit(batch_size).all()
            
            for log in old_logs:
                try:
                    db.delete(log)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete audit log {log.id}: {e}")
                    job.items_failed += 1
            
            db.commit()
            job.items_processed = deleted_count
            await DocumentLifecycleService._complete_cleanup_job(job, 'completed')
            
            logger.info(f"Cleaned up {deleted_count} old audit logs")
            return deleted_count
            
        except Exception as e:
            await DocumentLifecycleService._complete_cleanup_job(job, 'failed', str(e))
            logger.error(f"Audit cleanup job failed: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    async def _permanently_delete_document(doc: Document, db: Session):
        """Permanently delete a document and its associated data."""
        # Delete associated access logs
        db.query(DocumentAccessLog).filter(
            DocumentAccessLog.document_id == doc.id
        ).delete()
        
        # Delete lifecycle events
        db.query(DocumentLifecycleEvent).filter(
            DocumentLifecycleEvent.document_id == doc.id
        ).delete()
        
        # Log permanent deletion event before deleting the document
        deletion_event = DocumentLifecycleEvent(
            document_id=doc.id,
            event_type='permanently_deleted',
            automated=True,
            event_metadata={
                'original_filename': doc.file_name,
                'file_size': doc.file_size,
                'deletion_date': datetime.now().isoformat()
            }
        )
        db.add(deletion_event)
        db.flush()  # Ensure the event is saved before document deletion
        
        # Delete encrypted file from filesystem if it exists
        if hasattr(doc, 'encrypted_content_path') and doc.encrypted_content_path:
            try:
                if os.path.exists(doc.encrypted_content_path):
                    os.remove(doc.encrypted_content_path)
                    logger.info(f"Deleted encrypted file: {doc.encrypted_content_path}")
            except Exception as e:
                logger.warning(f"Failed to delete encrypted file {doc.encrypted_content_path}: {e}")
        
        # Finally delete the document record
        db.delete(doc)
    
    @staticmethod
    async def _start_cleanup_job(job_type: str) -> CleanupJob:
        """Start tracking a cleanup job."""
        db = next(get_db())
        try:
            job = CleanupJob(
                job_type=job_type,
                status='running'
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            return job
        finally:
            db.close()
    
    @staticmethod
    async def _complete_cleanup_job(job: CleanupJob, status: str, error_message: str = None):
        """Complete tracking a cleanup job."""
        db = next(get_db())
        try:
            # Refetch job to ensure we have the latest version
            job = db.query(CleanupJob).filter(CleanupJob.id == job.id).first()
            if job:
                job.status = status
                job.completed_at = datetime.now()
                if error_message:
                    job.error_message = error_message
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    async def get_documents_expiring_soon(days: int = 7) -> List[Document]:
        """Get documents expiring within specified days."""
        db = next(get_db())
        try:
            future_date = datetime.now() + timedelta(days=days)
            now = datetime.now()
            
            return db.query(Document).filter(
                and_(
                    Document.expires_at <= future_date,
                    Document.expires_at > now,
                    Document.status == DocumentStatus.ACTIVE
                )
            ).all()
        finally:
            db.close()
    
    @staticmethod
    async def get_lifecycle_statistics() -> Dict[str, Any]:
        """Get statistics about document lifecycle."""
        db = next(get_db())
        try:
            stats = {}
            
            # Document counts by status
            status_counts = db.query(
                Document.status, func.count(Document.id)
            ).group_by(Document.status).all()
            
            stats['documents_by_status'] = {status: count for status, count in status_counts}
            
            # Documents expiring soon
            stats['expiring_soon'] = len(await DocumentLifecycleService.get_documents_expiring_soon(7))
            
            # Recent cleanup job stats
            recent_jobs = db.query(CleanupJob).filter(
                CleanupJob.started_at >= datetime.now() - timedelta(days=7)
            ).all()
            
            stats['recent_jobs'] = {
                'total': len(recent_jobs),
                'completed': len([j for j in recent_jobs if j.status == 'completed']),
                'failed': len([j for j in recent_jobs if j.status == 'failed']),
                'running': len([j for j in recent_jobs if j.status == 'running'])
            }
            
            return stats
            
        finally:
            db.close()


# Initialize default configuration values
async def initialize_lifecycle_config():
    """Initialize default lifecycle configuration values."""
    defaults = [
        ('cleanup_grace_period_days', '30', 'Days to wait before permanent deletion'),
        ('notification_days_before_expiry', '7,1', 'Days before expiry to send notifications'),
        ('audit_log_retention_days', '2555', 'Days to retain audit logs (7 years)'),
        ('cleanup_batch_size', '100', 'Number of items to process per cleanup batch'),
        ('enable_expiration_notifications', 'true', 'Whether to send expiration notifications')
    ]
    
    for name, value, description in defaults:
        existing_config = await LifecycleConfigService.get_config_value(name)
        if not existing_config:
            await LifecycleConfigService.set_config_value(name, value, description)
            logger.info(f"Initialized config: {name} = {value}")