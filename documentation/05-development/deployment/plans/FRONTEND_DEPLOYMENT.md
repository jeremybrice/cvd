# Frontend Deployment Plan: User Soft Delete Feature
*CVD Application - User Management Enhancement*

## Executive Summary

This document outlines the comprehensive frontend implementation strategy for the user soft delete feature in the CVD application. The plan details specific changes to the user management table, modal components, state management, and user experience enhancements required to support the three-state user lifecycle: Active, Deactivated, and Soft Deleted.

## Prerequisites & Dependencies

### Technical Requirements
- CVD application with existing user-management.html page
- Centralized SVG sprite system at `/icons/svg-sprite.svg`
- Design system CSS at `/css/design-system.css`
- CVDApi class in `/api.js`
- Authentication system with session management

### Backend Dependencies
- New API endpoints: `PUT /api/users/{id}/deactivate`, `PUT /api/users/{id}/activate`, `DELETE /api/users/{id}/soft-delete`
- Database schema updates with `is_deleted`, `deleted_at`, `deleted_by` fields
- Service order constraint validation logic

## Phase 1: SVG Icon Verification & Updates

### 1.1 Icon Inventory Check
The existing SVG sprite already contains the required icons:
- ✅ `#icon-pause` - For deactivate action
- ✅ `#icon-trash` - For delete action  
- ✅ `#icon-check-circle` - For activate action
- ✅ `#icon-exclamation-triangle` - For warning modals
- ✅ `#icon-info-circle` - For info alerts
- ✅ `#icon-x-circle` - For error states

### 1.2 Icon Usage Pattern
All icons follow the centralized sprite system pattern:
```html
<svg class="icon icon--sm" aria-hidden="true">
  <use href="/icons/svg-sprite.svg#icon-name"></use>
</svg>
```

## Phase 2: CSS Design Token Integration

### 2.1 Button Group Styling
Add the following CSS to support button groups in user-management.html:

```css
/* Button Group Component */
.btn-group {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs); /* 4px spacing between buttons */
  border-radius: var(--radius-md);
}

.btn-group .btn {
  border-radius: 0;
  margin: 0;
  position: relative;
  z-index: 1;
}

.btn-group .btn:first-child {
  border-top-left-radius: var(--radius-md);
  border-bottom-left-radius: var(--radius-md);
}

.btn-group .btn:last-child {
  border-top-right-radius: var(--radius-md);
  border-bottom-right-radius: var(--radius-md);
}

.btn-group .btn:hover,
.btn-group .btn:focus {
  z-index: 2;
}

/* Button State Styles */
.btn--warning {
  background-color: var(--color-warning);
  color: var(--color-warning-text);
  border: 1px solid var(--color-warning);
}

.btn--warning:hover {
  background-color: #e0a800; /* Warning darkened by 100 */
  border-color: #e0a800;
}

.btn--success {
  background-color: var(--color-success);
  color: white;
  border: 1px solid var(--color-success);
}

.btn--success:hover {
  background-color: #218838; /* Success darkened by 100 */
  border-color: #218838;
}

/* Icon Sizing */
.icon--sm {
  width: 16px;
  height: 16px;
}

.icon--md {
  width: 20px;
  height: 20px;
}

/* Icon Colors for Semantic States */
.icon--danger {
  color: var(--color-danger);
}

.icon--warning {
  color: var(--color-warning);
}

.icon--success {
  color: var(--color-success);
}
```

### 2.2 Modal Enhancement Styles
Add enhanced modal styles for confirmation and constraint modals:

