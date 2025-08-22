# Story 1.4: User Management and Test Data Seeding

**Epic:** Foundation & Authentication Infrastructure
**Story Points:** 3
**Priority:** Must Have (P0)
**Sprint:** 1

## User Story
**As a** developer,  
**I want** to implement user registration functionality and seed test users,  
**so that** we have authenticated users available for document sharing operations testing.

## Description
Create user registration endpoints, user profile management, and seed test users for development and testing purposes.

## Acceptance Criteria
1. ⏳ User registration endpoint created (`POST /api/auth/register`) with input validation
2. ⏳ Email format validation and duplicate email prevention implemented
3. ⏳ Database seeding script created with 2-3 test users (different roles/departments for testing)
4. ⏳ User profile retrieval endpoint implemented (`GET /api/users/me`) for authenticated users
5. ⏳ Basic user listing endpoint (`GET /api/users`) for recipient selection functionality
6. ⏳ User password update functionality with current password verification
7. ⏳ Account status management (active/inactive) with appropriate access controls

## Technical Requirements
- Input validation with Pydantic schemas
- Duplicate email prevention
- Password strength validation
- User profile management
- Test data seeding script
- Proper error handling

## API Endpoints
```
POST /api/auth/register
- Input: {"email": "new@example.com", "password": "password123"}
- Output: {"message": "User created successfully", "user": {...}}

GET /api/users/me
- Headers: Authorization: Bearer <token>
- Output: {"id": "uuid", "email": "user@example.com", ...}

GET /api/users
- Headers: Authorization: Bearer <token>
- Output: [{"id": "uuid", "email": "user1@example.com"}, ...]

PUT /api/users/me/password
- Input: {"current_password": "old", "new_password": "new"}
- Output: {"message": "Password updated successfully"}
```

## Test Users to Seed
1. **Alice (sender@company.com)** - Primary document sender
2. **Bob (recipient@company.com)** - Primary document recipient  
3. **Carol (admin@company.com)** - Admin user for testing

## Definition of Done
- [ ] User registration works with validation
- [ ] Test users seeded successfully
- [ ] User profile endpoints functional
- [ ] User listing works for recipient selection
- [ ] Password update functionality works
- [ ] Account status management implemented
- [ ] All user management tests pass

## Blockers/Dependencies
- Story 1.3 (JWT Authentication System Implementation)

## Notes
- Use strong password validation
- Prevent user enumeration attacks
- Log user registration attempts
- Create seeding script for easy database reset