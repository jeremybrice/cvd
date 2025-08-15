import unittest
import sqlite3
import os
import tempfile
import json
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
        
        # Create admin session for testing
        self.admin_session_id = self.create_test_session()
        
    def tearDown(self):
        """Clean up after tests"""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def init_test_db(self):
        """Initialize test database with schema"""
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        
        # Create migrations table
        cursor.execute('''
            CREATE TABLE migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activity_count INTEGER DEFAULT 0,
                device_type TEXT DEFAULT 'unknown'
            )
        ''')
        
        # Create audit_log table
        cursor.execute('''
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id INTEGER,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create test users
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_active, is_deleted)
            VALUES 
            ('admin', 'admin@test.com', 'hash1', 'admin', 1, 0),
            ('manager', 'manager@test.com', 'hash2', 'manager', 1, 0),
            ('driver1', 'driver1@test.com', 'hash3', 'driver', 1, 0),
            ('driver2', 'driver2@test.com', 'hash4', 'driver', 0, 0),
            ('viewer', 'viewer@test.com', 'hash5', 'viewer', 1, 0)
        ''')
        
        db.commit()
        db.close()
    
    def create_test_session(self, user_id=1):
        """Create a test session for testing API endpoints"""
        session_id = 'test_session_123'
        expires_at = datetime.now()
        expires_at = expires_at.replace(year=expires_at.year + 1)  # Expire in 1 year
        
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (id, user_id, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, expires_at, '127.0.0.1', 'test-agent'))
        
        db.commit()
        db.close()
        
        return session_id
    
    def test_check_user_service_orders(self):
        """Test service orders constraint validation"""
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        
        # Create service order for user 3 (driver1)
        cursor.execute('''
            INSERT INTO service_orders (created_by, driver_id, status)
            VALUES (3, 3, 'pending')
        ''')
        db.commit()
        db.close()
        
        # Test that constraint is detected
        has_orders = check_user_service_orders(3)
        self.assertTrue(has_orders)
        
        # Test user without orders
        has_orders = check_user_service_orders(5)
        self.assertFalse(has_orders)
    
    def test_user_deactivation_api(self):
        """Test user deactivation API endpoint"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session_id
        
        # Test deactivating active user (driver1)
        response = self.client.put('/api/users/3/deactivate')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User deactivated successfully')
        
        # Verify user is deactivated
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        user = cursor.execute('SELECT is_active FROM users WHERE id = 3').fetchone()
        self.assertEqual(user[0], 0)
        db.close()
        
        # Test deactivating already inactive user
        response = self.client.put('/api/users/3/deactivate')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User is already deactivated')
    
    def test_user_activation_api(self):
        """Test user activation API endpoint"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session_id
        
        # Test activating inactive user (driver2)
        response = self.client.put('/api/users/4/activate')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User activated successfully')
        
        # Verify user is activated
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        user = cursor.execute('SELECT is_active FROM users WHERE id = 4').fetchone()
        self.assertEqual(user[0], 1)
        db.close()
        
        # Test activating already active user
        response = self.client.put('/api/users/4/activate')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User is already active')
    
    def test_user_soft_delete_api(self):
        """Test soft delete API endpoint"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session_id
        
        # Test soft deleting user without constraints (viewer)
        response = self.client.delete('/api/users/5/soft-delete')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User soft deleted successfully')
        
        # Verify user is soft deleted
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        user = cursor.execute('SELECT is_deleted, deleted_by FROM users WHERE id = 5').fetchone()
        self.assertEqual(user[0], 1)
        self.assertEqual(user[1], 1)  # Deleted by admin (user id 1)
        db.close()
        
        # Test soft deleting already deleted user
        response = self.client.delete('/api/users/5/soft-delete')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User not found')
    
    def test_constraint_violation(self):
        """Test that constraint violations are properly handled"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session_id
        
        # Create service order for driver1 (user id 3)
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO service_orders (created_by, driver_id, status)
            VALUES (3, 3, 'pending')
        ''')
        db.commit()
        db.close()
        
        # Test that deactivation is blocked
        response = self.client.put('/api/users/3/deactivate')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'CONSTRAINT_VIOLATION')
        
        # Test that soft delete is blocked
        response = self.client.delete('/api/users/3/soft-delete')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'CONSTRAINT_VIOLATION')
    
    def test_self_modification_prevention(self):
        """Test that users cannot deactivate/delete themselves"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session_id
        
        # Test self-deactivation prevention
        response = self.client.put('/api/users/1/deactivate')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Cannot deactivate your own account')
        
        # Test self-deletion prevention
        response = self.client.delete('/api/users/1/soft-delete')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Cannot delete your own account')
    
    def test_get_users_with_soft_delete(self):
        """Test get users endpoint with soft delete handling"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session_id
        
        # Soft delete a user first
        self.client.delete('/api/users/5/soft-delete')
        
        # Test getting users without deleted
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        user_ids = [user['id'] for user in data['users']]
        self.assertNotIn(5, user_ids)
        
        # Test getting users with deleted
        response = self.client.get('/api/users?include_deleted=true')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        user_ids = [user['id'] for user in data['users']]
        self.assertIn(5, user_ids)
        
        # Find the deleted user and verify metadata
        deleted_user = next((u for u in data['users'] if u['id'] == 5), None)
        self.assertIsNotNone(deleted_user)
        self.assertEqual(deleted_user['is_deleted'], 1)
        self.assertEqual(deleted_user['deleted_by_username'], 'admin')
    
    def test_user_lifecycle_metrics(self):
        """Test user lifecycle metrics endpoint"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session_id
        
        # Perform some lifecycle operations
        self.client.put('/api/users/3/deactivate')  # Deactivate driver1
        self.client.delete('/api/users/5/soft-delete')  # Delete viewer
        
        # Test metrics endpoint
        response = self.client.get('/api/metrics/user-lifecycle')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('user_counts', data)
        self.assertIn('recent_activity', data)
        
        # Verify counts
        counts = data['user_counts']
        self.assertEqual(counts['total'], 5)  # All users including deleted
        self.assertEqual(counts['active'], 2)  # admin, manager
        self.assertEqual(counts['inactive'], 2)  # deactivated driver1, driver2
        self.assertEqual(counts['deleted'], 1)  # soft deleted viewer
    
    def test_batch_deactivate(self):
        """Test batch deactivation endpoint"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session_id
        
        # Test batch deactivating multiple users
        response = self.client.post('/api/users/batch-deactivate',
                                  json={'user_ids': [3, 5]})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        results = data['results']
        self.assertEqual(len(results), 2)
        
        # Both should succeed
        success_count = sum(1 for r in results if r['status'] == 'success')
        self.assertEqual(success_count, 2)
        
        # Verify users are deactivated
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        user3 = cursor.execute('SELECT is_active FROM users WHERE id = 3').fetchone()
        user5 = cursor.execute('SELECT is_active FROM users WHERE id = 5').fetchone()
        self.assertEqual(user3[0], 0)
        self.assertEqual(user5[0], 0)
        db.close()

if __name__ == '__main__':
    unittest.main()