```css
/* Enhanced Modal Styles */
.modal__backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  z-index: var(--z-modal, 1000);
}

.modal__content {
  position: relative;
  background: var(--color-neutral-0);
  border-radius: var(--radius-xl, 12px);
  box-shadow: var(--shadow-xl, 0 25px 50px rgba(0, 0, 0, 0.25));
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn var(--duration-base, 250ms) var(--ease-out, ease-out);
}

@keyframes modalSlideIn {
  from {
    transform: scale(0.95) translateY(-10px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

.modal__header {
  padding: var(--space-lg) var(--space-lg) 0;
}

.modal__title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin: 0;
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-neutral-900);
}

.modal__body {
  padding: var(--space-lg);
}

.modal__footer {
  padding: 0 var(--space-lg) var(--space-lg);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

/* Alert Component */
.alert {
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  border: 1px solid;
  margin: var(--space-md) 0;
}

.alert--warning {
  background-color: var(--color-warning-bg);
  border-color: var(--color-warning-border);
  color: var(--color-warning-text);
}

.alert--info {
  background-color: var(--color-info-bg);
  border-color: var(--color-info-border);
  color: var(--color-info-text);
}

.alert--danger {
  background-color: var(--color-danger-bg);
  border-color: var(--color-danger-border);
  color: var(--color-danger-text);
}

.alert__icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.alert__content {
  flex: 1;
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
}

.alert__title {
  font-weight: var(--font-medium);
  margin-bottom: var(--space-xs);
}

/* Accessibility Enhancements */
@media (prefers-reduced-motion: reduce) {
  .modal__content {
    animation: none;
  }
}

/* Focus Management */
.modal:focus-within .modal__content {
  outline: var(--focus-width, 2px) solid var(--color-primary-500);
  outline-offset: -2px;
}
```

## Phase 3: HTML Structure Updates

### 3.1 SVG Sprite Integration
Add SVG sprite inclusion to the user-management.html head section:

```html
<!-- Add after existing styles -->
<script>
  // Load SVG sprite inline for better performance
  fetch('/icons/svg-sprite.svg')
    .then(response => response.text())
    .then(data => {
      const div = document.createElement('div');
      div.innerHTML = data;
      div.style.display = 'none';
      document.body.insertBefore(div, document.body.firstChild);
    });
</script>
```

### 3.2 Enhanced Action Buttons Structure
Replace the current action buttons section in the `createUserRow` function:

```html
<!-- Current action buttons (to be replaced) -->
<div class="action-buttons">
  <button class="btn btn-sm btn-secondary" onclick="editUser(${user.id})">Edit</button>
  <button class="btn btn-sm btn-secondary" onclick="resetPassword(${user.id})">Reset</button>
  <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">Delete</button>
</div>

<!-- New button group structure -->
<div class="action-buttons">
  <button class="btn btn--sm btn-secondary" onclick="editUser(${user.id})" 
          aria-label="Edit user ${user.username}">
    <svg class="icon icon--sm" aria-hidden="true">
      <use href="/icons/svg-sprite.svg#icon-pencil"></use>
    </svg>
    Edit
  </button>
  <button class="btn btn--sm btn-secondary" onclick="resetPassword(${user.id})"
          aria-label="Reset password for ${user.username}">
    <svg class="icon icon--sm" aria-hidden="true">
      <use href="/icons/svg-sprite.svg#icon-key"></use>
    </svg>
    Reset
  </button>
  <div class="btn-group" role="group" aria-label="User state actions for ${user.username}">
    ${getStateActionButton(user)}
    <button class="btn btn--sm btn--danger" onclick="confirmDeleteUser(${user.id})"
            aria-label="Delete user ${user.username}">
      <svg class="icon icon--sm" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-trash"></use>
      </svg>
      Delete
    </button>
  </div>
</div>
```

### 3.3 Modal Components
Add the new modal components to the HTML before the closing body tag:

