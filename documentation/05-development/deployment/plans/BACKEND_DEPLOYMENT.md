# User Soft Delete Backend Deployment Plan

## Executive Summary

This document provides a comprehensive implementation plan for deploying user soft delete functionality in the CVD application. The implementation follows a three-state user lifecycle model: Active, Deactivated, and Soft Deleted, with proper constraint validation, audit logging, and rollback procedures.

## 1. Database Schema Changes and Migration

### 1.1 Schema Modifications

The following schema changes are required for the `users` table:

```sql
-- Add soft delete columns to users table
ALTER TABLE users ADD COLUMN is_deleted BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN deleted_by INTEGER NULL;

-- Add foreign key constraint for deleted_by
-- Note: SQLite doesn't support adding FK constraints after table creation
-- This will be handled in the migration validation

-- Create performance index for active/deleted queries
CREATE INDEX idx_users_active_deleted ON users(is_active, is_deleted);
```

### 1.2 Migration Script

Create migration file: `/home/jbrice/Projects/365/migrations/001_user_soft_delete.py`

```python
"""
User Soft Delete Migration
Adds soft delete functionality to users table
"""

import sqlite3
from datetime import datetime

def migrate_up(db_path):
    """Apply the migration"""
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    try:
        # Add new columns
        cursor.execute('ALTER TABLE users ADD COLUMN is_deleted BOOLEAN DEFAULT 0')
        cursor.execute('ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL')
        cursor.execute('ALTER TABLE users ADD COLUMN deleted_by INTEGER NULL')
        
        # Set is_deleted = 0 for all existing users
        cursor.execute('UPDATE users SET is_deleted = 0 WHERE is_deleted IS NULL')
        
        # Create performance index
        cursor.execute('CREATE INDEX idx_users_active_deleted ON users(is_active, is_deleted)')
        
        # Record migration
        cursor.execute('''
            INSERT INTO migrations (name, applied_at) 
            VALUES (?, ?)
        ''', ('001_user_soft_delete', datetime.now()))
        
        db.commit()
        print("✓ User soft delete migration applied successfully")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        db.close()

def migrate_down(db_path):
    """Rollback the migration"""
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    try:
        # SQLite doesn't support DROP COLUMN, so we recreate the table
        cursor.execute('''
            CREATE TABLE users_backup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        # Copy data without soft delete columns
        cursor.execute('''
            INSERT INTO users_backup 
            SELECT id, username, email, password_hash, role, is_active, 
                   created_at, updated_at, last_login, failed_login_attempts, locked_until
            FROM users WHERE is_deleted = 0
        ''')
        
        # Drop original table and rename backup
        cursor.execute('DROP TABLE users')
        cursor.execute('ALTER TABLE users_backup RENAME TO users')
        
        # Remove migration record
        cursor.execute('DELETE FROM migrations WHERE name = ?', ('001_user_soft_delete',))
        
        db.commit()
        print("✓ User soft delete migration rolled back successfully")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Rollback failed: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python migration.py <up|down> <db_path>")
        sys.exit(1)
    
    action = sys.argv[1]
    db_path = sys.argv[2]
    
    if action == 'up':
        migrate_up(db_path)
    elif action == 'down':
        migrate_down(db_path)
    else:
        print("Action must be 'up' or 'down'")
        sys.exit(1)
```

### 1.3 Migration Execution Steps

1. **Backup Database**:
   ```bash
   cp cvd.db cvd.db.backup.$(date +%Y%m%d_%H%M%S)
   ```

2. **Run Migration**:
   ```bash
   python migrations/001_user_soft_delete.py up cvd.db
   ```

3. **Verify Schema**:
   ```bash
   sqlite3 cvd.db ".schema users"
   ```

4. **Test Queries**:
   ```bash
   sqlite3 cvd.db "SELECT COUNT(*) FROM users WHERE is_deleted = 0"
   ```

## 2. API Endpoint Implementation

### 2.1 Service Orders Constraint Validation

Create helper function in `auth.py`:

```python
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
```

### 2.2 Updated User Deactivation Endpoint

Modify existing `/api/users/<int:user_id>` PUT endpoint in `app.py`:

