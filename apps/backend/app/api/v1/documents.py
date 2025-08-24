"""
Document API endpoints for Briefcase application.
Handles document upload, listing, viewing, and management operations.
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
from app.models.user import User
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


@router.post("/", response_model=DocumentResponse)
async def upload_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new document with encryption.
    
    **Required permissions:** Authenticated user
    **Rate limits:** Apply rate limiting for file uploads
    """
    return DocumentService.create_document(document_data, current_user, db)


@router.get("/", response_model=List[DocumentResponse])
@router.get("", response_model=List[DocumentResponse])  # Alternative route without trailing slash
async def list_documents(
    sent: bool = Query(True, description="Include sent documents"),
    received: bool = Query(True, description="Include received documents"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List documents for the current user.
    
    **Query Parameters:**
    - sent: Include documents sent by the user
    - received: Include documents received by the user
    """
    return DocumentService.list_user_documents(current_user, db, sent, received)


# Bulk Operations (must come before /{document_id} routes)
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


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get document metadata and information.
    
    **Required permissions:** Document sender or recipient
    """
    return DocumentService.get_document(document_id, current_user, db)


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Download document content with decryption.
    
    **Required permissions:** Document sender or recipient
    **Security:** Content is decrypted in memory only
    """
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
    file_stream = io.BytesIO(file_bytes)
    
    # Determine content disposition
    filename = document_content.file_name
    safe_filename = filename.replace('"', '\\"')  # Escape quotes for header
    
    # Return streaming response
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
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update document metadata.
    
    **Required permissions:** Document sender only
    **Updatable fields:** title, description, expires_at, view_limit
    """
    return DocumentService.update_document(document_id, update_data, current_user, db)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a document.
    
    **Required permissions:** Document sender only
    **Note:** This performs a soft delete, not permanent removal
    """
    return DocumentService.delete_document(document_id, current_user, db)


@router.get("/{document_id}/content", response_model=DocumentContentResponse)
async def get_document_content(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get document content as base64 (for preview/viewing).
    
    **Required permissions:** Document sender or recipient
    **Note:** Returns base64 content for client-side handling
    """
    return DocumentService.download_document(document_id, current_user, db)



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