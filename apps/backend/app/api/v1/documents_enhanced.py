"""
Enhanced Document API endpoints with permission integration and bulk operations.
"""
from typing import List, Optional
import io
import base64
import zipfile
import tempfile
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_active_user
from app.dependencies.permissions import require_permission, require_document_access, require_bulk_permission
from app.models.user import User
from app.models.document import Document
from app.models.permissions import DocumentPermission
from app.services.document_service import DocumentService
from app.services.permission_service import PermissionService
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentContentResponse
)
from app.schemas.permissions import (
    BulkDeleteRequest,
    BulkShareRequest,
    BulkDownloadRequest,
    BulkOperationResponse,
    BulkOperationResult
)

router = APIRouter()


# Enhanced Document List with Permissions
@router.get("/accessible", response_model=List[DocumentResponse])
async def list_accessible_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all documents the user has access to based on permissions.
    Includes owned, received, and documents with explicit permissions.
    """
    documents = PermissionService.get_accessible_documents(db, current_user.id)
    
    # Convert to response format
    document_responses = []
    for doc in documents:
        # Get user's permissions for this document
        user_permissions = []
        
        # Check if owner (has all permissions)
        if doc.sender_id == current_user.id:
            user_permissions = ["read", "write", "share", "delete", "admin"]
        # Check if recipient (has read permission)
        elif doc.recipient_id == current_user.id:
            user_permissions = ["read"]
        
        # Add explicit permissions
        explicit_perms = db.query(
            DocumentPermission.permission_type
        ).filter(
            DocumentPermission.document_id == doc.id,
            DocumentPermission.user_id == current_user.id
        ).all()
        
        for perm in explicit_perms:
            if perm.permission_type not in user_permissions:
                user_permissions.append(perm.permission_type)
        
        # Create response with permission info
        doc_response = DocumentResponse.from_orm(doc)
        doc_response.user_permissions = user_permissions
        document_responses.append(doc_response)
    
    return document_responses


# Enhanced Document Operations with Permission Checks
@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_with_permissions(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get document with user's permission information."""
    # Check read permission
    if not PermissionService.check_document_permission(db, current_user.id, document_id, "read"):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions: read permission required"
        )
    
    document = DocumentService.get_document(document_id, current_user, db)
    
    # Add user permissions to response
    user_permissions = []
    for perm_type in ["read", "write", "share", "delete", "admin"]:
        if PermissionService.check_document_permission(db, current_user.id, document_id, perm_type):
            user_permissions.append(perm_type)
    
    document.user_permissions = user_permissions
    return document


@router.get("/{document_id}/download")
async def download_document_with_permission(
    document_id: str,
    request: Request,
    params: tuple = Depends(require_document_access("read"))
):
    """Download document with permission check."""
    document_id, current_user, db = params
    
    # Get client info for audit logging
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Get document with decrypted content
    document_content = DocumentService.download_document(document_id, current_user, db)
    
    # Decode base64 content to bytes
    try:
        file_bytes = base64.b64decode(document_content.content)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to process document content"
        )
    
    # Create file stream
    filename = document_content.file_name
    safe_filename = filename.replace('"', '\\"')
    
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=document_content.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "Content-Length": str(len(file_bytes)),
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document_with_permission(
    document_id: str,
    update_data: DocumentUpdate,
    params: tuple = Depends(require_document_access("write"))
):
    """Update document with permission check."""
    document_id, current_user, db = params
    return DocumentService.update_document(document_id, update_data, current_user, db)


@router.delete("/{document_id}")
async def delete_document_with_permission(
    document_id: str,
    params: tuple = Depends(require_document_access("delete"))
):
    """Delete document with permission check."""
    document_id, current_user, db = params
    return DocumentService.delete_document(document_id, current_user, db)