```python
@app.route('/api/users/<int:user_id>/deactivate', methods=['PUT'])
@auth_manager.require_role(['admin', 'manager'])
def deactivate_user(user_id):
    """Deactivate user account"""
    from auth import check_user_service_orders, log_audit_event
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists and is active
    user = cursor.execute('''
        SELECT id, username, email, role, is_active, is_deleted 
        FROM users WHERE id = ? AND is_deleted = 0
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user['is_active']:
        return jsonify({'error': 'User is already deactivated'}), 400
    
    # Prevent self-deactivation
    if user_id == g.user['id']:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    # Check for pending service orders
    if check_user_service_orders(user_id, db):
        return jsonify({
            'error': 'Cannot deactivate user with pending or in-progress service orders',
            'code': 'CONSTRAINT_VIOLATION'
        }), 409
    
    # Check if this is the last admin
    if user['role'] == 'admin':
        admin_count = cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE role = 'admin' AND is_active = 1 AND is_deleted = 0 AND id != ?
        ''', (user_id,)).fetchone()[0]
        
        if admin_count == 0:
            return jsonify({'error': 'Cannot deactivate the last active admin'}), 400
    
    try:
        # Deactivate user
        cursor.execute('''
            UPDATE users 
            SET is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now(), user_id))
        
        # Invalidate all sessions for this user
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        
        db.commit()
        
        # Log audit event
        log_audit_event(
            user_id=g.user['id'],
            action='USER_DEACTIVATED',
            resource_type='user',
            resource_id=user_id,
            details={'target_username': user['username']}
        )
        
        return jsonify({
            'message': 'User deactivated successfully',
            'user_id': user_id,
            'username': user['username']
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to deactivate user: {str(e)}'}), 500
```

### 2.3 User Activation Endpoint

```python
@app.route('/api/users/<int:user_id>/activate', methods=['PUT'])
@auth_manager.require_role(['admin', 'manager'])
def activate_user(user_id):
    """Activate user account"""
    from auth import log_audit_event
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists and is deactivated
    user = cursor.execute('''
        SELECT id, username, email, role, is_active, is_deleted 
        FROM users WHERE id = ? AND is_deleted = 0
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user['is_active']:
        return jsonify({'error': 'User is already active'}), 400
    
    try:
        # Activate user and clear any lock status
        cursor.execute('''
            UPDATE users 
            SET is_active = 1, updated_at = ?, failed_login_attempts = 0, locked_until = NULL
            WHERE id = ?
        ''', (datetime.now(), user_id))
        
        db.commit()
        
        # Log audit event
        log_audit_event(
            user_id=g.user['id'],
            action='USER_ACTIVATED',
            resource_type='user',
            resource_id=user_id,
            details={'target_username': user['username']}
        )
        
        return jsonify({
            'message': 'User activated successfully',
            'user_id': user_id,
            'username': user['username']
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to activate user: {str(e)}'}), 500
```

### 2.4 Soft Delete Endpoint

```python
@app.route('/api/users/<int:user_id>/soft-delete', methods=['DELETE'])
@auth_manager.require_role(['admin', 'manager'])
def soft_delete_user(user_id):
    """Soft delete a user"""
    from auth import check_user_service_orders, log_audit_event
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists and is not already deleted
    user = cursor.execute('''
        SELECT id, username, email, role, is_active, is_deleted 
        FROM users WHERE id = ? AND is_deleted = 0
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent self-deletion
    if user_id == g.user['id']:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    # Check for pending service orders
    if check_user_service_orders(user_id, db):
        return jsonify({
            'error': 'Cannot delete user with pending or in-progress service orders',
            'code': 'CONSTRAINT_VIOLATION'
        }), 409
    
    # Check if this is the last admin
    if user['role'] == 'admin':
        admin_count = cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE role = 'admin' AND is_active = 1 AND is_deleted = 0 AND id != ?
        ''', (user_id,)).fetchone()[0]
        
        if admin_count == 0:
            return jsonify({'error': 'Cannot delete the last active admin'}), 400
    
    try:
        # Soft delete user
        cursor.execute('''
            UPDATE users 
            SET is_deleted = 1, deleted_at = ?, deleted_by = ?, 
                is_active = 0, updated_at = ?
            WHERE id = ?
        ''', (datetime.now(), g.user['id'], datetime.now(), user_id))
        
        # Invalidate all sessions for this user
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        
        db.commit()
        
        # Log audit event
        log_audit_event(
            user_id=g.user['id'],
            action='USER_SOFT_DELETED',
            resource_type='user',
            resource_id=user_id,
            details={
                'target_username': user['username'],
                'target_email': user['email'],
                'target_role': user['role']
            }
        )
        
        return jsonify({
            'message': 'User soft deleted successfully',
            'user_id': user_id,
            'username': user['username']
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to soft delete user: {str(e)}'}), 500
```

