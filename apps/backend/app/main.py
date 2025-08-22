"""
FastAPI main application entry point for Briefcase.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, documents, admin, document_status, permissions, documents_enhanced, admin_enhanced, document_status_enhanced
from app.services.lifecycle_service import initialize_lifecycle_config
from app.services.permission_service import PermissionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup - initialize lifecycle configuration
    await initialize_lifecycle_config()
    
    # Initialize permission system
    from app.core.database import get_db
    db = next(get_db())
    try:
        PermissionService.initialize_default_roles(db)
    except Exception as e:
        print(f"Warning: Failed to initialize permission system: {e}")
    finally:
        db.close()
    
    yield
    # Shutdown - no cleanup needed


app = FastAPI(
    title="Briefcase API",
    description="RESTful API for secure internal document sharing with encryption and access controls",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    redirect_slashes=False,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

# Document APIs - both original and enhanced
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(documents_enhanced.router, prefix="/api/v1/documents-enhanced", tags=["documents-enhanced"])

# Admin APIs - both original and enhanced  
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(admin_enhanced.router, prefix="/api/v1/admin-enhanced", tags=["admin-enhanced"])

# Status APIs - both original and enhanced
app.include_router(document_status.router, prefix="/api/v1/status", tags=["document-status"])
app.include_router(document_status_enhanced.router, prefix="/api/v1/status-enhanced", tags=["document-status-enhanced"])

# Permission management APIs
app.include_router(permissions.router, prefix="/api/v1/permissions", tags=["permissions"])

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Briefcase API", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "briefcase-api",
        "version": "1.0.0"
    }


@app.get("/health/lifecycle")
async def lifecycle_health_check():
    """Health check for lifecycle processes."""
    from app.services.lifecycle_service import DocumentLifecycleService
    
    try:
        stats = await DocumentLifecycleService.get_lifecycle_statistics()
        
        return {
            "status": "healthy",
            "deployment_mode": "railway_cron",
            "pending_expirations": stats.get("expiring_soon", 0),
            "recent_job_failures": stats.get("recent_jobs", {}).get("failed", 0),
            "documents_by_status": stats.get("documents_by_status", {})
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "deployment_mode": "railway_cron"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)