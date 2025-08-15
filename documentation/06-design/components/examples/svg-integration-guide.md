# CVD SVG Icon System - Integration Guide

## Overview

This guide provides complete instructions for integrating the CVD SVG icon system into existing pages, with specific focus on the user management soft delete feature.

## Quick Start

### 1. Include the Icon Sprite

Add the SVG sprite at the beginning of each HTML page, immediately after the opening `<body>` tag:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Head content -->
    <link rel="stylesheet" href="/css/design-system.css">
</head>
<body>
    <!-- Include SVG Icon Sprite -->
    <svg style="display: none;" aria-hidden="true">
        <use href="/icons/svg-sprite.svg"></use>
    </svg>
    
    <!-- Page content -->
</body>
</html>
```

### 2. Basic Icon Usage

Use icons with the standard pattern:

```html
<!-- Basic icon -->
<svg class="icon">
    <use href="/icons/svg-sprite.svg#icon-name"></use>
</svg>

<!-- Icon with size -->
<svg class="icon icon--sm">
    <use href="/icons/svg-sprite.svg#icon-trash"></use>
</svg>

<!-- Icon with color -->
<svg class="icon icon--danger">
    <use href="/icons/svg-sprite.svg#icon-exclamation-triangle"></use>
</svg>
```

## User Management Integration

### Current User Management Buttons

Replace the existing user management action buttons with the new icon-enhanced versions:

#### Before (Current Implementation)
```html
<div class="action-buttons">
    <button class="btn btn-sm btn-secondary" onclick="editUser(${user.id})">Edit</button>
    <button class="btn btn-sm btn-secondary" onclick="resetPassword(${user.id})">Reset</button>
    <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">Delete</button>
</div>
```

#### After (With SVG Icons)
```html
<div class="action-buttons">
    <button class="btn btn--sm btn--secondary" onclick="editUser(${user.id})" aria-label="Edit user">
        <svg class="icon icon--sm" aria-hidden="true">
            <use href="/icons/svg-sprite.svg#icon-pencil"></use>
        </svg>
        Edit
    </button>
    
    <button class="btn btn--sm btn--secondary" onclick="resetPassword(${user.id})" aria-label="Reset password">
        <svg class="icon icon--sm" aria-hidden="true">
            <use href="/icons/svg-sprite.svg#icon-key"></use>
        </svg>
        Reset
    </button>
    
    <!-- Deactivate button (soft delete) -->
    <button class="btn btn--sm btn--warning" onclick="deactivateUser(${user.id})" aria-label="Deactivate user">
        <svg class="icon icon--sm" aria-hidden="true">
            <use href="/icons/svg-sprite.svg#icon-pause"></use>
        </svg>
        Deactivate
    </button>
    
    <!-- Hard delete button (if needed) -->
    <button class="btn btn--sm btn--danger" onclick="permanentDeleteUser(${user.id})" aria-label="Permanently delete user">
        <svg class="icon icon--sm" aria-hidden="true">
            <use href="/icons/svg-sprite.svg#icon-trash"></use>
        </svg>
        Delete
    </button>
</div>
```

### User Status Indicators

Enhance status indicators with appropriate icons:

```html
<!-- Active User -->
<span class="status-indicator">
    <svg class="icon icon--xs icon--success" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-check-circle"></use>
    </svg>
    Active
</span>

<!-- Inactive User (Deactivated) -->
<span class="status-indicator">
    <svg class="icon icon--xs icon--warning" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-pause"></use>
    </svg>
    Inactive
</span>

<!-- Locked User -->
<span class="status-indicator">
    <svg class="icon icon--xs icon--danger" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-lock"></use>
    </svg>
    Locked