### 2.5 Updated Get Users Endpoint

Update the existing `get_users()` function in `app.py`:

```python
@app.route('/api/users', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_users():
    """Get all users with pagination and filtering"""
    db = get_db()
    cursor = db.cursor()
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    offset = (page - 1) * per_page
    
    # Get filter parameters
    role_filter = request.args.get('role')
    status_filter = request.args.get('status')
    search = request.args.get('search')
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    
    # Build base query - exclude soft deleted by default
    base_query = '''
        SELECT id, username, email, role, is_active, created_at, 
               updated_at, last_login, failed_login_attempts, locked_until,
               is_deleted, deleted_at, deleted_by
        FROM users 
        WHERE 1=1
    '''
    
    params = []
    
    # Filter out soft deleted unless explicitly requested
    if not include_deleted:
        base_query += ' AND is_deleted = 0'
    
    # Apply filters
    if role_filter:
        base_query += ' AND role = ?'
        params.append(role_filter)
    
    if status_filter == 'active':
        base_query += ' AND is_active = 1'
    elif status_filter == 'inactive':
        base_query += ' AND is_active = 0'
    elif status_filter == 'deleted' and include_deleted:
        base_query += ' AND is_deleted = 1'
    
    if search:
        base_query += ' AND (username LIKE ? OR email LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param])
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM ({base_query}) as filtered"
    total = cursor.execute(count_query, params).fetchone()[0]
    
    # Add ordering and pagination
    query = base_query + ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    users = cursor.execute(query, params).fetchall()
    
    # Convert to list of dictionaries and add deleted_by username
    users_list = []
    for user in users:
        user_dict = dict(user)
        
        # Get deleted_by username if applicable
        if user_dict['deleted_by']:
            deleted_by_user = cursor.execute(
                'SELECT username FROM users WHERE id = ?', 
                (user_dict['deleted_by'],)
            ).fetchone()
            user_dict['deleted_by_username'] = deleted_by_user['username'] if deleted_by_user else 'Unknown'
        else:
            user_dict['deleted_by_username'] = None
            
        users_list.append(user_dict)
    
    return jsonify({
        'users': users_list,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })
```

## 3. Authentication and Permission Validation

### 3.1 Updated Session Validation

Modify the `validate_session()` method in `auth.py`:

```python
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
```

### 3.2 Permission Checks

Update role-based decorators to exclude soft deleted users:

```python
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
            if user.get('is_deleted', 0) == 1:
                return jsonify({'error': 'Account has been deactivated'}), 401
            
            if user['role'] not in allowed_roles:
                log_audit_event(
                    user_id=user['id'],
                    action='UNAUTHORIZED_ACCESS',
                    resource_type='endpoint',
                    details={
                        'endpoint': request.path,
                        'method': request.method,
                        'required_roles': allowed_roles,
                        'user_role': user['role']
                    }
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
```

## 4. Service Orders Constraint Validation

### 4.1 Constraint Query Implementation

The service orders constraint validation checks both created orders and assigned orders:

```python
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
```

### 4.2 Enhanced Error Response

```python
def validate_user_constraints(user_id, action_type='deactivate'):
    """Validate user constraints before deactivation/deletion"""
    from auth import get_user_service_order_details
    
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
```

## 5. Audit Logging Integration

### 5.1 Enhanced Audit Events

Update audit logging to include more detailed information:

```python
# Enhanced audit event types for user lifecycle
USER_AUDIT_EVENTS = {
    'USER_DEACTIVATED': 'User account deactivated',
    'USER_ACTIVATED': 'User account activated',
    'USER_SOFT_DELETED': 'User account soft deleted',
    'USER_DEACTIVATION_BLOCKED': 'User deactivation blocked by constraints',
    'USER_DELETION_BLOCKED': 'User deletion blocked by constraints',
    'USER_CONSTRAINT_VIOLATION': 'User operation failed due to constraint violation'
}

def log_user_lifecycle_event(actor_id, action, target_user_id, target_username, 
                           details=None, constraint_info=None):
    """Log user lifecycle events with enhanced detail"""
    from auth import log_audit_event
    
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
```

### 5.2 Audit Trail Queries

