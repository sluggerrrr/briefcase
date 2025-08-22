"""
Document API endpoints for Briefcase application.
Handles document upload, listing, viewing, and management operations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.document_service import DocumentService
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentContentResponse
)
import io
import base64

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