```html
<!-- Service Orders Constraint Modal -->
<div class="modal" id="constraintModal" role="dialog" aria-labelledby="constraint-modal-title" aria-modal="true">
  <div class="modal__backdrop" aria-hidden="true"></div>
  <div class="modal__content">
    <div class="modal__header">
      <h2 class="modal__title" id="constraint-modal-title">
        <svg class="icon icon--md icon--warning" aria-hidden="true">
          <use href="/icons/svg-sprite.svg#icon-exclamation-triangle"></use>
        </svg>
        Cannot Modify User
      </h2>
    </div>
    <div class="modal__body">
      <p><strong id="constraintUsername"></strong> has pending or in-progress service orders and cannot be deactivated or deleted.</p>
      <div class="alert alert--info">
        <svg class="icon alert__icon" aria-hidden="true">
          <use href="/icons/svg-sprite.svg#icon-info-circle"></use>
        </svg>
        <div class="alert__content">
          Complete or reassign all service orders before modifying this user account.
        </div>
      </div>
    </div>
    <div class="modal__footer">
      <button class="btn btn--primary" data-action="close" onclick="closeModal('constraintModal')">
        Understood
      </button>
    </div>
  </div>
</div>

<!-- Enhanced Delete Confirmation Modal -->
<div class="modal" id="deleteConfirmModal" role="dialog" aria-labelledby="delete-modal-title" aria-modal="true">
  <div class="modal__backdrop" aria-hidden="true"></div>
  <div class="modal__content">
    <div class="modal__header">
      <h2 class="modal__title" id="delete-modal-title">
        <svg class="icon icon--md icon--danger" aria-hidden="true">
          <use href="/icons/svg-sprite.svg#icon-exclamation-triangle"></use>
        </svg>
        Confirm User Deletion
      </h2>
    </div>
    <div class="modal__body">
      <p>Are you sure you want to permanently delete <strong id="deleteConfirmUsername"></strong>?</p>
      <div class="alert alert--warning">
        <svg class="icon alert__icon" aria-hidden="true">
          <use href="/icons/svg-sprite.svg#icon-info-circle"></use>
        </svg>
        <div class="alert__content">
          This user will no longer appear in the system, though their data will be preserved for audit purposes.
        </div>
      </div>
    </div>
    <div class="modal__footer">
      <button class="btn btn--secondary" data-action="cancel" onclick="closeModal('deleteConfirmModal')">
        Cancel
      </button>
      <button class="btn btn--danger" data-action="confirm" id="confirmDeleteBtn">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="/icons/svg-sprite.svg#icon-trash"></use>
        </svg>
        Confirm Delete
      </button>
    </div>
  </div>
</div>
```

## Phase 4: JavaScript Implementation

### 4.1 Enhanced API Integration
Add the new API methods to handle user state changes. Since the CVDApi class already exists, extend it with these methods:

```javascript
// Add these methods to the existing CVDApi class or extend it
class CVDApi {
  // ... existing methods

  async deactivateUser(userId) {
    return await this.makeRequest('PUT', `/users/${userId}/deactivate`);
  }

  async activateUser(userId) {
    return await this.makeRequest('PUT', `/users/${userId}/activate`);
  }

  async softDeleteUser(userId) {
    return await this.makeRequest('DELETE', `/users/${userId}/soft-delete`);
  }

  async getUserServiceOrders(userId) {
    return await this.makeRequest('GET', `/users/${userId}/service-orders`);
  }
}
```

### 4.2 Enhanced User Row Generation
Replace the `createUserRow` function with the enhanced version:

```javascript
function createUserRow(user) {
  const row = document.createElement('tr');
  row.dataset.userId = user.id;
  
  row.innerHTML = `
    <td>
      <input type="checkbox" class="row-checkbox" data-user-id="${user.id}"
             aria-label="Select user ${escapeHtml(user.username)}">
    </td>
    <td>${escapeHtml(user.username)}</td>
    <td>${escapeHtml(user.email)}</td>
    <td>
      <span class="role-badge role-${user.role}">${user.role}</span>
    </td>
    <td>
      ${getStatusIndicator(user)}
    </td>
    <td>${formatDate(user.last_login)}</td>
    <td>${user.failed_login_attempts || 0}</td>
    <td>
      <div class="action-buttons">
        <button class="btn btn--sm btn-secondary" onclick="editUser(${user.id})" 
                aria-label="Edit user ${escapeHtml(user.username)}">
          <svg class="icon icon--sm" aria-hidden="true">
            <use href="/icons/svg-sprite.svg#icon-pencil"></use>
          </svg>
          Edit
        </button>
        <button class="btn btn--sm btn-secondary" onclick="resetPassword(${user.id})"
                aria-label="Reset password for ${escapeHtml(user.username)}">
          <svg class="icon icon--sm" aria-hidden="true">
            <use href="/icons/svg-sprite.svg#icon-key"></use>
          </svg>
          Reset
        </button>
        <div class="btn-group" role="group" aria-label="User state actions for ${escapeHtml(user.username)}">
          ${getStateActionButton(user)}
          <button class="btn btn--sm btn--danger" onclick="confirmDeleteUser(${user.id})"
                  aria-label="Delete user ${escapeHtml(user.username)}">
            <svg class="icon icon--sm" aria-hidden="true">
              <use href="/icons/svg-sprite.svg#icon-trash"></use>
            </svg>
            Delete
          </button>
        </div>
      </div>
    </td>
  `;
  
  // Add checkbox event listener
  const checkbox = row.querySelector('.row-checkbox');
  checkbox.addEventListener('change', handleRowSelection);
  
  return row;
}

function getStateActionButton(user) {
  if (user.is_active) {
    return `
      <button class="btn btn--sm btn--warning" onclick="confirmDeactivateUser(${user.id})"
              aria-label="Deactivate user ${escapeHtml(user.username)}">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="/icons/svg-sprite.svg#icon-pause"></use>
        </svg>
        Deactivate
      </button>
    `;
  } else {
    return `
      <button class="btn btn--sm btn--success" onclick="confirmActivateUser(${user.id})"
              aria-label="Activate user ${escapeHtml(user.username)}">
        <svg class="icon icon--sm" aria-hidden="true">
          <use href="/icons/svg-sprite.svg#icon-check-circle"></use>
        </svg>
        Activate
      </button>
    `;
  }
}
```

