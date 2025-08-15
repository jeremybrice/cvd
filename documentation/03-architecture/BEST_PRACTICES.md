# Best Practices Guide


## Metadata
- **ID**: 03_ARCHITECTURE_BEST_PRACTICES
- **Type**: Architecture
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #architecture #authentication #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #quality-assurance #reporting #route-management #security #service-orders #system-design #technical #testing #troubleshooting #vending-machine
- **Intent**: Architecture for Best Practices Guide
- **Audience**: system administrators, managers, end users, architects
- **Related**: ANTI_PATTERNS.md, SETUP_GUIDE.md, SECURITY.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/03-architecture/
- **Category**: 03 Architecture
- **Search Keywords**: 1.0, 2025-08-12, benefits:, best, cabinet, cvd, device, dex, document, documentation, driver, guide, implementation:, last, maintenance

**Document Version:** 1.0  
**Last Updated:** 2025-08-12  
**Status:** Complete

## Introduction

This document consolidates the proven best practices for developing, maintaining, and deploying the CVD (Vision Device Configuration) system. These practices are derived from the current implementation and represent battle-tested approaches for building robust, scalable enterprise applications.

## Table of Contents

1. [Code Organization and Architecture](#code-organization-and-architecture)
2. [Database Design and Management](#database-design-and-management)
3. [API Design and Implementation](#api-design-and-implementation)
4. [Frontend Development](#frontend-development)
5. [Security Implementation](#security-implementation)
6. [Performance Optimization](#performance-optimization)
7. [Error Handling and Logging](#error-handling-and-logging)
8. [Testing Strategies](#testing-strategies)
9. [Deployment and Operations](#deployment-and-operations)
10. [Documentation and Maintenance](#documentation-and-maintenance)

## Code Organization and Architecture

### Modular Architecture

**Best Practice:** Organize code into focused, single-responsibility modules.

**CVD Implementation:**
```
app.py                    # Main Flask application with core routes
auth.py                   # Authentication and session management
dex_parser.py            # DEX file processing logic
planogram_optimizer.py   # AI-powered optimization
service_order_service.py # Service order business logic
activity_tracker.py     # User activity monitoring
security_monitor.py      # Security threat detection
knowledge_base.py        # Help system and knowledge base

# Organized subdirectories
/ai_services/            # AI integration modules
/migrations/             # Database schema changes
/tests/                  # Comprehensive test suite
/tools/                  # Administrative utilities
/docs/                   # System documentation
```

**Benefits:**
- Easier to maintain and debug
- Better code reusability
- Simplified testing
- Clear separation of concerns

### Configuration Management

**Best Practice:** Use environment-based configuration with secure defaults.

**Implementation:**
```python
import os
import secrets
from datetime import timedelta

class Config:
    """Application configuration with secure defaults"""
    
    # Security
    SECRET_KEY = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Database
    DATABASE = os.environ.get('DATABASE_PATH', 'cvd.db')
    DATABASE_BACKUP_ENABLED = os.environ.get('DB_BACKUP_ENABLED', 'true').lower() == 'true'
    
    # External Services
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    ENABLE_GEOCODING = os.environ.get('ENABLE_GEOCODING', 'false').lower() == 'true'
    
    # Performance
    CACHE_TTL = int(os.environ.get('CACHE_TTL', '3600'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_SIZE', '16777216'))  # 16MB
    
    # Monitoring
    ENABLE_ACTIVITY_TRACKING = os.environ.get('ACTIVITY_TRACKING', 'true').lower() == 'true'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Usage
app.config.from_object(Config)
```

### Dependency Management

**Best Practice:** Use virtual environments and pin specific versions.

**CVD Implementation:**
```bash
# requirements.txt - Pinned versions for reproducibility
Flask==2.3.3
anthropic==0.57.1
requests==2.31.0
Werkzeug==2.3.7
python-dateutil==2.8.2

# requirements-dev.txt - Development dependencies
pytest==7.4.3
pytest-cov==4.1.0
black==23.9.1
pylint==2.17.7

# Setup script
#!/bin/bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Database Design and Management

### Schema Design Principles

**Best Practice:** Design normalized schemas with proper constraints and indexes.

**CVD Implementation:**
```sql
-- Proper table design with constraints
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL CHECK(length(username) >= 3),
    email TEXT UNIQUE NOT NULL CHECK(email LIKE '%@%.%'),
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Soft delete support
    is_deleted BOOLEAN DEFAULT 0,
    deleted_at TIMESTAMP NULL,
    deleted_by INTEGER NULL,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (deleted_by) REFERENCES users(id)
);

-- Performance indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active_deleted ON users(is_active, is_deleted);
```

### Migration Strategy

**Best Practice:** Use versioned migrations for schema changes.

**Implementation:**
```python
# migrations/001_add_activity_monitoring.sql
-- Add activity monitoring fields to sessions table
ALTER TABLE sessions ADD COLUMN device_type TEXT;
ALTER TABLE sessions ADD COLUMN activity_count INTEGER DEFAULT 0;
CREATE INDEX idx_sessions_activity ON sessions(last_activity);

-- Insert migration record
INSERT INTO schema_migrations (version, applied_at) 
VALUES ('001_add_activity_monitoring.sql', CURRENT_TIMESTAMP);
```

```python
# Migration runner
class DatabaseMigrator:
    def apply_pending_migrations(self):
        """Apply all pending database migrations"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations(applied)
        
        for migration in sorted(pending):
            self.apply_migration(migration)
            print(f"Applied migration: {migration}")
```

### Data Integrity Practices

**Best Practice:** Use transactions for multi-table operations and implement comprehensive audit trails.

**CVD Implementation:**
```python
@atomic_operation
def create_service_order(route_id, cabinet_selections, created_by):
    """Create service order with full transactional integrity"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Start transaction (implicit with decorator)
        pick_list = ServiceOrderService.calculate_pick_list(cabinet_selections)
        
        # Create main order
        cursor.execute('''
            INSERT INTO service_orders 
            (route_id, created_by, status, total_units, estimated_duration_minutes)
            VALUES (?, ?, 'pending', ?, ?)
        ''', (route_id, created_by, len(pick_list), len(cabinet_selections) * 10))
        
        order_id = cursor.lastrowid
        
        # Create related records
        for selection in cabinet_selections:
            create_order_cabinet_items(cursor, order_id, selection)
        
        # Log audit event
        log_audit_event(created_by, 'service_order_created', 'service_order', order_id)
        
        return {'orderId': order_id, 'pickList': pick_list}
        
    except Exception as e:
        # Transaction automatically rolled back by decorator
        log_audit_event(created_by, 'service_order_creation_failed', 
                       details={'error': str(e)})
        raise
```

## API Design and Implementation

### RESTful Design Patterns

**Best Practice:** Follow consistent RESTful conventions with proper HTTP methods and status codes.

**CVD Implementation:**
```python
# Consistent resource naming and HTTP methods
@app.route('/api/devices', methods=['GET'])
@require_auth
def get_devices():
    """List devices with filtering support"""
    filters = {
        'route_id': request.args.get('route_id'),
        'location_id': request.args.get('location_id'),
        'status': request.args.get('status')
    }
    
    devices = get_filtered_devices(filters)
    return jsonify(devices), 200

@app.route('/api/devices', methods=['POST'])
@require_role(['admin', 'manager'])
def create_device():
    """Create new device with validation"""
    data = request.json
    
    # Validate input
    validation_errors = validate_device_data(data)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    # Create device
    device_id = create_device_record(data)
    log_audit_event(g.current_user['user_id'], 'device_created', 'device', device_id)
    
    return jsonify({'id': device_id, 'message': 'Device created'}), 201

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
@require_role(['admin', 'manager'])
def update_device(device_id):
    """Update existing device"""
    if not device_exists(device_id):
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.json
    validation_errors = validate_device_data(data, is_update=True)
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    
    update_device_record(device_id, data)
    log_audit_event(g.current_user['user_id'], 'device_updated', 'device', device_id)
    
    return jsonify({'message': 'Device updated'}), 200
```

### Input Validation and Sanitization

**Best Practice:** Validate all inputs at multiple levels with clear error messages.

**Implementation:**
```python
def validate_device_data(data, is_update=False):
    """Comprehensive device data validation"""
    errors = []
    
    # Required field validation
    required_fields = ['name', 'device_type_id'] if not is_update else []
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field} is required')
    
    # Name validation
    if 'name' in data:
        name = data['name'].strip()
        if len(name) < 2:
            errors.append('Device name must be at least 2 characters')
        elif len(name) > 100:
            errors.append('Device name must not exceed 100 characters')
        elif not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            errors.append('Device name contains invalid characters')
    
    # Serial number validation
    if 'serial_number' in data and data['serial_number']:
        serial = data['serial_number'].strip().upper()
        if not re.match(r'^[A-Z0-9\-]{5,50}$', serial):
            errors.append('Serial number format is invalid')
        
        # Check for duplicates
        if serial_number_exists(serial, exclude_device_id=data.get('id')):
            errors.append('Serial number already exists')
    
    # Foreign key validation
    if 'device_type_id' in data:
        if not device_type_exists(data['device_type_id']):
            errors.append('Invalid device type')
    
    if 'location_id' in data and data['location_id']:
        if not location_exists(data['location_id']):
            errors.append('Invalid location')
    
    return errors
```

### Error Handling Standards

**Best Practice:** Provide consistent, informative error responses with appropriate HTTP status codes.

**CVD Implementation:**
```python
def create_error_response(message, status_code, error_code=None, details=None):
    """Create standardized error response"""
    return jsonify({
        'success': False,
        'error': {
            'message': message,
            'code': error_code or f'HTTP_{status_code}',
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
    }), status_code

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return create_error_response(
        'Validation failed',
        400,
        'VALIDATION_ERROR',
        {'fields': e.errors}
    )

@app.errorhandler(404)
def handle_not_found(e):
    return create_error_response(
        'Resource not found',
        404,
        'NOT_FOUND'
    )

@app.errorhandler(500)
def handle_server_error(e):
    # Log error details
    logger.error(f"Server error: {str(e)}")
    
    return create_error_response(
        'Internal server error',
        500,
        'INTERNAL_ERROR'
    )
```

## Frontend Development

### Component Architecture

**Best Practice:** Create reusable, focused components with clear responsibilities.

**CVD Implementation:**
```javascript
// Reusable Modal Component
class ModalComponent {
    constructor(options = {}) {
        this.options = {
            title: options.title || 'Modal',
            size: options.size || 'medium',
            closeOnOverlay: options.closeOnOverlay !== false,
            ...options
        };
        
        this.isOpen = false;
        this.createElement();
        this.bindEvents();
    }
    
    createElement() {
        this.modal = document.createElement('div');
        this.modal.className = `modal modal-${this.options.size}`;
        this.modal.innerHTML = this.getTemplate();
        document.body.appendChild(this.modal);
    }
    
    getTemplate() {
        return `
            <div class="modal-backdrop"></div>
            <div class="modal-container" role="dialog" aria-labelledby="modal-title">
                <div class="modal-header">
                    <h3 id="modal-title" class="modal-title">${this.options.title}</h3>
                    <button class="modal-close" type="button" aria-label="Close">&times;</button>
                </div>
                <div class="modal-body">
                    ${this.options.content || ''}
                </div>
                <div class="modal-footer">
                    ${this.options.footer || ''}
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // Close button
        this.modal.querySelector('.modal-close').addEventListener('click', () => this.close());
        
        // Overlay click
        if (this.options.closeOnOverlay) {
            this.modal.querySelector('.modal-backdrop').addEventListener('click', () => this.close());
        }
        
        // Escape key
        this.escapeHandler = (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        };
    }
    
    open() {
        this.modal.classList.add('active');
        this.isOpen = true;
        
        // Focus management
        const firstFocusable = this.modal.querySelector('button, input, select, textarea');
        if (firstFocusable) {
            firstFocusable.focus();
        }
        
        document.addEventListener('keydown', this.escapeHandler);
        this.emit('open');
    }
    
    close() {
        this.modal.classList.remove('active');
        this.isOpen = false;
        
        document.removeEventListener('keydown', this.escapeHandler);
        this.emit('close');
    }
    
    emit(eventName) {
        const event = new CustomEvent(`modal:${eventName}`);
        this.modal.dispatchEvent(event);
    }
}
```

### Error Handling and User Feedback

**Best Practice:** Provide comprehensive error handling with user-friendly feedback.

**CVD Implementation:**
```javascript
// Global error handler
class ErrorHandler {
    constructor() {
        this.setupGlobalHandlers();
    }
    
    setupGlobalHandlers() {
        // JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError({
                type: 'javascript',
                message: event.message,
                filename: event.filename,
                error: event.error
            });
        });
        
        // Promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError({
                type: 'promise',
                message: 'Unhandled promise rejection',
                error: event.reason
            });
        });
        
        // Network errors
        this.interceptFetch();
    }
    
    interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                
                if (!response.ok) {
                    this.handleHttpError(response, args[0]);
                }
                
                return response;
            } catch (error) {
                this.handleNetworkError(error, args[0]);
                throw error;
            }
        };
    }
    
    handleError(errorInfo) {
        console.error('Application error:', errorInfo);
        
        // Show user-friendly message
        if (window.Toast) {
            Toast.error('An unexpected error occurred. Please try again.');
        }
        
        // Log to monitoring service
        this.logError(errorInfo);
    }
    
    handleHttpError(response, url) {
        if (response.status === 401) {
            // Redirect to login
            window.location.href = '/pages/login.html';
        } else if (response.status === 403) {
            Toast.error('You do not have permission to perform this action.');
        } else if (response.status >= 500) {
            Toast.error('Server error. Please try again later.');
        }
    }
}

// Initialize
new ErrorHandler();
```

### State Management

**Best Practice:** Use appropriate state management patterns for different scopes.

**Implementation:**
```javascript
// Local component state
class DeviceManager {
    constructor() {
        this.state = {
            devices: [],
            loading: false,
            error: null,
            filters: {}
        };
        
        this.init();
    }
    
    setState(updates) {
        this.state = { ...this.state, ...updates };
        this.render();
    }
    
    async loadDevices() {
        this.setState({ loading: true, error: null });
        
        try {
            const devices = await api.getDevices(this.state.filters);
            this.setState({ devices, loading: false });
        } catch (error) {
            this.setState({ 
                loading: false, 
                error: 'Failed to load devices' 
            });
        }
    }
}

// Application-level state (LocalStorage)
class AppState {
    constructor() {
        this.storage = new LocalStateManager('cvd-app');
    }
    
    getUserPreferences() {
        return {
            theme: this.storage.get('theme', 'light'),
            pageSize: this.storage.get('pageSize', 50),
            language: this.storage.get('language', 'en')
        };
    }
    
    setUserPreference(key, value) {
        this.storage.set(key, value);
        this.applyPreference(key, value);
    }
    
    applyPreference(key, value) {
        switch (key) {
            case 'theme':
                document.body.className = `theme-${value}`;
                break;
            case 'language':
                this.updateLanguage(value);
                break;
        }
    }
}
```

## Security Implementation

### Authentication and Authorization

**Best Practice:** Implement layered security with proper session management and role-based access control.

**CVD Implementation:**
```python
# Multi-layered security decorators
def require_auth(func):
    """Require valid authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        # Validate session
        if not validate_current_session():
            session.clear()
            return jsonify({'error': 'Session expired'}), 401
        
        return func(*args, **kwargs)
    return wrapper

def require_role(allowed_roles):
    """Require specific user roles"""
    def decorator(func):
        @wraps(func)
        @require_auth
        def wrapper(*args, **kwargs):
            if g.current_user['role'] not in allowed_roles:
                log_audit_event(g.current_user['user_id'], 'access_denied')
                return jsonify({'error': 'Insufficient permissions'}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_resource_access(resource_type):
    """Require access to specific resources"""
    def decorator(func):
        @wraps(func)
        @require_auth
        def wrapper(*args, **kwargs):
            resource_id = kwargs.get('device_id') or kwargs.get('order_id')
            
            if not has_resource_access(g.current_user, resource_type, resource_id):
                return jsonify({'error': 'Resource access denied'}), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Input Security

**Best Practice:** Validate and sanitize all inputs to prevent injection attacks.

**Implementation:**
```python
class SecurityValidator:
    @staticmethod
    def validate_sql_injection(value):
        """Check for SQL injection patterns"""
        dangerous_patterns = [
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b',
            r'\b(OR|AND)\s+\d+\s*=\s*\d+',
            r'[\'";]',
            r'(\-\-|\#|\/\*|\*\/)'
        ]
        
        return not any(re.search(pattern, value, re.IGNORECASE) for pattern in dangerous_patterns)
    
    @staticmethod
    def validate_xss(value):
        """Check for XSS patterns"""
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>'
        ]
        
        return not any(re.search(pattern, value, re.IGNORECASE | re.DOTALL) for pattern in xss_patterns)
    
    @staticmethod
    def sanitize_html(value):
        """Sanitize HTML content"""
        import html
        return html.escape(value)
```

## Performance Optimization

### Database Performance

**Best Practice:** Optimize queries with proper indexing and avoid N+1 problems.

**CVD Implementation:**
```python
# Optimized query with JOIN instead of N+1
def get_devices_with_metrics():
    """Get devices with performance metrics efficiently"""
    query = '''
        SELECT 
            d.id, d.name, d.serial_number,
            l.name as location_name,
            r.name as route_name,
            dm.last_sale_date,
            dm.total_sales,
            dm.units_sold,
            dm.sold_out_count
        FROM devices d
        LEFT JOIN locations l ON d.location_id = l.id
        LEFT JOIN routes r ON d.route_id = r.id
        LEFT JOIN device_metrics dm ON d.id = dm.device_id
        WHERE d.deleted = 0
        ORDER BY d.name
    '''
    
    return db.execute(query).fetchall()

# Proper indexing strategy
INDEX_DEFINITIONS = [
    'CREATE INDEX idx_devices_location ON devices(location_id)',
    'CREATE INDEX idx_devices_route ON devices(route_id)', 
    'CREATE INDEX idx_devices_deleted ON devices(deleted)',
    'CREATE INDEX idx_sales_device_date ON sales(device_id, created_at)',
    'CREATE INDEX idx_sessions_user_expires ON sessions(user_id, expires_at)'
]
```

### Caching Strategy

**Best Practice:** Implement multi-level caching with appropriate TTLs.

**Implementation:**
```python
# Multi-level caching
@cached(ttl=1800, key_prefix='device_metrics:')
def get_device_performance_metrics(device_id):
    """Get device metrics with caching"""
    return {
        'total_sales': calculate_total_sales(device_id),
        'units_sold': calculate_units_sold(device_id),
        'avg_daily_revenue': calculate_avg_revenue(device_id),
        'sold_out_slots': calculate_sold_out_count(device_id),
        'last_service_date': get_last_service_date(device_id)
    }

# Browser-side caching
class ApiCache {
    constructor() {
        this.cache = new Map();
        this.ttl = new Map();
    }
    
    set(key, value, ttlMs = 300000) { // 5 minutes default
        this.cache.set(key, value);
        this.ttl.set(key, Date.now() + ttlMs);
    }
    
    get(key) {
        if (!this.cache.has(key)) return null;
        
        if (Date.now() > this.ttl.get(key)) {
            this.cache.delete(key);
            this.ttl.delete(key);
            return null;
        }
        
        return this.cache.get(key);
    }
}
```

### Resource Optimization

**Best Practice:** Optimize static resources and implement lazy loading.

**Implementation:**
```javascript
// Lazy loading for heavy components
class LazyLoader {
    static async loadComponent(componentName) {
        const loadingState = document.getElementById('loading-indicator');
        if (loadingState) loadingState.style.display = 'block';
        
        try {
            const module = await import(`/components/${componentName}.js`);
            return module.default;
        } catch (error) {
            console.error(`Failed to load component ${componentName}:`, error);
            throw error;
        } finally {
            if (loadingState) loadingState.style.display = 'none';
        }
    }
}

// Image optimization
function optimizeImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}
```

## Error Handling and Logging

### Comprehensive Logging Strategy

**Best Practice:** Implement structured logging with appropriate levels and context.

**CVD Implementation:**
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.setup_handler()
    
    def setup_handler(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_structured(self, level, message, **context):
        """Log with structured context"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'context': context
        }
        
        if hasattr(g, 'current_user'):
            log_data['user_id'] = g.current_user.get('user_id')
            log_data['user_role'] = g.current_user.get('role')
        
        if request:
            log_data['request'] = {
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr
            }
        
        getattr(self.logger, level)(json.dumps(log_data))
    
    def info(self, message, **context):
        self.log_structured('info', message, **context)
    
    def error(self, message, **context):
        self.log_structured('error', message, **context)
    
    def warning(self, message, **context):
        self.log_structured('warning', message, **context)

# Usage
logger = StructuredLogger(__name__)

@app.route('/api/devices', methods=['POST'])
def create_device():
    try:
        data = request.json
        device_id = create_device_record(data)
        
        logger.info("Device created successfully", 
                   device_id=device_id, 
                   device_name=data.get('name'))
        
        return jsonify({'id': device_id})
        
    except ValidationError as e:
        logger.warning("Device creation failed - validation error",
                      errors=e.errors)
        raise
        
    except Exception as e:
        logger.error("Device creation failed - unexpected error",
                    error=str(e),
                    error_type=type(e).__name__)
        raise
```

### Error Recovery Patterns

**Best Practice:** Implement graceful degradation and recovery mechanisms.

**Implementation:**
```python
class GracefulService:
    def __init__(self):
        self.circuit_breakers = {}
        
    def with_fallback(self, primary_func, fallback_func, service_name):
        """Execute function with fallback on failure"""
        breaker = self.circuit_breakers.get(service_name)
        
        try:
            if breaker and breaker.is_open():
                logger.info(f"Circuit breaker open for {service_name}, using fallback")
                return fallback_func()
            
            result = primary_func()
            
            if breaker:
                breaker.record_success()
                
            return result
            
        except Exception as e:
            logger.error(f"Primary service {service_name} failed", error=str(e))
            
            if breaker:
                breaker.record_failure()
            
            return fallback_func()
    
    def get_device_recommendations(self, device_id):
        """Get AI recommendations with fallback"""
        return self.with_fallback(
            primary_func=lambda: self.ai_service.get_recommendations(device_id),
            fallback_func=lambda: self.get_basic_recommendations(device_id),
            service_name='ai_recommendations'
        )
```

## Testing Strategies

### Comprehensive Test Coverage

**Best Practice:** Implement tests at multiple levels with good coverage.

**CVD Test Structure:**
```python
# Unit Tests
class TestDeviceService(unittest.TestCase):
    def setUp(self):
        self.db = create_test_database()
        self.service = DeviceService(self.db)
    
    def test_create_device_success(self):
        device_data = {
            'name': 'Test Device',
            'serial_number': 'TEST123',
            'device_type_id': 1
        }
        
        device_id = self.service.create_device(device_data)
        
        self.assertIsNotNone(device_id)
        
        # Verify device was created
        device = self.service.get_device(device_id)
        self.assertEqual(device['name'], 'Test Device')
    
    def test_create_device_duplicate_serial(self):
        device_data = {'serial_number': 'DUPLICATE123'}
        
        # First creation should succeed
        self.service.create_device(device_data)
        
        # Second creation should fail
        with self.assertRaises(ValidationError):
            self.service.create_device(device_data)

# Integration Tests
class TestDeviceAPI(TestCase):
    def setUp(self):
        self.app = create_test_app()
        self.client = self.app.test_client()
        self.auth_headers = self.get_auth_headers()
    
    def test_create_device_endpoint(self):
        device_data = {
            'name': 'API Test Device',
            'serial_number': 'API123'
        }
        
        response = self.client.post(
            '/api/devices',
            json=device_data,
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)

# End-to-End Tests
class TestDeviceWorkflow(TestCase):
    def test_complete_device_lifecycle(self):
        # Create device
        device_id = self.create_test_device()
        
        # Add cabinets
        self.add_device_cabinets(device_id)
        
        # Create planogram
        planogram_id = self.create_device_planogram(device_id)
        
        # Create service order
        order_id = self.create_service_order(device_id)
        
        # Verify complete workflow
        self.verify_device_state(device_id, 'operational')
```

### Mock External Services

**Best Practice:** Use mocks and stubs for external service testing.

**Implementation:**
```python
# Mock external services
class MockGeocodingService:
    def geocode_address(self, address):
        # Return predictable test data
        test_coordinates = {
            '123 Main St': (40.7128, -74.0060),
            'Invalid Address': (None, None)
        }
        
        return test_coordinates.get(address, (None, None))

class MockAIService:
    def optimize_planogram(self, device_id, cabinet_index):
        return {
            'recommendations': [
                {
                    'slot': 'A1',
                    'product_id': 1,
                    'reason': 'High sales performance'
                }
            ],
            'expected_improvement': 15.5
        }

# Test with mocks
@patch('app.geocode_address', MockGeocodingService().geocode_address)
@patch('planogram_optimizer.PlanogramOptimizer')
def test_device_creation_with_external_services(self, mock_optimizer):
    mock_optimizer.return_value = MockAIService()
    
    # Test device creation with mocked services
    response = self.client.post('/api/devices', json=test_device_data)
    
    self.assertEqual(response.status_code, 201)
```

## Deployment and Operations

### Environment Management

**Best Practice:** Use infrastructure as code and environment-specific configurations.

**CVD Implementation:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  cvd-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=${FLASK_ENV:-production}
      - DATABASE_PATH=/app/data/cvd.db
      - SESSION_SECRET=${SESSION_SECRET}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - cvd-app
    restart: unless-stopped
```

```bash
#!/bin/bash
# deployment/deploy.sh
set -e

echo "Starting CVD deployment..."

# Pull latest code
git pull origin main

# Build and deploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run database migrations
docker-compose exec cvd-app python migrate_database.py

# Health check
sleep 10
curl -f http://localhost:5000/health || exit 1

echo "Deployment completed successfully"
```

### Monitoring and Alerting

**Best Practice:** Implement comprehensive monitoring with proactive alerting.

**Implementation:**
```python
# Health check endpoint
@app.route('/health')
def health_check():
    """Comprehensive health check"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'checks': {}
    }
    
    # Database connectivity
    try:
        db = get_db()
        db.execute('SELECT 1').fetchone()
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = f'error: {str(e)}'
    
    # External service availability
    if os.environ.get('ANTHROPIC_API_KEY'):
        try:
            # Test AI service
            client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
            # Lightweight test call
            health_status['checks']['ai_service'] = 'healthy'
        except Exception as e:
            health_status['checks']['ai_service'] = f'warning: {str(e)}'
    
    # Disk space check
    import shutil
    total, used, free = shutil.disk_usage('/')
    free_percent = (free / total) * 100
    
    if free_percent < 10:
        health_status['status'] = 'warning'
        health_status['checks']['disk_space'] = f'low: {free_percent:.1f}% free'
    else:
        health_status['checks']['disk_space'] = f'healthy: {free_percent:.1f}% free'
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

# Performance metrics endpoint
@app.route('/metrics')
@require_role(['admin'])
def get_metrics():
    """System performance metrics"""
    return jsonify({
        'active_sessions': get_active_session_count(),
        'requests_per_minute': get_request_rate(),
        'average_response_time': get_average_response_time(),
        'error_rate': get_error_rate(),
        'database_query_count': get_db_query_count()
    })
```

## Documentation and Maintenance

### Documentation Standards

**Best Practice:** Maintain comprehensive, up-to-date documentation.

**CVD Documentation Structure:**
```
/documentation/
├── 00-index/                    # Navigation and cross-references
├── 01-project-core/            # Project overview and quick start
├── 02-requirements/            # Business requirements and user guides
├── 03-architecture/            # Technical architecture and patterns
├── 04-implementation/          # Implementation details
├── 05-development/             # Development guides and standards
├── 06-design/                  # UI/UX design guidelines
├── 07-cvd-framework/           # Domain-specific documentation
├── 08-project-management/      # Process and workflow documentation
└── 09-reference/               # Reference materials and examples
```

### Code Documentation

**Best Practice:** Use clear, comprehensive docstrings and comments.

**Implementation:**
```python
def create_service_order(route_id: int, cabinet_selections: List[Dict], 
                        created_by: int) -> Dict:
    """
    Create a new service order for selected cabinets.
    
    This function creates a comprehensive service order with cabinet-level
    task breakdown and pick list generation. It ensures transactional
    integrity and proper audit logging.
    
    Args:
        route_id (int): ID of the route for this service order
        cabinet_selections (List[Dict]): List of cabinet selections, each containing:
            - deviceId (int): Device ID
            - cabinetIndex (int): Cabinet index (0-based)
        created_by (int): User ID of the order creator
    
    Returns:
        Dict: Service order details containing:
            - orderId (int): Created order ID
            - totalUnits (int): Total units across all products
            - estimatedMinutes (int): Estimated completion time
            - pickList (List[Dict]): Aggregated pick list for driver
    
    Raises:
        ValidationError: If cabinet selections are invalid
        DatabaseError: If database operation fails
    
    Example:
        >>> cabinet_selections = [
        ...     {'deviceId': 1, 'cabinetIndex': 0},
        ...     {'deviceId': 2, 'cabinetIndex': 1}
        ... ]
        >>> order = create_service_order(5, cabinet_selections, 123)
        >>> print(order['orderId'])
        456
    """
    # Implementation details...
```

### Maintenance Procedures

**Best Practice:** Establish regular maintenance routines and procedures.

**CVD Maintenance Tasks:**
```python
# Database maintenance
def perform_database_maintenance():
    """Regular database maintenance tasks"""
    db = get_db()
    
    # Clean up old sessions
    db.execute('''
        DELETE FROM sessions 
        WHERE expires_at < datetime('now', '-7 days')
    ''')
    
    # Clean up old audit logs (keep 1 year)
    db.execute('''
        DELETE FROM audit_log 
        WHERE created_at < datetime('now', '-365 days')
    ''')
    
    # Vacuum database to reclaim space
    db.execute('VACUUM')
    
    # Update statistics
    db.execute('ANALYZE')
    
    db.commit()
    logger.info("Database maintenance completed")

# Log rotation
def rotate_logs():
    """Rotate application logs"""
    import glob
    import gzip
    
    log_files = glob.glob('logs/*.log')
    
    for log_file in log_files:
        # Compress old logs
        with open(log_file, 'rb') as f_in:
            with gzip.open(f'{log_file}.gz', 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Clear current log
        with open(log_file, 'w') as f:
            f.write('')
    
    logger.info("Log rotation completed")

# Scheduled maintenance
if __name__ == '__main__':
    import schedule
    
    # Schedule daily maintenance at 2 AM
    schedule.every().day.at("02:00").do(perform_database_maintenance)
    schedule.every().week.do(rotate_logs)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
```

## Implementation Checklist

### Development Checklist
- [ ] Code follows established patterns and conventions
- [ ] Comprehensive input validation implemented
- [ ] Error handling covers all scenarios
- [ ] Logging provides adequate troubleshooting information
- [ ] Tests cover critical functionality
- [ ] Documentation is complete and accurate

### Security Checklist
- [ ] Authentication and authorization properly implemented
- [ ] Input sanitization prevents injection attacks
- [ ] Secrets managed securely
- [ ] Audit logging captures security events
- [ ] Rate limiting protects against abuse

### Performance Checklist
- [ ] Database queries optimized with proper indexes
- [ ] Caching implemented where appropriate
- [ ] N+1 query problems avoided
- [ ] Long-running operations handled asynchronously
- [ ] Resource usage monitored and optimized

### Deployment Checklist
- [ ] Environment configuration properly managed
- [ ] Health checks implemented
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery procedures tested
- [ ] Deployment process documented and automated

## Related Documentation

- [Anti-Patterns](./ANTI_PATTERNS.md) - Patterns to avoid
- [Architecture Patterns](./patterns/) - Specific implementation patterns
- [Security Guidelines](./SECURITY.md) - Detailed security practices
- [Development Setup](../05-development/SETUP_GUIDE.md) - Development environment setup

## References

- Clean Code: A Handbook of Agile Software Craftsmanship
- The Pragmatic Programmer
- Building Secure and Reliable Systems
- Site Reliability Engineering
- Flask Web Development Best Practices