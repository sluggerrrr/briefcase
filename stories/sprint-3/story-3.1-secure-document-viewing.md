# Story 3.1: Secure Document Viewing and Download

**Epic:** Document Access Control & Lifecycle Management
**Story Points:** 5
**Priority:** Must Have (P0)
**Sprint:** 3

## User Story
**As a** recipient user,  
**I want** to securely view and download documents assigned to me,  
**so that** I can access the content while maintaining security and audit compliance.

## Description
Implement secure document viewing and download functionality with proper access controls, decryption, and audit logging. Users should only be able to access documents explicitly assigned to them.

## Acceptance Criteria
1. ⏳ Document download endpoint with access validation (recipient-only access)
2. ⏳ Real-time document decryption using stored encryption keys
3. ⏳ Secure file streaming for large documents without storing decrypted files
4. ⏳ Access validation ensuring only assigned recipients can download
5. ⏳ Document access logging for every view/download attempt
6. ⏳ Support for different document types (PDF, DOC, images, etc.)
7. ⏳ Rate limiting to prevent abuse and brute force attempts
8. ⏳ Temporary download URLs with expiration for security
9. ⏳ Document status tracking (viewed, downloaded, accessed)

## Technical Requirements
- FastAPI endpoint for secure document retrieval
- AES-256 decryption integration from Story 2.2
- Database access control validation
- Streaming response for large files
- Audit logging integration
- JWT authentication for access control

## API Endpoints
```
GET /api/v1/documents/{document_id}/download
- Headers: Authorization (JWT token)
- Response: File stream with appropriate Content-Type
- Status Codes: 200 (success), 403 (forbidden), 404 (not found)

GET /api/v1/documents/{document_id}/view
- Headers: Authorization (JWT token)  
- Response: Document metadata and temporary view URL
- Status Codes: 200 (success), 403 (forbidden), 404 (not found)

GET /api/v1/documents/{document_id}/info
- Headers: Authorization (JWT token)
- Response: Document information without content
- Status Codes: 200 (success), 403 (forbidden), 404 (not found)
```

## Security Requirements
- **Access Control**: Verify user is assigned recipient before allowing access
- **Decryption**: Decrypt document in memory only, never store decrypted files
- **Audit Trail**: Log all access attempts (successful and failed)
- **Rate Limiting**: Prevent abuse with reasonable download limits
- **Token Validation**: Verify JWT token and user permissions
- **Secure Headers**: Include security headers in file responses

## Database Schema Additions
```sql
-- Document access tracking
CREATE TABLE document_access_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    user_id UUID REFERENCES users(id),
    access_type VARCHAR(20) NOT NULL, -- 'view', 'download', 'info'
    access_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL
);

-- Update documents table for access tracking
ALTER TABLE documents 
ADD COLUMN view_count INTEGER DEFAULT 0,
ADD COLUMN download_count INTEGER DEFAULT 0,
ADD COLUMN last_accessed TIMESTAMP;
```

## Error Handling
- **Document Not Found**: Return 404 with clear message
- **Access Denied**: Return 403 when user not authorized
- **Decryption Failed**: Return 500 with generic error message
- **File Corruption**: Return 500 with appropriate error
- **Rate Limit Exceeded**: Return 429 with retry information

## Performance Considerations
- Stream large files to avoid memory issues
- Use database connection pooling
- Implement caching for document metadata
- Optimize decryption for large files
- Monitor response times and file transfer speeds

## Definition of Done
- [ ] Document download endpoint implemented and tested
- [ ] Access control validation working correctly
- [ ] Document decryption integrated and secure
- [ ] Audit logging captures all access attempts
- [ ] Rate limiting prevents abuse
- [ ] Large file streaming works efficiently
- [ ] Error handling covers all edge cases
- [ ] Security headers included in responses
- [ ] Performance tested with various file sizes
- [ ] Integration tests pass for all scenarios

## Blockers/Dependencies
- Story 1.3 (JWT Authentication System Implementation)
- Story 2.1 (Document Data Models)
- Story 2.2 (AES Encryption Implementation)
- Story 2.3 (Document Upload & Assignment)

## Notes
- Consider implementing content disposition headers for proper file downloads
- Ensure MIME type detection works correctly for various file types
- Plan for future virus scanning integration
- Consider implementing download resume functionality for large files
- Monitor and log suspicious access patterns