```python
@app.route('/api/users/<int:user_id>/audit-trail', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_user_audit_trail(user_id):
    """Get comprehensive audit trail for a user"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists (including soft deleted)
    user = cursor.execute('''
        SELECT username, email, role, is_deleted 
        FROM users WHERE id = ?
    ''', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get audit trail
    audit_events = cursor.execute('''
        SELECT al.*, u.username as actor_username
        FROM audit_log al
        LEFT JOIN users u ON al.user_id = u.id
        WHERE al.resource_type IN ('user', 'user_lifecycle') 
        AND (al.resource_id = ? OR JSON_EXTRACT(al.details, '$.target_user_id') = ?)
        ORDER BY al.created_at DESC
    ''', (user_id, user_id)).fetchall()
    
    return jsonify({
        'user_id': user_id,
        'username': user['username'],
        'is_deleted': user['is_deleted'],
        'audit_events': [dict(event) for event in audit_events]
    })
```

## 6. Testing Strategy

### 6.1 Unit Tests

Create test file: `/home/jbrice/Projects/365/tests/test_user_soft_delete.py`

```python
import unittest
import sqlite3
import os
import tempfile
from datetime import datetime
from app import app
from auth import AuthManager, check_user_service_orders

class TestUserSoftDelete(unittest.TestCase):
    
    def setUp(self):
        """Set up test database and client"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Initialize test database
        self.init_test_db()
        
    def tearDown(self):
        """Clean up after tests"""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def init_test_db(self):
        """Initialize test database with schema"""
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        
        # Create users table with soft delete columns
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                is_deleted BOOLEAN DEFAULT 0,
                deleted_at TIMESTAMP NULL,
                deleted_by INTEGER NULL
            )
        ''')
        
        # Create service orders table
        cursor.execute('''
            CREATE TABLE service_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                driver_id INTEGER,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled'))
            )
        ''')
        
        # Create test users
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_active)
            VALUES 
            ('admin', 'admin@test.com', 'hash1', 'admin', 1),
            ('manager', 'manager@test.com', 'hash2', 'manager', 1),
            ('driver', 'driver@test.com', 'hash3', 'driver', 1),
            ('inactive_user', 'inactive@test.com', 'hash4', 'viewer', 0)
        ''')
        
        db.commit()
        db.close()
    
    def test_user_deactivation(self):
        """Test user deactivation"""
        # Test deactivating active user
        response = self.client.put('/api/users/3/deactivate')
        # Add authentication headers for actual test
        
    def test_constraint_validation(self):
        """Test service orders constraint validation"""
        # Create service order for user
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO service_orders (created_by, driver_id, status)
            VALUES (3, 3, 'pending')
        ''')
        db.commit()
        db.close()
        
        # Test that constraint is enforced
        has_orders = check_user_service_orders(3)
        self.assertTrue(has_orders)
    
    def test_soft_delete(self):
        """Test soft delete functionality"""
        # Test soft deleting user without constraints
        pass  # Implement with proper auth
    
    def test_audit_logging(self):
        """Test audit logging for user lifecycle events"""
        pass  # Implement audit verification

if __name__ == '__main__':
    unittest.main()
```

### 6.2 Integration Tests

```python
# Integration test scenarios
TEST_SCENARIOS = [
    {
        'name': 'deactivate_user_with_pending_orders',
        'setup': 'Create user with pending service order',
        'action': 'Attempt deactivation',
        'expected': '409 Conflict with constraint violation message'
    },
    {
        'name': 'soft_delete_last_admin',
        'setup': 'Ensure only one admin exists',
        'action': 'Attempt to delete admin',
        'expected': '400 Bad Request with last admin message'
    },
    {
        'name': 'successful_deactivation_reactivation_cycle',
        'setup': 'Create user without constraints',
        'action': 'Deactivate then reactivate',
        'expected': 'Success with proper audit trail'
    }
]
```

### 6.3 API Testing

Use the following curl commands for manual API testing:

```bash
# Test deactivation
curl -X PUT http://localhost:5000/api/users/3/deactivate \
     -H "Content-Type: application/json" \
     -b "session_id=your_session_id"

# Test activation
curl -X PUT http://localhost:5000/api/users/3/activate \
     -H "Content-Type: application/json" \
     -b "session_id=your_session_id"

# Test soft delete
curl -X DELETE http://localhost:5000/api/users/3/soft-delete \
     -H "Content-Type: application/json" \
     -b "session_id=your_session_id"

# Test get users with deleted
curl -X GET "http://localhost:5000/api/users?include_deleted=true" \
     -H "Content-Type: application/json" \
     -b "session_id=your_session_id"
```

## 7. Rollback Procedures

### 7.1 Database Rollback

