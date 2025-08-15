# Authentication Component


## Metadata
- **ID**: 04_IMPLEMENTATION_COMPONENTS_AUTHENTICATION
- **Type**: Implementation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #code #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #driver-app #features #implementation #integration #logistics #machine-learning #mobile #operations #optimization #performance #planogram #product-placement #pwa #route-management #security #service-orders #troubleshooting #vending-machine
- **Intent**: The authentication component (`auth
- **Audience**: developers, system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/04-implementation/components/
- **Category**: Components
- **Search Keywords**: ###, 401, 403, access, activity, admin, algorithm, audit, auth, auth.py, authentication, authmanager, authorization, automatic, bcrypt

## Overview

The authentication component (`auth.py`) provides comprehensive authentication and authorization functionality for the CVD application. It implements session-based authentication with role-based access control, security monitoring, and audit logging.

## Core Components

### AuthManager Class

The `AuthManager` class is the central authentication service that handles user sessions, validation, and security enforcement.

#### Initialization
```python
class AuthManager:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path
        self.setup_session_config()
```

### Session Management

#### Session Creation
- **Implementation**: `create_session(user_id, db=None)`
- **Token Generation**: Uses `secrets.token_urlsafe(32)` for cryptographically secure session IDs
- **Expiration**: 8-hour session lifetime configured in Flask app settings
- **Device Detection**: Automatically detects device type (mobile, tablet, desktop, bot) from User-Agent
- **Activity Tracking**: Includes IP address, user agent, and activity counters

```python
def create_session(self, user_id, db=None):
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=8)
    
    # Database insertion with activity tracking fields
    cursor.execute('''
        INSERT INTO sessions (id, user_id, expires_at, ip_address, user_agent,
                            last_activity, activity_count, device_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, user_id, expires_at, 
          request.remote_addr, user_agent,
          datetime.now(), 0, device_type))
```

#### Session Validation
- **Implementation**: `validate_session(session_id)`
- **Multi-table Join**: Validates against both `sessions` and `users` tables
- **Expiration Check**: Automatically filters expired sessions
- **User Status Check**: Ensures user is active and not soft-deleted
- **Database Context**: Uses Flask's application context for database connections

```python
def validate_session(self, session_id):
    user = cursor.execute('''
        SELECT u.id, u.username, u.email, u.role, u.is_active, u.is_deleted
        FROM users u
        JOIN sessions s ON s.user_id = u.id
        WHERE s.id = ? AND s.expires_at > ? AND u.is_active = 1 AND u.is_deleted = 0
    ''', (session_id, datetime.now())).fetchone()
```

#### Session Cleanup
- **Implementation**: `cleanup_expired_sessions()`
- **Automatic Cleanup**: Removes expired sessions from database
- **Logging**: Provides feedback on cleanup operations

### Password Security

#### Hashing Implementation
- **Library**: Uses Werkzeug's `generate_password_hash` and `check_password_hash`
- **Algorithm**: bcrypt with automatic salt generation
- **Integration**: Password verification integrated into login flow

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Password hashing in user creation
hashed_password = generate_password_hash(password)

# Password verification in authentication
if check_password_hash(stored_hash, provided_password):
    # Authentication successful
```

### Role-Based Access Control

#### Role Hierarchy
The system implements four distinct user roles with hierarchical permissions:

1. **Admin**: Full system access including user management and database queries
2. **Manager**: Device and planogram management, reports, settings
3. **Driver**: Limited access focused on service orders and device viewing
4. **Viewer**: Read-only access to devices, planograms, routes, and reports

#### Permission Matrix
```python
permissions = {
    'admin': {
        'devices': ['view', 'create', 'edit', 'delete'],
        'planograms': ['view', 'create', 'edit', 'delete'],
        'routes': ['view', 'create', 'edit', 'delete'],
        'service_orders': ['view', 'create', 'edit', 'delete'],
        'reports': ['view', 'create'],
        'users': ['view', 'create', 'edit', 'delete'],
        'database': ['view', 'query'],
        'settings': ['view', 'edit']
    },
    # ... other roles
}
```

### Authentication Decorators

#### Basic Authentication
- **Decorator**: `@auth_manager.require_auth`
- **Usage**: Applied to routes requiring any authenticated user
- **Functionality**: Validates session and populates `g.user` context

```python
@auth_manager.require_auth
def protected_endpoint():
    # g.user contains validated user information
    return jsonify({'user': g.user['username']})
```

#### Role-Based Authorization
- **Decorator**: `@auth_manager.require_role(['admin', 'manager'])`
- **Usage**: Applied to routes requiring specific roles
- **Functionality**: Validates session and checks role permissions
- **Audit Logging**: Logs unauthorized access attempts

```python
@auth_manager.require_role(['admin'])
def admin_only_endpoint():
    # Only admin users can access
    return jsonify({'data': 'sensitive_admin_data'})
```

#### Specialized Decorators
- **Monitoring Access**: `@require_admin_for_monitoring`
- **Usage**: Specific to activity monitoring endpoints
- **Enhanced Logging**: Detailed audit trails for monitoring access

### Security Features

#### User Constraint Validation
- **Service Orders Check**: Prevents deactivation of users with pending service orders
- **Implementation**: `validate_user_constraints(user_id, action_type)`
- **Return Format**: Structured response with constraint details

```python
def validate_user_constraints(user_id, action_type='deactivate'):
    service_orders = get_user_service_order_details(user_id)
    
    if service_orders:
        return {
            'has_constraints': True,
            'constraint_type': 'service_orders',
            'message': f'Cannot {action_type} user with pending service orders',
            'details': {'orders_count': len(service_orders)}
        }
```

#### Audit Logging
- **Implementation**: `log_audit_event(user_id, action, resource_type, resource_id, details)`
- **Automatic Logging**: Integrated into authentication decorators
- **Data Captured**: User ID, action type, resource information, IP address, timestamp

```python
def log_audit_event(user_id, action, resource_type=None, resource_id=None, details=None):
    cursor.execute('''
        INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, action, resource_type, resource_id, details, request.remote_addr))