</span>
```

### Modal Enhancements

#### Confirmation Modal with Warning Icon

```html
<!-- Delete/Deactivate Confirmation Modal -->
<div class="modal" id="deactivateUserModal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>
                <svg class="icon icon--warning" aria-hidden="true">
                    <use href="/icons/svg-sprite.svg#icon-exclamation-triangle"></use>
                </svg>
                Deactivate User
            </h2>
        </div>
        <div class="modal-body">
            <p>Are you sure you want to deactivate <strong id="deactivateUsername"></strong>?</p>
            <p>This user will be unable to log in but their data will be preserved.</p>
        </div>
        <div class="modal-footer">
            <button class="btn btn--secondary" onclick="closeModal('deactivateUserModal')">
                <svg class="icon icon--sm" aria-hidden="true">
                    <use href="/icons/svg-sprite.svg#icon-x"></use>
                </svg>
                Cancel
            </button>
            <button class="btn btn--warning" id="confirmDeactivateBtn">
                <svg class="icon icon--sm" aria-hidden="true">
                    <use href="/icons/svg-sprite.svg#icon-pause"></use>
                </svg>
                Deactivate User
            </button>
        </div>
    </div>
</div>
```

### Table Headers with Sort Icons

Update sortable table headers:

```html
<th class="sortable-header" data-column="username">
    Username 
    <svg class="icon icon--xs table__sort-icon" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-chevron-down"></use>
    </svg>
</th>
```

## Icon Reference for User Management

### Core User Management Icons

| Icon ID | Use Case | Example |
|---------|----------|---------|
| `icon-user` | User profile, user-related actions | User avatar, profile button |
| `icon-pencil` | Edit user information | Edit user button |
| `icon-key` | Reset password, security actions | Reset password button |
| `icon-pause` | Deactivate user (soft delete) | Deactivate button |
| `icon-trash` | Delete user permanently | Delete button |
| `icon-check-circle` | Active user status | Status indicator |
| `icon-exclamation-triangle` | Warning states | Confirmation modals |
| `icon-lock` | Locked account status | Status indicator |
| `icon-unlock` | Unlock account action | Unlock button |

### Button Color Combinations

```html
<!-- Success Actions (Activate, Confirm) -->
<button class="btn btn--success">
    <svg class="icon icon--sm icon--success" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-check-circle"></use>
    </svg>
    Activate
</button>

<!-- Warning Actions (Deactivate, Suspend) -->
<button class="btn btn--warning">
    <svg class="icon icon--sm" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-pause"></use>
    </svg>
    Deactivate
</button>

<!-- Danger Actions (Delete, Remove) -->
<button class="btn btn--danger">
    <svg class="icon icon--sm" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-trash"></use>
    </svg>
    Delete
</button>

<!-- Secondary Actions (Edit, View) -->
<button class="btn btn--secondary">
    <svg class="icon icon--sm" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-pencil"></use>
    </svg>
    Edit
</button>
```

## Complete User Management Page Integration

### Page Header Include

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Management - CVD</title>
    <link rel="stylesheet" href="/css/design-system.css">
</head>
<body>
    <!-- SVG Sprite Include -->
    <svg style="display: none;" aria-hidden="true">
        <use href="/icons/svg-sprite.svg"></use>
    </svg>
```

### Enhanced Action Bar

```html
<div class="actions-bar">
    <div class="left-actions">
        <button class="btn btn--primary" id="addUserBtn">
            <svg class="icon icon--sm" aria-hidden="true">
                <use href="/icons/svg-sprite.svg#icon-plus"></use>
            </svg>
            Add User
        </button>
        
        <button class="btn btn--secondary" id="bulkDeactivateBtn" disabled>
            <svg class="icon icon--sm" aria-hidden="true">
                <use href="/icons/svg-sprite.svg#icon-pause"></use>
            </svg>
            Deactivate Selected
        </button>
        
        <button class="btn btn--secondary" id="exportBtn">
            <svg class="icon icon--sm" aria-hidden="true">
                <use href="/icons/svg-sprite.svg#icon-download"></use>
            </svg>
            Export to CSV
        </button>
    </div>
    
    <div class="right-actions">
        <!-- Filter controls with icons -->
        <div class="search-box">
            <svg class="icon icon--sm icon--muted" aria-hidden="true">
                <use href="/icons/svg-sprite.svg#icon-search"></use>
            </svg>
            <input type="text" class="search-input" id="searchInput" placeholder="Search users...">
        </div>
    </div>
</div>
```

