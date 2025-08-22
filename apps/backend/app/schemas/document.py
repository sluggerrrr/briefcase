"""
Document schemas for Briefcase application.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.document import DocumentStatus


class DocumentCreate(BaseModel):
    """Schema for creating a new document."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    file_name: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., description="Base64 encoded file content")
    mime_type: Optional[str] = None
    recipient_id: str = Field(..., description="ID of the recipient user")
    expires_at: Optional[datetime] = None
    view_limit: Optional[int] = Field(None, ge=1, le=10)
    
    @field_validator('expires_at')
    @classmethod
    def validate_expiration(cls, v):
        """Validate expiration date is in the future."""
        if v and v <= datetime.now(v.tzinfo):
            raise ValueError('Expiration date must be in the future')
        # Maximum 1 year in the future
        max_date = datetime.now(v.tzinfo if v else None)
        max_date = max_date.replace(year=max_date.year + 1)
        if v and v > max_date:
            raise ValueError('Expiration date cannot be more than 1 year in the future')
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content_size(cls, v):
        """Validate base64 content size (roughly 10MB limit)."""
        # Base64 increases size by ~33%, so 10MB file = ~13.3MB base64
        if len(v) > 14 * 1024 * 1024:  # 14MB limit for base64
            raise ValueError('File size exceeds 10MB limit')
        return v


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    view_limit: Optional[int] = Field(None, ge=1, le=10)
    
    @field_validator('expires_at')
    @classmethod
    def validate_expiration(cls, v):
        """Validate expiration date is in the future."""
        if v and v <= datetime.now(v.tzinfo):
            raise ValueError('Expiration date must be in the future')
        # Maximum 1 year in the future
        max_date = datetime.now(v.tzinfo if v else None)
        max_date = max_date.replace(year=max_date.year + 1)
        if v and v > max_date:
            raise ValueError('Expiration date cannot be more than 1 year in the future')
        return v


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: str
    title: str
    description: Optional[str]
    file_name: str
    file_size: int
    mime_type: Optional[str]
    sender_id: str
    sender_email: Optional[str] = None
    recipient_id: str
    recipient_email: Optional[str] = None
    expires_at: Optional[datetime]
    view_limit: Optional[int]
    access_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def from_orm_with_users(cls, document):
        """Create response with user email information."""
        data = {
            "id": document.id,
            "title": document.title,
            "description": document.description,
            "file_name": document.file_name,
            "file_size": document.file_size,
            "mime_type": document.mime_type,
            "sender_id": document.sender_id,
            "sender_email": document.sender.email if document.sender else None,
            "recipient_id": document.recipient_id,
            "recipient_email": document.recipient.email if document.recipient else None,
            "expires_at": document.expires_at,
            "view_limit": document.view_limit,
            "access_count": document.access_count,
            "status": document.status.value,
            "created_at": document.created_at,
            "updated_at": document.updated_at
        }
        return cls(**data)


class DocumentContentResponse(BaseModel):
    """Schema for document content response (includes encrypted content)."""
    id: str
    title: str
    file_name: str
    mime_type: Optional[str]
    content: str  # Base64 encoded content (will be decrypted before sending)
    access_count: int
    view_limit: Optional[int]
    
    model_config = {"from_attributes": True}