# Bulk Operations
@router.post("/bulk/delete", response_model=BulkOperationResponse)
async def bulk_delete_documents(
    request: BulkDeleteRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bulk delete documents with individual permission checks."""
    results = []
    successful = 0
    failed = 0
    
    for doc_id in request.document_ids:
        try:
            # Check delete permission
            if not PermissionService.check_document_permission(db, current_user.id, doc_id, "delete"):
                results.append(BulkOperationResult(
                    document_id=doc_id,
                    status="permission_denied",
                    error="Insufficient permissions: delete permission required"
                ))
                failed += 1
                continue
            
            # Perform deletion
            DocumentService.delete_document(doc_id, current_user, db)
            results.append(BulkOperationResult(
                document_id=doc_id,
                status="success"
            ))
            successful += 1
            
        except HTTPException as e:
            results.append(BulkOperationResult(
                document_id=doc_id,
                status="failed",
                error=e.detail
            ))
            failed += 1
        except Exception as e:
            results.append(BulkOperationResult(
                document_id=doc_id,
                status="failed",
                error=str(e)
            ))
            failed += 1
    
    return BulkOperationResponse(
        total_documents=len(request.document_ids),
        successful=successful,
        failed=failed,
        results=results
    )


@router.post("/bulk/share", response_model=BulkOperationResponse)
async def bulk_share_documents(
    request: BulkShareRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bulk share documents with multiple recipients."""
    results = []
    successful = 0
    failed = 0
    
    for doc_id in request.document_ids:
        try:
            # Check share permission
            if not PermissionService.check_document_permission(db, current_user.id, doc_id, "share"):
                results.append(BulkOperationResult(
                    document_id=doc_id,
                    status="permission_denied",
                    error="Insufficient permissions: share permission required"
                ))
                failed += 1
                continue
            
            # Grant permissions to all recipients
            for recipient_id in request.recipient_ids:
                PermissionService.grant_document_permission(
                    db=db,
                    document_id=doc_id,
                    user_id=recipient_id,
                    permission_type=request.permission_type,
                    granted_by=current_user.id,
                    expires_at=request.expires_at
                )
            
            results.append(BulkOperationResult(
                document_id=doc_id,
                status="success"
            ))
            successful += 1
            
        except Exception as e:
            results.append(BulkOperationResult(
                document_id=doc_id,
                status="failed",
                error=str(e)
            ))
            failed += 1
    
    return BulkOperationResponse(
        total_documents=len(request.document_ids),
        successful=successful,
        failed=failed,
        results=results
    )


@router.post("/bulk/download")
async def bulk_download_documents(
    request: BulkDownloadRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bulk download documents as ZIP archive."""
    # Check permissions for all documents
    permission_results = PermissionService.can_perform_bulk_operation(
        db, current_user.id, request.document_ids, "read"
    )
    
    # Filter documents user has access to
    accessible_docs = [
        doc_id for doc_id, has_perm in permission_results.items() 
        if has_perm
    ]
    
    if not accessible_docs:
        raise HTTPException(
            status_code=403,
            detail="No accessible documents in the requested list"
        )
    
    # Create ZIP archive in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for doc_id in accessible_docs:
            try:
                # Get document content
                document_content = DocumentService.download_document(doc_id, current_user, db)
                file_bytes = base64.b64decode(document_content.content)
                
                # Add to ZIP with safe filename
                safe_filename = document_content.file_name.replace('/', '_').replace('\\', '_')
                zip_file.writestr(safe_filename, file_bytes)
                
            except Exception as e:
                # Add error file to ZIP
                error_content = f"Error downloading {doc_id}: {str(e)}"
                zip_file.writestr(f"ERROR_{doc_id}.txt", error_content.encode())
    
    zip_buffer.seek(0)
    
    # Return ZIP file
    return StreamingResponse(
        io.BytesIO(zip_buffer.getvalue()),
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=documents.zip",
            "Content-Length": str(len(zip_buffer.getvalue()))
        }
    )


# Advanced Search with Permission Filtering
@router.get("/search", response_model=List[DocumentResponse])
async def search_documents(
    query: Optional[str] = Query(None, description="Search query"),
    file_types: Optional[List[str]] = Query(None, description="Filter by file types"),
    date_from: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date (ISO format)"),
    status: Optional[str] = Query(None, description="Document status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Advanced search with permission filtering."""
    # Get accessible documents first
    accessible_docs = PermissionService.get_accessible_documents(db, current_user.id)
    
    # Apply filters
    filtered_docs = accessible_docs
    
    if query:
        filtered_docs = [
            doc for doc in filtered_docs 
            if query.lower() in doc.title.lower() or 
               (doc.description and query.lower() in doc.description.lower())
        ]
    
    if file_types:
        filtered_docs = [
            doc for doc in filtered_docs 
            if any(doc.file_name.lower().endswith(f'.{ft.lower()}') for ft in file_types)
        ]
    
    if date_from:
        from datetime import datetime
        start_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        filtered_docs = [doc for doc in filtered_docs if doc.created_at >= start_date]
    
    if date_to:
        from datetime import datetime
        end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        filtered_docs = [doc for doc in filtered_docs if doc.created_at <= end_date]
    
    if status:
        filtered_docs = [doc for doc in filtered_docs if doc.status.value == status]
    
    # Convert to response format with permissions
    document_responses = []
    for doc in filtered_docs:
        user_permissions = []
        for perm_type in ["read", "write", "share", "delete", "admin"]:
            if PermissionService.check_document_permission(db, current_user.id, doc.id, perm_type):
                user_permissions.append(perm_type)
        
        doc_response = DocumentResponse.from_orm(doc)
        doc_response.user_permissions = user_permissions
        document_responses.append(doc_response)
    
    return document_responses