```bash
# 1. Stop application
sudo systemctl stop cvd-app

# 2. Restore database from backup
cp cvd.db.backup.YYYYMMDD_HHMMSS cvd.db

# 3. Verify rollback
sqlite3 cvd.db ".schema users" | grep -v "is_deleted\|deleted_at\|deleted_by"

# 4. Start application
sudo systemctl start cvd-app
```

### 7.2 Code Rollback

```bash
# 1. Revert API endpoints
git checkout HEAD~1 -- app.py auth.py

# 2. Remove migration files
rm migrations/001_user_soft_delete.py

# 3. Restart application
sudo systemctl restart cvd-app
```

### 7.3 Feature Flag Rollback

Add feature flag support to allow runtime disable:

```python
# In app.py
SOFT_DELETE_ENABLED = os.environ.get('SOFT_DELETE_ENABLED', 'true').lower() == 'true'

@app.route('/api/users/<int:user_id>/soft-delete', methods=['DELETE'])
@auth_manager.require_role(['admin', 'manager'])
def soft_delete_user(user_id):
    """Soft delete a user"""
    if not SOFT_DELETE_ENABLED:
        return jsonify({'error': 'Soft delete feature is disabled'}), 503
    
    # ... rest of implementation
```

## 8. Performance Considerations

### 8.1 Query Optimization

The new index `idx_users_active_deleted` optimizes common queries:

```sql
-- Optimized queries
SELECT * FROM users WHERE is_active = 1 AND is_deleted = 0;  -- Uses index
SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1 AND is_deleted = 0;  -- Partial index scan
```

### 8.2 Session Cleanup

Update session cleanup to handle soft deleted users:

```python
def cleanup_soft_deleted_user_sessions():
    """Clean up sessions for soft deleted users"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    deleted = cursor.execute('''
        DELETE FROM sessions 
        WHERE user_id IN (
            SELECT id FROM users WHERE is_deleted = 1
        )
    ''').rowcount
    
    db.commit()
    db.close()
    
    if deleted > 0:
        print(f'Cleaned up {deleted} sessions for soft deleted users')
```

### 8.3 Bulk Operations

For large-scale operations, provide batch endpoints:

```python
@app.route('/api/users/batch-deactivate', methods=['POST'])
@auth_manager.require_role(['admin'])
def batch_deactivate_users():
    """Batch deactivate multiple users"""
    data = request.json
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'error': 'No user IDs provided'}), 400
    
    db = get_db()
    results = []
    
    for user_id in user_ids:
        # Check constraints for each user
        if check_user_service_orders(user_id, db):
            results.append({
                'user_id': user_id,
                'status': 'failed',
                'reason': 'Has pending service orders'
            })
            continue
        
        # Process deactivation
        try:
            # ... deactivation logic
            results.append({
                'user_id': user_id,
                'status': 'success'
            })
        except Exception as e:
            results.append({
                'user_id': user_id,
                'status': 'failed',
                'reason': str(e)
            })
    
    return jsonify({'results': results})
```

## 9. Security Considerations

### 9.1 Additional Permission Checks

```python
def can_modify_user(actor_role, actor_id, target_user_id, target_role):
    """Check if actor can modify target user"""
    
    # Self-modification check
    if actor_id == target_user_id:
        return False, "Cannot modify your own account"
    
    # Admin can modify anyone except themselves
    if actor_role == 'admin':
        return True, None
    
    # Manager can modify drivers and viewers only
    if actor_role == 'manager' and target_role in ['driver', 'viewer']:
        return True, None
    
    return False, "Insufficient permissions for this operation"
```

### 9.2 Rate Limiting

```python
from collections import defaultdict
from time import time

# Simple in-memory rate limiting
user_action_timestamps = defaultdict(list)
MAX_USER_ACTIONS_PER_MINUTE = 10

def check_rate_limit(user_id, action_type):
    """Check if user has exceeded rate limit for user management actions"""
    now = time()
    user_timestamps = user_action_timestamps[user_id]
    
    # Remove timestamps older than 1 minute
    user_timestamps[:] = [ts for ts in user_timestamps if now - ts < 60]
    
    if len(user_timestamps) >= MAX_USER_ACTIONS_PER_MINUTE:
        return False, "Rate limit exceeded for user management actions"
    
    user_timestamps.append(now)
    return True, None
```

## 10. Monitoring and Alerting

### 10.1 Metrics Collection

