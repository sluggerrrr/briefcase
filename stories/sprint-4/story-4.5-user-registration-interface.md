# Story 4.5: User Registration Interface with Modal Integration

**Epic:** User Interface & Document Management Dashboard
**Story Points:** 3
**Priority:** High (P1)
**Sprint:** 4

## User Story
**As a** new user,  
**I want** to create an account through a registration modal on the login page,  
**so that** I can gain access to the secure document sharing platform without navigating away from the authentication flow.

## Description
Implement a user registration interface integrated as a modal component on the existing login page, providing a seamless authentication experience where users can switch between login and registration without page navigation.

## Acceptance Criteria
1. ⏳ Registration modal component integrated into the existing login page
2. ⏳ Toggle functionality between "Sign In" and "Sign Up" modes within the same interface
3. ⏳ Registration form with required fields: email, password, confirm password, full name
4. ⏳ Real-time form validation with password strength indicators
5. ⏳ Email format validation and duplicate email checking
6. ⏳ Password confirmation matching validation
7. ⏳ Terms of service and privacy policy acceptance checkbox
8. ⏳ Successful registration automatically logs user in and redirects to dashboard
9. ⏳ Clear error handling for registration failures (email exists, weak password, etc.)
10. ⏳ Accessible design with proper ARIA labels and keyboard navigation
11. ⏳ Mobile-responsive modal design

## Technical Requirements
- Extend existing authentication components
- Use shadcn/ui Dialog component for modal functionality
- React Hook Form for form validation and state management
- Integration with existing AuthContext
- API integration with backend registration endpoint
- Consistent styling with existing login form

## Component Structure
```
src/components/auth/
├── LoginForm.tsx           # Updated to include registration toggle
├── RegistrationForm.tsx    # New registration form component
├── AuthModal.tsx          # New modal wrapper for auth forms
└── ProtectedRoute.tsx     # Existing (no changes needed)

src/pages/auth/
└── login.tsx              # Updated to use AuthModal
```

## UI/UX Design Requirements
- **Modal Integration**: Registration form appears as overlay on login page
- **Seamless Toggle**: Smooth transition between login and registration modes
- **Progressive Disclosure**: Show additional fields only when registering
- **Visual Feedback**: Loading states, success animations, error states
- **Consistent Branding**: Match existing login page design
- **Mobile Optimized**: Full-screen modal on small screens

## Registration Flow
1. User visits login page
2. User clicks "Sign Up" or "Create Account" button
3. Registration modal opens with registration form
4. User fills required fields with real-time validation
5. Password strength indicator provides feedback
6. Email uniqueness checked on blur
7. User accepts terms of service
8. Successful registration creates account and auto-logs user in
9. User redirected to dashboard
10. Error handling shows specific messages for common issues

## Form Fields
- **Email**: Required, email format validation, uniqueness check
- **Full Name**: Required, minimum 2 characters
- **Password**: Required, strength validation (8+ chars, mixed case, numbers, symbols)
- **Confirm Password**: Required, must match password field
- **Terms Acceptance**: Required checkbox for terms of service

## Validation Rules
- **Email**: Valid email format, not already registered
- **Password**: Minimum 8 characters, at least one uppercase, one lowercase, one number
- **Name**: Minimum 2 characters, maximum 50 characters
- **Real-time validation**: Show errors as user types/leaves fields

## API Integration
- **Endpoint**: `POST /auth/register`
- **Request**: `{ email, password, full_name, terms_accepted }`
- **Response**: JWT token for immediate login or error details
- **Error Handling**: Specific messages for duplicate email, weak password, validation errors

## Definition of Done
- [ ] Registration modal renders correctly within login page
- [ ] Toggle between login and registration works smoothly
- [ ] All form fields validate correctly with proper error messages
- [ ] Password strength indicator provides real-time feedback
- [ ] Email uniqueness validation works
- [ ] Successful registration creates user account
- [ ] Auto-login after registration redirects to dashboard
- [ ] Error handling displays user-friendly messages
- [ ] Modal is accessible and keyboard navigable
- [ ] Responsive design works on all devices
- [ ] Terms of service integration completed
- [ ] All registration tests pass

## Blockers/Dependencies
- Story 4.1 (Authentication UI) - Must be completed
- Story 1.3 (JWT Authentication System) - Backend registration endpoint
- Terms of Service and Privacy Policy pages (can be placeholder links initially)

## Notes
- Use existing shadcn/ui components for consistency
- Consider password strength libraries (zxcvbn) for security
- Plan for future email verification workflow
- Keep registration simple - avoid asking for too much information initially
- Consider social registration options for future enhancement