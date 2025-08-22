# Story 2.1: Document Data Models and Metadata Management

**Epic:** Document Security & Storage System
**Story Points:** 5
**Priority:** Must Have (P0)
**Sprint:** 2

## User Story
**As a** developer,  
**I want** to create comprehensive document data models and metadata management,  
**so that** we can track document lifecycle, ownership, and access controls effectively.

## Description
Create database models for documents and document access tracking, including proper relationships, constraints, and status management for the secure document delivery system.

## Acceptance Criteria
1. ⏳ Document model created with fields: id, title, sender_id, recipient_id, created_at, expires_at, view_limit, access_count, status, encrypted_content
2. ⏳ Document-to-User relationship models established with proper foreign key constraints
3. ⏳ Document status enumeration implemented (active, expired, view_exhausted, deleted)
4. ⏳ Database migrations created for document schema with proper indexes
5. ⏳ Document metadata CRUD operations implemented with authorization checks
6. ⏳ Document ownership validation ensuring only sender can modify metadata
7. ⏳ Document status calculation logic based on expiration date and view count

## Technical Requirements
- SQLAlchemy models with proper relationships
- UUID primary keys for security
- Proper foreign key constraints
- Database indexes for performance
- Status enumeration with validation
- Comprehensive metadata tracking

## Database Schema
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    sender_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recipient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    encrypted_content TEXT NOT NULL,
    encryption_key_id VARCHAR(255) NOT NULL,
    view_limit INTEGER CHECK (view_limit > 0 AND view_limit <= 10),
    access_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'view_exhausted', 'deleted')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE document_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    access_type VARCHAR(20) NOT NULL CHECK (access_type IN ('view', 'download', 'metadata')),
    success BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Model Features
- **Document Status Logic**: Automatic status calculation based on view limits and expiration
- **Access Tracking**: Complete audit trail for all document interactions
- **Security Validation**: Ownership and permission checks at model level
- **Metadata Management**: Rich metadata with description, limits, and timing

## Definition of Done
- [ ] Document model created with all required fields
- [ ] Document access model for audit trail
- [ ] Database migrations run successfully
- [ ] All relationships and constraints work
- [ ] Status calculation logic implemented
- [ ] Authorization checks in place
- [ ] Performance indexes created
- [ ] Model tests pass

## Blockers/Dependencies
- Story 1.2 (Database Setup and User Data Models)

## Notes
- Use CASCADE deletes carefully for data integrity
- Implement soft delete for documents (status = 'deleted')
- Consider partitioning for document_access table at scale
- Add database triggers for automatic timestamp updates