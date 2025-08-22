"""
Document service for Briefcase application.
Handles document encryption, storage, and retrieval with authorization.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.document import Document, DocumentStatus
from app.models.document_access_log import DocumentAccessLog, AccessAction
from app.models.user import User
from app.core.encryption import DocumentEncryption, EncryptionError
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentContentResponse
import base64


class DocumentService:
    """Service for document operations with encryption and authorization."""
    
    @staticmethod
    def create_document(
        document_data: DocumentCreate,
        sender_user: User,
        db: Session
    ) -> DocumentResponse:
        """
        Create a new document with encryption.
        
        Args:
            document_data: Document creation data
            sender_user: User creating the document
            db: Database session
            
        Returns:
            DocumentResponse: Created document information
            
        Raises:
            HTTPException: If recipient not found or encryption fails
        """
        # Validate recipient exists
        recipient = db.query(User).filter(
            User.id == document_data.recipient_id,
            User.is_active == True
        ).first()
        
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient user not found"
            )
        
        # Calculate file size from base64 content
        try:
            content_bytes = base64.b64decode(document_data.content.encode('utf-8'))
            file_size = len(content_bytes)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid base64 content"
            )
        
        # Create document instance to get ID for encryption
        document = Document(
            title=document_data.title,
            description=document_data.description,
            file_name=document_data.file_name,
            file_size=file_size,
            mime_type=document_data.mime_type,
            sender_id=sender_user.id,
            recipient_id=document_data.recipient_id,
            expires_at=document_data.expires_at,
            view_limit=document_data.view_limit,
            encrypted_content="",  # Will be set after encryption
            encryption_iv=""  # Will be set after encryption
        )
        
        # Add to get ID
        db.add(document)
        db.flush()  # Get ID without committing
        
        try:
            # Encrypt content using document ID
            encrypted_content, iv = DocumentEncryption.encrypt_base64_content(
                document_data.content, 
                document.id
            )
            
            # Update document with encrypted content
            document.encrypted_content = encrypted_content
            document.encryption_iv = iv
            
            # Commit the transaction
            db.commit()
            db.refresh(document)
            
            # Log the upload
            DocumentService._log_access(
                document.id, sender_user.id, AccessAction.UPLOAD, True, db
            )
            
            # Return response with user emails
            return DocumentResponse.from_orm_with_users(document)
            
        except EncryptionError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Encryption failed: {str(e)}"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document creation failed: {str(e)}"
            )
    
    @staticmethod
    def get_document(
        document_id: str,
        current_user: User,
        db: Session
    ) -> DocumentResponse:
        """
        Get document information (metadata only).
        
        Args:
            document_id: Document ID
            current_user: User requesting the document
            db: Database session
            
        Returns:
            DocumentResponse: Document information
            
        Raises:
            HTTPException: If document not found or access denied
        """
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            DocumentService._log_access(
                document_id, current_user.id, AccessAction.ACCESS_DENIED, False, db,
                error_message="Document not found"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check authorization
        if not document.is_accessible_by(current_user.id):
            DocumentService._log_access(
                document_id, current_user.id, AccessAction.ACCESS_DENIED, False, db,
                error_message="User not authorized to access this document"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document"
            )
        
        # Log successful access
        DocumentService._log_access(
            document_id, current_user.id, AccessAction.VIEW, True, db
        )
        
        return DocumentResponse.from_orm_with_users(document)
    
    @staticmethod
    def download_document(
        document_id: str,
        current_user: User,
        db: Session
    ) -> DocumentContentResponse:
        """
        Download document content with decryption.
        
        Args:
            document_id: Document ID
            current_user: User requesting the download
            db: Database session
            
        Returns:
            DocumentContentResponse: Document with decrypted content
            
        Raises:
            HTTPException: If document not found, access denied, or decryption fails
        """
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            DocumentService._log_access(
                document_id, current_user.id, AccessAction.ACCESS_DENIED, False, db,
                error_message="Document not found"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check authorization and status
        if not document.is_accessible_by(current_user.id):
            DocumentService._log_access(
                document_id, current_user.id, AccessAction.ACCESS_DENIED, False, db,
                error_message="User not authorized or document not accessible"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document or document has expired"
            )
        
        try:
            # Decrypt content
            decrypted_content = DocumentEncryption.decrypt_to_base64_content(
                document.encrypted_content,
                document.encryption_iv,
                document.id
            )
            
            # Increment access count
            document.increment_access_count()
            db.commit()
            
            # Log successful download
            DocumentService._log_access(
                document_id, current_user.id, AccessAction.DOWNLOAD, True, db
            )
            
            return DocumentContentResponse(
                id=document.id,
                title=document.title,
                file_name=document.file_name,
                mime_type=document.mime_type,
                content=decrypted_content,
                access_count=document.access_count,
                view_limit=document.view_limit
            )
            
        except EncryptionError as e:
            DocumentService._log_access(
                document_id, current_user.id, AccessAction.ACCESS_DENIED, False, db,
                error_message=f"Decryption failed: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to decrypt document content"
            )
    
    @staticmethod
    def update_document(
        document_id: str,
        update_data: DocumentUpdate,
        current_user: User,
        db: Session
    ) -> DocumentResponse:
        """
        Update document metadata (sender only).
        
        Args:
            document_id: Document ID
            update_data: Update data
            current_user: User making the update
            db: Database session
            
        Returns:
            DocumentResponse: Updated document information
            
        Raises:
            HTTPException: If document not found or user not authorized
        """
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Only sender can update document metadata
        if document.sender_id != current_user.id:
            DocumentService._log_access(
                document_id, current_user.id, AccessAction.ACCESS_DENIED, False, db,
                error_message="Only sender can update document metadata"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the sender can update document metadata"
            )
        
        # Update fields
        if update_data.title is not None:
            document.title = update_data.title
        if update_data.description is not None:
            document.description = update_data.description
        if update_data.expires_at is not None:
            document.expires_at = update_data.expires_at
        if update_data.view_limit is not None:
            document.view_limit = update_data.view_limit
        
        # Update status based on new parameters
        document.update_status()
        
        db.commit()
        db.refresh(document)
        
        # Log the update
        DocumentService._log_access(
            document_id, current_user.id, AccessAction.UPDATE, True, db
        )
        
        return DocumentResponse.from_orm_with_users(document)
    
    @staticmethod
    def delete_document(
        document_id: str,
        current_user: User,
        db: Session
    ) -> dict:
        """
        Soft delete a document (sender only).
        
        Args:
            document_id: Document ID
            current_user: User requesting deletion
            db: Database session
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If document not found or user not authorized
        """
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Only sender can delete document
        if document.sender_id != current_user.id:
            DocumentService._log_access(
                document_id, current_user.id, AccessAction.ACCESS_DENIED, False, db,
                error_message="Only sender can delete document"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the sender can delete the document"
            )
        
        # Soft delete
        document.soft_delete()
        db.commit()
        
        # Log the deletion
        DocumentService._log_access(
            document_id, current_user.id, AccessAction.DELETE, True, db
        )
        
        return {"message": "Document deleted successfully"}
    
    @staticmethod
    def list_user_documents(
        current_user: User,
        db: Session,
        sent: bool = True,
        received: bool = True
    ) -> List[DocumentResponse]:
        """
        List documents for a user (sent and/or received).
        
        Args:
            current_user: User requesting the list
            db: Database session
            sent: Include sent documents
            received: Include received documents
            
        Returns:
            List[DocumentResponse]: List of documents
        """
        from sqlalchemy import or_, and_

        query = db.query(Document).filter(Document.status != DocumentStatus.DELETED)

        # Build role-aware conditions at the SQL level. If the user is the
        # recipient, exclude rows whose view limit is exhausted.
        conditions = []
        if sent:
            conditions.append(Document.sender_id == current_user.id)
        if received:
            conditions.append(
                and_(
                    Document.recipient_id == current_user.id,
                    or_(Document.view_limit.is_(None), Document.access_count < Document.view_limit),
                )
            )

        if conditions:
            query = query.filter(or_(*conditions))
        else:
            # If neither sent nor received, return empty list
            return []

        documents = query.order_by(Document.created_at.desc()).all()
        return [DocumentResponse.from_orm_with_users(doc) for doc in documents]
    
    @staticmethod
    def _log_access(
        document_id: str,
        user_id: str,
        action: AccessAction,
        success: bool,
        db: Session,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log document access attempt.
        
        Args:
            document_id: Document ID
            user_id: User ID
            action: Access action
            success: Whether the access was successful
            db: Database session
            error_message: Error message if access failed
            ip_address: User's IP address
            user_agent: User's user agent
        """
        log = DocumentAccessLog(
            document_id=document_id,
            user_id=user_id,
            action=action,
            success="true" if success else "false",
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(log)
        try:
            db.commit()
        except Exception:
            # Don't fail the main operation if logging fails
            db.rollback()