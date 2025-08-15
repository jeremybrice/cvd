# Security Architecture Patterns


## Metadata
- **ID**: 03_ARCHITECTURE_PATTERNS_SECURITY_PATTERNS
- **Type**: Architecture
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #architecture #authentication #data-layer #database #debugging #deployment #device-management #devops #driver-app #integration #logistics #machine-learning #mobile #optimization #pwa #quality-assurance #route-management #security #system-design #technical #testing #troubleshooting #vending-machine
- **Intent**: Architecture for Security Architecture Patterns
- **Audience**: system administrators, managers, end users, architects
- **Related**: SECURITY.md, FRONTEND_PATTERNS.md, API_PATTERNS.md, DATABASE_PATTERNS.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/03-architecture/patterns/
- **Category**: Patterns
- **Search Keywords**: ###, 1.0, 2025-08-12, anomaly, architecture, audit, authentication, authorization, cvd:, data, defaults, defense, depth, detection, device

**Document Version:** 1.0  
**Last Updated:** 2025-08-12  
**Status:** Complete

## Introduction

This document outlines the security architecture patterns, authentication strategies, and protection mechanisms implemented in the CVD system. These patterns ensure comprehensive security coverage from authentication to data protection and threat detection.

## Table of Contents

1. [Authentication Patterns](#authentication-patterns)
2. [Authorization Patterns](#authorization-patterns)
3. [Session Management](#session-management)
4. [Input Validation and Sanitization](#input-validation-and-sanitization)
5. [Audit Trail and Monitoring](#audit-trail-and-monitoring)
6. [Threat Detection Patterns](#threat-detection-patterns)
7. [Data Protection Patterns](#data-protection-patterns)
8. [Security Middleware Patterns](#security-middleware-patterns)
9. [Frontend Security Patterns](#frontend-security-patterns)
10. [Compliance and Governance](#compliance-and-governance)

## Authentication Patterns

### Session-Based Authentication

**Implementation in CVD:**
```python
class AuthManager:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path
        self.setup_session_config()
    
    def setup_session_config(self):
        """Configure secure session settings"""
        self.app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
        self.app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    
    def create_session(self, user_id, db=None):
        """Create secure session with comprehensive tracking"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=8)
        
        if db is None:
            db = current_app.config.get('get_db')()
        
        cursor = db.cursor()
        
        # Determine device type from user agent
        user_agent = request.headers.get('User-Agent', '')
        device_type = self.get_device_type(user_agent)
        
        # Create session with security metadata
        cursor.execute('''
            INSERT INTO sessions (id, user_id, expires_at, ip_address, user_agent,
                                last_activity, activity_count, device_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, user_id, expires_at, 
              request.remote_addr, user_agent,
              datetime.now(), 0, device_type, datetime.now()))
        
        db.commit()
        
        # Set Flask session
        session['session_id'] = session_id
        session['user_id'] = user_id
        session.permanent = True
        
        return session_id
    
    def validate_session(self, session_id):
        """Validate session with security checks"""
        db = get_db()
        cursor = db.cursor()
        
        # Get session with user data
        session_data = cursor.execute('''
            SELECT s.*, u.role, u.deleted, u.locked_until
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.id = ? AND s.expires_at > ?
        ''', (session_id, datetime.now())).fetchone()
        
        if not session_data:
            return None
        
        # Check if user is locked
        if session_data['locked_until'] and datetime.fromisoformat(session_data['locked_until']) > datetime.now():
            return None
        
        # Check if user is deleted
        if session_data['deleted']:
            return None
        
        # Update session activity
        cursor.execute('''
            UPDATE sessions 
            SET last_activity = ?, activity_count = activity_count + 1
            WHERE id = ?
        ''', (datetime.now(), session_id))
        
        db.commit()
        
        return dict(session_data)
```

### Multi-Factor Authentication Pattern (Future)

```python
class MFAManager:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def generate_totp_secret(self, user_id):
        """Generate TOTP secret for user"""
        import pyotp
        
        secret = pyotp.random_base32()
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET mfa_secret = ?, mfa_enabled = 1, mfa_backup_codes = ?
            WHERE id = ?
        ''', (secret, self.generate_backup_codes(), user_id))
        
        db.commit()
        
        return secret
    
    def verify_totp(self, user_id, token):
        """Verify TOTP token"""
        import pyotp
        
        db = get_db()
        user = db.execute('SELECT mfa_secret FROM users WHERE id = ?', 
                         (user_id,)).fetchone()
        
        if not user or not user['mfa_secret']:
            return False
        
        totp = pyotp.TOTP(user['mfa_secret'])
        return totp.verify(token, valid_window=1)  # Allow 1 window tolerance
```

## Authorization Patterns

### Role-Based Access Control (RBAC)

**Implementation in CVD:**
```python
def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'session_id' not in session or 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Validate session
        session_data = auth_manager.validate_session(session['session_id'])
        
        if not session_data:
            session.clear()
            return jsonify({'error': 'Session expired'}), 401
        
        g.current_user = session_data
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

# Usage examples
@app.route('/api/users', methods=['GET'])
@require_role(['admin'])
def get_users():
    # Only admins can access user management
    pass

@app.route('/api/devices', methods=['POST'])
@require_role(['admin', 'manager'])
def create_device():
    # Admins and managers can create devices
    pass

@app.route('/api/service-orders', methods=['GET'])
@require_role(['admin', 'manager', 'driver'])
def get_service_orders():
    # Filter based on role
    if g.current_user['role'] == 'driver':
        # Drivers only see their own orders
        driver_id = g.current_user['user_id']
        orders = get_orders_for_driver(driver_id)
    else:
        # Admins and managers see all orders
        orders = get_all_orders()
    
    return jsonify(orders)
```

### Resource-Based Authorization

```python
def require_resource_access(resource_type, permission='read'):
    """Decorator for resource-based access control"""
    def decorator(func):
        @wraps(func)
        @require_auth
        def wrapper(*args, **kwargs):
            # Extract resource ID from route parameters
            resource_id = kwargs.get('device_id') or kwargs.get('order_id') or kwargs.get('user_id')
            
            if not has_resource_access(g.current_user, resource_type, resource_id, permission):
                log_audit_event(g.current_user['user_id'], 'resource_access_denied',
                               f'Resource: {resource_type}, ID: {resource_id}, Permission: {permission}')
                return jsonify({'error': 'Access denied to resource'}), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def has_resource_access(user, resource_type, resource_id, permission):
    """Check if user has access to specific resource"""
    # Admin has access to everything
    if user['role'] == 'admin':
        return True
    
    # Manager role checks
    if user['role'] == 'manager':
        if resource_type == 'device':
            # Managers can access devices in their assigned locations/routes
            return check_manager_device_access(user['user_id'], resource_id)
        elif resource_type == 'service_order':
            # Managers can access orders in their territory
            return check_manager_order_access(user['user_id'], resource_id)
    
    # Driver role checks
    if user['role'] == 'driver':
        if resource_type == 'service_order':
            # Drivers can only access their own orders
            return check_driver_order_access(user['user_id'], resource_id)
    
    return False
```

## Session Management

### Secure Session Pattern

**Implementation in CVD:**
```python
class SecureSessionManager:
    def __init__(self):
        self.session_timeout = timedelta(hours=8)
        self.max_concurrent_sessions = 3  # Per user
        self.session_rotation_interval = timedelta(hours=1)
    
    def create_session(self, user_id, request_info):
        """Create secure session with metadata tracking"""
        session_id = secrets.token_urlsafe(32)
        
        # Extract security metadata
        ip_address = request_info.get('remote_addr')
        user_agent = request_info.get('user_agent')
        
        # Detect potential risks
        risk_score = self.calculate_risk_score(user_id, ip_address, user_agent)
        
        session_data = {
            'id': session_id,
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'expires_at': datetime.now() + self.session_timeout,
            'risk_score': risk_score,
            'activity_count': 0
        }
        
        # Clean up old sessions for user
        self.cleanup_user_sessions(user_id)
        
        # Store session
        self.store_session(session_data)
        
        return session_id
    
    def calculate_risk_score(self, user_id, ip_address, user_agent):
        """Calculate risk score for session"""
        risk_score = 0
        
        # Check for unusual location
        if self.is_unusual_location(user_id, ip_address):
            risk_score += 30
        
        # Check for unusual user agent
        if self.is_unusual_user_agent(user_id, user_agent):
            risk_score += 20
        
        # Check for concurrent sessions
        active_sessions = self.get_active_sessions(user_id)
        if len(active_sessions) >= self.max_concurrent_sessions:
            risk_score += 25
        
        # Check for recent failed attempts
        if self.has_recent_failed_attempts(user_id):
            risk_score += 15
        
        return min(risk_score, 100)  # Cap at 100
    
    def validate_session(self, session_id, request_info):
        """Validate session with security checks"""
        session_data = self.get_session(session_id)
        
        if not session_data:
            return None
        
        # Check expiration
        if datetime.now() > session_data['expires_at']:
            self.invalidate_session(session_id)
            return None
        
        # Verify IP consistency (with some tolerance for mobile users)
        if not self.verify_ip_consistency(session_data, request_info.get('remote_addr')):
            log_security_event('session_ip_mismatch', {
                'session_id': session_id,
                'original_ip': session_data['ip_address'],
                'current_ip': request_info.get('remote_addr')
            })
            
            # Invalidate suspicious session
            self.invalidate_session(session_id)
            return None
        
        # Update activity
        self.update_session_activity(session_id)
        
        # Check if session needs rotation
        if self.needs_rotation(session_data):
            new_session_id = self.rotate_session(session_id)
            session_data['id'] = new_session_id
        
        return session_data
```

## Input Validation and Sanitization

### Validation Middleware Pattern

**Implementation in CVD:**
```python
import re
import html
from werkzeug.security import safe_str_cmp

class InputValidator:
    def __init__(self):
        # Define validation patterns
        self.patterns = {
            'username': re.compile(r'^[a-zA-Z0-9_]{3,30}$'),
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'device_name': re.compile(r'^[a-zA-Z0-9\s\-_]{1,100}$'),
            'phone': re.compile(r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$'),
            'serial_number': re.compile(r'^[A-Z0-9\-]{5,50}$')
        }
        
        # SQL injection patterns (basic detection)
        self.sql_injection_patterns = [
            re.compile(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)', re.IGNORECASE),
            re.compile(r'(\b(OR|AND)\s+\d+\s*=\s*\d+)', re.IGNORECASE),
            re.compile(r'[\'";]'),
            re.compile(r'(\-\-|\#|\/\*|\*\/)')
        ]
        
        # XSS patterns
        self.xss_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'<iframe[^>]*>', re.IGNORECASE)
        ]
    
    def validate_and_sanitize(self, data, schema):
        """Validate and sanitize data according to schema"""
        errors = []
        sanitized_data = {}
        
        for field, rules in schema.items():
            value = data.get(field)
            
            # Check required fields
            if rules.get('required', False) and (value is None or value == ''):
                errors.append(f'{field} is required')
                continue
            
            # Skip validation for optional empty fields
            if value is None or value == '':
                sanitized_data[field] = value
                continue
            
            # Convert to string for validation
            str_value = str(value).strip()
            
            # Length validation
            if 'max_length' in rules and len(str_value) > rules['max_length']:
                errors.append(f'{field} must be no more than {rules["max_length"]} characters')
                continue
            
            if 'min_length' in rules and len(str_value) < rules['min_length']:
                errors.append(f'{field} must be at least {rules["min_length"]} characters')
                continue
            
            # Pattern validation
            if 'pattern' in rules:
                pattern_name = rules['pattern']
                if pattern_name in self.patterns:
                    if not self.patterns[pattern_name].match(str_value):
                        errors.append(f'{field} format is invalid')
                        continue
            
            # Security validation
            if self.contains_sql_injection(str_value):
                errors.append(f'{field} contains potentially dangerous characters')
                continue
            
            if rules.get('allow_html', False):
                # Sanitize HTML but allow safe tags
                sanitized_value = self.sanitize_html(str_value)
            else:
                # Check for XSS
                if self.contains_xss(str_value):
                    errors.append(f'{field} contains potentially dangerous content')
                    continue
                
                # HTML escape by default
                sanitized_value = html.escape(str_value)
            
            # Type conversion
            if 'type' in rules:
                try:
                    if rules['type'] == 'int':
                        sanitized_value = int(sanitized_value)
                    elif rules['type'] == 'float':
                        sanitized_value = float(sanitized_value)
                    elif rules['type'] == 'bool':
                        sanitized_value = str_value.lower() in ('true', '1', 'yes')
                except ValueError:
                    errors.append(f'{field} must be a valid {rules["type"]}')
                    continue
            
            sanitized_data[field] = sanitized_value
        
        return sanitized_data, errors
    
    def contains_sql_injection(self, value):
        """Check for SQL injection patterns"""
        return any(pattern.search(value) for pattern in self.sql_injection_patterns)
    
    def contains_xss(self, value):
        """Check for XSS patterns"""
        return any(pattern.search(value) for pattern in self.xss_patterns)
    
    def sanitize_html(self, value):
        """Sanitize HTML content - basic implementation"""
        # In production, use a library like bleach
        import html
        return html.escape(value)

# Validation schemas
USER_SCHEMA = {
    'username': {
        'required': True,
        'pattern': 'username',
        'max_length': 30,
        'min_length': 3
    },
    'email': {
        'required': True,
        'pattern': 'email',
        'max_length': 100
    },
    'password': {
        'required': True,
        'min_length': 8,
        'max_length': 128
    },
    'role': {
        'required': True,
        'type': 'str'
    }
}

DEVICE_SCHEMA = {
    'name': {
        'required': True,
        'pattern': 'device_name',
        'max_length': 100
    },
    'serial_number': {
        'required': True,
        'pattern': 'serial_number',
        'max_length': 50
    },
    'location_id': {
        'type': 'int'
    },
    'route_id': {
        'type': 'int'
    }
}

# Usage in API endpoints
validator = InputValidator()

@app.route('/api/users', methods=['POST'])
@require_role(['admin'])
def create_user():
    data = request.json
    
    # Validate and sanitize input
    sanitized_data, errors = validator.validate_and_sanitize(data, USER_SCHEMA)
    
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
    
    # Additional business logic validation
    if user_exists(sanitized_data['username']):
        return jsonify({'error': 'Username already exists'}), 409
    
    # Create user with sanitized data
    user_id = create_user_record(sanitized_data)
    
    return jsonify({'id': user_id, 'message': 'User created successfully'}), 201
```

## Audit Trail and Monitoring

### Comprehensive Audit Logging

**Implementation in CVD:**
```python
def log_audit_event(user_id, action, resource_type=None, resource_id=None, 
                   details=None, ip_address=None, risk_level='low'):
    """Log comprehensive audit events"""
    
    if ip_address is None:
        ip_address = request.remote_addr if request else 'system'
    
    user_agent = request.headers.get('User-Agent') if request else 'system'
    
    # Prepare details as JSON
    details_data = {
        'timestamp': datetime.now().isoformat(),
        'request_id': getattr(g, 'request_id', None),
        'session_id': session.get('session_id'),
        'endpoint': request.endpoint if request else None,
        'method': request.method if request else None,
        'risk_level': risk_level,
        'additional_details': details
    }
    
    details_json = json.dumps(details_data)
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO audit_log 
            (user_id, action, resource_type, resource_id, details, 
             ip_address, user_agent, risk_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, action, resource_type, resource_id, details_json, 
              ip_address, user_agent, risk_level, datetime.now()))
        
        db.commit()
        
        # Send high-risk events to monitoring system
        if risk_level in ['high', 'critical']:
            send_security_alert(user_id, action, details_data)
            
    except Exception as e:
        logger.error(f"Audit logging failed: {e}")
        # Don't let audit failure break the application
```

## Threat Detection Patterns

### Brute Force Detection

**Implementation in CVD (security_monitor.py):**
```python
class SecurityMonitor:
    def __init__(self, db_path, activity_tracker):
        self.db_path = db_path
        self.activity_tracker = activity_tracker
        
        self.brute_force_config = {
            'max_failed_attempts': 5,
            'time_window_minutes': 10,
            'lockout_duration_minutes': 30,
            'alert_threshold': 3,
            'distributed_threshold': 10
        }
        
        self.failed_login_cache = defaultdict(list)
    
    def check_brute_force(self, ip_address, user_id=None, success=False):
        """Monitor for brute force attacks"""
        now = datetime.now()
        window_start = now - timedelta(minutes=self.brute_force_config['time_window_minutes'])
        
        # Clean up old entries
        self._cleanup_cache()
        
        if success:
            # Clear cache on successful login
            if ip_address in self.failed_login_cache:
                del self.failed_login_cache[ip_address]
            return False, False, None
        
        # Add failed attempt
        self.failed_login_cache[ip_address].append((now, user_id))
        
        # Count recent failures
        recent_failures = [
            (timestamp, uid) for timestamp, uid in self.failed_login_cache[ip_address]
            if timestamp >= window_start
        ]
        
        failure_count = len(recent_failures)
        
        # Check if IP should be blocked
        should_block = failure_count >= self.brute_force_config['max_failed_attempts']
        
        # Check if alert should be sent
        should_alert = failure_count >= self.brute_force_config['alert_threshold']
        
        alert_details = None
        if should_alert:
            alert_details = {
                'ip_address': ip_address,
                'failure_count': failure_count,
                'time_window': self.brute_force_config['time_window_minutes'],
                'targeted_users': list(set([uid for _, uid in recent_failures if uid])),
                'should_block': should_block
            }
        
        # Check for distributed attacks
        total_failures = sum(len(attempts) for attempts in self.failed_login_cache.values())
        if total_failures >= self.brute_force_config['distributed_threshold']:
            alert_details = {
                **alert_details,
                'attack_type': 'distributed',
                'total_failures': total_failures,
                'source_ips': list(self.failed_login_cache.keys())
            }
        
        return should_block, should_alert, alert_details
```

### Anomaly Detection

```python
def detect_login_anomalies(user_id, ip_address, user_agent):
    """Detect unusual login patterns"""
    anomalies = []
    
    # Get user's login history
    db = get_db()
    recent_logins = db.execute('''
        SELECT ip_address, user_agent, created_at, device_type
        FROM sessions
        WHERE user_id = ? AND created_at > ?
        ORDER BY created_at DESC
        LIMIT 50
    ''', (user_id, datetime.now() - timedelta(days=30))).fetchall()
    
    if recent_logins:
        # Check for new IP address
        known_ips = {login['ip_address'] for login in recent_logins}
        if ip_address not in known_ips:
            anomalies.append({
                'type': 'new_ip_address',
                'severity': 'medium',
                'details': {'new_ip': ip_address, 'known_ips': list(known_ips)}
            })
        
        # Check for new user agent
        known_agents = {login['user_agent'] for login in recent_logins}
        if user_agent not in known_agents:
            anomalies.append({
                'type': 'new_user_agent',
                'severity': 'low',
                'details': {'new_agent': user_agent}
            })
        
        # Check for unusual timing
        last_login = recent_logins[0]
        time_since_last = datetime.now() - datetime.fromisoformat(last_login['created_at'])
        
        if time_since_last < timedelta(minutes=5):
            anomalies.append({
                'type': 'rapid_relogin',
                'severity': 'medium',
                'details': {'time_since_last': str(time_since_last)}
            })
    
    return anomalies
```

## Data Protection Patterns

### Encryption at Rest

```python
import os
from cryptography.fernet import Fernet

class DataProtection:
    def __init__(self):
        # Get encryption key from environment or generate
        key = os.environ.get('DATA_ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            # In production, store this securely
            os.environ['DATA_ENCRYPTION_KEY'] = key.decode()
        
        self.cipher = Fernet(key if isinstance(key, bytes) else key.encode())
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data before storage"""
        if not data:
            return None
        
        encrypted_data = self.cipher.encrypt(data.encode())
        return encrypted_data.decode()
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data after retrieval"""
        if not encrypted_data:
            return None
        
        decrypted_data = self.cipher.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    def hash_password(self, password):
        """Hash password with salt"""
        from werkzeug.security import generate_password_hash
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        from werkzeug.security import check_password_hash
        return check_password_hash(password_hash, password)

# Usage in user management
data_protection = DataProtection()

def create_user_with_encryption(user_data):
    """Create user with encrypted sensitive data"""
    # Hash password
    user_data['password_hash'] = data_protection.hash_password(user_data['password'])
    del user_data['password']  # Remove plaintext password
    
    # Encrypt sensitive fields if needed
    if 'phone' in user_data:
        user_data['phone_encrypted'] = data_protection.encrypt_sensitive_data(user_data['phone'])
        del user_data['phone']
    
    # Store user
    return create_user_record(user_data)
```

### Data Masking and Anonymization

```python
def mask_sensitive_data(data, field_mappings):
    """Mask sensitive data for logging/display"""
    masked_data = data.copy()
    
    for field, mask_type in field_mappings.items():
        if field in masked_data:
            value = masked_data[field]
            
            if mask_type == 'email':
                # Mask email: j***@example.com
                if '@' in value:
                    local, domain = value.split('@', 1)
                    masked_data[field] = f"{local[0]}***@{domain}"
            
            elif mask_type == 'phone':
                # Mask phone: ***-***-1234
                if len(value) >= 4:
                    masked_data[field] = f"***-***-{value[-4:]}"
            
            elif mask_type == 'partial':
                # Mask middle characters
                if len(value) > 6:
                    masked_data[field] = f"{value[:2]}***{value[-2:]}"
            
            elif mask_type == 'full':
                # Full masking
                masked_data[field] = '*' * len(value)
    
    return masked_data

# Usage in audit logging
sensitive_fields = {
    'email': 'email',
    'phone': 'phone',
    'social_security': 'full',
    'credit_card': 'partial'
}

audit_data = mask_sensitive_data(original_data, sensitive_fields)
log_audit_event(user_id, 'data_access', details=audit_data)
```

## Security Middleware Patterns

### Request Security Middleware

```python
from flask import request, abort
import ipaddress

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
        self.blocked_ips = set()
        self.rate_limits = defaultdict(list)
        
        # Security headers
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': self._get_csp_header(),
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        self.setup_middleware()
    
    def setup_middleware(self):
        """Setup security middleware"""
        @self.app.before_request
        def security_check():
            # Check if IP is blocked
            if self.is_ip_blocked(request.remote_addr):
                abort(403, 'IP address blocked')
            
            # Rate limiting
            if self.is_rate_limited(request.remote_addr):
                abort(429, 'Too many requests')
            
            # Validate content type for POST/PUT requests
            if request.method in ['POST', 'PUT', 'PATCH']:
                if not self.is_valid_content_type():
                    abort(400, 'Invalid content type')
        
        @self.app.after_request
        def add_security_headers(response):
            # Add security headers
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            return response
    
    def is_ip_blocked(self, ip_address):
        """Check if IP address is blocked"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check against blocked IPs
            if ip_address in self.blocked_ips:
                return True
            
            # Check against blocked ranges (if configured)
            # for blocked_range in self.blocked_ranges:
            #     if ip in blocked_range:
            #         return True
            
        except ValueError:
            # Invalid IP address
            return True
        
        return False
    
    def is_rate_limited(self, ip_address):
        """Simple rate limiting implementation"""
        now = time.time()
        window = 60  # 1 minute window
        max_requests = 100  # requests per window
        
        # Clean old entries
        self.rate_limits[ip_address] = [
            timestamp for timestamp in self.rate_limits[ip_address]
            if now - timestamp < window
        ]
        
        # Check if over limit
        if len(self.rate_limits[ip_address]) >= max_requests:
            return True
        
        # Add current request
        self.rate_limits[ip_address].append(now)
        return False
    
    def is_valid_content_type(self):
        """Validate content type for data requests"""
        content_type = request.content_type
        
        if request.endpoint and '/api/' in request.endpoint:
            # API endpoints should use JSON
            return content_type and 'application/json' in content_type
        
        return True
    
    def _get_csp_header(self):
        """Generate Content Security Policy header"""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-src 'none';"
        )
```

## Frontend Security Patterns

### Client-Side Security

**Implementation in CVD:**
```javascript
// CSRF Protection
class CSRFProtection {
    constructor() {
        this.token = null;
        this.tokenHeader = 'X-CSRF-Token';
        this.init();
    }
    
    init() {
        // Get CSRF token from meta tag or API
        this.token = document.querySelector('meta[name="csrf-token"]')?.content;
        
        if (!this.token) {
            this.fetchToken();
        }
        
        // Add to all fetch requests
        this.interceptFetch();
    }
    
    async fetchToken() {
        try {
            const response = await fetch('/api/csrf-token');
            const data = await response.json();
            this.token = data.token;
        } catch (error) {
            console.error('Failed to fetch CSRF token:', error);
        }
    }
    
    interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = (url, options = {}) => {
            // Add CSRF token to non-GET requests
            if (options.method && options.method.toUpperCase() !== 'GET') {
                options.headers = {
                    ...options.headers,
                    [this.tokenHeader]: this.token
                };
            }
            
            return originalFetch(url, options);
        };
    }
}

// Input Sanitization
class InputSanitizer {
    static sanitizeHTML(input) {
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }
    
    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    static sanitizeUserInput(input, type = 'text') {
        if (typeof input !== 'string') {
            return '';
        }
        
        // Remove potential XSS
        input = this.sanitizeHTML(input);
        
        switch (type) {
            case 'numeric':
                return input.replace(/[^0-9.-]/g, '');
            
            case 'alphanumeric':
                return input.replace(/[^a-zA-Z0-9\s]/g, '');
            
            case 'email':
                return input.toLowerCase().trim();
            
            default:
                return input.trim();
        }
    }
}

// Secure Storage
class SecureStorage {
    static setItem(key, value, encrypt = false) {
        try {
            const data = {
                value: value,
                timestamp: Date.now(),
                encrypted: encrypt
            };
            
            if (encrypt) {
                // Simple encryption for demo - use proper encryption in production
                data.value = btoa(JSON.stringify(value));
            }
            
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error('Failed to store item:', error);
        }
    }
    
    static getItem(key, decrypt = false) {
        try {
            const stored = localStorage.getItem(key);
            if (!stored) return null;
            
            const data = JSON.parse(stored);
            
            if (decrypt && data.encrypted) {
                return JSON.parse(atob(data.value));
            }
            
            return data.value;
        } catch (error) {
            console.error('Failed to retrieve item:', error);
            return null;
        }
    }
    
    static removeItem(key) {
        localStorage.removeItem(key);
    }
    
    static clear() {
        localStorage.clear();
    }
}

// Initialize security features
document.addEventListener('DOMContentLoaded', () => {
    new CSRFProtection();
    
    // Sanitize all form inputs
    document.addEventListener('input', (event) => {
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            const sanitized = InputSanitizer.sanitizeUserInput(
                event.target.value, 
                event.target.type
            );
            
            if (sanitized !== event.target.value) {
                event.target.value = sanitized;
            }
        }
    });
});
```

## Implementation Guidelines

### Security Implementation Checklist

- [ ] **Authentication**: Multi-layered authentication with session management
- [ ] **Authorization**: Role-based access control with resource permissions
- [ ] **Input Validation**: Comprehensive validation and sanitization
- [ ] **Audit Logging**: Complete audit trail for sensitive operations
- [ ] **Threat Detection**: Automated detection of suspicious activities
- [ ] **Data Protection**: Encryption of sensitive data at rest and in transit
- [ ] **Security Headers**: Proper HTTP security headers configuration
- [ ] **Rate Limiting**: Protection against abuse and DoS attacks
- [ ] **Monitoring**: Real-time security monitoring and alerting

### Security Best Practices

1. **Defense in Depth**: Implement multiple layers of security controls
2. **Least Privilege**: Grant minimum necessary permissions
3. **Input Validation**: Validate all inputs at multiple levels
4. **Secure Defaults**: Use secure configurations by default
5. **Regular Updates**: Keep all dependencies and frameworks updated
6. **Monitoring**: Implement comprehensive logging and monitoring
7. **Incident Response**: Have procedures for security incident handling

## Related Documentation

- [API Patterns](./API_PATTERNS.md) - API security integration
- [Database Patterns](./DATABASE_PATTERNS.md) - Data protection patterns
- [Frontend Patterns](./FRONTEND_PATTERNS.md) - Client-side security
- [Compliance Documentation](../../SECURITY.md) - Security compliance requirements

## References

- OWASP Security Guidelines
- NIST Cybersecurity Framework
- Flask Security Best Practices
- Session Management Security
- Input Validation Techniques