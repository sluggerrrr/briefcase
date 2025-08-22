"""
Enhanced Admin API endpoints with permission integration.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.permissions import get_admin_user, require_role
from app.models.user import User
from app.models.lifecycle import LifecycleConfig, CleanupJob
from app.services.lifecycle_service import (
    DocumentLifecycleService, 
    LifecycleConfigService
)
from app.services.permission_service import PermissionService
from app.schemas.lifecycle import (
    LifecycleStatusResponse,
    LifecycleConfigResponse,
    LifecycleConfigUpdate,
    CleanupJobResponse,
    ManualCleanupRequest,
    ManualCleanupResponse
)
from app.schemas.permissions import SystemPermissionOverview

router = APIRouter()


@router.get("/lifecycle/status", response_model=LifecycleStatusResponse)
@require_role("admin")
async def get_lifecycle_status(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive status of all lifecycle processes.
    
    **Required Role:** Admin
    **Returns:** Scheduler status, recent job history, and system statistics.
    """
    try:
        # Get recent cleanup jobs (last 7 days)
        from datetime import datetime, timedelta
        recent_jobs = db.query(CleanupJob).filter(
            CleanupJob.started_at >= datetime.now() - timedelta(days=7)
        ).order_by(CleanupJob.started_at.desc()).all()
        
        # Get lifecycle statistics with permission context
        stats = await DocumentLifecycleService.get_lifecycle_statistics()
        
        # Add permission statistics
        permission_stats = await PermissionService.get_system_permission_overview(db)
        stats.update({
            'total_permissions': permission_stats.total_permissions,
            'users_by_role': permission_stats.users_by_role,
            'permissions_by_type': permission_stats.permissions_by_type
        })
        
        # Railway cron jobs info
        railway_jobs = [
            {"id": "expire_documents", "name": "Document Expiration", "next_run": "Every 30 minutes", "trigger": "*/30 * * * *"},
            {"id": "cleanup_documents", "name": "Document Cleanup", "next_run": "Daily at 2 AM UTC", "trigger": "0 2 * * *"},
            {"id": "cleanup_audit_logs", "name": "Audit Log Cleanup", "next_run": "Weekly Sunday 3 AM UTC", "trigger": "0 3 * * 0"},
            {"id": "cleanup_permissions", "name": "Permission Cleanup", "next_run": "Daily at 3 AM UTC", "trigger": "0 3 * * *"}
        ]
        
        return LifecycleStatusResponse(
            scheduler_running=True,
            scheduled_jobs=railway_jobs,
            recent_jobs=[
                CleanupJobResponse(
                    id=job.id,
                    job_type=job.job_type,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    status=job.status,
                    items_processed=job.items_processed,
                    items_failed=job.items_failed,
                    error_message=job.error_message
                ) for job in recent_jobs
            ],
            statistics=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lifecycle status: {str(e)}"
        )


