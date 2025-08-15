# User Soft Delete Feature - Product Requirements Document

## Executive Summary

Enable proper user lifecycle management through a three-state system: Active, Deactivated, and Soft Deleted. This feature enhances user management by providing reversible deactivation and permanent (but recoverable) soft deletion capabilities.

## Feature Overview

Transform the current binary user state system into a comprehensive user lifecycle management feature that allows administrators to temporarily deactivate users, reactivate them, or permanently remove them from the active system while maintaining data integrity.

## User Stories

### Story 1: Deactivate User
**As an** Administrator  
**I want to** temporarily deactivate a user account  
**So that** I can prevent access without losing user data or history

**Acceptance Criteria:**
- Yellow "Deactivate" button visible for all active users
- Cannot deactivate users with pending or in-progress service orders
- Show warning modal when service orders constraint violated
- Clicking deactivate immediately disables user login
- User's status changes to "Deactivated" in the database
- Deactivated users cannot log in
- User's historical data remains intact
- Action is logged in audit trail

### Story 2: Reactivate User
**As an** Administrator  
**I want to** reactivate a previously deactivated user  
**So that** I can restore access for returning employees or corrected mistakes

**Acceptance Criteria:**
- Green "Activate" button replaces yellow button for deactivated users
- Clicking activate immediately restores user access
- User can log in with existing credentials
- All previous permissions and settings are restored
- Action is logged in audit trail

### Story 3: Soft Delete User
**As an** Administrator  
**I want to** permanently remove a user from the active system  
**So that** I can clean up the user interface while maintaining data integrity

**Acceptance Criteria:**
- Red "Delete" button appears as rightmost action for all users
- Cannot delete users with pending or in-progress service orders
- Show warning modal when service orders constraint violated
- Clicking delete triggers confirmation modal
- Modal clearly warns about permanent removal
- Confirming soft deletes the user
- Soft deleted users disappear from UI
- User data remains in database with deleted flag
- Action is logged in audit trail

### Story 4: Confirmation Modal
**As an** Administrator  
**I want to** confirm deletion actions  
**So that** I can prevent accidental permanent deletions

**Acceptance Criteria:**
- Modal appears on delete button click
- Modal displays user's name and email
- Clear warning message about permanent action
- "Cancel" and "Confirm Delete" buttons
- Cancel closes modal with no changes
- Confirm executes soft delete
- Modal prevents background interaction

## Technical Requirements

### Database Schema Changes
```sql
-- Add to users table
ALTER TABLE users ADD COLUMN is_deleted BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN deleted_by INTEGER NULL;

-- Update indexes for performance
CREATE INDEX idx_users_active ON users(is_active, is_deleted);
```

### API Endpoints

#### Update Existing
- `PUT /api/users/{id}/deactivate` - Deactivate user (set is_active = 0)
  - Validates no pending/in-progress service orders
  - Returns 409 Conflict if service orders exist
- `PUT /api/users/{id}/activate` - Activate user (set is_active = 1)

#### New Endpoints
- `DELETE /api/users/{id}/soft-delete` - Soft delete user (set is_deleted = 1)
  - Validates no pending/in-progress service orders
  - Returns 409 Conflict if service orders exist
- `GET /api/users` - Modified to exclude soft deleted by default
- `GET /api/users?include_deleted=true` - Include soft deleted (admin only)

### Frontend Changes

#### User Management Table

- Replace single delete button with button group containing:
  1. **Conditional State Button**: Yellow "Deactivate" (active users) / Green "Activate" (deactivated users)
  2. **Delete Button**: Red "Delete" (always visible, rightmost)
- **Button Group Structure**:
  ```html
  <div class="btn-group" role="group" aria-label="User actions">
    <!-- Conditional button -->
    <button class="btn btn--sm btn--warning" aria-label="Deactivate user">
      <svg class="icon icon--sm" aria-hidden="true"><use href="#icon-pause"></use></svg>
      Deactivate
    </button>
    <!-- OR -->
    <button class="btn btn--sm btn--success" aria-label="Activate user">
      <svg class="icon icon--sm" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
      Activate
    </button>
    <!-- Delete button -->
    <button class="btn btn--sm btn--danger" aria-label="Delete user">
      <svg class="icon icon--sm" aria-hidden="true"><use href="#icon-trash"></use></svg>
      Delete
    </button>
  </div>
  ```
- **Spacing**: Use `var(--space-xs)` (4px) between buttons
- **Size**: Use `.btn--sm` for table actions

#### Confirmation Modal