### 4.3 User State Management Functions
Add the new functions to handle user state changes:

```javascript
async function confirmDeactivateUser(userId) {
  const user = users.find(u => u.id === userId);
  if (!user) return;
  
  try {
    // Check for service orders constraint
    const serviceOrders = await api.getUserServiceOrders(userId);
    
    if (serviceOrders.pending_count > 0 || serviceOrders.in_progress_count > 0) {
      showConstraintModal(user.username);
      return;
    }
    
    // Proceed with deactivation
    await api.deactivateUser(userId);
    
    showSuccess(`User ${user.username} has been deactivated`);
    announceToScreenReader(`User ${user.username} deactivated`);
    loadUsers(); // Refresh the table
    
  } catch (error) {
    if (error.message.includes('service orders')) {
      showConstraintModal(user.username);
    } else {
      showError('Failed to deactivate user: ' + error.message);
    }
  }
}

async function confirmActivateUser(userId) {
  const user = users.find(u => u.id === userId);
  if (!user) return;
  
  try {
    await api.activateUser(userId);
    
    showSuccess(`User ${user.username} has been activated`);
    announceToScreenReader(`User ${user.username} activated`);
    loadUsers(); // Refresh the table
    
  } catch (error) {
    showError('Failed to activate user: ' + error.message);
  }
}

async function confirmDeleteUser(userId) {
  const user = users.find(u => u.id === userId);
  if (!user) return;
  
  try {
    // Check for service orders constraint
    const serviceOrders = await api.getUserServiceOrders(userId);
    
    if (serviceOrders.pending_count > 0 || serviceOrders.in_progress_count > 0) {
      showConstraintModal(user.username);
      return;
    }
    
    // Show confirmation modal
    showDeleteConfirmationModal(user);
    
  } catch (error) {
    if (error.message.includes('service orders')) {
      showConstraintModal(user.username);
    } else {
      showError('Failed to check user constraints: ' + error.message);
    }
  }
}

async function executeSoftDelete(userId) {
  const user = users.find(u => u.id === userId);
  if (!user) return;
  
  try {
    await api.softDeleteUser(userId);
    
    showSuccess(`User ${user.username} has been permanently deleted`);
    announceToScreenReader(`User ${user.username} deleted from system`);
    closeModal('deleteConfirmModal');
    loadUsers(); // Refresh the table
    
  } catch (error) {
    showError('Failed to delete user: ' + error.message);
  }
}
```

### 4.4 Modal Management Functions
Add enhanced modal management with accessibility features:

```javascript
function showConstraintModal(username) {
  document.getElementById('constraintUsername').textContent = username;
  openModal('constraintModal');
}

function showDeleteConfirmationModal(user) {
  document.getElementById('deleteConfirmUsername').textContent = user.username;
  
  const confirmBtn = document.getElementById('confirmDeleteBtn');
  confirmBtn.onclick = () => executeSoftDelete(user.id);
  
  openModal('deleteConfirmModal');
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.classList.add('active');
  modal.style.display = 'flex';
  
  // Focus management
  trapFocus(modal);
  
  // Set initial focus to first focusable element
  const firstFocusable = modal.querySelector('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
  if (firstFocusable) {
    firstFocusable.focus();
  }
  
  // Handle escape key
  const handleEscape = (e) => {
    if (e.key === 'Escape') {
      closeModal(modalId);
      document.removeEventListener('keydown', handleEscape);
    }
  };
  document.addEventListener('keydown', handleEscape);
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.classList.remove('active');
  
  // Animate out
  setTimeout(() => {
    modal.style.display = 'none';
  }, 250);
  
  // Return focus to trigger element if available
  const trigger = document.activeElement;
  if (trigger) {
    trigger.focus();
  }
}

function trapFocus(modal) {
  const focusableElements = modal.querySelectorAll(
    'button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];
  
  const handleTabKey = (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          lastFocusable.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          firstFocusable.focus();
          e.preventDefault();
        }
      }
    }
  };
  
  modal.addEventListener('keydown', handleTabKey);
}
```

