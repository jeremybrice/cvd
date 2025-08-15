"""
Authentication module for CVD application
Provides authentication and authorization functionality
"""

from functools import wraps
from flask import session, jsonify, request, g
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import sqlite3
from datetime import datetime, timedelta
import os

class AuthManager:
    def __init__(self, app, db_path):
        self.app = app
        self.db_path = db_path
        self.setup_session_config()
    
    def setup_session_config(self):
        """Configure session settings"""
        # Already configured in app.py, but can be overridden here if needed
        pass
    
    def create_session(self, user_id, db=None):
        """Create a new session for user"""
        from flask import current_app
        
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=8)
        
        # Use provided db connection or get from Flask context
        if db is None:
            db = current_app.config.get('get_db')()
        
        cursor = db.cursor()
        
        # Determine device type from user agent
        user_agent = request.headers.get('User-Agent', '')
        device_type = self.get_device_type(user_agent)
        
        # Create session with activity tracking fields
        cursor.execute('''
            INSERT INTO sessions (id, user_id, expires_at, ip_address, user_agent,
                                last_activity, activity_count, device_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, user_id, expires_at, 
              request.remote_addr, user_agent,
              datetime.now(), 0, device_type))
        
        # Don't commit here, let the caller handle it
        
        return session_id
    
    def get_device_type(self, user_agent):
        """Determine device type from user agent string"""
        if not user_agent:
            return 'unknown'
        
        user_agent = user_agent.lower()
        
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            return 'mobile'
        elif 'ipad' in user_agent or 'tablet' in user_agent:
            return 'tablet'
        elif 'bot' in user_agent or 'crawler' in user_agent:
            return 'bot'
        else:
            return 'desktop'
    
    def validate_session(self, session_id):
        """Validate and return user info for session"""
        from flask import current_app
        
        # Get db from Flask context
        get_db = current_app.config.get('get_db')
        if get_db:
            db = get_db()
        else:
            db = sqlite3.connect(self.db_path)
            db.row_factory = sqlite3.Row
        
        cursor = db.cursor()
        
        user = cursor.execute('''
            SELECT u.id, u.username, u.email, u.role, u.is_active, u.is_deleted
            FROM users u
            JOIN sessions s ON s.user_id = u.id
            WHERE s.id = ? AND s.expires_at > ? AND u.is_active = 1 AND u.is_deleted = 0
        ''', (session_id, datetime.now())).fetchone()
        
        # Don't close if using Flask's db
        if not get_db:
            db.close()
        
        return user
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        deleted = cursor.execute('''
            DELETE FROM sessions WHERE expires_at < ?
        ''', (datetime.now(),)).rowcount
        
        db.commit()
        db.close()
        
        if deleted > 0:
            print(f'Cleaned up {deleted} expired sessions')
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'session_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = self.validate_session(session['session_id'])
            if not user:
                return jsonify({'error': 'Invalid or expired session'}), 401
            
            g.user = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
            
            return f(*args, **kwargs)
        return decorated_function
    
    def require_role(self, allowed_roles):
        """Decorator to require specific roles (updated for soft delete)"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'session_id' not in session:
                    return jsonify({'error': 'Authentication required'}), 401
                
                user = self.validate_session(session['session_id'])
                if not user:
                    return jsonify({'error': 'Invalid or expired session'}), 401
                
                # Additional check for soft deleted users
                if user['is_deleted'] == 1:
                    return jsonify({'error': 'Account has been deactivated'}), 401
                
                if user['role'] not in allowed_roles:
                    import json
                    log_audit_event(
                        user_id=user['id'],
                        action='UNAUTHORIZED_ACCESS',
                        resource_type='endpoint',
                        details=json.dumps({
                            'endpoint': request.path,
                            'method': request.method,
                            'required_roles': allowed_roles,
                            'user_role': user['role']
                        })
                    )
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                g.user = {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def get_user_permissions(self, role):
        """Get permissions for a specific role"""
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
            'manager': {
                'devices': ['view', 'create', 'edit'],
                'planograms': ['view', 'create', 'edit'],
                'routes': ['view', 'create', 'edit'],
                'service_orders': ['view', 'create', 'edit'],
                'reports': ['view', 'create'],
                'users': [],
                'database': [],
                'settings': ['view', 'edit']
            },
            'driver': {
                'devices': ['view'],
                'planograms': ['view'],
                'routes': ['view'],
                'service_orders': ['view', 'edit'],
                'reports': [],
                'users': [],
                'database': [],
                'settings': []
            },
            'viewer': {
                'devices': ['view'],
                'planograms': ['view'],
                'routes': ['view'],
                'service_orders': ['view'],
                'reports': ['view'],
                'users': [],
                'database': [],
                'settings': []
            }
        }
        
        return permissions.get(role, {})


def check_user_service_orders(user_id, db=None):
    """Check if user has pending or in-progress service orders"""
    from flask import current_app
    
    if db is None:
        db_path = current_app.config.get('DATABASE', 'cvd.db')
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        should_close = True
    else:
        should_close = False
    
    cursor = db.cursor()
    
    try:
        # Check for pending or in-progress service orders
        pending_orders = cursor.execute('''
            SELECT COUNT(*) as count
            FROM service_orders 
            WHERE (created_by = ? OR driver_id = ?) 
            AND status IN ('pending', 'in_progress')
        ''', (user_id, user_id)).fetchone()
        
        return pending_orders['count'] > 0
        
    finally:
        if should_close:
            db.close()

def get_user_service_order_details(user_id, db=None):
    """Get detailed information about user's service orders for constraint validation"""
    from flask import current_app
    
    if db is None:
        db_path = current_app.config.get('DATABASE', 'cvd.db')
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        should_close = True
    else:
        should_close = False
    
    cursor = db.cursor()
    
    try:
        # Get detailed service order information
        orders = cursor.execute('''
            SELECT so.id, so.status, so.created_at, so.driver_id, so.created_by,
                   r.name as route_name, r.route_number
            FROM service_orders so
            LEFT JOIN routes r ON so.route_id = r.id
            WHERE (so.created_by = ? OR so.driver_id = ?) 
            AND so.status IN ('pending', 'in_progress')
            ORDER BY so.created_at DESC
        ''', (user_id, user_id)).fetchall()
        
        return [dict(order) for order in orders]
        
    finally:
        if should_close:
            db.close()

def validate_user_constraints(user_id, action_type='deactivate'):
    """Validate user constraints before deactivation/deletion"""
    service_orders = get_user_service_order_details(user_id)
    
    if service_orders:
        return {
            'has_constraints': True,
            'constraint_type': 'service_orders',
            'message': f'Cannot {action_type} user with pending or in-progress service orders',
            'details': {
                'orders_count': len(service_orders),
                'orders': service_orders
            }
        }
    
    return {'has_constraints': False}

def log_user_lifecycle_event(actor_id, action, target_user_id, target_username, 
                           details=None, constraint_info=None):
    """Log user lifecycle events with enhanced detail"""
    import json
    
    audit_details = {
        'target_user_id': target_user_id,
        'target_username': target_username,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        audit_details.update(details)
    
    if constraint_info:
        audit_details['constraint_violation'] = constraint_info
    
    log_audit_event(
        user_id=actor_id,
        action=action,
        resource_type='user_lifecycle',
        resource_id=target_user_id,
        details=json.dumps(audit_details)
    )

def log_audit_event(user_id, action, resource_type=None, resource_id=None, details=None):
    """Log an audit event"""
    import json
    from flask import current_app
    
    db_path = current_app.config.get('DATABASE', 'cvd.db')
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    # Handle case where dictionary is passed as third parameter (details in resource_type position)
    if isinstance(resource_type, dict):
        details = json.dumps(resource_type)
        resource_type = None
    elif isinstance(details, dict):
        details = json.dumps(details)
    
    cursor.execute('''
        INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, action, resource_type, resource_id, details, request.remote_addr))
    
    db.commit()
    db.close()

def require_admin_for_monitoring(f):
    """Decorator to require admin role for monitoring endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app, g
        
        if 'session_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get auth manager from app context
        auth_manager = getattr(current_app, 'auth_manager', None)
        if not auth_manager:
            return jsonify({'error': 'Auth system not initialized'}), 500
        
        user = auth_manager.validate_session(session['session_id'])
        if not user:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        g.user = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
        
        if g.user['role'] != 'admin':
            # Log unauthorized access attempt
            log_audit_event(
                user_id=g.user['id'],
                action='UNAUTHORIZED_MONITORING_ACCESS',
                resource_type='activity_monitor',
                details={'attempted_endpoint': request.path}
            )
            return jsonify({'error': 'Admin access required for monitoring'}), 403
        
        # Log successful monitoring access
        log_audit_event(
            user_id=g.user['id'],
            action='ACCESS_MONITORING',
            resource_type='activity_monitor',
            details={'endpoint': request.path}
        )
        
        return f(*args, **kwargs)
    return decorated_function