```html
<div class="modal" role="dialog" aria-labelledby="delete-modal-title" aria-modal="true">
  <div class="modal__backdrop" aria-hidden="true"></div>
  <div class="modal__content">
    <div class="modal__header">
      <h2 class="modal__title" id="delete-modal-title">
        <svg class="icon icon--md icon--danger" aria-hidden="true"><use href="#icon-exclamation-triangle"></use></svg>
        Confirm User Deletion
      </h2>
    </div>
    <div class="modal__body">
      <p>Are you sure you want to permanently delete <strong>{username}</strong>?</p>
      <div class="alert alert--warning">
        <svg class="icon alert__icon" aria-hidden="true"><use href="#icon-info-circle"></use></svg>
        <div class="alert__content">
          This user will no longer appear in the system, though their data will be preserved for audit purposes.
        </div>
      </div>
    </div>
    <div class="modal__footer">
      <button class="btn btn--secondary" data-action="cancel">Cancel</button>
      <button class="btn btn--danger" data-action="confirm">
        <svg class="icon icon--sm" aria-hidden="true"><use href="#icon-trash"></use></svg>
        Confirm Delete
      </button>
    </div>
  </div>
</div>
```

## UI/UX Specifications

### Button States

- **Deactivate Button**
  - Color: `var(--color-warning)` (#FFC107)
  - Icon: SVG from centralized sprite - `<svg class="icon icon--sm" aria-hidden="true"><use href="#icon-pause"></use></svg>`
  - Text: "Deactivate"
  - Hover: `var(--color-warning)` darkened by 100 (#E0A800)
  - Class: `btn btn--warning`

- **Activate Button**
  - Color: `var(--color-success)` (#28A745)
  - Icon: SVG from centralized sprite - `<svg class="icon icon--sm" aria-hidden="true"><use href="#icon-check-circle"></use></svg>`
  - Text: "Activate"
  - Hover: `var(--color-success)` darkened by 100 (#218838)
  - Class: `btn btn--success`

- **Delete Button**
  - Color: `var(--color-danger)` (#DC3545)
  - Icon: SVG from centralized sprite - `<svg class="icon icon--sm" aria-hidden="true"><use href="#icon-trash"></use></svg>`
  - Text: "Delete"
  - Position: Always rightmost in button group
  - Hover: `var(--color-danger)` darkened by 100 (#C82333)
  - Class: `btn btn--danger`

### Modal Design

- **Container**: Use `.modal` class structure from style guide
- **Width**: `max-width: 500px` (per style guide modal spec)
- **Background**: `var(--color-neutral-0)` with `var(--shadow-xl)`
- **Backdrop**: `.modal__backdrop` with `rgba(0, 0, 0, 0.5)` and `backdrop-filter: blur(2px)`
- **Border Radius**: `var(--radius-xl)` (12px)
- **Animation**: Use `var(--duration-base)` (250ms) with `var(--ease-out)`
- **Close Actions**: Confirm button, Cancel button, or Escape key
- **Focus Management**: Trap focus within modal when open

## Security & Permissions

### Access Control
- Admin and Manager roles can deactivate/activate/delete users
- Users cannot deactivate/delete themselves
- Super admin account cannot be deleted
- Audit all state changes with timestamp and actor
- Service orders constraint validation enforced for both roles

### Data Protection
- Soft deleted users' data remains queryable for reports
- Personal data remains encrypted
- Sessions invalidated on deactivation/deletion
- API tokens revoked on state change

## Edge Cases & Error Handling

### Edge Cases
1. **Self-deletion attempt**: Show error "You cannot delete your own account"
2. **Last admin deletion**: Prevent if user is last active admin
3. **Active sessions**: Force logout on deactivation/deletion
4. **Pending service orders**: Block deactivation/deletion if user has open service orders
5. **Service orders constraint**: Show warning modal for both deactivate and delete operations
6. **Cascade effects**: Handle related data (assignments, permissions)

### Error Messages

- "Unable to deactivate user: User has pending or in-progress service orders"
- "Unable to delete user: User has pending or in-progress service orders"
- "Operation failed: Insufficient permissions"
- "Network error: Please try again"

**Error Display Format**:
```html
<div class="alert alert--danger" role="alert">
  <svg class="icon alert__icon" aria-hidden="true"><use href="#icon-x-circle"></use></svg>
  <div class="alert__content">
    <div class="alert__title">Operation Failed</div>
    {Error message text}
  </div>
</div>
```

**Service Orders Constraint Modal**:
```html
<div class="modal" role="dialog" aria-labelledby="constraint-modal-title" aria-modal="true">
  <div class="modal__backdrop" aria-hidden="true"></div>
  <div class="modal__content">
    <div class="modal__header">
      <h2 class="modal__title" id="constraint-modal-title">
        <svg class="icon icon--md icon--warning" aria-hidden="true"><use href="#icon-exclamation-triangle"></use></svg>
        Cannot Modify User
      </h2>
    </div>
    <div class="modal__body">
      <p><strong>{username}</strong> has pending or in-progress service orders and cannot be deactivated or deleted.</p>
      <div class="alert alert--info">
        <svg class="icon alert__icon" aria-hidden="true"><use href="#icon-info-circle"></use></svg>
        <div class="alert__content">
          Complete or reassign all service orders before modifying this user account.
        </div>
      </div>
    </div>
    <div class="modal__footer">
      <button class="btn btn--primary" data-action="close">Understood</button>
    </div>
  </div>
</div>
```

## Implementation Phases

### Phase 1: Backend Infrastructure

- Database schema updates
- API endpoint implementation
- Audit logging setup

### Phase 2: Frontend UI

- Button group implementation with centralized SVG sprite system
- State management logic with service orders validation
- Visual feedback system using design tokens
- Service orders constraint modal implementation
- Add required SVG icons to centralized sprite if missing:
  - `#icon-pause` for deactivate
  - `#icon-trash` for delete
  - `#icon-check-circle` for activate (already exists)
  - `#icon-exclamation-triangle` for warning (already exists)

### Phase 3: Modal & Confirmation

- Modal component creation following `.modal` structure
- Confirmation flow with proper ARIA attributes
- Keyboard navigation with focus trap
- Animation using CSS variables for timing

### Phase 4: Testing & Polish

- End-to-end testing
- Permission testing
- Accessibility audit (WCAG AA compliance)
- Animation respecting `prefers-reduced-motion`

## Success Metrics

### Quantitative

- 0% accidental deletions (tracked via support tickets)
- <2 seconds for all state changes
- 100% audit trail coverage
- <0.1% error rate on operations
- WCAG AA compliance score
- All animations at 60fps

### Qualitative

- Improved admin confidence in user management
- Reduced support tickets for user access issues
- Clear understanding of user states through visual indicators
- Simplified offboarding process
- Consistent with CVD design system patterns

## Testing Requirements

### Unit Tests

- Database state transitions
- Permission checks
- API endpoint validation
- Audit logging

### Integration Tests

- Full deactivate/activate cycle
- Soft delete with confirmation
- Session invalidation
- Permission inheritance

### UI Tests

- Button state changes
- Modal interactions
- Keyboard navigation (focus trap in modal)
- Error message display with proper ARIA alerts
- Icon rendering and accessibility

### User Acceptance Tests

- Admin can deactivate and reactivate users
- Confirmation prevents accidental deletion
- Soft deleted users don't appear in UI
- Audit trail shows all actions
- Keyboard-only navigation works throughout
- Screen reader announces state changes

## Migration Strategy

### Data Migration
- Set is_deleted = 0 for all existing users
- No data loss during migration
- Backup before migration

### Rollback Plan
- Feature flag for new functionality
- Database changes are backward compatible
- Can disable via configuration

## Documentation Requirements

### Admin Guide
- How to deactivate/activate users
- Understanding user states
- Soft delete implications
- Audit trail access

### API Documentation
- Endpoint specifications
- Response formats
- Error codes
- Authentication requirements

## Dependencies

### Technical Dependencies
- Flask backend with SQLAlchemy
- Existing authentication system
- Audit logging module
- Session management

### Team Dependencies
- Backend development team
- Frontend development team
- QA team for testing
- DevOps for deployment

## Timeline Estimate
- Week 1-2: Backend implementation
- Week 2-3: Frontend development
- Week 3-4: Testing and refinement
- Week 4: Documentation and deployment

## Risk Assessment

### Technical Risks
- **Data integrity**: LOW - Soft delete preserves data
- **Performance impact**: LOW - Indexed queries
- **Security vulnerabilities**: MEDIUM - Requires careful permission checks

### Business Risks
- **User confusion**: LOW - Clear visual indicators
- **Accidental deletion**: LOW - Confirmation modal
- **Compliance issues**: LOW - Audit trail maintained

## Appendix

### Visual Implementation Notes

#### Color Palette Usage
- **Warning (Deactivate)**: `var(--color-warning)` #FFC107
- **Success (Activate)**: `var(--color-success)` #28A745
- **Danger (Delete)**: `var(--color-danger)` #DC3545
- **Modal Backdrop**: `rgba(0, 0, 0, 0.5)`
- **Button Hover States**: Darken by 100 in color scale

#### Required SVG Icons
Ensure these icons are available in the centralized SVG sprite system:
- `#icon-pause` - Deactivate action
- `#icon-check-circle` - Activate action (exists)
- `#icon-trash` - Delete action
- `#icon-exclamation-triangle` - Warning in modal (exists)
- `#icon-info-circle` - Info alerts (exists)
- `#icon-x-circle` - Error states (exists)

**Implementation Notes:**
- All icons must use the centralized SVG sprite system
- Icons are decorative and should include `aria-hidden="true"`
- Consistent sizing with `.icon--sm` class for buttons
- Follow existing CVD icon implementation patterns

#### Container Configuration
- User Management page should use `container--narrow` class (768px max-width)
- Modal uses standard modal sizing (500px max-width)

#### Accessibility Checklist
- [ ] All buttons have appropriate ARIA labels
- [ ] Modal has proper ARIA attributes (role, labelledby, modal)
- [ ] Focus trap implemented in modal
- [ ] Keyboard navigation fully functional
- [ ] Screen reader announcements for state changes
- [ ] Color contrast meets WCAG AA (4.5:1 for normal text)
- [ ] Icons are decorative with aria-hidden="true"
- [ ] Respects prefers-reduced-motion setting

### Current State Screenshot
[Placeholder for current user management interface]

### Proposed State Mockup
[Placeholder for new button group design with SVG icons]

### Database ERD
[Placeholder for entity relationship diagram]