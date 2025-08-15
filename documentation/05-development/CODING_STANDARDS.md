# CVD Coding Standards and Style Guide


## Metadata
- **ID**: 05_DEVELOPMENT_CODING_STANDARDS
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #coding #data-exchange #data-layer #database #debugging #deployment #development #device-management #devops #dex-parser #driver-app #integration #logistics #machine-learning #mobile #operations #optimization #performance #planogram #product-placement #pwa #quality-assurance #route-management #security #service-orders #testing #troubleshooting #vending-machine #workflows
- **Intent**: This document establishes coding standards and style guidelines for the CVD (Vision Device Configuration) project
- **Audience**: developers, system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/
- **Category**: 05 Development
- **Search Keywords**: ###, api, api-first, app.py, architecture, attributes, auth.py, base, branch, cabinet, classes, client, coding, colors, comments

## Overview

This document establishes coding standards and style guidelines for the CVD (Vision Device Configuration) project. These standards are derived from analysis of the existing codebase and follow industry best practices for Python, JavaScript, HTML, and CSS development.

## Table of Contents

1. [General Principles](#general-principles)
2. [Python Standards](#python-standards)
3. [JavaScript Standards](#javascript-standards)
4. [HTML Standards](#html-standards)
5. [CSS Standards](#css-standards)
6. [File Organization](#file-organization)
7. [Documentation Standards](#documentation-standards)
8. [Version Control](#version-control)
9. [Code Review Guidelines](#code-review-guidelines)

## General Principles

### Code Quality Standards
- **Readability First**: Code is written once but read many times
- **Consistency**: Follow established patterns within the project
- **Simplicity**: Choose simple solutions over complex ones
- **Maintainability**: Write code that future developers can understand
- **Security**: Follow secure coding practices throughout

### Project-Specific Patterns
- **Modular Architecture**: Clear separation between backend and frontend
- **API-First Design**: Backend provides RESTful APIs consumed by frontend
- **Progressive Enhancement**: Frontend works without JavaScript for basic features
- **Role-Based Security**: All operations respect user role permissions

## Python Standards

Based on analysis of `app.py`, `auth.py`, `service_order_service.py`, and test files.

### PEP 8 Compliance
Follow [PEP 8](https://pep8.org/) with these project-specific additions:

```python
# Line length: 88 characters (Black formatter standard)
# Indentation: 4 spaces (no tabs)
# Imports: Grouped and sorted

# Standard imports
import os
import json
from datetime import datetime, timedelta

# Third-party imports
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash

# Local imports
from auth import AuthManager
from service_order_service import ServiceOrderService
```

### Function and Class Naming
```python
# Classes: PascalCase
class ServiceOrderService:
    """Service for managing service orders"""

# Functions and methods: snake_case
def get_service_orders():
    """Retrieve all service orders"""
    
def create_user_session(user_id, device_type="web"):
    """Create authentication session"""

# Constants: UPPER_SNAKE_CASE
DATABASE_URL = 'cvd.db'
MAX_LOGIN_ATTEMPTS = 3
```

### Database Operations Pattern
```python
# Consistent database connection pattern
def get_database_operation():
    """Example of standard database operation pattern"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Database operations
        result = cursor.execute('''
            SELECT id, name, status 
            FROM table_name 
            WHERE active = 1
            ORDER BY created_at DESC
        ''').fetchall()
        
        db.commit()
        return [dict(row) for row in result]
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        # Connection is managed by Flask g context
        pass
```

### Error Handling Pattern
```python
# Standard error handling for API endpoints
@app.route('/api/endpoint', methods=['POST'])
@auth_manager.require_auth(['admin', 'manager'])
def api_endpoint():
    """Standard API endpoint pattern"""
    try:
        # Validate input
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        # Business logic
        result = process_data(data)
        
        # Success response
        return jsonify({'success': True, 'data': result}), 200
        
    except ValueError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f'Unexpected error in api_endpoint: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
```

### Docstring Standards
```python
def create_service_order(route_id, cabinet_selections, created_by=None):
    """
    Create a service order from cabinet selections.
    
    Args:
        route_id (int): ID of the route for the service order
        cabinet_selections (list): List of {'deviceId': int, 'cabinetIndex': int}
        created_by (int, optional): User ID of creator. Defaults to None.
        
    Returns:
        dict: Service order details with ID and status
        
    Raises:
        ValueError: If route_id is invalid or cabinet_selections is empty
        DatabaseError: If database operation fails
        
    Example:
        >>> selections = [{'deviceId': 1, 'cabinetIndex': 0}]
        >>> order = create_service_order(route_id=5, cabinet_selections=selections)
        >>> print(order['id'])
        42
    """
```

### Authentication Decorator Pattern
```python
# Consistent use of authentication decorators
from auth import AuthManager

@app.route('/api/admin-only', methods=['GET'])
@auth_manager.require_auth(['admin'])
def admin_only_endpoint():
    """Admin-only endpoint"""
    return jsonify({'message': 'Admin access granted'})

@app.route('/api/restricted', methods=['POST'])
@auth_manager.require_auth(['admin', 'manager'])
def restricted_endpoint():
    """Manager and admin access"""
    return jsonify({'data': get_sensitive_data()})
```

## JavaScript Standards

Based on analysis of `api.js`, driver app files, and page scripts.

### ES6+ Modern JavaScript
```javascript
// Use modern JavaScript features
class CVDApi {
    constructor() {
        this.baseUrl = '/api';
        this.maxRetries = 3;
    }
    
    async getData(endpoint) {
        try {
            const response = await this.request('GET', endpoint);
            return response.data;
        } catch (error) {
            console.error(`Failed to get data from ${endpoint}:`, error);
            throw error;
        }
    }
}

// Use arrow functions for short callbacks
const processItems = items => items
    .filter(item => item.active)
    .map(item => ({
        id: item.id,
        name: item.name,
        status: item.status
    }));
```

### API Client Pattern
```javascript
// Consistent API client usage pattern
class FeatureManager {
    constructor() {
        this.api = new CVDApi();
    }
    
    async loadData() {
        try {
            const data = await this.api.get('/feature-data');
            this.renderData(data);
        } catch (error) {
            this.showError('Failed to load data');
            console.error('Load data error:', error);
        }
    }
    
    async saveData(formData) {
        try {
            const result = await this.api.post('/feature-data', formData);
            this.showSuccess('Data saved successfully');
            return result;
        } catch (error) {
            this.showError('Failed to save data');
            throw error;
        }
    }
}
```

### Event Handling Pattern
```javascript
// Standard event handling for forms and interactions
document.addEventListener('DOMContentLoaded', () => {
    const feature = new FeatureManager();
    
    // Form submission
    const form = document.getElementById('feature-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            await feature.saveData(data);
        });
    }
    
    // Button clicks
    const loadButton = document.getElementById('load-data');
    if (loadButton) {
        loadButton.addEventListener('click', () => {
            feature.loadData();
        });
    }
});
```

### Error Handling and Logging
```javascript
// Consistent error handling pattern
class DataService {
    async processData(data) {
        try {
            const result = await this.api.post('/process', data);
            
            // Log successful operations
            console.log('Data processed successfully:', result.id);
            
            return result;
        } catch (error) {
            // Log errors with context
            console.error('Data processing failed:', {
                error: error.message,
                data: data,
                timestamp: new Date().toISOString()
            });
            
            // Re-throw for caller to handle UI updates
            throw new Error(`Processing failed: ${error.message}`);
        }
    }
}
```

### Cross-Frame Communication
```javascript
// Standard iframe communication pattern
function notifyParent(type, payload = {}) {
    if (window.parent !== window) {
        window.parent.postMessage({
            type: type,
            payload: payload,
            source: 'cvd-iframe'
        }, window.location.origin);
    }
}

// Usage examples
notifyParent('NAVIGATE', { page: 'devices' });
notifyParent('REFRESH_DATA', { table: 'service_orders' });
notifyParent('SHOW_NOTIFICATION', { message: 'Success', type: 'success' });
```

## HTML Standards

Based on analysis of page templates and components.

### Document Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title - CVD</title>
    
    <!-- Design System CSS -->
    <link rel="stylesheet" href="/css/design-system.css">
    
    <!-- Page-specific styles -->
    <style>
        /* Minimal page-specific overrides */
        .page-specific-class {
            /* Custom styles here */
        }
    </style>
</head>
<body>
    <!-- Skip navigation for accessibility -->
    <a href="#main-content" class="skip-link">Skip to main content</a>
    
    <main id="main-content">
        <!-- Page content here -->
    </main>
    
    <!-- API client (required for all interactive pages) -->
    <script src="/api.js"></script>
    
    <!-- Page-specific JavaScript -->
    <script>
        // Page initialization code
    </script>
</body>
</html>
```

### Semantic HTML Structure
```html
<!-- Use semantic HTML elements -->
<header class="page-header">
    <h1>Page Title</h1>
    <nav aria-label="Page navigation">
        <ul class="nav-list">
            <li><a href="#section1">Section 1</a></li>
            <li><a href="#section2">Section 2</a></li>
        </ul>
    </nav>
</header>

<main class="main-content">
    <section id="section1" class="content-section">
        <h2>Section Heading</h2>
        <p>Section content...</p>
    </section>
    
    <aside class="sidebar" role="complementary">
        <h3>Related Information</h3>
        <p>Sidebar content...</p>
    </aside>
</main>

<footer class="page-footer">
    <p>&copy; 2024 CVD Application</p>
</footer>
```

### Form Standards
```html
<!-- Accessible form structure -->
<form class="standard-form" method="post" action="/api/endpoint">
    <fieldset>
        <legend>User Information</legend>
        
        <div class="form-group">
            <label for="username">Username <span class="required">*</span></label>
            <input 
                type="text" 
                id="username" 
                name="username" 
                required 
                aria-describedby="username-help"
                autocomplete="username"
            >
            <div id="username-help" class="form-help">
                Enter your username (3-20 characters)
            </div>
        </div>
        
        <div class="form-group">
            <label for="role">User Role</label>
            <select id="role" name="role" required>
                <option value="">Select a role</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="driver">Driver</option>
                <option value="viewer">Viewer</option>
            </select>
        </div>
    </fieldset>
    
    <div class="form-actions">
        <button type="submit" class="btn btn-primary">
            Save User
        </button>
        <button type="reset" class="btn btn-secondary">
            Reset Form
        </button>
    </div>
</form>
```

### Data Attributes
```html
<!-- Use data attributes for JavaScript interaction -->
<div 
    class="device-card" 
    data-device-id="123"
    data-device-type="cooler"
    data-status="active"
>
    <h3>Device Name</h3>
    <button 
        class="btn btn-primary" 
        data-action="edit"
        data-device-id="123"
    >
        Edit Device
    </button>
</div>
```

## CSS Standards

Based on analysis of `design-system.css` and page styles.

### CSS Custom Properties (Variables)
```css
/* Use design system variables consistently */
:root {
  /* Colors from design system */
  --color-primary-500: #006dfe;
  --color-neutral-100: #f1f3f5;
  --color-success: #28a745;
  --color-danger: #dc3545;
  
  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  
  /* Spacing */
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  
  /* Layout */
  --nav-height: 60px;
  --border-radius: 4px;
}
```

### BEM-Inspired Class Naming
```css
/* Component-based class naming */
.device-card {
  /* Base component styles */
}

.device-card__header {
  /* Component element */
}

.device-card__title {
  /* Component element */
}

.device-card--featured {
  /* Component modifier */
}

.device-card--inactive {
  /* Component modifier */
}

/* State classes */
.is-loading {
  opacity: 0.6;
  pointer-events: none;
}

.is-hidden {
  display: none;
}

.has-error {
  border-color: var(--color-danger);
}
```

### Responsive Design
```css
/* Mobile-first responsive design */
.container {
  width: 100%;
  padding: 0 var(--space-md);
  margin: 0 auto;
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    max-width: 768px;
    padding: 0 var(--space-lg);
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
  }
}
```

### Component Styles
```css
/* Self-contained component styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-sm) var(--space-md);
  border: 1px solid transparent;
  border-radius: var(--border-radius);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.5;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn--primary {
  background-color: var(--color-primary-500);
  color: white;
}

.btn--primary:hover {
  background-color: var(--color-primary-600);
  transform: translateY(-1px);
}

.btn--secondary {
  background-color: var(--color-neutral-100);
  color: var(--color-neutral-800);
}
```

## File Organization

### Directory Structure
```
/home/jbrice/Projects/365/
├── app.py                  # Main Flask application
├── auth.py                 # Authentication module
├── service_order_service.py # Business logic services
├── api.js                  # Frontend API client
├── auth-check.js          # Authentication utilities
├── index.html             # Main application shell
│
├── pages/                 # Frontend pages
│   ├── login.html
│   ├── home-dashboard.html
│   ├── PCP.html           # Device listing
│   ├── NSPT.html          # Planogram management
│   └── driver-app/        # PWA application
│
├── css/
│   └── design-system.css  # Design system variables
│
├── js/                    # Shared JavaScript utilities
│   ├── toast-helper.js
│   ├── loading-helper.js
│   └── user-preferences.js
│
├── tests/                 # Test files
│   ├── test_auth_flow.py
│   ├── test_user_soft_delete.py
│   └── test_knowledge_base_api.py
│
├── documentation/         # Project documentation
├── tools/                # Development utilities
└── migrations/           # Database migrations
```

### File Naming Conventions
```
# Python files: snake_case.py
service_order_service.py
user_management.py
activity_tracker.py

# HTML files: kebab-case.html or PascalCase.html (legacy)
user-management.html
service-orders.html
PCP.html (legacy Device listing)
NSPT.html (legacy Planogram)

# JavaScript files: kebab-case.js or camelCase.js
api.js
auth-check.js
toast-helper.js

# CSS files: kebab-case.css
design-system.css
component-styles.css

# Test files: test_*.py
test_auth_flow.py
test_service_orders.py
```

## Documentation Standards

### Code Comments
```python
# Python documentation
def calculate_inventory_levels(device_id, cabinet_index):
    """
    Calculate current inventory levels for a specific cabinet.
    
    This function analyzes sales data, current stock, and par levels
    to determine restock requirements for service orders.
    """
    
    # Get current stock levels from planogram
    current_stock = get_cabinet_stock(device_id, cabinet_index)
    
    # Calculate sales velocity over last 30 days
    sales_data = get_sales_history(device_id, cabinet_index, days=30)
    
    # Apply business rules for minimum stock levels
    if sales_data['avg_daily_sales'] > 0:
        # High-velocity products need higher par levels
        recommended_par = sales_data['avg_daily_sales'] * 7  # 7-day supply
    else:
        # Use default par level for new or slow-moving products
        recommended_par = DEFAULT_PAR_LEVEL
    
    return {
        'current_stock': current_stock,
        'recommended_par': recommended_par,
        'restock_needed': current_stock < recommended_par
    }
```

```javascript
// JavaScript documentation
class ServiceOrderManager {
    /**
     * Create a new service order from selected cabinets
     * @param {Array} cabinetSelections - Array of {deviceId, cabinetIndex} objects
     * @param {number} routeId - ID of the route for this service order
     * @returns {Promise<Object>} Service order details with ID and items
     */
    async createServiceOrder(cabinetSelections, routeId) {
        // Validate input parameters
        if (!Array.isArray(cabinetSelections) || cabinetSelections.length === 0) {
            throw new Error('Cabinet selections must be a non-empty array');
        }
        
        // Process each cabinet selection
        const orderItems = [];
        for (const selection of cabinetSelections) {
            // Calculate inventory needs for this cabinet
            const inventory = await this.calculateInventoryNeeds(
                selection.deviceId, 
                selection.cabinetIndex
            );
            
            orderItems.push(inventory);
        }
        
        return this.api.post('/service-orders', {
            route_id: routeId,
            items: orderItems
        });
    }
}
```

### README Files
Each major component should include a README.md:

```markdown
# Component Name

## Purpose
Brief description of what this component does.

## Usage
```python
# Code example showing how to use the component
from component import ComponentClass

component = ComponentClass()
result = component.do_something()
```

## API Reference
- `method_name(param1, param2)` - Description of what it does
- `property_name` - Description of the property

## Dependencies
- List of required dependencies
- Version requirements if specific

## Configuration
- Environment variables needed
- Configuration file requirements
```

## Version Control

### Git Workflow (When Using Git)
```bash
# Feature branch workflow
git checkout -b feature/new-feature-name
git add .
git commit -m "Add new feature: brief description"
git push origin feature/new-feature-name

# Create pull request for review
```

### Commit Message Standards
```bash
# Format: <type>(<scope>): <description>

# Types:
feat: new feature
fix: bug fix
docs: documentation changes
style: code style changes (formatting, etc.)
refactor: code refactoring
test: adding or updating tests
chore: maintenance tasks

# Examples:
feat(auth): add role-based access control
fix(api): resolve service order creation bug
docs(readme): update installation instructions
style(css): improve button component styling
refactor(db): optimize database query performance
test(auth): add user authentication test cases
chore(deps): update Flask to version 2.3.3
```

### Branch Naming
```bash
# Feature branches
feature/service-order-management
feature/user-role-permissions
feature/planogram-optimization

# Bug fix branches
fix/login-redirect-issue
fix/database-connection-timeout

# Documentation branches
docs/api-documentation
docs/deployment-guide

# Maintenance branches
chore/dependency-updates
chore/code-cleanup
```

## Code Review Guidelines

### Before Submitting Code
1. **Self-Review**: Review your own changes before requesting review
2. **Test Coverage**: Ensure new code includes appropriate tests
3. **Documentation**: Update relevant documentation
4. **Standards Compliance**: Verify code follows these standards

### Review Checklist
- [ ] Code follows established patterns and conventions
- [ ] Security considerations are addressed
- [ ] Error handling is appropriate and consistent
- [ ] Performance implications are considered
- [ ] Tests are included and passing
- [ ] Documentation is updated if needed
- [ ] No debugging code or console.log statements
- [ ] Database operations include proper error handling
- [ ] API endpoints follow RESTful conventions
- [ ] Frontend code works across supported browsers

### Review Process
1. **Functionality**: Does the code work as intended?
2. **Design**: Is the code well-designed and consistent?
3. **Complexity**: Is the code easy to understand?
4. **Tests**: Are the tests well-designed and comprehensive?
5. **Naming**: Are variable and function names clear?
6. **Comments**: Are comments clear and necessary?
7. **Documentation**: Is relevant documentation updated?

These coding standards ensure consistency, maintainability, and quality across the CVD codebase. They should be followed for all new development and applied during refactoring of existing code.