```

#### User Lifecycle Events
- **Enhanced Logging**: `log_user_lifecycle_event()`
- **Constraint Tracking**: Records constraint violations and their details
- **JSON Details**: Structured logging for complex user operations

### Flask Integration

#### Application Configuration
```python
# Session configuration in app.py
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# AuthManager initialization
auth_manager = AuthManager(app, DATABASE)
```

#### Database Context Integration
- **Connection Management**: Integrates with Flask's application context
- **Connection Reuse**: Uses Flask's `g` object for request-scoped database connections
- **Fallback Strategy**: Direct SQLite connection when Flask context unavailable

### Frontend Integration

#### Session Management
The authentication component integrates with the frontend through:

- **Login Flow**: POST to `/api/auth/login` creates session
- **Session Validation**: GET to `/api/auth/current-user` validates active session
- **Logout Process**: POST to `/api/auth/logout` destroys session
- **Global Auth Check**: `auth-check.js` validates authentication on page loads

#### Cross-Page Communication
```javascript
// Frontend authentication check
await AuthCheck.verify();
// Redirects to login if unauthorized
```

#### API Integration
The CVDApi class handles authentication automatically:
- **Credential Inclusion**: `credentials: 'include'` ensures cookies are sent
- **401 Handling**: Automatic redirect to login on authentication failure
- **Session Persistence**: Maintains session across page navigations

### Security Best Practices

#### Session Security
- **Secure Token Generation**: Cryptographically secure random tokens
- **HTTP-Only Cookies**: Prevents JavaScript access to session cookies
- **HTTPS Enforcement**: Secure cookies in production environment
- **SameSite Protection**: CSRF protection through SameSite cookie attribute

#### Access Control
- **Principle of Least Privilege**: Role-based permissions limit access scope
- **Resource-Level Authorization**: Granular permissions per resource type
- **Audit Trail**: Complete logging of access attempts and privilege escalations

#### Data Protection
- **Soft Delete Support**: Respects soft delete flags in user validation
- **IP Tracking**: Records IP addresses for security monitoring
- **Device Classification**: Tracks device types for anomaly detection

## Error Handling

### Authentication Errors
- **401 Unauthorized**: Invalid or missing session
- **403 Forbidden**: Insufficient permissions for requested resource
- **401 Deactivated**: Account has been deactivated (soft delete)

### Response Format
```json
{
    "error": "Authentication required|Invalid session|Insufficient permissions",
    "details": {
        "required_roles": ["admin", "manager"],
        "user_role": "viewer"
    }
}
```

## Database Schema Requirements

### Sessions Table
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    last_activity TIMESTAMP,
    activity_count INTEGER DEFAULT 0,
    device_type TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Users Table Integration
```sql
-- Required fields for authentication
id INTEGER PRIMARY KEY,
username TEXT UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
email TEXT UNIQUE NOT NULL,
role TEXT NOT NULL,
is_active BOOLEAN DEFAULT 1,
is_deleted BOOLEAN DEFAULT 0,
deleted_at TIMESTAMP,
deleted_by TEXT
```

### Audit Log Table
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id INTEGER,
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Performance Considerations

### Database Optimization
- **Session Cleanup**: Regular cleanup of expired sessions prevents table bloat
- **Index Strategy**: Primary keys and foreign keys provide efficient lookups
- **Connection Pooling**: Flask's request context provides connection reuse

### Security Performance
- **bcrypt Efficiency**: Werkzeug's implementation provides optimal performance
- **Session Validation**: Single query joins for efficient user validation
- **Audit Logging**: Asynchronous logging to prevent performance impact

## Troubleshooting

### Common Issues
1. **Session Expiry**: Check `PERMANENT_SESSION_LIFETIME` configuration
2. **Permission Denied**: Verify role assignments and permission matrix
3. **Database Lock**: Ensure proper connection cleanup in exception handling
4. **Cookie Issues**: Verify HTTPS configuration for secure cookies

### Debug Information
- **Session Details**: Available in audit log for debugging
- **Permission Matrix**: Accessible via `get_user_permissions(role)`
- **User Context**: Available in `g.user` within request context