"""
Document status API endpoints for Briefcase application.
"""
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.document_access_log import DocumentAccessLog
from app.models.lifecycle import DocumentLifecycleEvent
from app.services.document_status_service import DocumentStatusService
from app.schemas.document_status import (
    DocumentStatusResponse,
    DocumentAnalyticsResponse,
    DocumentStatusHistoryResponse,
    SystemStatusOverview,
    SystemMetricsResponse,
    BulkStatusRequest,
    BulkStatusResponse,
    DocumentStatusFilters,
    DocumentHealthCheck,
    SystemHealthCheck
)

router = APIRouter()


@router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive status information for a document.
    
    Returns lifecycle information, access statistics, health status,
    and all relevant metadata for document monitoring.
    """
    try:
        # Get document and verify access
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check if user has access to this document
        if document.sender_id != current_user.id and document.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to document status"
            )
        
        # Calculate comprehensive status
        status_data = await DocumentStatusService.calculate_document_status(document, db)
        
        return DocumentStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate document status: {str(e)}"
        )


@router.post("/documents/status/bulk", response_model=BulkStatusResponse)
async def get_bulk_document_status(
    request: BulkStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get status for multiple documents in a single request.
    
    Efficient bulk operation for checking status of multiple documents
    with optional analytics inclusion.
    """
    start_time = time.time()
    
    try:
        results = []
        not_found_ids = []
        
        # Get documents user has access to
        documents = db.query(Document).filter(
            Document.id.in_(request.document_ids),
            (Document.sender_id == current_user.id) | (Document.recipient_id == current_user.id)
        ).all()
        
        found_ids = {doc.id for doc in documents}
        not_found_ids = [doc_id for doc_id in request.document_ids if doc_id not in found_ids]
        
        # Calculate status for each document
        for document in documents:
            try:
                status_data = await DocumentStatusService.calculate_document_status(document, db)
                results.append(DocumentStatusResponse(**status_data))
            except Exception as e:
                # Log error but continue processing other documents
                not_found_ids.append(document.id)
        
        processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        return BulkStatusResponse(
            results=results,
            total_requested=len(request.document_ids),
            total_found=len(results),
            not_found_ids=not_found_ids,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process bulk status request: {str(e)}"
        )


@router.get("/documents/{document_id}/status/history", response_model=DocumentStatusHistoryResponse)
async def get_document_status_history(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, le=200, description="Maximum number of history entries")
):
    """
    Get status change history for a document.
    
    Returns chronological history of status changes, lifecycle events,
    and access patterns for audit and monitoring purposes.
    """
    try:
        # Get document and verify access
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.sender_id != current_user.id and document.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to document history"
            )
        
        # Get lifecycle events
        lifecycle_events = db.query(DocumentLifecycleEvent).filter(
            DocumentLifecycleEvent.document_id == document_id
        ).order_by(DocumentLifecycleEvent.event_timestamp.desc()).limit(limit).all()
        
        # Get access history for status changes
        access_logs = db.query(DocumentAccessLog).filter(
            DocumentAccessLog.document_id == document_id
        ).order_by(DocumentAccessLog.accessed_at.desc()).limit(limit).all()
        
        # Format lifecycle events
        lifecycle_data = []
        for event in lifecycle_events:
            lifecycle_data.append({
                'id': event.id,
                'event_type': event.event_type,
                'timestamp': event.event_timestamp,
                'automated': event.automated,
                'triggered_by': event.triggered_by,
                'metadata': event.event_metadata
            })
        
        # Format status changes (derived from access patterns and lifecycle events)
        status_changes = []
        
        # Add document creation
        status_changes.append({
            'timestamp': document.created_at,
            'status': 'created',
            'description': 'Document created',
            'automated': False
        })
        
        # Add lifecycle events as status changes
        for event in reversed(lifecycle_events):  # Chronological order
            status_changes.append({
                'timestamp': event.event_timestamp,
                'status': event.event_type,
                'description': f'Document {event.event_type}',
                'automated': event.automated
            })
        
        # Sort by timestamp
        status_changes.sort(key=lambda x: x['timestamp'])
        
        return DocumentStatusHistoryResponse(
            document_id=document_id,
            title=document.title,
            status_changes=status_changes,
            lifecycle_events=lifecycle_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document history: {str(e)}"
        )