@router.post("/lifecycle/run-cleanup", response_model=ManualCleanupResponse)
@require_role("admin")
async def trigger_manual_cleanup(
    request: ManualCleanupRequest,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger cleanup processes.
    
    **Required Role:** Admin
    **Allowed job types:** expire_documents, cleanup_deleted_documents, cleanup_audit_logs, cleanup_permissions
    """
    try:
        # Log admin action
        from app.models.document_access_log import DocumentAccessLog
        
        # Manually trigger the appropriate lifecycle job
        if request.job_type == "expire_documents":
            result = await DocumentLifecycleService.expire_documents()
        elif request.job_type == "cleanup_deleted_documents":
            result = await DocumentLifecycleService.cleanup_deleted_documents()
        elif request.job_type == "cleanup_audit_logs":
            result = await DocumentLifecycleService.cleanup_old_audit_logs()
        elif request.job_type == "cleanup_permissions":
            result = await PermissionService.cleanup_expired_permissions(db)
        else:
            raise ValueError(f"Unknown job type: {request.job_type}")
        
        return ManualCleanupResponse(
            job_type=request.job_type,
            triggered_at=datetime.now(),
            triggered_by=current_user.id,
            items_processed=result,
            success=True
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger cleanup: {str(e)}"
        )


@router.get("/lifecycle/config", response_model=List[LifecycleConfigResponse])
@require_role("admin")
async def get_lifecycle_config(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all lifecycle configuration settings.
    
    **Required Role:** Admin
    **Returns:** Current configuration values for grace periods, notification settings, and permissions.
    """
    try:
        configs = db.query(LifecycleConfig).order_by(LifecycleConfig.setting_name).all()
        
        return [
            LifecycleConfigResponse(
                id=config.id,
                setting_name=config.setting_name,
                setting_value=config.setting_value,
                description=config.description,
                updated_at=config.updated_at
            ) for config in configs
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lifecycle config: {str(e)}"
        )


@router.put("/lifecycle/config/{setting_name}", response_model=LifecycleConfigResponse)
@require_role("admin")
async def update_lifecycle_config(
    setting_name: str,
    config_update: LifecycleConfigUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific lifecycle configuration setting.
    
    **Required Role:** Admin
    **Allows:** Modification of grace periods, notification schedules, and permission settings.
    """
    try:
        # Update the configuration
        await LifecycleConfigService.set_config_value(
            setting_name,
            config_update.setting_value,
            config_update.description
        )
        
        # Return updated config
        config = db.query(LifecycleConfig).filter(
            LifecycleConfig.setting_name == setting_name
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration setting '{setting_name}' not found"
            )
        
        return LifecycleConfigResponse(
            id=config.id,
            setting_name=config.setting_name,
            setting_value=config.setting_value,
            description=config.description,
            updated_at=config.updated_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update lifecycle config: {str(e)}"
        )


@router.get("/lifecycle/jobs", response_model=List[CleanupJobResponse])
@require_role("admin")
async def get_cleanup_job_history(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    days: int = 30,
    job_type: str = None
):
    """
    Get history of cleanup jobs.
    
    **Required Role:** Admin
    **Returns:** Execution history for lifecycle management jobs, including permission-related jobs.
    """
    try:
        from datetime import datetime, timedelta
        query = db.query(CleanupJob).filter(
            CleanupJob.started_at >= datetime.now() - timedelta(days=days)
        )
        
        if job_type:
            query = query.filter(CleanupJob.job_type == job_type)
        
        jobs = query.order_by(CleanupJob.started_at.desc()).all()
        
        return [
            CleanupJobResponse(
                id=job.id,
                job_type=job.job_type,
                started_at=job.started_at,
                completed_at=job.completed_at,
                status=job.status,
                items_processed=job.items_processed,
                items_failed=job.items_failed,
                error_message=job.error_message
            ) for job in jobs
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cleanup job history: {str(e)}"
        )


@router.get("/permissions/overview", response_model=SystemPermissionOverview)
@require_role("admin")
async def get_permission_system_overview(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive permission system overview.
    
    **Required Role:** Admin
    **Returns:** System-wide permission statistics and health metrics.
    """
    try:
        overview = await PermissionService.get_system_permission_overview(db)
        return overview
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get permission overview: {str(e)}"
        )


@router.post("/permissions/initialize")
@require_role("admin")
async def initialize_permission_system(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Initialize default permission system components.
    
    **Required Role:** Admin
    **Action:** Creates default roles and assigns admin role to current user.
    """
    try:
        # Initialize default roles
        PermissionService.initialize_default_roles(db)
        
        # Assign admin role to current user if not already assigned
        user_roles = PermissionService.get_user_roles(db, current_user.id)
        if 'admin' not in user_roles:
            PermissionService.assign_user_role(
                db=db,
                user_id=current_user.id,
                role_name='admin',
                assigned_by=current_user.id
            )
        
        return {
            "message": "Permission system initialized successfully",
            "admin_user": current_user.id,
            "roles_created": ["admin", "owner", "editor", "viewer"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize permission system: {str(e)}"
        )