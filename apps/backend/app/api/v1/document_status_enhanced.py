"""
Enhanced Document Status API with permission integration.
"""
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_active_user
from app.dependencies.permissions import get_admin_user, require_permission
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.document_access_log import DocumentAccessLog
from app.models.lifecycle import DocumentLifecycleEvent
from app.services.document_status_service import DocumentStatusService
from app.services.permission_service import PermissionService
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
async def get_document_status_with_permissions(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive status information for a document with permission validation.
    
    **Required Permission:** Read access to the document
    **Returns:** Lifecycle information, access statistics, health status, and permissions
    """
    try:
        # Check read permission
        if not PermissionService.check_document_permission(db, current_user.id, document_id, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions: read permission required"
            )
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Calculate comprehensive status
        status_data = await DocumentStatusService.calculate_document_status(document, db)
        
        # Add user's permission information
        user_permissions = []
        for perm_type in ["read", "write", "share", "delete", "admin"]:
            if PermissionService.check_document_permission(db, current_user.id, document_id, perm_type):
                user_permissions.append(perm_type)
        
        status_data["user_permissions"] = user_permissions
        status_data["is_owner"] = document.sender_id == current_user.id
        status_data["is_recipient"] = document.recipient_id == current_user.id
        
        return DocumentStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate document status: {str(e)}"
        )


@router.post("/documents/status/bulk", response_model=BulkStatusResponse)
async def get_bulk_document_status_with_permissions(
    request: BulkStatusRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get status for multiple documents with permission filtering.
    
    **Behavior:** Only returns status for documents the user has read access to
    **Returns:** Status information for accessible documents only
    """
    start_time = time.time()
    
    try:
        results = []
        not_found_ids = []
        permission_denied_ids = []
        
        # Check permissions for all requested documents
        for doc_id in request.document_ids:
            if not PermissionService.check_document_permission(db, current_user.id, doc_id, "read"):
                permission_denied_ids.append(doc_id)
        
        # Get documents user has access to
        accessible_doc_ids = [
            doc_id for doc_id in request.document_ids 
            if doc_id not in permission_denied_ids
        ]
        
        documents = db.query(Document).filter(
            Document.id.in_(accessible_doc_ids)
        ).all()
        
        found_ids = {doc.id for doc in documents}
        not_found_ids = [doc_id for doc_id in accessible_doc_ids if doc_id not in found_ids]
        
        # Calculate status for each accessible document
        for document in documents:
            try:
                status_data = await DocumentStatusService.calculate_document_status(document, db)
                
                # Add permission information
                user_permissions = []
                for perm_type in ["read", "write", "share", "delete", "admin"]:
                    if PermissionService.check_document_permission(db, current_user.id, document.id, perm_type):
                        user_permissions.append(perm_type)
                
                status_data["user_permissions"] = user_permissions
                status_data["is_owner"] = document.sender_id == current_user.id
                status_data["is_recipient"] = document.recipient_id == current_user.id
                
                results.append(DocumentStatusResponse(**status_data))
                
            except Exception as e:
                # Log error but continue processing other documents
                not_found_ids.append(document.id)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return BulkStatusResponse(
            results=results,
            total_requested=len(request.document_ids),
            total_found=len(results),
            not_found_ids=not_found_ids + permission_denied_ids,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process bulk status request: {str(e)}"
        )


@router.get("/documents/{document_id}/status/history", response_model=DocumentStatusHistoryResponse)
async def get_document_status_history_with_permissions(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, le=200, description="Maximum number of history entries")
):
    """
    Get status change history for a document with permission validation.
    
    **Required Permission:** Read access to the document
    **Returns:** Chronological history including permission changes
    """
    try:
        # Check read permission
        if not PermissionService.check_document_permission(db, current_user.id, document_id, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions: read permission required"
            )
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get lifecycle events
        lifecycle_events = db.query(DocumentLifecycleEvent).filter(
            DocumentLifecycleEvent.document_id == document_id
        ).order_by(DocumentLifecycleEvent.event_timestamp.desc()).limit(limit).all()
        
        # Get access history for status changes
        access_logs = db.query(DocumentAccessLog).filter(
            DocumentAccessLog.document_id == document_id
        ).order_by(DocumentAccessLog.accessed_at.desc()).limit(limit).all()
        
        # Get permission history if user has admin access
        permission_history = []
        if PermissionService.check_document_permission(db, current_user.id, document_id, "admin"):
            from app.models.permissions import DocumentPermission
            permissions = db.query(DocumentPermission).filter(
                DocumentPermission.document_id == document_id
            ).order_by(DocumentPermission.granted_at.desc()).limit(limit).all()
            
            permission_history = [
                {
                    'id': perm.id,
                    'user_id': perm.user_id,
                    'permission_type': perm.permission_type,
                    'granted_at': perm.granted_at,
                    'granted_by': perm.granted_by,
                    'expires_at': perm.expires_at
                } for perm in permissions
            ]
        
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
        
        # Format status changes
        status_changes = []
        
        # Add document creation
        status_changes.append({
            'timestamp': document.created_at,
            'status': 'created',
            'description': 'Document created',
            'automated': False
        })
        
        # Add lifecycle events as status changes
        for event in reversed(lifecycle_events):
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
            lifecycle_events=lifecycle_data,
            permission_history=permission_history
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document history: {str(e)}"
        )


