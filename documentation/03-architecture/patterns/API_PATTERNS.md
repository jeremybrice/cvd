# API Design Patterns


## Metadata
- **ID**: 03_ARCHITECTURE_PATTERNS_API_PATTERNS
- **Type**: Architecture
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #architecture #authentication #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #quality-assurance #reporting #route-management #security #service-orders #system-design #technical #testing #troubleshooting #vending-machine
- **Intent**: Architecture for API Design Patterns
- **Audience**: developers, system administrators, managers, end users, architects
- **Related**: INTEGRATION_PATTERNS.md, FRONTEND_PATTERNS.md, SECURITY_PATTERNS.md, DATABASE_PATTERNS.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/03-architecture/patterns/
- **Category**: Patterns
- **Search Keywords**: 1.0, 2025-08-12, api, args,, authentication, authorization, cabinet, consistent, conventions, conventions:, cvd:, design, device, dex, document

**Document Version:** 1.0  
**Last Updated:** 2025-08-12  
**Status:** Complete

## Introduction

This document outlines the REST API design patterns, conventions, and best practices implemented in the CVD system. These patterns ensure consistency, maintainability, and reliability across all API endpoints.

## Table of Contents

1. [REST Resource Design](#rest-resource-design)
2. [HTTP Method Conventions](#http-method-conventions)
3. [URL Structure Patterns](#url-structure-patterns)
4. [Error Handling Patterns](#error-handling-patterns)
5. [Request/Response Patterns](#requestresponse-patterns)
6. [Authentication Patterns](#authentication-patterns)
7. [Validation Patterns](#validation-patterns)
8. [Pagination and Filtering](#pagination-and-filtering)
9. [Rate Limiting and Throttling](#rate-limiting-and-throttling)
10. [API Versioning Strategy](#api-versioning-strategy)

## REST Resource Design

### Resource Naming Conventions

**Implementation in CVD:**
```python
# Collection resources (plural nouns)
@app.route('/api/users', methods=['GET', 'POST'])
@app.route('/api/devices', methods=['GET', 'POST'])
@app.route('/api/service-orders', methods=['GET', 'POST'])
@app.route('/api/planograms', methods=['GET', 'POST'])

# Individual resources (with ID)
@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/api/devices/<int:device_id>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/api/service-orders/<int:order_id>', methods=['GET', 'PUT'])

# Sub-resources
@app.route('/api/users/<int:user_id>/activity', methods=['GET'])
@app.route('/api/devices/<int:device_id>/cabinets', methods=['GET'])
@app.route('/api/service-orders/<int:order_id>/pick-list', methods=['GET'])
```

**Conventions:**
- Use plural nouns for collections (`/users`, `/devices`)
- Use specific resource IDs for individual items (`/users/123`)
- Use sub-resources for related data (`/users/123/activity`)
- Use kebab-case for multi-word resources (`service-orders`)

### Resource Hierarchy Pattern

```
/api/devices/{device_id}
├── /cabinets                     # Device cabinets
├── /planograms                   # Device planograms
├── /metrics                      # Device performance metrics
└── /maintenance-history          # Service history

/api/service-orders/{order_id}
├── /pick-list                    # Order pick list
├── /execution                    # Order execution
└── /photos                       # Service photos

/api/users/{user_id}
├── /activity                     # User activity log
├── /audit-trail                  # Audit events
└── /preferences                  # User preferences
```

## HTTP Method Conventions

### Standard CRUD Operations

**Implementation in CVD:**
```python
# CREATE - POST to collection
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    # Validation and creation logic
    return jsonify({'id': new_user_id, 'message': 'User created'}), 201

# READ - GET collection or individual
@app.route('/api/users', methods=['GET'])
def get_users():
    users = db.execute('SELECT * FROM users WHERE deleted = 0').fetchall()
    return jsonify([dict(user) for user in users]), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.execute('SELECT * FROM users WHERE id = ? AND deleted = 0', 
                     (user_id,)).fetchone()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(dict(user)), 200

# UPDATE - PUT for full update
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    # Update logic
    return jsonify({'message': 'User updated'}), 200

# DELETE - DELETE for removal (soft delete in CVD)
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Soft delete implementation
    db.execute('''UPDATE users SET deleted = 1, deleted_at = ?, deleted_by = ?
                  WHERE id = ?''', (datetime.now(), current_user_id, user_id))
    return jsonify({'message': 'User deleted'}), 200
```

### Non-CRUD Operations

**Implementation in CVD:**
```python
# Action-oriented endpoints use POST
@app.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@app.route('/api/users/<int:user_id>/deactivate', methods=['PUT'])
@app.route('/api/users/<int:user_id>/activate', methods=['PUT'])
@app.route('/api/service-orders/execute', methods=['POST'])
@app.route('/api/dex/parse', methods=['POST'])

# Batch operations
@app.route('/api/users/batch-deactivate', methods=['POST'])
@app.route('/api/devices/bulk-update', methods=['PUT'])
```

## URL Structure Patterns

### Hierarchical Resource Structure

```python
# Base API namespace
API_BASE = '/api'

# Version-agnostic structure
/api/auth/*                       # Authentication operations
/api/users/*                      # User management
/api/devices/*                    # Device management
/api/planograms/*                 # Planogram operations
/api/service-orders/*             # Service order management
/api/analytics/*                  # Analytics and reporting
/api/dex/*                        # DEX file processing
/api/metrics/*                    # Performance metrics
/api/security/*                   # Security operations
```

### Query Parameter Conventions

**Implementation in CVD:**
```python
# Filtering
@app.route('/api/devices')
def get_devices():
    route_id = request.args.get('route_id')
    location_id = request.args.get('location_id')
    status = request.args.get('status')
    
    query = 'SELECT * FROM devices WHERE deleted = 0'
    params = []
    
    if route_id:
        query += ' AND route_id = ?'
        params.append(route_id)
    
    if location_id:
        query += ' AND location_id = ?'
        params.append(location_id)
        
    devices = db.execute(query, params).fetchall()
    return jsonify([dict(device) for device in devices])

# Sorting and pagination
# GET /api/devices?sort=name&order=asc&limit=50&offset=0
```

## Error Handling Patterns

### Standardized Error Response Format

**Implementation in CVD:**
```python
def create_error_response(message, status_code, error_code=None, details=None):
    """Create standardized error response"""
    error_response = {
        'error': {
            'message': message,
            'code': error_code or status_code,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
    }
    return jsonify(error_response), status_code

# Usage examples
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = db.execute('SELECT * FROM users WHERE id = ? AND deleted = 0', 
                         (user_id,)).fetchone()
        if not user:
            return create_error_response('User not found', 404, 'USER_NOT_FOUND')
        
        return jsonify(dict(user)), 200
        
    except sqlite3.IntegrityError as e:
        return create_error_response('Database integrity error', 400, 
                                   'INTEGRITY_ERROR', str(e))
    except Exception as e:
        log_audit_event('system', 'error', f'Unexpected error: {str(e)}')
        return create_error_response('Internal server error', 500, 
                                   'INTERNAL_ERROR')
```

### HTTP Status Code Conventions

```python
# Success responses
200  # OK - Successful GET, PUT requests
201  # Created - Successful POST requests
202  # Accepted - Async operation started
204  # No Content - Successful DELETE requests

# Client error responses
400  # Bad Request - Invalid request data
401  # Unauthorized - Authentication required
403  # Forbidden - Insufficient permissions
404  # Not Found - Resource doesn't exist
409  # Conflict - Resource state conflict
422  # Unprocessable Entity - Validation errors

# Server error responses
500  # Internal Server Error - Unexpected error
502  # Bad Gateway - Upstream service error
503  # Service Unavailable - Temporary unavailability

# CVD-specific error codes
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(403)  
def forbidden(error):
    return jsonify({'error': 'Forbidden - insufficient permissions'}), 403
```

## Request/Response Patterns

### Request Validation Pattern

**Implementation in CVD:**
```python
def validate_request_data(required_fields, optional_fields=None):
    """Decorator for request validation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.json:
                return create_error_response('Request body required', 400)
            
            data = request.json
            
            # Check required fields
            missing_fields = [field for field in required_fields 
                            if field not in data or data[field] is None]
            if missing_fields:
                return create_error_response(
                    f'Missing required fields: {", ".join(missing_fields)}', 
                    400, 'MISSING_FIELDS'
                )
            
            # Validate field types and constraints
            validation_errors = validate_field_constraints(data)
            if validation_errors:
                return create_error_response(
                    'Validation errors', 422, 'VALIDATION_ERROR', 
                    validation_errors
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@app.route('/api/users', methods=['POST'])
@validate_request_data(['username', 'password', 'role'], ['email', 'full_name'])
@require_role(['admin'])
def create_user():
    data = request.json
    # User creation logic
    return jsonify({'id': user_id, 'message': 'User created'}), 201
```

### Response Formatting Pattern

**Implementation in CVD:**
```python
def create_success_response(data=None, message=None, status_code=200):
    """Create standardized success response"""
    response = {}
    
    if data is not None:
        response['data'] = data
        
    if message:
        response['message'] = message
        
    response['timestamp'] = datetime.now().isoformat()
    response['success'] = True
    
    return jsonify(response), status_code

# Consistent response formats
@app.route('/api/devices/<int:device_id>')
def get_device(device_id):
    device = get_device_by_id(device_id)
    if not device:
        return create_error_response('Device not found', 404)
    
    return create_success_response({
        'device': dict(device),
        'cabinets': get_device_cabinets(device_id),
        'metrics': get_device_metrics(device_id)
    })
```

## Authentication Patterns

### Session-Based Authentication

**Implementation in CVD:**
```python
def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'session_id' not in session or 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Validate session
        db_session = db.execute('''
            SELECT s.*, u.role, u.deleted
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.id = ? AND s.expires_at > ? AND u.deleted = 0
        ''', (session['session_id'], datetime.now())).fetchone()
        
        if not db_session:
            session.clear()
            return jsonify({'error': 'Session expired'}), 401
        
        # Update session activity
        db.execute('''
            UPDATE sessions 
            SET last_activity = ?, activity_count = activity_count + 1
            WHERE id = ?
        ''', (datetime.now(), session['session_id']))
        
        g.current_user = dict(db_session)
        return func(*args, **kwargs)
    
    return wrapper

def require_role(allowed_roles):
    """Decorator to require specific roles"""
    def decorator(func):
        @wraps(func)
        @require_auth
        def wrapper(*args, **kwargs):
            if g.current_user['role'] not in allowed_roles:
                log_audit_event(g.current_user['user_id'], 'access_denied',
                               f'Attempted access to {request.endpoint}')
                return jsonify({'error': 'Insufficient permissions'}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### API Key Authentication Pattern (for future implementation)

```python
def require_api_key(func):
    """Decorator for API key authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key
        key_record = db.execute('''
            SELECT * FROM api_keys 
            WHERE key_hash = ? AND active = 1 AND expires_at > ?
        ''', (hash_api_key(api_key), datetime.now())).fetchone()
        
        if not key_record:
            return jsonify({'error': 'Invalid API key'}), 401
        
        g.api_key_info = dict(key_record)
        return func(*args, **kwargs)
    
    return wrapper
```

## Validation Patterns

### Input Validation Pattern

**Implementation in CVD:**
```python
def validate_user_data(data, is_update=False):
    """Validate user creation/update data"""
    errors = []
    
    # Username validation
    if 'username' in data:
        username = data['username']
        if not username or len(username.strip()) < 3:
            errors.append('Username must be at least 3 characters long')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores')
    
    # Password validation (only for new users or password changes)
    if 'password' in data and not is_update:
        password = data['password']
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', password):
            errors.append('Password must contain at least one number')
    
    # Role validation
    if 'role' in data:
        valid_roles = ['admin', 'manager', 'driver', 'viewer']
        if data['role'] not in valid_roles:
            errors.append(f'Role must be one of: {", ".join(valid_roles)}')
    
    return errors

@app.route('/api/users', methods=['POST'])
@require_role(['admin'])
def create_user():
    data = request.json
    
    # Validate input
    validation_errors = validate_user_data(data)
    if validation_errors:
        return create_error_response(
            'Validation failed', 422, 'VALIDATION_ERROR', 
            validation_errors
        )
    
    # Check for duplicate username
    existing_user = db.execute('''
        SELECT id FROM users WHERE username = ? AND deleted = 0
    ''', (data['username'],)).fetchone()
    
    if existing_user:
        return create_error_response(
            'Username already exists', 409, 'DUPLICATE_USERNAME'
        )
    
    # Create user
    # ... user creation logic
```

## Pagination and Filtering

### Pagination Pattern

```python
def paginate_query(base_query, page=1, per_page=50, max_per_page=100):
    """Add pagination to SQL query"""
    per_page = min(per_page, max_per_page)
    offset = (page - 1) * per_page
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_subquery"
    total_count = db.execute(count_query).fetchone()[0]
    
    # Add pagination
    paginated_query = f"{base_query} LIMIT ? OFFSET ?"
    results = db.execute(paginated_query, (per_page, offset)).fetchall()
    
    return {
        'data': [dict(row) for row in results],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': (total_count + per_page - 1) // per_page,
            'has_next': page * per_page < total_count,
            'has_prev': page > 1
        }
    }

@app.route('/api/devices')
@require_auth
def get_devices():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    base_query = '''
        SELECT d.*, l.name as location_name, r.name as route_name
        FROM devices d
        LEFT JOIN locations l ON d.location_id = l.id
        LEFT JOIN routes r ON d.route_id = r.id
        WHERE d.deleted = 0
        ORDER BY d.name
    '''
    
    result = paginate_query(base_query, page, per_page)
    return jsonify(result)
```

## Rate Limiting and Throttling

### Basic Rate Limiting Pattern

```python
from collections import defaultdict, deque
from time import time

# Simple in-memory rate limiter (for production, use Redis)
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(deque)
    
    def is_allowed(self, key, limit, window):
        """Check if request is allowed within rate limit"""
        now = time()
        request_times = self.requests[key]
        
        # Remove old requests outside window
        while request_times and request_times[0] < now - window:
            request_times.popleft()
        
        # Check if under limit
        if len(request_times) < limit:
            request_times.append(now)
            return True
        
        return False

rate_limiter = RateLimiter()

def rate_limit(limit=100, window=3600):  # 100 requests per hour default
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use IP address as key (or API key if available)
            key = request.remote_addr
            if hasattr(g, 'api_key_info'):
                key = f"api_key_{g.api_key_info['id']}"
            
            if not rate_limiter.is_allowed(key, limit, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }), 429
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@app.route('/api/dex/parse', methods=['POST'])
@rate_limit(limit=10, window=300)  # 10 requests per 5 minutes
@require_auth
def parse_dex_file():
    # DEX parsing logic
    pass
```

## API Versioning Strategy

### URL Path Versioning (Recommended for Future)

```python
# Version 1 (current - no explicit version)
@app.route('/api/devices', methods=['GET'])
@app.route('/api/users', methods=['GET'])

# Version 2 (future)
@app.route('/api/v2/devices', methods=['GET'])
@app.route('/api/v2/users', methods=['GET'])

# Version compatibility layer
@app.route('/api/v1/devices', methods=['GET'])
def get_devices_v1():
    # Map to current implementation or provide compatibility
    return get_devices()
```

### Header-Based Versioning (Alternative)

```python
def get_api_version():
    """Get API version from request headers"""
    return request.headers.get('API-Version', 'v1')

@app.route('/api/devices', methods=['GET'])
def get_devices():
    version = get_api_version()
    
    if version == 'v2':
        return get_devices_v2()
    else:
        return get_devices_v1()
```

## Implementation Guidelines

### API Endpoint Checklist

- [ ] **Authentication**: Proper auth decorators applied
- [ ] **Authorization**: Role-based access control
- [ ] **Validation**: Input validation and sanitization
- [ ] **Error Handling**: Consistent error responses
- [ ] **Logging**: Audit trail for sensitive operations
- [ ] **Documentation**: Endpoint documentation updated
- [ ] **Testing**: Unit and integration tests written
- [ ] **Rate Limiting**: Applied where appropriate

### Development Standards

1. **Consistent Naming**: Follow REST conventions
2. **Error Handling**: Always provide meaningful error messages
3. **Validation**: Validate all inputs before processing
4. **Security**: Apply appropriate auth/authz patterns
5. **Logging**: Log important operations and errors
6. **Testing**: Write comprehensive tests for all endpoints

## Related Documentation

- [Database Patterns](./DATABASE_PATTERNS.md) - Data access patterns
- [Security Patterns](./SECURITY_PATTERNS.md) - Authentication and authorization
- [Frontend Patterns](./FRONTEND_PATTERNS.md) - Client-side API consumption
- [Integration Patterns](./INTEGRATION_PATTERNS.md) - Service integration patterns

## Examples and References

- Flask REST API Best Practices
- RESTful Web Services Design Guidelines
- HTTP Status Code Reference
- OAuth 2.0 and JWT Authentication Patterns