## Accessibility Implementation

### Screen Reader Support

```html
<!-- Icon with text label (recommended) -->
<button class="btn btn--danger" aria-label="Delete user permanently">
    <svg class="icon icon--sm" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-trash"></use>
    </svg>
    Delete
</button>

<!-- Icon-only button with screen reader text -->
<button class="btn btn--icon-only btn--danger" aria-label="Delete user">
    <svg class="icon icon--sm" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-trash"></use>
    </svg>
    <span class="sr-only">Delete user</span>
</button>

<!-- Status with accessible text -->
<span class="status-indicator" role="status" aria-label="User is active">
    <svg class="icon icon--xs icon--success" aria-hidden="true">
        <use href="/icons/svg-sprite.svg#icon-check-circle"></use>
    </svg>
    <span aria-hidden="true">Active</span>
    <span class="sr-only">User status is active</span>
</span>
```

### High Contrast Support

The icon system automatically inherits color from the parent element, ensuring proper contrast ratios:

```css
/* Icons automatically use currentColor and inherit contrast ratios */
.btn--danger .icon {
    color: currentColor; /* Inherits from button text color */
}

/* Custom high contrast overrides if needed */
@media (prefers-contrast: high) {
    .icon--warning {
        color: #cc8800; /* Higher contrast yellow */
    }
}
```

## Performance Considerations

### Icon Loading Optimization

1. **Sprite Loading**: The SVG sprite is included once per page and cached by the browser
2. **No Additional Requests**: All icons are bundled in a single SVG file
3. **Scalable**: SVG icons scale perfectly at all sizes without pixelation
4. **Small File Size**: Optimized SVG paths keep the total sprite size minimal

### Browser Support

- **Modern Browsers**: Full support for SVG `<use>` elements
- **Legacy Support**: Automatic fallback to text labels
- **Screen Readers**: Full compatibility with assistive technologies

## Testing Checklist

### Visual Testing
- [ ] Icons display correctly at all sizes (xs, sm, md, lg, xl, 2xl)
- [ ] Colors apply correctly with semantic classes
- [ ] Hover states work as expected on interactive elements
- [ ] Icons align properly with text in buttons and labels

### Accessibility Testing
- [ ] Screen readers announce button purposes correctly
- [ ] Keyboard navigation works with icon buttons
- [ ] Focus indicators are visible and properly positioned
- [ ] Color contrast meets WCAG AA standards (4.5:1 for normal text, 3:1 for large text)

### Functionality Testing
- [ ] All user management actions work with new icon buttons
- [ ] Modal confirmations display appropriate warning icons
- [ ] Status indicators show correct icons for user states
- [ ] Table sorting icons update correctly

### Performance Testing
- [ ] Page load times remain acceptable with sprite inclusion
- [ ] No icon rendering delays or flash of unstyled content
- [ ] SVG sprite loads only once and is cached properly

## Migration Notes

### Updating Existing Pages

1. **Include Design System CSS**: Ensure `/css/design-system.css` is loaded
2. **Add SVG Sprite**: Include the sprite at the top of each page
3. **Update Button Classes**: Change from `btn-*` to `btn--*` pattern
4. **Add Icons**: Insert appropriate icon markup in buttons and status indicators
5. **Test Accessibility**: Verify screen reader support and keyboard navigation

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Icons not displaying | Check that the SVG sprite is properly included and the path is correct |
| Icons too large/small | Use appropriate size classes (`icon--xs`, `icon--sm`, etc.) |
| Poor color contrast | Use semantic color classes (`icon--success`, `icon--danger`, etc.) |
| Accessibility issues | Add proper `aria-label` attributes and `aria-hidden="true"` to decorative icons |

