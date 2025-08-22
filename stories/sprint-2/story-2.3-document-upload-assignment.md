# Story 2.3: Document Upload and Recipient Assignment

**Epic:** Document Security & Storage System
**Story Points:** 5
**Priority:** Must Have (P0)
**Sprint:** 2

## User Story
**As a** user,  
**I want** to upload documents and assign them to specific recipients with security parameters,  
**so that** I can securely share sensitive documents with controlled access.

## Description
Implement document upload functionality with recipient assignment, security parameter configuration (view limits, expiration), and proper validation.

## Acceptance Criteria
1. ⏳ Document upload endpoint created (`POST /api/documents/upload`) with multipart form support
2. ⏳ Base64 file content encoding and validation implemented for development purposes
3. ⏳ Recipient selection from authenticated user list with validation
4. ⏳ Optional view limit configuration (1-10 views) with default values
5. ⏳ Optional expiration date setting with validation (future dates only, maximum 1 year)
6. ⏳ File type validation and reasonable size limits (e.g., 10MB max for base64)
7. ⏳ Document title and description metadata capture
8. ⏳ Comprehensive upload success/error responses with detailed feedback
9. ⏳ Upload progress tracking and error recovery mechanisms

## Technical Requirements
- FastAPI multipart form handling
- Base64 content encoding for development
- File size and type validation
- Recipient validation against user database
- Security parameter validation
- Comprehensive error handling

## API Endpoint Specification
```
POST /api/documents/upload
Content-Type: application/json
Authorization: Bearer <jwt_token>

Request Body:
{
  "title": "Confidential Report Q4 2024",
  "description": "Quarterly financial report - confidential",
  "recipient_id": "uuid-of-recipient-user",
  "content": "base64-encoded-file-content",
  "content_type": "application/pdf",
  "filename": "report-q4-2024.pdf",
  "view_limit": 3,  // Optional: 1-10 views
  "expires_at": "2024-12-31T23:59:59Z"  // Optional: future date
}

Response (201 Created):
{
  "id": "document-uuid",
  "title": "Confidential Report Q4 2024",
  "status": "active",
  "recipient": {
    "id": "recipient-uuid",
    "email": "recipient@company.com"
  },
  "view_limit": 3,
  "access_count": 0,
  "expires_at": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Validation Rules
- **Title**: Required, 1-255 characters
- **Description**: Optional, max 1000 characters
- **Recipient**: Must be valid user ID, cannot be sender
- **Content**: Base64 encoded, max 10MB decoded size
- **View Limit**: Optional, 1-10 views, default unlimited
- **Expiration**: Optional, future date, max 1 year from now
- **File Type**: Configurable allowed types (PDF, DOC, TXT, images)

## Security Features
- **Automatic Encryption**: Content encrypted before storage
- **Access Control**: Only sender and recipient can access
- **Audit Logging**: All upload attempts logged
- **Validation**: Comprehensive input validation
- **Rate Limiting**: Prevent abuse of upload endpoint

## Definition of Done
- [ ] Upload endpoint accepts multipart/form data
- [ ] Base64 content handling works correctly
- [ ] Recipient validation prevents invalid assignments
- [ ] View limits and expiration validation working
- [ ] File size and type validation implemented
- [ ] Success/error responses comprehensive
- [ ] Upload logging and audit trail
- [ ] All upload tests pass

## Blockers/Dependencies
- Story 2.1 (Document Data Models and Metadata Management)
- Story 2.2 (AES Encryption Implementation and Key Management)
- Story 1.4 (User Management and Test Data Seeding)

## Notes
- Start with base64 encoding for simplicity
- Plan for future file upload (multipart) support
- Implement virus scanning in future iterations
- Consider compression for large text documents
- Add upload progress tracking for large files