@router.get("/documents/{document_id}/analytics", response_model=DocumentAnalyticsResponse)
async def get_document_analytics_with_permissions(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a document with permission validation.
    
    **Required Permission:** Read access to the document
    **Enhanced Analytics:** Includes permission-based access patterns
    """
    try:
        # Check read permission
        if not PermissionService.check_document_permission(db, current_user.id, document_id, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions: read permission required"
            )
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Calculate comprehensive analytics
        analytics_data = await DocumentStatusService.calculate_document_analytics(document, db)
        
        # Add permission-based analytics if user has admin access
        if PermissionService.check_document_permission(db, current_user.id, document_id, "admin"):
            from app.models.permissions import DocumentPermission
            permissions = db.query(DocumentPermission).filter(
                DocumentPermission.document_id == document_id
            ).all()
            
            permission_analytics = {
                'total_permissions_granted': len(permissions),
                'permissions_by_type': {},
                'users_with_access': len(set([p.user_id for p in permissions])),
                'recent_permission_grants': len([
                    p for p in permissions 
                    if (datetime.now() - p.granted_at).days <= 7
                ])
            }
            
            for perm in permissions:
                perm_type = perm.permission_type
                if perm_type not in permission_analytics['permissions_by_type']:
                    permission_analytics['permissions_by_type'][perm_type] = 0
                permission_analytics['permissions_by_type'][perm_type] += 1
            
            analytics_data['permission_analytics'] = permission_analytics
        
        return DocumentAnalyticsResponse(**analytics_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate document analytics: {str(e)}"
        )


# System-wide status endpoints with permission integration
@router.get("/admin/status/overview", response_model=SystemStatusOverview)
async def get_enhanced_system_status_overview(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get enhanced system-wide status overview including permissions.
    
    **Required Role:** Admin
    **Returns:** Comprehensive statistics including permission metrics
    """
    try:
        # Get base overview data
        overview_data = await DocumentStatusService.get_system_status_overview(db)
        
        # Add permission statistics
        permission_overview = await PermissionService.get_system_permission_overview(db)
        
        # Merge data
        enhanced_overview = {**overview_data, **permission_overview}
        
        return SystemStatusOverview(**enhanced_overview)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get enhanced system status overview: {str(e)}"
        )


@router.get("/admin/status/health", response_model=SystemHealthCheck)
async def get_enhanced_system_health_check(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Enhanced system health check including permission system health.
    
    **Required Role:** Admin
    **Returns:** Comprehensive health assessment including permission metrics
    """
    try:
        now = datetime.now()
        
        # Get base system overview
        overview_data = await DocumentStatusService.get_system_status_overview(db)
        permission_overview = await PermissionService.get_system_permission_overview(db)
        
        # Component health assessment
        database_status = "healthy"
        storage_status = "healthy" 
        cleanup_status = "healthy"
        api_status = "healthy"
        permission_status = "healthy"
        
        issues = []
        recommendations = []
        
        # Database health checks
        if overview_data.get('total_documents', 0) == 0:
            database_status = "warning"
            issues.append("No documents in system")
        
        # Storage health checks
        if overview_data.get('total_storage_used', 0) > 10 * 1024**3:  # 10GB
            storage_status = "warning"
            issues.append("High storage usage")
            recommendations.append("Consider implementing storage cleanup policies")
        
        # Cleanup health checks
        pending_cleanup = overview_data.get('pending_cleanup_items', 0)
        if pending_cleanup > 100:
            cleanup_status = "critical"
            issues.append(f"{pending_cleanup} items pending cleanup")
            recommendations.append("Run manual cleanup or check cleanup job status")
        elif pending_cleanup > 50:
            cleanup_status = "warning"
        
        # Permission system health checks
        total_permissions = permission_overview.get('total_permissions', 0)
        total_users = permission_overview.get('total_users', 0)
        
        if total_users > 0 and total_permissions == 0:
            permission_status = "warning"
            issues.append("No permissions configured")
            recommendations.append("Initialize permission system and assign user roles")
        
        # Check for permission inconsistencies
        admin_count = permission_overview.get('users_by_role', {}).get('admin', 0)
        if admin_count == 0:
            permission_status = "critical"
            issues.append("No admin users configured")
            recommendations.append("Assign admin role to at least one user")
        
        # Overall health assessment
        component_statuses = [database_status, storage_status, cleanup_status, api_status, permission_status]
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
                "api": api_status,
                "permissions": permission_status
            },
            issues=issues,
            recommendations=recommendations,
            database_status=database_status,
            storage_status=storage_status,
            cleanup_status=cleanup_status,
            api_status=api_status,
            permission_system_status=permission_status,
            permission_metrics=permission_overview
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform enhanced system health check: {str(e)}"
        )