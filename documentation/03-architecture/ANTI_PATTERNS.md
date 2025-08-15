# Architectural Anti-Patterns to Avoid


## Metadata
- **ID**: 03_ARCHITECTURE_ANTI_PATTERNS
- **Type**: Architecture
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #architecture #authentication #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #quality-assurance #reporting #route-management #security #service-orders #system-design #technical #testing #troubleshooting #vending-machine
- **Intent**: Architecture for Architectural Anti-Patterns to Avoid
- **Audience**: system administrators, managers, end users, architects
- **Related**: CODING_STANDARDS.md, BEST_PRACTICES.md, PERFORMANCE.md, SECURITY_PATTERNS.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/03-architecture/
- **Category**: 03 Architecture
- **Search Keywords**: **better, 1.0, 2025-08-12, analysis, anti, anti-pattern:, api, approach:, approach:**, architectural, avoid, bad:, better, code, database:

**Document Version:** 1.0  
**Last Updated:** 2025-08-12  
**Status:** Complete

## Introduction

This document identifies common architectural anti-patterns, design mistakes, and implementation pitfalls that should be avoided when working with the CVD system. Learning from these anti-patterns helps maintain code quality, system performance, and long-term maintainability.

## Table of Contents

1. [Database Anti-Patterns](#database-anti-patterns)
2. [API Design Anti-Patterns](#api-design-anti-patterns)
3. [Frontend Architecture Anti-Patterns](#frontend-architecture-anti-patterns)
4. [Security Anti-Patterns](#security-anti-patterns)
5. [Performance Anti-Patterns](#performance-anti-patterns)
6. [Integration Anti-Patterns](#integration-anti-patterns)
7. [Code Organization Anti-Patterns](#code-organization-anti-patterns)
8. [Error Handling Anti-Patterns](#error-handling-anti-patterns)
9. [Testing Anti-Patterns](#testing-anti-patterns)
10. [Deployment Anti-Patterns](#deployment-anti-patterns)

## Database Anti-Patterns

### 1. The God Table

**Anti-Pattern:**
Creating massive tables that try to handle multiple concerns in a single entity.

**Problem Example:**
```sql
-- BAD: Mixing device data with sales, maintenance, and user data
CREATE TABLE everything (
    id INTEGER PRIMARY KEY,
    device_name TEXT,
    device_serial TEXT,
    location_address TEXT,
    user_name TEXT,
    user_email TEXT,
    sale_amount DECIMAL,
    sale_date DATE,
    maintenance_date DATE,
    maintenance_notes TEXT,
    -- ... 50+ more columns
);
```

**Why It's Bad:**
- Violates normalization principles
- Creates unnecessary data duplication
- Makes queries complex and slow
- Difficult to maintain and extend
- Poor data integrity

**Better Approach:**
```sql
-- GOOD: Properly normalized tables
CREATE TABLE devices (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    serial_number TEXT UNIQUE,
    location_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    device_id INTEGER NOT NULL,
    amount DECIMAL NOT NULL,
    sale_date DATE NOT NULL,
    FOREIGN KEY (device_id) REFERENCES devices(id)
);

CREATE TABLE maintenance_records (
    id INTEGER PRIMARY KEY,
    device_id INTEGER NOT NULL,
    maintenance_date DATE NOT NULL,
    notes TEXT,
    FOREIGN KEY (device_id) REFERENCES devices(id)
);
```

### 2. Hard Delete Without Backup Strategy

**Anti-Pattern:**
Physically deleting data without considering recovery or audit requirements.

**Problem Example:**
```python
# BAD: Permanent data deletion
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    return jsonify({'message': 'User deleted permanently'})
```

**Why It's Bad:**
- No way to recover accidentally deleted data
- Loses audit trail
- May break referential integrity
- Compliance issues

**Better Approach (CVD Implementation):**
```python
# GOOD: Soft delete with audit trail
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_role(['admin'])
def delete_user(user_id):
    db.execute('''
        UPDATE users 
        SET is_deleted = 1, deleted_at = ?, deleted_by = ?
        WHERE id = ?
    ''', (datetime.now(), g.current_user['id'], user_id))
    
    log_audit_event(g.current_user['id'], 'user_deleted', 
                   'user', user_id)
    
    return jsonify({'message': 'User deleted successfully'})
```

### 3. Missing Database Constraints

**Anti-Pattern:**
Relying solely on application logic for data validation without database constraints.

**Problem Example:**
```sql
-- BAD: No constraints, invalid data possible
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    email TEXT,
    role TEXT
);
```

**Better Approach:**
```sql
-- GOOD: Proper constraints prevent invalid data
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL CHECK(length(username) >= 3),
    email TEXT UNIQUE NOT NULL CHECK(email LIKE '%@%.%'),
    role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Design Anti-Patterns

### 4. Inconsistent REST Endpoints

**Anti-Pattern:**
Mixing different naming conventions and HTTP methods inappropriately.

**Problem Example:**
```python
# BAD: Inconsistent naming and methods
@app.route('/getUsers', methods=['GET'])           # camelCase
@app.route('/api/device-list', methods=['GET'])    # kebab-case  
@app.route('/CreateOrder', methods=['GET'])        # Wrong method
@app.route('/api/planogram/delete/<id>')           # Should use DELETE method
```

**Better Approach (CVD Implementation):**
```python
# GOOD: Consistent RESTful design
@app.route('/api/users', methods=['GET'])                    # Collection GET
@app.route('/api/users', methods=['POST'])                   # Collection POST
@app.route('/api/users/<int:user_id>', methods=['GET'])      # Resource GET
@app.route('/api/users/<int:user_id>', methods=['PUT'])      # Resource PUT
@app.route('/api/users/<int:user_id>', methods=['DELETE'])   # Resource DELETE
@app.route('/api/service-orders', methods=['POST'])          # kebab-case consistently
```

### 5. Exposing Internal Implementation Details

**Anti-Pattern:**
Including database-specific details or internal system information in API responses.

**Problem Example:**
```python
# BAD: Exposing internal details
@app.route('/api/users')
def get_users():
    users = db.execute('SELECT * FROM users').fetchall()
    return jsonify([{
        'id': user['id'],
        'username': user['username'],
        'password_hash': user['password_hash'],  # NEVER expose!
        'table_name': 'users',                   # Internal detail
        'query_time_ms': 45,                     # Internal metric
        'deleted_by': user['deleted_by']         # Internal soft delete field
    } for user in users])
```

**Better Approach:**
```python
# GOOD: Clean, filtered API response
@app.route('/api/users')
@require_role(['admin'])
def get_users():
    users = db.execute('''
        SELECT id, username, email, role, created_at, is_active
        FROM users WHERE is_deleted = 0
    ''').fetchall()
    
    return jsonify([{
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role': user['role'],
        'created_at': user['created_at'],
        'is_active': user['is_active']
    } for user in users])
```

### 6. No Input Validation

**Anti-Pattern:**
Trusting user input without validation or sanitization.

**Problem Example:**
```python
# BAD: No validation, vulnerable to attacks
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    
    # Direct database insertion without validation
    cursor.execute(f'''
        INSERT INTO users (username, email, role)
        VALUES ('{data["username"]}', '{data["email"]}', '{data["role"]}')
    ''')  # SQL injection vulnerability!
```

**Better Approach:**
```python
# GOOD: Proper validation and parameterized queries
@app.route('/api/users', methods=['POST'])
@require_role(['admin'])
def create_user():
    data = request.json
    
    # Validate input
    validation_errors = validate_user_data(data)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    # Parameterized query prevents SQL injection
    cursor.execute('''
        INSERT INTO users (username, email, role, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (data['username'], data['email'], data['role'], 
          generate_password_hash(data['password'])))
```

## Frontend Architecture Anti-Patterns

### 7. Monolithic Frontend Files

**Anti-Pattern:**
Putting all JavaScript functionality in a single massive file.

**Problem Example:**
```javascript
// BAD: 5000+ line single file with everything
// pages/everything.html
<script>
// Authentication code
function login() { /* 200 lines */ }
function logout() { /* 50 lines */ }

// Device management code  
function createDevice() { /* 300 lines */ }
function updateDevice() { /* 250 lines */ }

// Planogram code
function loadPlanogram() { /* 500 lines */ }
function savePlanogram() { /* 400 lines */ }

// Service order code
function createServiceOrder() { /* 600 lines */ }

// Map functionality
function initializeMap() { /* 800 lines */ }

// And much more...
</script>
```

**Better Approach (CVD Implementation):**
```html
<!-- GOOD: Modular approach with separated concerns -->
<!DOCTYPE html>
<html>
<head>
    <title>Device Management</title>
</head>
<body>
    <!-- Page content -->
    
    <!-- Core scripts -->
    <script src="/api.js"></script>
    <script src="/auth-check.js"></script>
    
    <!-- Helper modules -->
    <script src="/js/toast-helper.js"></script>
    <script src="/js/loading-helper.js"></script>
    
    <!-- Page-specific functionality -->
    <script>
        // Only device management code here
        class DeviceManager {
            // Focused, single-responsibility code
        }
    </script>
</body>
</html>
```

### 8. No Error Boundaries

**Anti-Pattern:**
Not handling errors gracefully, causing the entire application to crash.

**Problem Example:**
```javascript
// BAD: No error handling
async function loadDevices() {
    const response = await fetch('/api/devices');
    const devices = await response.json();  // Will crash on 500 error
    
    devices.forEach(device => {
        document.getElementById('device-list').innerHTML += 
            `<div>${device.name}</div>`;  // Will crash if devices is null
    });
}
```

**Better Approach:**
```javascript
// GOOD: Comprehensive error handling
async function loadDevices() {
    try {
        const response = await fetch('/api/devices');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const devices = await response.json();
        
        if (!devices || !Array.isArray(devices)) {
            throw new Error('Invalid device data received');
        }
        
        const deviceList = document.getElementById('device-list');
        if (!deviceList) {
            throw new Error('Device list container not found');
        }
        
        deviceList.innerHTML = devices.map(device => 
            `<div class="device-item">${escapeHtml(device.name || 'Unknown')}</div>`
        ).join('');
        
    } catch (error) {
        console.error('Failed to load devices:', error);
        
        if (window.Toast) {
            Toast.error('Failed to load devices. Please try again.');
        }
        
        // Show fallback UI
        showErrorState('device-list', 'Unable to load devices');
    }
}
```

### 9. Inline Event Handlers

**Anti-Pattern:**
Using inline JavaScript event handlers in HTML.

**Problem Example:**
```html
<!-- BAD: Inline handlers, hard to maintain -->
<button onclick="deleteUser(123); updateCounter(); showToast('Deleted');">
    Delete User
</button>
<form onsubmit="validateForm(); submitData(); trackEvent(); return false;">
    <!-- form fields -->
</form>
```

**Better Approach:**
```html
<!-- GOOD: Proper event handling -->
<button class="btn btn-danger" data-user-id="123" data-action="delete-user">
    Delete User
</button>
<form class="user-form" data-form-type="user-creation">
    <!-- form fields -->
</form>

<script>
// Centralized event handling
document.addEventListener('DOMContentLoaded', () => {
    // Delete button handler
    document.addEventListener('click', (event) => {
        if (event.target.matches('[data-action="delete-user"]')) {
            event.preventDefault();
            const userId = event.target.dataset.userId;
            handleUserDeletion(userId);
        }
    });
    
    // Form submission handler
    document.addEventListener('submit', (event) => {
        if (event.target.matches('.user-form')) {
            event.preventDefault();
            handleFormSubmission(event.target);
        }
    });
});
</script>
```

## Security Anti-Patterns

### 10. Storing Secrets in Code

**Anti-Pattern:**
Hard-coding API keys, passwords, and other secrets in source code.

**Problem Example:**
```python
# BAD: Secrets in source code
ANTHROPIC_API_KEY = "sk-ant-api03-xyz123..."  # Visible in version control!
DATABASE_PASSWORD = "supersecret123"
JWT_SECRET = "my-jwt-secret"

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
```

**Better Approach (CVD Implementation):**
```python
# GOOD: Environment variables for secrets
import os

# Secrets from environment
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_hex(32))

# Validate required secrets
if not ANTHROPIC_API_KEY:
    print("Warning: ANTHROPIC_API_KEY not configured")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
```

### 11. No Rate Limiting

**Anti-Pattern:**
Allowing unlimited requests that can lead to abuse or DoS attacks.

**Problem Example:**
```python
# BAD: No rate limiting, vulnerable to abuse
@app.route('/api/expensive-operation', methods=['POST'])
def expensive_operation():
    # This could be called 1000s of times per second
    result = perform_expensive_calculation()
    return jsonify(result)
```

**Better Approach:**
```python
# GOOD: Rate limiting implementation
from collections import defaultdict
import time

request_counts = defaultdict(list)

def rate_limit(max_requests=10, window=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            now = time.time()
            
            # Clean old requests
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if now - req_time < window
            ]
            
            # Check limit
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Record request
            request_counts[client_ip].append(now)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/api/expensive-operation', methods=['POST'])
@rate_limit(max_requests=5, window=300)  # 5 requests per 5 minutes
@require_auth
def expensive_operation():
    result = perform_expensive_calculation()
    return jsonify(result)
```

### 12. SQL Injection Vulnerabilities

**Anti-Pattern:**
Building SQL queries with string concatenation using user input.

**Problem Example:**
```python
# BAD: SQL injection vulnerability
@app.route('/api/users/search')
def search_users():
    search_term = request.args.get('q', '')
    
    # DANGEROUS: Direct string interpolation
    query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"
    results = db.execute(query).fetchall()
    
    return jsonify([dict(row) for row in results])
```

**Better Approach:**
```python
# GOOD: Parameterized queries prevent SQL injection
@app.route('/api/users/search')
@require_auth
def search_users():
    search_term = request.args.get('q', '').strip()
    
    if len(search_term) < 2:
        return jsonify({'error': 'Search term too short'}), 400
    
    # Safe parameterized query
    query = '''
        SELECT id, username, email, role, created_at
        FROM users 
        WHERE (username LIKE ? OR email LIKE ?) 
        AND is_deleted = 0
    '''
    
    search_pattern = f'%{search_term}%'
    results = db.execute(query, (search_pattern, search_pattern)).fetchall()
    
    return jsonify([dict(row) for row in results])
```

## Performance Anti-Patterns

### 13. N+1 Query Problem

**Anti-Pattern:**
Making multiple database queries in a loop instead of using joins or batch queries.

**Problem Example:**
```python
# BAD: N+1 queries (1 + N queries for N devices)
@app.route('/api/devices/with-locations')
def get_devices_with_locations():
    devices = db.execute('SELECT * FROM devices').fetchall()  # 1 query
    
    result = []
    for device in devices:  # N additional queries
        location = db.execute(
            'SELECT * FROM locations WHERE id = ?', 
            (device['location_id'],)
        ).fetchone()
        
        result.append({
            'device': dict(device),
            'location': dict(location) if location else None
        })
    
    return jsonify(result)
```

**Better Approach:**
```python
# GOOD: Single query with JOIN
@app.route('/api/devices/with-locations')
@require_auth
def get_devices_with_locations():
    query = '''
        SELECT 
            d.*,
            l.name as location_name,
            l.address as location_address,
            l.latitude as location_latitude,
            l.longitude as location_longitude
        FROM devices d
        LEFT JOIN locations l ON d.location_id = l.id
        WHERE d.deleted = 0
        ORDER BY d.name
    '''
    
    results = db.execute(query).fetchall()
    
    devices = []
    for row in results:
        device_data = {
            'id': row['id'],
            'name': row['name'],
            'serial_number': row['serial_number'],
            'location': {
                'name': row['location_name'],
                'address': row['location_address'],
                'latitude': row['location_latitude'],
                'longitude': row['location_longitude']
            } if row['location_name'] else None
        }
        devices.append(device_data)
    
    return jsonify(devices)
```

### 14. Missing Database Indexes

**Anti-Pattern:**
Not adding indexes for frequently queried columns, leading to slow queries.

**Problem Example:**
```sql
-- BAD: No indexes on frequently searched columns
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT,
    resource_type TEXT,
    created_at TIMESTAMP
);

-- Slow queries:
-- SELECT * FROM audit_log WHERE user_id = 123;
-- SELECT * FROM audit_log WHERE created_at > '2023-01-01';
-- SELECT * FROM audit_log WHERE action = 'login';
```

**Better Approach (CVD Implementation):**
```sql
-- GOOD: Proper indexes for query performance
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id INTEGER,
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Performance indexes
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);

-- Composite index for common query patterns
CREATE INDEX idx_audit_user_action ON audit_log(user_id, action);
```

### 15. Synchronous Long-Running Operations

**Anti-Pattern:**
Performing time-consuming operations in the request-response cycle.

**Problem Example:**
```python
# BAD: Synchronous heavy operation blocks request
@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    # This takes 30+ seconds and blocks the request
    data = fetch_all_sales_data()      # 10 seconds
    processed = analyze_data(data)     # 15 seconds  
    report = generate_pdf(processed)   # 5 seconds
    
    return send_file(report, as_attachment=True)  # User waits 30+ seconds
```

**Better Approach:**
```python
# GOOD: Asynchronous processing with status tracking
import threading
import uuid

report_status = {}  # In production, use Redis or database

@app.route('/api/reports/generate', methods=['POST'])
@require_auth
def generate_report():
    task_id = str(uuid.uuid4())
    user_id = g.current_user['user_id']
    
    # Start background task
    threading.Thread(
        target=generate_report_async,
        args=(task_id, user_id),
        daemon=True
    ).start()
    
    report_status[task_id] = {
        'status': 'processing',
        'created_at': datetime.now().isoformat(),
        'user_id': user_id
    }
    
    return jsonify({
        'task_id': task_id,
        'status': 'processing',
        'message': 'Report generation started'
    }), 202

@app.route('/api/reports/status/<task_id>')
@require_auth
def get_report_status(task_id):
    status = report_status.get(task_id)
    if not status:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check if user can access this task
    if status['user_id'] != g.current_user['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(status)

def generate_report_async(task_id, user_id):
    try:
        report_status[task_id]['status'] = 'processing'
        
        # Heavy operations
        data = fetch_all_sales_data()
        report_status[task_id]['status'] = 'analyzing'
        
        processed = analyze_data(data)
        report_status[task_id]['status'] = 'generating'
        
        report_path = generate_pdf(processed)
        
        report_status[task_id] = {
            'status': 'completed',
            'download_url': f'/api/reports/download/{task_id}',
            'completed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        report_status[task_id] = {
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        }
```

## Integration Anti-Patterns

### 16. Tight Coupling to External Services

**Anti-Pattern:**
Making the application heavily dependent on external service availability.

**Problem Example:**
```python
# BAD: Application fails if external service is down
@app.route('/api/devices', methods=['POST'])
def create_device():
    data = request.json
    
    # Geocode address - if this fails, device creation fails
    lat, lon = geocode_address(data['address'])  # No fallback!
    if not lat or not lon:
        return jsonify({'error': 'Invalid address'}), 400
    
    # Create device
    device_id = create_device_record(data, lat, lon)
    return jsonify({'id': device_id})
```

**Better Approach (CVD Implementation):**
```python
# GOOD: Graceful degradation with fallbacks
@app.route('/api/devices', methods=['POST'])
@require_role(['admin', 'manager'])
def create_device():
    data = request.json
    
    # Validate input
    validation_errors = validate_device_data(data)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    # Try to geocode, but don't fail if it doesn't work
    lat, lon = None, None
    if data.get('address'):
        try:
            lat, lon = geocode_address(data['address'])
        except Exception as e:
            # Log error but continue
            print(f"Geocoding failed: {e}")
            # Could queue for retry later
    
    # Create device regardless of geocoding success
    device_id = create_device_record(data, lat, lon)
    
    response_data = {
        'id': device_id,
        'message': 'Device created successfully'
    }
    
    if not lat or not lon:
        response_data['warnings'] = ['Address could not be geocoded']
    
    return jsonify(response_data), 201
```

### 17. No Circuit Breaker for External Calls

**Anti-Pattern:**
Continuing to call failing external services, causing cascading failures.

**Problem Example:**
```python
# BAD: No protection against failing external service
def get_ai_recommendations(device_id):
    # This will keep failing if AI service is down
    response = requests.post('https://ai-service.com/optimize', 
                           json={'device_id': device_id})
    return response.json()  # Crashes entire request chain

@app.route('/api/planograms/optimize/<int:device_id>')
def optimize_planogram(device_id):
    recommendations = get_ai_recommendations(device_id)  # Fails hard
    return jsonify(recommendations)
```

**Better Approach:**
```python
# GOOD: Circuit breaker pattern (see Integration Patterns)
class CircuitBreaker:
    # Implementation in integration_patterns.md
    pass

ai_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=300)

def get_ai_recommendations(device_id):
    try:
        return ai_breaker.call(lambda: call_ai_service(device_id))
    except Exception as e:
        # Return fallback recommendations
        return get_fallback_recommendations(device_id)

@app.route('/api/planograms/optimize/<int:device_id>')
@require_auth
def optimize_planogram(device_id):
    try:
        recommendations = get_ai_recommendations(device_id)
        
        if not recommendations:
            return jsonify({
                'message': 'AI service unavailable, showing basic recommendations',
                'recommendations': get_basic_recommendations(device_id)
            })
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({
            'error': 'Unable to generate recommendations',
            'fallback': get_basic_recommendations(device_id)
        }), 503
```

## Code Organization Anti-Patterns

### 18. Everything in One File

**Anti-Pattern:**
Putting all application logic in a single massive file.

**Problem Example:**
```python
# BAD: 5000+ line app.py with everything
# app.py contains:
# - All route handlers (100+ endpoints)
# - Database models and queries  
# - Business logic
# - External service integrations
# - Utility functions
# - Configuration
# - Authentication logic
# - Email handling
# - File processing
# - And more...
```

**Better Approach (CVD Implementation):**
```
# GOOD: Modular organization
app.py                     # Main application and core routes
auth.py                    # Authentication logic
dex_parser.py             # DEX file processing
planogram_optimizer.py    # AI optimization logic
service_order_service.py  # Service order business logic
activity_tracker.py      # Activity monitoring
security_monitor.py       # Security monitoring
knowledge_base.py         # Knowledge base functionality

# Supporting directories
/ai_services/             # AI service integrations
/migrations/              # Database migrations  
/tests/                   # Test files
/tools/                   # Utility scripts
/docs/                    # Documentation
```

### 19. Magic Numbers and Strings

**Anti-Pattern:**
Using hard-coded values throughout the code without explanation.

**Problem Example:**
```python
# BAD: Magic numbers and strings everywhere
def process_sales_data(data):
    if data['amount'] > 50:        # What is 50?
        category = 'high'
    elif data['amount'] > 20:      # What is 20?
        category = 'medium'
    else:
        category = 'low'
    
    # What do these status codes mean?
    if data['status'] == 'PEND':
        process_pending()
    elif data['status'] == 'PROC':
        process_processing()
    elif data['status'] == 'COMP':
        process_completed()
```

**Better Approach:**
```python
# GOOD: Named constants with clear meaning
class SalesCategories:
    HIGH_VALUE_THRESHOLD = 50.00
    MEDIUM_VALUE_THRESHOLD = 20.00

class OrderStatus:
    PENDING = 'PEND'
    PROCESSING = 'PROC' 
    COMPLETED = 'COMP'
    FAILED = 'FAIL'

def process_sales_data(data):
    """Process sales data and categorize by value"""
    amount = data.get('amount', 0)
    
    if amount > SalesCategories.HIGH_VALUE_THRESHOLD:
        category = 'high'
    elif amount > SalesCategories.MEDIUM_VALUE_THRESHOLD:
        category = 'medium'
    else:
        category = 'low'
    
    status = data.get('status')
    
    if status == OrderStatus.PENDING:
        process_pending()
    elif status == OrderStatus.PROCESSING:
        process_processing()
    elif status == OrderStatus.COMPLETED:
        process_completed()
    else:
        handle_unknown_status(status)
```

## Error Handling Anti-Patterns

### 20. Swallowing Exceptions

**Anti-Pattern:**
Catching exceptions without proper handling or logging.

**Problem Example:**
```python
# BAD: Silent failure, no visibility into problems
def update_device_metrics(device_id):
    try:
        metrics = calculate_complex_metrics(device_id)
        save_metrics(device_id, metrics)
    except:
        pass  # Silent failure - problems hidden!

def process_payment(transaction_data):
    try:
        result = payment_processor.charge(transaction_data)
        return result
    except Exception as e:
        return None  # Lost information about why it failed
```

**Better Approach:**
```python
# GOOD: Proper error handling with logging and recovery
import logging

logger = logging.getLogger(__name__)

def update_device_metrics(device_id):
    """Update device metrics with proper error handling"""
    try:
        metrics = calculate_complex_metrics(device_id)
        save_metrics(device_id, metrics)
        logger.info(f"Updated metrics for device {device_id}")
        
    except DatabaseError as e:
        logger.error(f"Database error updating metrics for device {device_id}: {e}")
        # Could retry or queue for later
        raise
        
    except CalculationError as e:
        logger.warning(f"Metrics calculation failed for device {device_id}: {e}")
        # Use fallback metrics
        fallback_metrics = get_basic_metrics(device_id)
        save_metrics(device_id, fallback_metrics)
        
    except Exception as e:
        logger.error(f"Unexpected error updating metrics for device {device_id}: {e}")
        # Re-raise to handle at higher level
        raise

def process_payment(transaction_data):
    """Process payment with comprehensive error handling"""
    try:
        result = payment_processor.charge(transaction_data)
        
        logger.info(f"Payment processed successfully: {result['transaction_id']}")
        return {
            'success': True,
            'transaction_id': result['transaction_id'],
            'amount': result['amount']
        }
        
    except PaymentDeclinedError as e:
        logger.warning(f"Payment declined: {e}")
        return {
            'success': False,
            'error_type': 'declined',
            'message': 'Payment was declined',
            'decline_reason': str(e)
        }
        
    except NetworkError as e:
        logger.error(f"Network error during payment processing: {e}")
        return {
            'success': False,
            'error_type': 'network',
            'message': 'Payment service temporarily unavailable',
            'retry_after': 300
        }
        
    except Exception as e:
        logger.error(f"Unexpected payment processing error: {e}")
        return {
            'success': False,
            'error_type': 'system',
            'message': 'Payment processing failed'
        }
```

## Prevention Guidelines

### Code Review Checklist

Use this checklist during code reviews to catch anti-patterns:

**Database:**
- [ ] Are database queries parameterized to prevent SQL injection?
- [ ] Are appropriate indexes created for query performance?
- [ ] Is soft delete used for important business data?
- [ ] Are database constraints properly defined?

**API Design:**
- [ ] Are REST conventions followed consistently?
- [ ] Is input validation comprehensive?
- [ ] Are error responses standardized?
- [ ] Is authentication/authorization properly implemented?

**Frontend:**
- [ ] Is JavaScript code modular and organized?
- [ ] Are errors handled gracefully with user feedback?
- [ ] Are event handlers properly attached (not inline)?
- [ ] Is user input sanitized before display?

**Security:**
- [ ] Are secrets stored in environment variables?
- [ ] Is rate limiting implemented for sensitive endpoints?
- [ ] Are audit logs comprehensive?
- [ ] Is input validation done on both client and server?

**Performance:**
- [ ] Are N+1 query problems avoided?
- [ ] Are long-running operations handled asynchronously?
- [ ] Is appropriate caching implemented?
- [ ] Are database queries optimized?

**Integration:**
- [ ] Are external service failures handled gracefully?
- [ ] Is circuit breaker pattern used for unreliable services?
- [ ] Are timeouts configured appropriately?
- [ ] Are fallback strategies implemented?

### Tools and Techniques

1. **Static Analysis**: Use tools like pylint, ESLint to catch common issues
2. **Code Reviews**: Regular peer reviews to identify anti-patterns
3. **Monitoring**: Implement monitoring to detect performance issues
4. **Testing**: Comprehensive tests including failure scenarios
5. **Documentation**: Clear documentation helps prevent misunderstanding

## Related Documentation

- [Best Practices](./BEST_PRACTICES.md) - Positive patterns to follow
- [Security Patterns](./patterns/SECURITY_PATTERNS.md) - Security best practices
- [Performance Optimization](../PERFORMANCE.md) - Performance improvement strategies
- [Code Standards](../../05-development/CODING_STANDARDS.md) - Coding conventions

## References

- Clean Code by Robert Martin
- Refactoring: Improving the Design of Existing Code
- Enterprise Integration Patterns
- SQL Anti-patterns by Bill Karwin
- RESTful Web APIs Design Guidelines