### 4.5 Accessibility & Screen Reader Support
Add screen reader announcements and accessibility enhancements:

```javascript
function announceToScreenReader(message) {
  const announcer = document.createElement('div');
  announcer.setAttribute('aria-live', 'polite');
  announcer.setAttribute('aria-atomic', 'true');
  announcer.className = 'sr-only';
  announcer.style.cssText = `
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  `;
  
  document.body.appendChild(announcer);
  announcer.textContent = message;
  
  setTimeout(() => {
    document.body.removeChild(announcer);
  }, 1000);
}

function enhanceAccessibility() {
  // Add ARIA live region for status updates
  const liveRegion = document.createElement('div');
  liveRegion.id = 'status-live-region';
  liveRegion.setAttribute('aria-live', 'polite');
  liveRegion.setAttribute('aria-atomic', 'true');
  liveRegion.className = 'sr-only';
  document.body.appendChild(liveRegion);
  
  // Enhanced success/error messaging
  const originalShowSuccess = showSuccess;
  const originalShowError = showError;
  
  showSuccess = function(message) {
    originalShowSuccess(message);
    liveRegion.textContent = 'Success: ' + message;
  };
  
  showError = function(message) {
    originalShowError(message);
    liveRegion.textContent = 'Error: ' + message;
  };
}

// Initialize accessibility enhancements
document.addEventListener('DOMContentLoaded', function() {
  enhanceAccessibility();
  setupEventListeners();
  loadUsers();
});
```

## Phase 5: Error Handling & User Feedback

### 5.1 Enhanced Error Display
Replace the basic alert-based error handling with proper UI components:

```javascript
function showError(message) {
  // Remove any existing error alerts
  const existingAlerts = document.querySelectorAll('.alert--danger');
  existingAlerts.forEach(alert => alert.remove());
  
  // Create new error alert
  const alert = document.createElement('div');
  alert.className = 'alert alert--danger';
  alert.setAttribute('role', 'alert');
  alert.innerHTML = `
    <svg class="icon alert__icon" aria-hidden="true">
      <use href="/icons/svg-sprite.svg#icon-x-circle"></use>
    </svg>
    <div class="alert__content">
      <div class="alert__title">Operation Failed</div>
      ${escapeHtml(message)}
    </div>
  `;
  
  // Insert at the top of the container
  const container = document.querySelector('.container');
  container.insertBefore(alert, container.firstChild);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (alert.parentNode) {
      alert.remove();
    }
  }, 5000);
  
  // Scroll to alert
  alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showSuccess(message) {
  // Remove any existing success alerts
  const existingAlerts = document.querySelectorAll('.alert--success');
  existingAlerts.forEach(alert => alert.remove());
  
  // Create new success alert
  const alert = document.createElement('div');
  alert.className = 'alert alert--success';
  alert.setAttribute('role', 'status');
  alert.innerHTML = `
    <svg class="icon alert__icon" aria-hidden="true">
      <use href="/icons/svg-sprite.svg#icon-check-circle"></use>
    </svg>
    <div class="alert__content">
      ${escapeHtml(message)}
    </div>
  `;
  
  // Insert at the top of the container
  const container = document.querySelector('.container');
  container.insertBefore(alert, container.firstChild);
  
  // Auto-remove after 3 seconds
  setTimeout(() => {
    if (alert.parentNode) {
      alert.remove();
    }
  }, 3000);
}
```

### 5.2 Loading States
Add loading states for user actions:

```javascript
function setButtonLoading(button, isLoading) {
  if (isLoading) {
    button.disabled = true;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `
      <div class="loading-spinner--sm"></div>
      Processing...
    `;
  } else {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText;
  }
}

// Add loading spinner styles
const loadingSpinnerCSS = `
.loading-spinner--sm {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: var(--space-xs);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;

// Inject loading spinner styles
const styleSheet = document.createElement('style');
styleSheet.textContent = loadingSpinnerCSS;
document.head.appendChild(styleSheet);
```

## Phase 6: Responsive Design Considerations

### 6.1 Mobile-First Button Groups
Add responsive behavior for button groups on smaller screens:

```css
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
    gap: var(--space-xs);
    align-items: stretch;
  }
  
  .btn-group {
    width: 100%;
  }
  
  .btn-group .btn {
    flex: 1;
    justify-content: center;
  }
  
  .actions-column {
    min-width: 120px;
  }
}

@media (max-width: 480px) {
  .modal__content {
    width: 95%;
    margin: var(--space-sm);
  }
  
  .modal__footer {
    flex-direction: column-reverse;
  }
  
  .modal__footer .btn {
    width: 100%;
  }
}
```

### 6.2 Touch-Friendly Interactions
Ensure buttons are touch-friendly on mobile devices:

```css
@media (max-width: 768px) {
  .btn--sm {
    padding: var(--space-sm) var(--space-md);
    min-height: 44px; /* iOS touch target requirement */
  }
  
  .btn-group .btn {
    min-height: 44px;
  }
}
```

## Phase 7: Testing Procedures

### 7.1 Unit Testing Checklist
- [ ] Button state changes correctly based on user.is_active
- [ ] Modal focus management works properly
- [ ] API calls are made with correct parameters
- [ ] Error handling displays appropriate messages
- [ ] Screen reader announcements work
- [ ] Keyboard navigation functions correctly

### 7.2 Integration Testing Checklist
- [ ] Service order constraint validation works
- [ ] User state changes persist after page refresh
- [ ] Bulk operations respect individual constraints
- [ ] Audit trail is populated correctly
- [ ] Session handling works during state changes

### 7.3 Accessibility Testing Checklist
- [ ] All buttons have proper ARIA labels
- [ ] Modal dialogs have correct ARIA attributes
- [ ] Focus trap works in modals
- [ ] Screen reader users can navigate effectively
- [ ] Keyboard-only navigation works
- [ ] Color contrast meets WCAG AA standards
- [ ] Reduced motion preferences are respected

### 7.4 Browser Testing Matrix
Test in the following browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile Safari (iOS)
- Chrome Mobile (Android)

### 7.5 Manual Testing Scenarios

#### Scenario 1: Deactivate Active User
1. Navigate to User Management page
2. Find an active user without service orders
3. Click "Deactivate" button
4. Verify button changes to "Activate"
5. Verify user cannot log in
6. Verify success message appears

#### Scenario 2: Service Order Constraint
1. Navigate to User Management page
2. Find a user with pending service orders
3. Click "Deactivate" button
4. Verify constraint modal appears
5. Verify user remains active
6. Click "Delete" button
7. Verify same constraint modal appears

#### Scenario 3: Soft Delete Confirmation
1. Find a user without service orders
2. Click "Delete" button
3. Verify confirmation modal appears
4. Click "Cancel" - verify modal closes
5. Click "Delete" again
6. Click "Confirm Delete"
7. Verify user disappears from table
8. Verify success message

#### Scenario 4: Keyboard Navigation
1. Use Tab key to navigate to user table
2. Use Tab to reach action buttons
3. Use Enter/Space to activate buttons
4. In modals, use Tab to navigate
5. Use Escape to close modals
6. Verify focus returns appropriately

## Phase 8: Performance Optimization

### 8.1 Debounced State Changes
Implement debouncing for rapid button clicks:

```javascript
function debounceUserAction(fn, delay = 1000) {
  let timeout;
  let isRunning = false;
  
  return function(...args) {
    if (isRunning) return;
    
    clearTimeout(timeout);
    timeout = setTimeout(async () => {
      isRunning = true;
      try {
        await fn.apply(this, args);
      } finally {
        isRunning = false;
      }
    }, delay);
  };
}