```python
# User lifecycle metrics
USER_LIFECYCLE_METRICS = {
    'users_deactivated_count': 0,
    'users_activated_count': 0,
    'users_soft_deleted_count': 0,
    'constraint_violations_count': 0
}

def increment_metric(metric_name):
    """Increment user lifecycle metric"""
    if metric_name in USER_LIFECYCLE_METRICS:
        USER_LIFECYCLE_METRICS[metric_name] += 1

@app.route('/api/metrics/user-lifecycle', methods=['GET'])
@auth_manager.require_role(['admin'])
def get_user_lifecycle_metrics():
    """Get user lifecycle metrics"""
    return jsonify(USER_LIFECYCLE_METRICS)
```

### 10.2 Alert Conditions

```python
# Alert conditions for monitoring
ALERT_CONDITIONS = {
    'multiple_failed_deactivations': {
        'threshold': 5,
        'window_minutes': 10,
        'message': 'Multiple user deactivation failures detected'
    },
    'constraint_violation_spike': {
        'threshold': 10,
        'window_minutes': 5,
        'message': 'High number of constraint violations detected'
    }
}
```

## 11. Documentation Updates

### 11.1 API Documentation

Update API documentation to include new endpoints:

```yaml
# OpenAPI specification excerpt
paths:
  /api/users/{user_id}/deactivate:
    put:
      summary: Deactivate user account
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: User deactivated successfully
        '409':
          description: Constraint violation (has pending service orders)
        '400':
          description: Invalid request or cannot deactivate last admin
```

### 11.2 Admin Guide

Create admin guide section for user lifecycle management:

```markdown
# User Lifecycle Management

## Deactivating Users
1. Navigate to User Management
2. Click "Deactivate" for target user
3. Confirm action in modal
4. User loses access immediately

## Constraint Violations
If deactivation fails due to pending service orders:
1. Review user's assigned orders
2. Reassign or complete orders
3. Retry deactivation

## Audit Trail
All user lifecycle actions are logged and can be viewed in the audit section.
```

## 12. Deployment Steps

### 12.1 Pre-deployment Checklist

- [ ] Database backup completed
- [ ] Migration script tested
- [ ] API endpoints tested
- [ ] Constraint validation verified
- [ ] Audit logging confirmed
- [ ] Rollback procedure documented
- [ ] Performance impact assessed

### 12.2 Deployment Sequence

1. **Maintenance Mode**: Enable maintenance mode
2. **Database Backup**: Create timestamped backup
3. **Run Migration**: Execute schema changes
4. **Deploy Code**: Update application files
5. **Restart Services**: Restart Flask application
6. **Verify Deployment**: Run health checks
7. **Monitor**: Watch for errors in logs
8. **Exit Maintenance**: Disable maintenance mode

### 12.3 Post-deployment Verification

```bash
# Verify database schema
sqlite3 cvd.db ".schema users" | grep -E "(is_deleted|deleted_at|deleted_by)"

# Test API endpoints
curl -X GET http://localhost:5000/api/users -b "session_id=admin_session"

# Check audit logging
sqlite3 cvd.db "SELECT COUNT(*) FROM audit_log WHERE action LIKE '%USER_%'"

# Monitor error logs
tail -f /var/log/cvd/app.log | grep -i error
```

## 13. Risk Mitigation

### 13.1 Data Loss Prevention

- Database backups before migration
- Soft delete preserves all data
- Audit trail maintains operation history
- Foreign key constraints prevent orphaned records

### 13.2 Performance Impact

- Indexed queries minimize performance impact
- Batch operations for bulk changes
- Connection pooling for high concurrency
- Query optimization for filtered results

### 13.3 Security Risks

- Rate limiting prevents abuse
- Role-based access control maintained
- Session invalidation on state changes
- Audit logging for compliance

## 14. Success Metrics

### 14.1 Technical Metrics

- Migration completion: 100% success
- API response time: <200ms for user operations
- Database query performance: <50ms for filtered queries
- Error rate: <0.1% for user operations

### 14.2 Business Metrics

- Reduced accidental deletions: 0% (measured by support tickets)
- Improved user management efficiency: 50% reduction in time spent
- Enhanced audit compliance: 100% action coverage
- Better user experience: Positive feedback from administrators

## Conclusion

This deployment plan provides a comprehensive approach to implementing user soft delete functionality in the CVD application. The implementation maintains data integrity, provides proper constraint validation, ensures security through role-based access control, and includes comprehensive audit logging.

The phased approach allows for safe deployment with proper rollback procedures, while the testing strategy ensures reliability and performance. The monitoring and alerting capabilities provide operational visibility, and the documentation updates ensure proper adoption by administrators.