@router.get("/documents/{document_id}/analytics", response_model=DocumentAnalyticsResponse)
async def get_document_analytics(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a document.
    
    Provides comprehensive usage statistics, access patterns,
    and predictive metrics for document lifecycle management.
    """
    try:
        # Get document and verify access
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.sender_id != current_user.id and document.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to document analytics"
            )
        
        # Calculate comprehensive analytics
        analytics_data = await DocumentStatusService.calculate_document_analytics(document, db)
        
        return DocumentAnalyticsResponse(**analytics_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate document analytics: {str(e)}"
        )


@router.get("/documents/{document_id}/health", response_model=DocumentHealthCheck)
async def get_document_health_check(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform health check for a specific document.
    
    Analyzes document status and identifies potential issues
    with recommendations for resolution.
    """
    try:
        # Get document and verify access
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.sender_id != current_user.id and document.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to document health check"
            )
        
        # Calculate status for health assessment
        status_data = await DocumentStatusService.calculate_document_status(document, db)
        
        issues = []
        recommendations = []
        
        # Analyze potential issues
        if status_data['is_expired']:
            issues.append("Document has expired")
            recommendations.append("Consider extending expiry date or archiving document")
        
        if status_data['view_limit_exceeded']:
            issues.append("View limit has been exceeded")
            recommendations.append("Consider increasing view limit or creating new document")
        
        if status_data['never_accessed'] and (datetime.now() - document.created_at).days > 7:
            issues.append("Document has never been accessed")
            recommendations.append("Notify recipient or verify document sharing is working")
        
        if status_data['days_until_expiry'] is not None and status_data['days_until_expiry'] <= 3:
            issues.append(f"Document expires in {status_data['days_until_expiry']} days")
            recommendations.append("Consider extending expiry date if document is still needed")
        
        if document.file_size > 50 * 1024 * 1024:  # 50MB
            issues.append("Large file size may impact performance")
            recommendations.append("Consider compressing file or using external storage")
        
        return DocumentHealthCheck(
            document_id=document_id,
            title=document.title,
            health_status=status_data['status_health'],
            issues=issues,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform document health check: {str(e)}"
        )


# System-wide status endpoints (admin only)
@router.get("/admin/status/overview", response_model=SystemStatusOverview)
async def get_system_status_overview(
    current_user: User = Depends(get_current_user),  # TODO: Add admin check
    db: Session = Depends(get_db)
):
    """
    Get system-wide document status overview.
    
    Provides comprehensive statistics about all documents,
    storage usage, and system health metrics for administrators.
    """
    try:
        overview_data = await DocumentStatusService.get_system_status_overview(db)
        return SystemStatusOverview(**overview_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status overview: {str(e)}"
        )


@router.get("/admin/status/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    timeframe: str = Query("24h", regex="^(1h|24h|7d|30d)$", description="Time period for metrics"),
    current_user: User = Depends(get_current_user),  # TODO: Add admin check
    db: Session = Depends(get_db)
):
    """
    Get system metrics for specified timeframe.
    
    Returns performance metrics, usage statistics, and system
    health indicators for the specified time period.
    """
    try:
        metrics_data = await DocumentStatusService.get_system_metrics(timeframe, db)
        return SystemMetricsResponse(**metrics_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system metrics: {str(e)}"
        )


@router.get("/admin/status/health", response_model=SystemHealthCheck)
async def get_system_health_check(
    current_user: User = Depends(get_current_user),  # TODO: Add admin check
    db: Session = Depends(get_db)
):
    """
    Comprehensive system health check.
    
    Analyzes all system components and provides overall health
    status with specific recommendations for any issues found.
    """
    try:
        now = datetime.now()
        
        # Check various system components
        overview_data = await DocumentStatusService.get_system_status_overview(db)
        
        # Assess component health
        database_status = "healthy"
        storage_status = "healthy" 
        cleanup_status = "healthy"
        api_status = "healthy"
        
        issues = []
        recommendations = []
        
        # Database health checks
        if overview_data['total_documents'] == 0:
            database_status = "warning"
            issues.append("No documents in system")
        
        # Storage health checks
        if overview_data['total_storage_used'] > 10 * 1024**3:  # 10GB
            storage_status = "warning"
            issues.append("High storage usage")
            recommendations.append("Consider implementing storage cleanup policies")
        
        # Cleanup health checks
        if overview_data['pending_cleanup_items'] > 100:
            cleanup_status = "critical"
            issues.append(f"{overview_data['pending_cleanup_items']} items pending cleanup")
            recommendations.append("Run manual cleanup or check cleanup job status")
        elif overview_data['pending_cleanup_items'] > 50:
            cleanup_status = "warning"
        
        # Overall health assessment
        component_statuses = [database_status, storage_status, cleanup_status, api_status]
        if "critical" in component_statuses:
            overall_status = "critical"
        elif "warning" in component_statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return SystemHealthCheck(
            overall_status=overall_status,
            timestamp=now,
            components={
                "database": database_status,
                "storage": storage_status,
                "cleanup": cleanup_status,
                "api": api_status
            },
            issues=issues,
            recommendations=recommendations,
            database_status=database_status,
            storage_status=storage_status,
            cleanup_status=cleanup_status,
            api_status=api_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform system health check: {str(e)}"
        )