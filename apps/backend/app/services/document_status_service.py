"""
Document status calculation and analytics service.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.document_access_log import DocumentAccessLog, AccessAction
from app.models.lifecycle import DocumentLifecycleEvent, CleanupJob
from app.models.user import User


class DocumentStatusService:
    """Service for calculating comprehensive document status and analytics."""
    
    @staticmethod
    async def calculate_document_status(document: Document, db: Session = None) -> Dict[str, Any]:
        """Calculate comprehensive status for a document."""
        if db is None:
            db = next(get_db())
        
        now = datetime.now(timezone.utc)
        
        try:
            # Get access metrics
            access_metrics = await DocumentStatusService._get_access_metrics(document.id, db)
            
            # Calculate lifecycle information
            lifecycle_info = DocumentStatusService._calculate_lifecycle_info(document, now)
            
            # Calculate view limit information
            view_limit_info = DocumentStatusService._calculate_view_limit_info(document, access_metrics['access_count'])
            
            # Calculate expiry information
            expiry_info = DocumentStatusService._calculate_expiry_info(document, now)
            
            # Determine system health
            health_status = DocumentStatusService._assess_document_health(document, access_metrics, expiry_info)
            
            # Get sender and recipient info
            sender = db.query(User).filter(User.id == document.sender_id).first()
            recipient = db.query(User).filter(User.id == document.recipient_id).first()
            
            return {
                'id': document.id,
                'title': document.title,
                'status': document.status.value,
                'lifecycle_stage': lifecycle_info['lifecycle_stage'],
                
                # Access information
                'access_count': access_metrics['access_count'],
                'last_accessed': access_metrics['last_accessed'],
                'never_accessed': access_metrics['never_accessed'],
                
                # Lifecycle information
                'created_at': document.created_at,
                'expires_at': document.expires_at,
                'days_until_expiry': expiry_info['days_until_expiry'],
                'is_expired': expiry_info['is_expired'],
                
                # View limits
                'view_limit': document.view_limit,
                'remaining_views': view_limit_info['remaining_views'],
                'view_limit_exceeded': view_limit_info['view_limit_exceeded'],
                
                # Size and storage
                'file_size': document.file_size,
                'storage_location': f"encrypted/{document.id[:2]}/{document.id}",
                
                # Access control
                'sender_email': sender.email if sender else None,
                'recipient_email': recipient.email if recipient else None,
                'is_accessible': DocumentStatusService._is_document_accessible(document, now),
                
                # System information
                'last_status_check': now,
                'status_health': health_status
            }
        finally:
            if db:
                db.close()
    
    @staticmethod
    async def calculate_document_analytics(document: Document, db: Session = None) -> Dict[str, Any]:
        """Calculate detailed analytics for a document."""
        if db is None:
            db = next(get_db())
        
        now = datetime.now(timezone.utc)
        
        try:
            # Get all access logs for this document
            access_logs = db.query(DocumentAccessLog).filter(
                and_(
                    DocumentAccessLog.document_id == document.id,
                    DocumentAccessLog.success == "true"
                )
            ).order_by(DocumentAccessLog.accessed_at).all()
            
            # Calculate time-based metrics
            time_metrics = DocumentStatusService._calculate_time_metrics(document, access_logs, now)
            
            # Calculate access patterns
            access_patterns = DocumentStatusService._analyze_access_patterns(access_logs)
            
            # Calculate lifecycle metrics
            lifecycle_metrics = DocumentStatusService._calculate_lifecycle_metrics(document, now)
            
            # Get audit events count
            audit_events = db.query(DocumentLifecycleEvent).filter(
                DocumentLifecycleEvent.document_id == document.id
            ).count()
            
            security_events = db.query(DocumentAccessLog).filter(
                and_(
                    DocumentAccessLog.document_id == document.id,
                    DocumentAccessLog.success == "false"
                )
            ).count()
            
            last_security_event = db.query(DocumentAccessLog).filter(
                and_(
                    DocumentAccessLog.document_id == document.id,
                    DocumentAccessLog.success == "false"
                )
            ).order_by(DocumentAccessLog.accessed_at.desc()).first()
            
            return {
                'document_id': document.id,
                'title': document.title,
                
                # Access patterns
                'total_accesses': len(access_logs),
                'unique_access_days': access_patterns['unique_access_days'],
                'last_access': access_logs[-1].accessed_at if access_logs else None,
                'access_frequency': access_patterns['access_frequency'],
                
                # Time-based metrics
                'time_since_creation': time_metrics['time_since_creation'],
                'time_since_last_access': time_metrics['time_since_last_access'],
                'average_time_between_accesses': access_patterns['avg_time_between_accesses'],
                
                # Usage statistics
                'peak_access_day': access_patterns['peak_access_day'],
                'access_pattern': access_patterns['pattern_classification'],
                
                # Lifecycle metrics
                'lifecycle_percentage': lifecycle_metrics['lifecycle_percentage'],
                'predicted_deletion_date': lifecycle_metrics['predicted_deletion_date'],
                
                # Audit trail
                'audit_events_count': audit_events,
                'security_events_count': security_events,
                'last_security_event': last_security_event.accessed_at if last_security_event else None
            }
        finally:
            if db:
                db.close()
    
    @staticmethod
    async def get_system_status_overview(db: Session = None) -> Dict[str, Any]:
        """Get comprehensive system-wide status overview."""
        if db is None:
            db = next(get_db())
        
        try:
            now = datetime.now(timezone.utc)
            
            # Document counts by status
            status_counts = db.query(
                Document.status, func.count(Document.id)
            ).group_by(Document.status).all()
            
            status_dict = {status.value: count for status, count in status_counts}
            total_documents = sum(status_dict.values())
            
            # Documents expiring soon (within 7 days)
            expiring_soon = db.query(Document).filter(
                and_(
                    Document.status == DocumentStatus.ACTIVE,
                    Document.expires_at.isnot(None),
                    Document.expires_at <= now + timedelta(days=7),
                    Document.expires_at > now
                )
            ).count()
            
            # Never accessed documents
            never_accessed_subquery = db.query(DocumentAccessLog.document_id).filter(
                DocumentAccessLog.success == "true"
            ).distinct().subquery()
            
            never_accessed = db.query(Document).filter(
                and_(
                    Document.status == DocumentStatus.ACTIVE,
                    ~Document.id.in_(func.select(never_accessed_subquery.c.document_id))
                )
            ).count()
            
            # Documents over view limit
            over_view_limit = db.query(Document).filter(
                and_(
                    Document.view_limit.isnot(None),
                    Document.access_count >= Document.view_limit
                )
            ).count()
            
            # Storage metrics
            storage_stats = db.query(
                func.sum(Document.file_size).label('total_storage'),
                func.avg(Document.file_size).label('avg_size')
            ).first()
            
            # Last cleanup job
            last_cleanup = db.query(CleanupJob).filter(
                CleanupJob.status == 'completed'
            ).order_by(CleanupJob.completed_at.desc()).first()
            
            # Pending cleanup items (soft deleted documents)
            pending_cleanup = db.query(Document).filter(
                Document.status == DocumentStatus.DELETED
            ).count()
            
            # Active users in last 24 hours
            active_users_24h = db.query(DocumentAccessLog.user_id).filter(
                DocumentAccessLog.accessed_at >= now - timedelta(hours=24)
            ).distinct().count()
            
            # Determine system health
            system_health = DocumentStatusService._assess_system_health(
                total_documents, expiring_soon, never_accessed, pending_cleanup
            )
            
            return {
                'total_documents': total_documents,
                'active_documents': status_dict.get('ACTIVE', 0),
                'expired_documents': status_dict.get('EXPIRED', 0),
                'deleted_documents': status_dict.get('DELETED', 0),
                
                'documents_expiring_soon': expiring_soon,
                'documents_never_accessed': never_accessed,
                'documents_over_view_limit': over_view_limit,
                
                'total_storage_used': int(storage_stats.total_storage or 0),
                'average_document_size': float(storage_stats.avg_size or 0),
                
                'last_cleanup_run': last_cleanup.completed_at if last_cleanup else None,
                'pending_cleanup_items': pending_cleanup,
                
                'system_health': system_health,
                'active_users_24h': active_users_24h,
                
                'status_breakdown': status_dict
            }
        finally:
            if db:
                db.close()
    
    @staticmethod
    async def get_system_metrics(timeframe: str = "24h", db: Session = None) -> Dict[str, Any]:
        """Get system metrics for specified timeframe."""
        if db is None:
            db = next(get_db())
        
        try:
            now = datetime.now(timezone.utc)
            
            # Parse timeframe
            timeframe_map = {
                '1h': timedelta(hours=1),
                '24h': timedelta(hours=24),
                '7d': timedelta(days=7),
                '30d': timedelta(days=30)
            }
            
            time_delta = timeframe_map.get(timeframe, timedelta(hours=24))
            start_time = now - time_delta
            
            # Document creation metrics
            documents_created = db.query(Document).filter(
                Document.created_at >= start_time
            ).count()
            
            # Access metrics
            total_accesses = db.query(DocumentAccessLog).filter(
                and_(
                    DocumentAccessLog.accessed_at >= start_time,
                    DocumentAccessLog.success == "true"
                )
            ).count()
            
            unique_users = db.query(DocumentAccessLog.user_id).filter(
                DocumentAccessLog.accessed_at >= start_time
            ).distinct().count()
            
            # Error metrics
            failed_accesses = db.query(DocumentAccessLog).filter(
                and_(
                    DocumentAccessLog.accessed_at >= start_time,
                    DocumentAccessLog.success == "false"
                )
            ).count()
            
            # Storage metrics
            storage_added = db.query(func.sum(Document.file_size)).filter(
                Document.created_at >= start_time
            ).scalar() or 0
            
            # Lifecycle events
            lifecycle_events = db.query(DocumentLifecycleEvent).filter(
                DocumentLifecycleEvent.event_timestamp >= start_time
            ).count()
            
            # Cleanup job metrics
            cleanup_jobs = db.query(CleanupJob).filter(
                CleanupJob.started_at >= start_time
            ).all()
            
            successful_jobs = len([j for j in cleanup_jobs if j.status == 'completed'])
            failed_jobs = len([j for j in cleanup_jobs if j.status == 'failed'])
            
            return {
                'timeframe': timeframe,
                'period_start': start_time,
                'period_end': now,
                
                # Document metrics
                'documents_created': documents_created,
                'total_accesses': total_accesses,
                'failed_accesses': failed_accesses,
                'success_rate': (total_accesses / max(total_accesses + failed_accesses, 1)) * 100,
                
                # User metrics
                'unique_active_users': unique_users,
                'average_accesses_per_user': total_accesses / max(unique_users, 1),
                
                # Storage metrics
                'storage_added_bytes': int(storage_added),
                'average_document_size': storage_added / max(documents_created, 1),
                
                # System metrics
                'lifecycle_events': lifecycle_events,
                'cleanup_jobs_successful': successful_jobs,
                'cleanup_jobs_failed': failed_jobs,
                'system_uptime_percentage': 99.9  # Placeholder - would be calculated from actual monitoring
            }
        finally:
            if db:
                db.close()
    
    # Helper methods
    @staticmethod
    async def _get_access_metrics(document_id: str, db: Session) -> Dict[str, Any]:
        """Calculate access-related metrics."""
        access_logs = db.query(DocumentAccessLog).filter(
            and_(
                DocumentAccessLog.document_id == document_id,
                DocumentAccessLog.success == "true"
            )
        ).all()
        
        return {
            'access_count': len(access_logs),
            'last_accessed': max([log.accessed_at for log in access_logs], default=None),
            'never_accessed': len(access_logs) == 0
        }
    
    @staticmethod
    def _calculate_lifecycle_info(document: Document, now: datetime) -> Dict[str, str]:
        """Determine the current lifecycle stage."""
        if document.status == DocumentStatus.DELETED:
            lifecycle_stage = 'deleted'
        elif document.status == DocumentStatus.EXPIRED:
            lifecycle_stage = 'expired'
        elif document.expires_at and (document.expires_at - now).days <= 7:
            lifecycle_stage = 'expiring_soon'
        else:
            lifecycle_stage = 'active'
        
        return {'lifecycle_stage': lifecycle_stage}
    
    @staticmethod
    def _calculate_view_limit_info(document: Document, access_count: int) -> Dict[str, Any]:
        """Calculate view limit related information."""
        if document.view_limit is None:
            return {
                'remaining_views': None,
                'view_limit_exceeded': False
            }
        
        remaining = max(0, document.view_limit - access_count)
        exceeded = access_count >= document.view_limit
        
        return {
            'remaining_views': remaining,
            'view_limit_exceeded': exceeded
        }
    
    @staticmethod
    def _calculate_expiry_info(document: Document, now: datetime) -> Dict[str, Any]:
        """Calculate expiry-related information."""
        if document.expires_at is None:
            return {
                'days_until_expiry': None,
                'is_expired': False
            }
        
        time_diff = document.expires_at - now
        days_until_expiry = time_diff.days if time_diff.total_seconds() > 0 else 0
        is_expired = now >= document.expires_at
        
        return {
            'days_until_expiry': days_until_expiry,
            'is_expired': is_expired
        }
    
    @staticmethod
    def _is_document_accessible(document: Document, now: datetime) -> bool:
        """Determine if document is currently accessible."""
        if document.status != DocumentStatus.ACTIVE:
            return False
        
        if document.expires_at and now >= document.expires_at:
            return False
        
        if document.view_limit and document.access_count >= document.view_limit:
            return False
        
        return True
    
    @staticmethod
    def _assess_document_health(document: Document, access_metrics: Dict, expiry_info: Dict) -> str:
        """Assess the health status of a document."""
        if document.status == DocumentStatus.DELETED:
            return 'critical'
        
        if expiry_info['is_expired']:
            return 'critical'
        
        if expiry_info['days_until_expiry'] is not None and expiry_info['days_until_expiry'] <= 1:
            return 'warning'
        
        # TODO: Fix timezone issue - can't subtract offset-naive and offset-aware datetimes
        if access_metrics['never_accessed'] and (datetime.now() - document.created_at).days > 7:
            return 'warning'
        
        return 'healthy'
    
    @staticmethod
    def _assess_system_health(total_docs: int, expiring_soon: int, never_accessed: int, pending_cleanup: int) -> str:
        """Assess overall system health."""
        if total_docs == 0:
            return 'healthy'
        
        expiring_ratio = expiring_soon / total_docs
        never_accessed_ratio = never_accessed / total_docs
        
        if expiring_ratio > 0.2 or never_accessed_ratio > 0.3 or pending_cleanup > 100:
            return 'critical'
        elif expiring_ratio > 0.1 or never_accessed_ratio > 0.15 or pending_cleanup > 50:
            return 'warning'
        else:
            return 'healthy'
    
    @staticmethod
    def _calculate_time_metrics(document: Document, access_logs: List, now: datetime) -> Dict[str, Any]:
        """Calculate time-based metrics."""
        # TODO: Fix timezone issue - can't subtract offset-naive and offset-aware datetimes
        time_since_creation = now - document.created_at
        
        if not access_logs:
            return {
                'time_since_creation': time_since_creation,
                'time_since_last_access': None
            }
        
        last_access = access_logs[-1].accessed_at
        time_since_last_access = now - last_access
        
        return {
            'time_since_creation': time_since_creation,
            'time_since_last_access': time_since_last_access
        }
    
    @staticmethod
    def _analyze_access_patterns(access_logs: List) -> Dict[str, Any]:
        """Analyze access patterns and classify usage."""
        if not access_logs:
            return {
                'unique_access_days': 0,
                'access_frequency': 0.0,
                'avg_time_between_accesses': None,
                'peak_access_day': None,
                'pattern_classification': 'never'
            }
        
        # Calculate unique access days
        access_dates = set(log.accessed_at.date() for log in access_logs)
        unique_access_days = len(access_dates)
        
        # Calculate access frequency (accesses per day)
        if len(access_logs) >= 2:
            # TODO: Fix timezone issue - can't subtract offset-naive and offset-aware datetimes
            time_span = (access_logs[-1].accessed_at - access_logs[0].accessed_at).days or 1
            access_frequency = len(access_logs) / time_span
        else:
            access_frequency = 0.0
        
        # Calculate average time between accesses
        if len(access_logs) >= 2:
            time_diffs = []
            for i in range(1, len(access_logs)):
                # TODO: Fix timezone issue - can't subtract offset-naive and offset-aware datetimes
                diff = access_logs[i].accessed_at - access_logs[i-1].accessed_at
                time_diffs.append(diff)
            
            avg_time_between = sum(time_diffs, timedelta()) / len(time_diffs)
        else:
            avg_time_between = None
        
        # Find peak access day
        from collections import Counter
        day_counts = Counter(log.accessed_at.strftime('%A') for log in access_logs)
        peak_access_day = day_counts.most_common(1)[0][0] if day_counts else None
        
        # Classify access pattern
        if access_frequency >= 1.0:
            pattern = 'frequent'
        elif access_frequency >= 0.1:
            pattern = 'occasional'
        elif len(access_logs) > 0:
            pattern = 'rare'
        else:
            pattern = 'never'
        
        return {
            'unique_access_days': unique_access_days,
            'access_frequency': access_frequency,
            'avg_time_between_accesses': avg_time_between,
            'peak_access_day': peak_access_day,
            'pattern_classification': pattern
        }
    
    @staticmethod
    def _calculate_lifecycle_metrics(document: Document, now: datetime) -> Dict[str, Any]:
        """Calculate lifecycle-related metrics."""
        # TODO: Fix timezone issue - can't subtract offset-naive and offset-aware datetimes
        time_since_creation = now - document.created_at
        
        if document.expires_at:
            total_lifecycle = document.expires_at - document.created_at
            lifecycle_percentage = min(100, (time_since_creation.total_seconds() / total_lifecycle.total_seconds()) * 100)
            
            # Predict deletion date (30 days after expiry by default)
            predicted_deletion = document.expires_at + timedelta(days=30)
        else:
            lifecycle_percentage = 0.0  # No expiry set
            predicted_deletion = None
        
        return {
            'lifecycle_percentage': lifecycle_percentage,
            'predicted_deletion_date': predicted_deletion
        }