## Complete Example: Updated User Management Row

```html
function createUserRow(user) {
    const row = document.createElement('tr');
    row.dataset.userId = user.id;
    
    row.innerHTML = `
        <td>
            <input type="checkbox" class="row-checkbox" data-user-id="${user.id}">
        </td>
        <td>
            <div class="user-info">
                <svg class="icon icon--sm icon--muted" aria-hidden="true">
                    <use href="/icons/svg-sprite.svg#icon-user"></use>
                </svg>
                ${escapeHtml(user.username)}
            </div>
        </td>
        <td>
            <div class="email-info">
                <svg class="icon icon--xs icon--muted" aria-hidden="true">
                    <use href="/icons/svg-sprite.svg#icon-mail"></use>
                </svg>
                ${escapeHtml(user.email)}
            </div>
        </td>
        <td>
            <span class="role-badge role-${user.role}">${user.role}</span>
        </td>
        <td>
            ${getStatusIndicator(user)}
        </td>
        <td>${formatDate(user.last_login)}</td>
        <td>${user.failed_login_attempts || 0}</td>
        <td>
            <div class="btn-group">
                <button class="btn btn--sm btn--secondary" onclick="editUser(${user.id})" aria-label="Edit user">
                    <svg class="icon icon--sm" aria-hidden="true">
                        <use href="/icons/svg-sprite.svg#icon-pencil"></use>
                    </svg>
                    Edit
                </button>
                
                <button class="btn btn--sm btn--secondary" onclick="resetPassword(${user.id})" aria-label="Reset password">
                    <svg class="icon icon--sm" aria-hidden="true">
                        <use href="/icons/svg-sprite.svg#icon-key"></use>
                    </svg>
                    Reset
                </button>
                
                ${user.is_active ? `
                    <button class="btn btn--sm btn--warning" onclick="deactivateUser(${user.id})" aria-label="Deactivate user">
                        <svg class="icon icon--sm" aria-hidden="true">
                            <use href="/icons/svg-sprite.svg#icon-pause"></use>
                        </svg>
                        Deactivate
                    </button>
                ` : `
                    <button class="btn btn--sm btn--success" onclick="activateUser(${user.id})" aria-label="Activate user">
                        <svg class="icon icon--sm" aria-hidden="true">
                            <use href="/icons/svg-sprite.svg#icon-check-circle"></use>
                        </svg>
                        Activate
                    </button>
                `}
                
                <button class="btn btn--sm btn--danger" onclick="permanentDeleteUser(${user.id})" aria-label="Permanently delete user">
                    <svg class="icon icon--sm" aria-hidden="true">
                        <use href="/icons/svg-sprite.svg#icon-trash"></use>
                    </svg>
                    Delete
                </button>
            </div>
        </td>
    `;
    
    return row;
}

function getStatusIndicator(user) {
    if (user.is_locked) {
        return `
            <span class="status-indicator" role="status" aria-label="User account is locked">
                <svg class="icon icon--xs icon--danger" aria-hidden="true">
                    <use href="/icons/svg-sprite.svg#icon-lock"></use>
                </svg>
                <span aria-hidden="true">Locked</span>
            </span>
        `;
    } else if (user.is_active) {
        return `
            <span class="status-indicator" role="status" aria-label="User account is active">
                <svg class="icon icon--xs icon--success" aria-hidden="true">
                    <use href="/icons/svg-sprite.svg#icon-check-circle"></use>
                </svg>
                <span aria-hidden="true">Active</span>
            </span>
        `;
    } else {
        return `
            <span class="status-indicator" role="status" aria-label="User account is inactive">
                <svg class="icon icon--xs icon--warning" aria-hidden="true">
                    <use href="/icons/svg-sprite.svg#icon-pause"></use>
                </svg>
                <span aria-hidden="true">Inactive</span>
            </span>
        `;
    }
}
```

This integration guide provides everything needed to successfully implement the CVD SVG icon system with proper accessibility, performance, and visual consistency.