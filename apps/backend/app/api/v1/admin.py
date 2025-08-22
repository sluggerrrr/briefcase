"""
Admin API endpoints for lifecycle management.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.lifecycle import LifecycleConfig, CleanupJob
from app.services.lifecycle_service import (
    DocumentLifecycleService, 
    LifecycleConfigService
)
from app.schemas.lifecycle import (
    LifecycleStatusResponse,
    LifecycleConfigResponse,
    LifecycleConfigUpdate,
    CleanupJobResponse,
    ManualCleanupRequest,
    ManualCleanupResponse
)

router = APIRouter()


# For now, we'll assume all authenticated users are admins
# In a real system, you'd check for admin roles
async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and ensure they have admin privileges."""
    # TODO: Add proper admin role checking
    return current_user


@router.get("/lifecycle/status", response_model=LifecycleStatusResponse)
async def get_lifecycle_status(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive status of all lifecycle processes.
    
    Returns scheduler status, recent job history, and system statistics.
    """
    try:
        # Get recent cleanup jobs (last 7 days)
        recent_jobs = db.query(CleanupJob).filter(
            CleanupJob.started_at >= datetime.now() - timedelta(days=7)
        ).order_by(CleanupJob.started_at.desc()).all()
        
        # Get lifecycle statistics
        stats = await DocumentLifecycleService.get_lifecycle_statistics()
        
        # Railway cron jobs info
        railway_jobs = [
            {"id": "expire_documents", "name": "Document Expiration", "next_run": "Every 30 minutes", "trigger": "*/30 * * * *"},
            {"id": "cleanup_documents", "name": "Document Cleanup", "next_run": "Daily at 2 AM UTC", "trigger": "0 2 * * *"},
            {"id": "cleanup_audit_logs", "name": "Audit Log Cleanup", "next_run": "Weekly Sunday 3 AM UTC", "trigger": "0 3 * * 0"}
        ]
        
        return LifecycleStatusResponse(
            scheduler_running=True,  # Railway cron is always "running"
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
async def trigger_manual_cleanup(
    request: ManualCleanupRequest,
    admin_user: User = Depends(get_admin_user)
):
    """
    Manually trigger cleanup processes.
    
    Allows admins to run lifecycle processes on-demand rather than 
    waiting for scheduled execution.
    """
    try:
        # Manually trigger the appropriate lifecycle job
        if request.job_type == "expire_documents":
            result = await DocumentLifecycleService.expire_documents()
        elif request.job_type == "cleanup_deleted_documents":
            result = await DocumentLifecycleService.cleanup_deleted_documents()
        elif request.job_type == "cleanup_audit_logs":
            result = await DocumentLifecycleService.cleanup_old_audit_logs()
        else:
            raise ValueError(f"Unknown job type: {request.job_type}")
        
        return ManualCleanupResponse(
            job_type=request.job_type,
            triggered_at=datetime.now(),
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
async def get_lifecycle_config(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all lifecycle configuration settings.
    
    Returns current configuration values for grace periods,
    notification settings, and other lifecycle parameters.
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
async def update_lifecycle_config(
    setting_name: str,
    config_update: LifecycleConfigUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific lifecycle configuration setting.
    
    Allows admins to modify grace periods, notification schedules,
    and other lifecycle management parameters.
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
async def get_cleanup_job_history(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    days: int = 30,
    job_type: str = None
):
    """
    Get history of cleanup jobs.
    
    Returns execution history for lifecycle management jobs,
    including success/failure status and performance metrics.
    """
    try:
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