// Apply debouncing to user actions
const debouncedDeactivate = debounceUserAction(confirmDeactivateUser);
const debouncedActivate = debounceUserAction(confirmActivateUser);
const debouncedDelete = debounceUserAction(confirmDeleteUser);
```

### 8.2 Optimized Re-renders
Only update specific table rows instead of full table re-render:

```javascript
function updateUserRow(user) {
  const existingRow = document.querySelector(`tr[data-user-id="${user.id}"]`);
  if (existingRow) {
    const newRow = createUserRow(user);
    existingRow.replaceWith(newRow);
  }
}

function optimizedUserUpdate(userId, newUserData) {
  // Update local data
  const userIndex = users.findIndex(u => u.id === userId);
  if (userIndex !== -1) {
    users[userIndex] = { ...users[userIndex], ...newUserData };
    updateUserRow(users[userIndex]);
    updateUserCount();
  }
}
```

## Phase 9: Deployment Instructions

### 9.1 Pre-Deployment Checklist
1. **Backend Validation**
   - [ ] New API endpoints are deployed and functional
   - [ ] Database schema updates are applied
   - [ ] Service order constraint logic is working

2. **Frontend Preparation**
   - [ ] SVG sprite includes all required icons
   - [ ] CSS design tokens are properly defined
   - [ ] All modal components are implemented
   - [ ] JavaScript functions are tested

3. **Integration Testing**
   - [ ] API integration works with CVDApi class
   - [ ] Authentication checks are maintained
   - [ ] Error handling covers all edge cases

### 9.2 Step-by-Step Deployment

#### Step 1: Update SVG Sprite (if needed)
The existing sprite already contains all required icons, so no changes needed.

#### Step 2: Update CSS
Add the new CSS classes to the user-management.html `<style>` section or create a separate CSS file:

```html
<style>
  /* Add existing styles plus new ones from Phase 2.1 and 2.2 */
</style>
```

#### Step 3: Update HTML Structure
1. Replace the `createUserRow` function with the enhanced version
2. Add the new modal components before `</body>`
3. Add the SVG sprite loading script in `<head>`

#### Step 4: Update JavaScript
1. Add the new API methods to CVDApi usage
2. Add all the new user state management functions
3. Add modal management functions
4. Add accessibility enhancements
5. Update error handling functions

#### Step 5: Test in Development
1. Test all user state transitions
2. Test constraint modal triggers
3. Test accessibility features
4. Test responsive behavior

#### Step 6: Deploy to Production
1. Deploy backend changes first
2. Deploy frontend changes
3. Clear browser caches
4. Test critical user paths

### 9.3 Rollback Plan
If issues are encountered:

1. **Database Rollback**: New columns are nullable, so rollback is safe
2. **Frontend Rollback**: Keep backup of original user-management.html
3. **Feature Flag**: Consider adding a feature flag to toggle new functionality

### 9.4 Post-Deployment Validation
1. **Functionality Check**
   - [ ] All three user states work correctly
   - [ ] Service order constraints are enforced
   - [ ] Audit trail is populated
   - [ ] Bulk operations work

2. **Performance Check**
   - [ ] Page load times are acceptable
   - [ ] API response times are reasonable
   - [ ] No memory leaks in long-running sessions

3. **Accessibility Check**
   - [ ] Screen reader functionality
   - [ ] Keyboard navigation
   - [ ] Focus management
   - [ ] Color contrast

## Phase 10: Documentation & Training

### 10.1 User Documentation Updates
Update the admin guide to include:
- How to deactivate/activate users
- Understanding the new user states
- Service order constraint explanations
- Audit trail interpretation

### 10.2 Developer Documentation
Document the new:
- CSS classes and design patterns
- JavaScript functions and APIs
- Modal component usage
- Accessibility implementation

### 10.3 Support Team Training
Provide training on:
- New user management workflow
- Troubleshooting constraint issues
- Understanding audit trail entries
- Common user questions

## Conclusion

This comprehensive deployment plan provides a systematic approach to implementing the user soft delete feature in the CVD application. The plan maintains compatibility with the existing iframe-based architecture, leverages the established design system, and ensures accessibility compliance while delivering a polished user experience.

Key success factors:
- Incremental deployment with thorough testing at each phase
- Proper accessibility implementation from the start
- Comprehensive error handling and user feedback
- Responsive design considerations for all device types
- Performance optimization for smooth user interactions

The implementation follows CVD application patterns and integrates seamlessly with the existing user management infrastructure while providing the enhanced functionality required for modern user lifecycle management.