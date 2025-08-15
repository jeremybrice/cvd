#!/usr/bin/env python3
"""
CVD Component Unit Testing Examples

This file demonstrates comprehensive unit testing patterns for CVD application components,
focusing on isolated testing with mocked dependencies, edge cases, and business logic validation.
These examples show how to test individual components without external dependencies.
"""

import unittest
import sqlite3
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, call
import hashlib

# Add CVD application to Python path for testing
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

# Import CVD application components
try:
    from auth import AuthManager, hash_password, verify_password
    from service_order_service import ServiceOrderService
    from planogram_optimizer import PlanogramOptimizer
except ImportError as e:
    print(f"Warning: Could not import CVD modules: {e}")
    print("This example requires the CVD application components to be in the Python path")


class AuthManagerUnitTests(unittest.TestCase):
    """
    Unit tests for the AuthManager component.
    
    These tests demonstrate:
    - Password hashing and verification
    - User authentication logic
    - Session management
    - Role-based access control
    - Error handling for authentication failures
    """
    
    def setUp(self):
        """Set up test environment with mocked database."""
        # Create in-memory database for testing
        self.db_path = ':memory:'
        self.auth_manager = None
        
        # Create mock Flask app
        self.mock_app = Mock()
        self.mock_app.config = {'DATABASE': self.db_path, 'SECRET_KEY': 'test-key'}
        
        # Initialize test database
        self.init_auth_test_database()
        
        print(f"AuthManager unit test setup complete")
    
    def init_auth_test_database(self):
        """Initialize database with users table for authentication testing."""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer',
                deleted_at TIMESTAMP NULL,
                active BOOLEAN DEFAULT 1,
                last_login TIMESTAMP,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            CREATE INDEX idx_users_username ON users(username);
            CREATE INDEX idx_sessions_user_id ON sessions(user_id);
        """)
        
        # Create test users
        test_users = [
            ('admin', hash_password('admin'), 'admin', 1),
            ('manager', hash_password('manager'), 'manager', 1),
            ('driver', hash_password('driver'), 'driver', 1),
            ('viewer', hash_password('viewer'), 'viewer', 1),
            ('locked_user', hash_password('password'), 'viewer', 1),
            ('inactive_user', hash_password('password'), 'viewer', 0),
            ('deleted_user', hash_password('password'), 'viewer', 1)
        ]
        
        cursor.executemany("""
            INSERT INTO users (username, password_hash, role, active)
            VALUES (?, ?, ?, ?)
        """, test_users)
        
        # Set deleted_at for soft-deleted user
        cursor.execute("""
            UPDATE users SET deleted_at = CURRENT_TIMESTAMP 
            WHERE username = 'deleted_user'
        """)
        
        # Set failed attempts for locked user
        cursor.execute("""
            UPDATE users SET failed_attempts = 5, 
                           locked_until = datetime('now', '+1 hour')
            WHERE username = 'locked_user'
        """)
        
        db.commit()
        db.close()
        
        print("Auth test database initialized with sample users")
    
    def test_password_hashing_and_verification(self):
        """
        Test password hashing and verification functions.
        
        This test verifies:
        - Passwords are properly hashed (not stored in plaintext)
        - Same password produces different hashes (salt is random)
        - Verification correctly validates passwords
        - Invalid passwords are rejected
        """
        print("\n=== Testing Password Hashing and Verification ===")
        
        # Test 1: Basic password hashing
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different due to random salt
        self.assertNotEqual(hash1, hash2, "Same password should produce different hashes")
        
        # But both should verify correctly
        self.assertTrue(verify_password(password, hash1), "First hash should verify correctly")
        self.assertTrue(verify_password(password, hash2), "Second hash should verify correctly")
        
        print("✓ Password hashing produces unique salted hashes")
        print("✓ Password verification works correctly")
        
        # Test 2: Hash properties
        self.assertGreater(len(hash1), 50, "Hash should be reasonable length")
        self.assertNotIn(password, hash1, "Plaintext password should not appear in hash")
        
        print("✓ Hash has proper security properties")
        
        # Test 3: Invalid password verification
        wrong_password = "wrong_password"
        self.assertFalse(verify_password(wrong_password, hash1), 
                        "Wrong password should not verify")
        
        # Test empty/None passwords
        self.assertFalse(verify_password("", hash1), "Empty password should not verify")
        self.assertFalse(verify_password(None, hash1), "None password should not verify")
        
        print("✓ Invalid passwords properly rejected")
        
        # Test 4: Edge cases
        edge_case_passwords = [
            "",  # Empty password
            " ",  # Space only
            "a",  # Single character
            "a" * 1000,  # Very long password
            "🚀🔒💻",  # Unicode characters
            "password with spaces and symbols!@#$%^&*()",
        ]
        
        for edge_password in edge_case_passwords:
            hash_result = hash_password(edge_password)
            self.assertTrue(verify_password(edge_password, hash_result),
                          f"Edge case password should hash and verify: '{edge_password}'")
        
        print("✓ Edge case passwords handled correctly")
    
    def test_user_authentication_logic(self):
        """
        Test user authentication business logic.
        
        This test demonstrates:
        - Successful authentication with valid credentials
        - Authentication failure with invalid credentials
        - Account status validation (active, not deleted, not locked)
        - Error handling for various authentication scenarios
        """
        print("\n=== Testing User Authentication Logic ===")
        
        # Mock AuthManager with database connection
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            auth_manager = AuthManager(self.mock_app, self.db_path)
            
            # Test 1: Successful authentication
            print("Testing successful authentication...")
            
            # Mock database response for valid user
            mock_cursor.fetchone.return_value = (
                1, 'admin', hash_password('admin'), 'admin', None, 1, 0, None  # id, username, hash, role, deleted_at, active, failed_attempts, locked_until
            )
            
            result = auth_manager.authenticate_user('admin', 'admin')
            
            self.assertIsNotNone(result, "Authentication should succeed for valid credentials")
            self.assertEqual(result['username'], 'admin')
            self.assertEqual(result['role'], 'admin')
            self.assertIn('id', result)
            
            # Verify database query was made
            mock_cursor.execute.assert_called()
            
            print("✓ Valid credentials authenticated successfully")
            
            # Test 2: Authentication failure - wrong password
            print("Testing authentication failure (wrong password)...")
            
            # Reset mock for new test
            mock_cursor.reset_mock()
            mock_cursor.fetchone.return_value = (
                1, 'admin', hash_password('admin'), 'admin', None, 1, 0, None
            )
            
            result = auth_manager.authenticate_user('admin', 'wrong_password')
            
            self.assertIsNone(result, "Authentication should fail for wrong password")
            
            print("✓ Wrong password properly rejected")
            
            # Test 3: Authentication failure - user not found
            print("Testing authentication failure (user not found)...")
            
            mock_cursor.reset_mock()
            mock_cursor.fetchone.return_value = None
            
            result = auth_manager.authenticate_user('nonexistent', 'password')
            
            self.assertIsNone(result, "Authentication should fail for non-existent user")
            
            print("✓ Non-existent user properly handled")
            
            # Test 4: Account status validation - inactive user
            print("Testing inactive user rejection...")
            
            mock_cursor.reset_mock()
            mock_cursor.fetchone.return_value = (
                1, 'inactive_user', hash_password('password'), 'viewer', None, 0, 0, None  # active = 0
            )
            
            result = auth_manager.authenticate_user('inactive_user', 'password')
            
            self.assertIsNone(result, "Authentication should fail for inactive user")
            
            print("✓ Inactive user properly rejected")
            
            # Test 5: Account status validation - deleted user
            print("Testing deleted user rejection...")
            
            mock_cursor.reset_mock()
            mock_cursor.fetchone.return_value = (
                1, 'deleted_user', hash_password('password'), 'viewer', '2024-01-01 12:00:00', 1, 0, None  # deleted_at set
            )
            
            result = auth_manager.authenticate_user('deleted_user', 'password')
            
            self.assertIsNone(result, "Authentication should fail for deleted user")
            
            print("✓ Deleted user properly rejected")
            
            # Test 6: Account lockout handling
            print("Testing account lockout handling...")
            
            mock_cursor.reset_mock()
            future_time = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            mock_cursor.fetchone.return_value = (
                1, 'locked_user', hash_password('password'), 'viewer', None, 1, 5, future_time  # locked_until in future
            )
            
            result = auth_manager.authenticate_user('locked_user', 'password')
            
            self.assertIsNone(result, "Authentication should fail for locked account")
            
            print("✓ Locked account properly rejected")
    
    def test_session_management(self):
        """
        Test session creation, validation, and cleanup.
        
        This test demonstrates:
        - Session creation with unique identifiers
        - Session validation and expiration
        - Session cleanup and logout
        - Concurrent session handling
        """
        print("\n=== Testing Session Management ===")
        
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            auth_manager = AuthManager(self.mock_app, self.db_path)
            
            # Test 1: Session creation
            print("Testing session creation...")
            
            user_data = {
                'id': 1,
                'username': 'admin',
                'role': 'admin'
            }
            
            with patch('secrets.token_urlsafe', return_value='test_session_token'):
                session_token = auth_manager.create_session(user_data)
            
            self.assertEqual(session_token, 'test_session_token')
            
            # Verify session was inserted into database
            mock_cursor.execute.assert_called()
            execute_calls = mock_cursor.execute.call_args_list
            
            # Should have called execute to insert session
            session_insert_call = any('INSERT INTO sessions' in str(call) for call in execute_calls)
            self.assertTrue(session_insert_call, "Session should be inserted into database")
            
            print("✓ Session created successfully")
            
            # Test 2: Session validation - valid session
            print("Testing valid session validation...")
            
            mock_cursor.reset_mock()
            # Mock valid session response
            mock_cursor.fetchone.return_value = (
                'test_session_token', 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')  # expires in 1 hour
            )
            
            # Mock user data response
            with patch.object(auth_manager, 'get_user_by_id') as mock_get_user:
                mock_get_user.return_value = user_data
                
                session_user = auth_manager.validate_session('test_session_token')
            
            self.assertIsNotNone(session_user, "Valid session should return user data")
            self.assertEqual(session_user['username'], 'admin')
            
            print("✓ Valid session validated successfully")
            
            # Test 3: Session validation - expired session
            print("Testing expired session handling...")
            
            mock_cursor.reset_mock()
            # Mock expired session response
            mock_cursor.fetchone.return_value = (
                'test_session_token', 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')  # expired 1 hour ago
            )
            
            session_user = auth_manager.validate_session('test_session_token')
            
            self.assertIsNone(session_user, "Expired session should return None")
            
            print("✓ Expired session properly handled")
            
            # Test 4: Session cleanup
            print("Testing session cleanup...")
            
            mock_cursor.reset_mock()
            auth_manager.cleanup_expired_sessions()
            
            # Should execute DELETE query for expired sessions
            delete_call = any('DELETE FROM sessions' in str(call) for call in mock_cursor.execute.call_args_list)
            self.assertTrue(delete_call, "Should delete expired sessions")
            
            print("✓ Session cleanup executed")
    
    def test_role_based_access_control(self):
        """
        Test role-based access control validation.
        
        This test demonstrates:
        - Permission checking for different roles
        - Hierarchical role permissions
        - Access denied scenarios
        - Special permission handling
        """
        print("\n=== Testing Role-Based Access Control ===")
        
        auth_manager = AuthManager(self.mock_app, self.db_path)
        
        # Define role hierarchy and permissions
        role_permissions = {
            'admin': ['read', 'write', 'delete', 'manage_users', 'system_admin'],
            'manager': ['read', 'write', 'delete', 'manage_service_orders'],
            'driver': ['read', 'write', 'update_service_orders'],
            'viewer': ['read']
        }
        
        # Test 1: Admin role permissions
        print("Testing admin role permissions...")
        
        admin_user = {'role': 'admin', 'username': 'admin'}
        
        for permission in role_permissions['admin']:
            has_permission = auth_manager.check_permission(admin_user, permission)
            self.assertTrue(has_permission, f"Admin should have {permission} permission")
        
        print("✓ Admin has all required permissions")
        
        # Test 2: Manager role permissions
        print("Testing manager role permissions...")
        
        manager_user = {'role': 'manager', 'username': 'manager'}
        
        # Should have manager permissions
        for permission in role_permissions['manager']:
            has_permission = auth_manager.check_permission(manager_user, permission)
            self.assertTrue(has_permission, f"Manager should have {permission} permission")
        
        # Should NOT have admin-only permissions
        admin_only_permissions = ['manage_users', 'system_admin']
        for permission in admin_only_permissions:
            has_permission = auth_manager.check_permission(manager_user, permission)
            self.assertFalse(has_permission, f"Manager should NOT have {permission} permission")
        
        print("✓ Manager has correct permission restrictions")
        
        # Test 3: Driver role permissions
        print("Testing driver role permissions...")
        
        driver_user = {'role': 'driver', 'username': 'driver'}
        
        # Should have driver permissions
        for permission in role_permissions['driver']:
            has_permission = auth_manager.check_permission(driver_user, permission)
            self.assertTrue(has_permission, f"Driver should have {permission} permission")
        
        # Should NOT have management permissions
        restricted_permissions = ['delete', 'manage_users', 'manage_service_orders']
        for permission in restricted_permissions:
            has_permission = auth_manager.check_permission(driver_user, permission)
            self.assertFalse(has_permission, f"Driver should NOT have {permission} permission")
        
        print("✓ Driver has correct permission restrictions")
        
        # Test 4: Viewer role permissions
        print("Testing viewer role permissions...")
        
        viewer_user = {'role': 'viewer', 'username': 'viewer'}
        
        # Should only have read permission
        has_read = auth_manager.check_permission(viewer_user, 'read')
        self.assertTrue(has_read, "Viewer should have read permission")
        
        # Should NOT have write permissions
        write_permissions = ['write', 'delete', 'manage_users', 'update_service_orders']
        for permission in write_permissions:
            has_permission = auth_manager.check_permission(viewer_user, permission)
            self.assertFalse(has_permission, f"Viewer should NOT have {permission} permission")
        
        print("✓ Viewer has correct read-only permissions")
        
        # Test 5: Invalid role handling
        print("Testing invalid role handling...")
        
        invalid_user = {'role': 'invalid_role', 'username': 'test'}
        
        for permission in ['read', 'write', 'delete']:
            has_permission = auth_manager.check_permission(invalid_user, permission)
            self.assertFalse(has_permission, f"Invalid role should not have {permission} permission")
        
        print("✓ Invalid roles properly denied")
    
    def test_authentication_error_handling(self):
        """
        Test error handling in authentication scenarios.
        
        This test demonstrates:
        - Database connection error handling
        - Invalid input handling
        - Rate limiting and brute force protection
        - Logging of authentication attempts
        """
        print("\n=== Testing Authentication Error Handling ===")
        
        # Test 1: Database connection errors
        print("Testing database connection error handling...")
        
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.OperationalError("Database is locked")
            
            auth_manager = AuthManager(self.mock_app, self.db_path)
            
            # Should handle database errors gracefully
            result = auth_manager.authenticate_user('admin', 'admin')
            self.assertIsNone(result, "Should return None when database is unavailable")
            
            print("✓ Database connection errors handled gracefully")
        
        # Test 2: Invalid input handling
        print("Testing invalid input handling...")
        
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            auth_manager = AuthManager(self.mock_app, self.db_path)
            
            # Test various invalid inputs
            invalid_inputs = [
                (None, 'password'),
                ('username', None),
                ('', 'password'),
                ('username', ''),
                (None, None),
                (123, 'password'),  # Non-string username
                ('username', 123)   # Non-string password
            ]
            
            for username, password in invalid_inputs:
                result = auth_manager.authenticate_user(username, password)
                self.assertIsNone(result, f"Should reject invalid input: {username}, {password}")
            
            print("✓ Invalid inputs properly rejected")
        
        # Test 3: Rate limiting simulation
        print("Testing rate limiting protection...")
        
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            auth_manager = AuthManager(self.mock_app, self.db_path)
            
            # Mock user with multiple failed attempts
            mock_cursor.fetchone.return_value = (
                1, 'admin', hash_password('admin'), 'admin', None, 1, 3, None  # 3 failed attempts
            )
            
            # Simulate rate limiting check
            is_rate_limited = auth_manager.check_rate_limit('admin')
            
            if hasattr(auth_manager, 'check_rate_limit'):
                # If rate limiting is implemented
                print("✓ Rate limiting check performed")
            else:
                print("! Rate limiting not implemented (consider adding for production)")
        
        # Test 4: SQL injection protection
        print("Testing SQL injection protection...")
        
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            auth_manager = AuthManager(self.mock_app, self.db_path)
            
            # Try SQL injection attempts
            sql_injection_attempts = [
                "admin'; DROP TABLE users; --",
                "' OR '1'='1' --",
                "admin' UNION SELECT * FROM users --"
            ]
            
            for malicious_input in sql_injection_attempts:
                result = auth_manager.authenticate_user(malicious_input, 'password')
                # Should not cause errors and should not authenticate
                self.assertIsNone(result, f"Should safely handle SQL injection: {malicious_input}")
            
            print("✓ SQL injection attempts safely handled")


class ServiceOrderServiceUnitTests(unittest.TestCase):
    """
    Unit tests for ServiceOrderService component.
    
    These tests demonstrate:
    - Service order creation business logic
    - Cabinet selection validation
    - Status transition logic
    - Pick list generation
    - Service completion workflows
    """
    
    def setUp(self):
        """Set up test environment for service order testing."""
        self.db_path = ':memory:'
        self.service = ServiceOrderService(self.db_path)
        self.init_service_order_test_data()
        
        print("ServiceOrderService unit test setup complete")
    
    def init_service_order_test_data(self):
        """Initialize test data for service order testing."""
        # This would normally set up mock database data
        # For unit tests, we'll mock the database interactions
        pass
    
    def test_service_order_creation_logic(self):
        """
        Test service order creation business logic.
        
        This test focuses on the business logic without database dependencies,
        using mocks to simulate database operations.
        """
        print("\n=== Testing Service Order Creation Logic ===")
        
        # Mock database operations
        with patch.object(self.service, 'get_db_connection') as mock_db:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            # Test 1: Valid service order creation
            print("Testing valid service order creation logic...")
            
            # Mock successful database operations
            mock_cursor.lastrowid = 123  # Mock generated order ID
            mock_cursor.fetchall.return_value = [
                (111, 0, 1),  # device_id, cabinet_index, cabinet_config_id
                (222, 0, 2),
                (222, 1, 3)
            ]
            
            order_data = {
                'route_id': 1,
                'cabinet_selections': [
                    {'deviceId': 111, 'cabinetIndex': 0},
                    {'deviceId': 222, 'cabinetIndex': 0},
                    {'deviceId': 222, 'cabinetIndex': 1}
                ],
                'created_by': 1,
                'notes': 'Test order'
            }
            
            result = self.service.create_service_order(**order_data)
            
            # Verify business logic results
            self.assertIsInstance(result, dict, "Should return dictionary result")
            self.assertIn('id', result, "Should include generated order ID")
            self.assertIn('cabinets', result, "Should include cabinet information")
            
            # Verify database operations were called correctly
            mock_cursor.execute.assert_called()  # Should have executed database queries
            
            print("✓ Service order creation logic executed correctly")
            
            # Test 2: Validation logic
            print("Testing cabinet selection validation...")
            
            # Test invalid cabinet selections
            invalid_selections = [
                [],  # Empty selections
                [{'deviceId': 111}],  # Missing cabinet_index
                [{'cabinetIndex': 0}],  # Missing device_id
                [{'deviceId': 'invalid', 'cabinetIndex': 0}]  # Invalid device_id type
            ]
            
            for invalid_selection in invalid_selections:
                with self.assertRaises((ValueError, TypeError)):
                    self.service.create_service_order(
                        route_id=1,
                        cabinet_selections=invalid_selection,
                        created_by=1
                    )
            
            print("✓ Cabinet selection validation working correctly")
    
    def test_status_transition_logic(self):
        """
        Test service order status transition business logic.
        
        This test verifies:
        - Valid status transitions
        - Invalid transition prevention
        - State validation rules
        - Timestamp management
        """
        print("\n=== Testing Status Transition Logic ===")
        
        with patch.object(self.service, 'get_db_connection') as mock_db:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            # Test 1: Valid status transitions
            print("Testing valid status transitions...")
            
            valid_transitions = [
                ('pending', 'in_progress'),
                ('in_progress', 'completed'),
                ('pending', 'cancelled'),
                ('in_progress', 'cancelled')
            ]
            
            for from_status, to_status in valid_transitions:
                # Mock current order state
                mock_cursor.fetchone.return_value = (123, 1, from_status, None)  # id, route_id, status, completed_at
                
                result = self.service.update_service_order_status(123, to_status)
                
                self.assertTrue(result, f"Should allow transition from {from_status} to {to_status}")
                
                # Verify database update was called
                self.assertTrue(mock_cursor.execute.called, "Should execute database update")
                mock_cursor.reset_mock()
            
            print("✓ Valid status transitions allowed")
            
            # Test 2: Invalid status transitions
            print("Testing invalid status transitions...")
            
            invalid_transitions = [
                ('completed', 'pending'),
                ('completed', 'in_progress'),
                ('cancelled', 'pending'),
                ('cancelled', 'in_progress'),
                ('pending', 'invalid_status')
            ]
            
            for from_status, to_status in invalid_transitions:
                mock_cursor.fetchone.return_value = (123, 1, from_status, None)
                
                with self.assertRaises(ValueError):
                    self.service.update_service_order_status(123, to_status)
            
            print("✓ Invalid status transitions properly rejected")
            
            # Test 3: Completion timestamp logic
            print("Testing completion timestamp logic...")
            
            # Mock order being completed
            mock_cursor.fetchone.return_value = (123, 1, 'in_progress', None)
            
            result = self.service.update_service_order_status(123, 'completed')
            
            # Should set completion timestamp when transitioning to completed
            execute_calls = [str(call) for call in mock_cursor.execute.call_args_list]
            timestamp_update = any('completed_at' in call for call in execute_calls)
            self.assertTrue(timestamp_update, "Should set completion timestamp")
            
            print("✓ Completion timestamp logic working correctly")
    
    def test_pick_list_generation(self):
        """
        Test pick list generation for service orders.
        
        This test demonstrates:
        - Pick list calculation based on par levels
        - Stock level analysis
        - Product prioritization
        - Error handling for missing data
        """
        print("\n=== Testing Pick List Generation ===")
        
        with patch.object(self.service, 'get_db_connection') as mock_db:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            # Test 1: Basic pick list generation
            print("Testing basic pick list generation...")
            
            # Mock cabinet and slot data
            mock_cursor.fetchall.return_value = [
                # cabinet_id, device_name, cabinet_index, product_id, product_name, current_qty, par_level
                (1, 'Cooler A1', 0, 1, 'Coca Cola', 5, 20),
                (1, 'Cooler A1', 0, 2, 'Pepsi Cola', 0, 15),  # Out of stock
                (1, 'Cooler A1', 0, 3, 'Sprite', 10, 12),     # Adequate stock
                (2, 'Cooler B2', 0, 1, 'Coca Cola', 8, 25),   # Below par
            ]
            
            pick_list = self.service.generate_pick_list(123)  # order_id = 123
            
            # Verify pick list structure and logic
            self.assertIsInstance(pick_list, list, "Pick list should be a list")
            
            # Should include items that need restocking
            product_needs = {item['product_id']: item for item in pick_list}
            
            # Product 2 (Pepsi) should need full restock (0 current, 15 par)
            self.assertIn(2, product_needs, "Should include out-of-stock product")
            self.assertEqual(product_needs[2]['quantity_needed'], 15, 
                           "Should need full par level for out-of-stock")
            
            # Product 1 (Coca Cola) should need partial restock
            # Cabinet 1: needs 15 (20 par - 5 current)
            # Cabinet 2: needs 17 (25 par - 8 current)
            coca_cola_total = sum(item['quantity_needed'] for item in pick_list if item['product_id'] == 1)
            self.assertEqual(coca_cola_total, 32, "Should calculate correct total need for Coca Cola")
            
            print("✓ Pick list generation logic working correctly")
            
            # Test 2: Pick list with no items needed
            print("Testing pick list when no items needed...")
            
            # Mock scenario where all products are at or above par
            mock_cursor.fetchall.return_value = [
                (1, 'Cooler A1', 0, 1, 'Coca Cola', 25, 20),  # Above par
                (1, 'Cooler A1', 0, 2, 'Pepsi Cola', 15, 15), # At par
            ]
            
            pick_list_empty = self.service.generate_pick_list(124)
            
            self.assertEqual(len(pick_list_empty), 0, "Pick list should be empty when all products at par")
            
            print("✓ Empty pick list generation handled correctly")
            
            # Test 3: Error handling for missing data
            print("Testing error handling for missing order data...")
            
            # Mock non-existent order
            mock_cursor.fetchall.return_value = []
            
            pick_list_missing = self.service.generate_pick_list(999)
            
            self.assertEqual(len(pick_list_missing), 0, 
                           "Should return empty list for non-existent order")
            
            print("✓ Missing order data handled gracefully")


class PlanogramOptimizerUnitTests(unittest.TestCase):
    """
    Unit tests for PlanogramOptimizer component.
    
    These tests demonstrate:
    - AI integration with fallback behavior
    - Sales data analysis logic
    - Optimization algorithm testing
    - Performance and error handling
    """
    
    def setUp(self):
        """Set up test environment for planogram optimizer testing."""
        self.db_path = ':memory:'
        self.api_key = 'test_api_key'
        self.optimizer = None
        
        print("PlanogramOptimizer unit test setup complete")
    
    def test_sales_data_analysis_logic(self):
        """
        Test sales data analysis business logic.
        
        This test focuses on the mathematical and analytical logic
        without external AI API dependencies.
        """
        print("\n=== Testing Sales Data Analysis Logic ===")
        
        # Initialize optimizer with mocked database
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            optimizer = PlanogramOptimizer(self.api_key, self.db_path)
            
            # Test 1: Sales velocity calculation
            print("Testing sales velocity calculation...")
            
            # Mock sales data for analysis
            mock_sales_data = [
                (1, 'Coca Cola', 45, 30),    # product_id, name, total_sales, days_in_period
                (2, 'Pepsi Cola', 30, 30),
                (3, 'Sprite', 15, 30),
                (7, 'Chips', 60, 30),        # High-velocity snack
                (12, 'Crackers', 5, 30)      # Low-velocity item
            ]
            
            mock_cursor.fetchall.return_value = mock_sales_data
            
            analysis = optimizer.analyze_sales_data(device_id=111, cabinet_index=0, days=30)
            
            # Verify analysis results
            self.assertIsInstance(analysis, dict, "Analysis should return dictionary")
            self.assertIn('products', analysis, "Should include product analysis")
            self.assertIn('insights', analysis, "Should include analytical insights")
            
            products = analysis['products']
            
            # Verify velocity calculations
            coca_cola = next((p for p in products if p['name'] == 'Coca Cola'), None)
            self.assertIsNotNone(coca_cola, "Should include Coca Cola in analysis")
            self.assertEqual(coca_cola['daily_velocity'], 1.5, "Coca Cola velocity should be 45/30 = 1.5")
            
            chips = next((p for p in products if p['name'] == 'Chips'), None)
            self.assertIsNotNone(chips, "Should include Chips in analysis")
            self.assertEqual(chips['daily_velocity'], 2.0, "Chips velocity should be 60/30 = 2.0")
            
            print("✓ Sales velocity calculations correct")
            
            # Test 2: Product ranking logic
            print("Testing product ranking logic...")
            
            # Products should be ranked by velocity (highest first)
            velocities = [p['daily_velocity'] for p in products]
            self.assertEqual(velocities, sorted(velocities, reverse=True),
                           "Products should be sorted by velocity (descending)")
            
            # Highest velocity product should be marked as top performer
            top_product = products[0]
            self.assertEqual(top_product['name'], 'Chips', "Chips should be top performer")
            
            print("✓ Product ranking logic correct")
    
    def test_ai_integration_with_fallback(self):
        """
        Test AI integration with proper fallback behavior.
        
        This test demonstrates:
        - Successful AI API integration
        - Graceful fallback when AI is unavailable
        - Response validation and error handling
        """
        print("\n=== Testing AI Integration with Fallback ===")
        
        # Test 1: Successful AI integration
        print("Testing successful AI API integration...")
        
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            # Mock sales data
            mock_cursor.fetchall.return_value = [
                (1, 'Coca Cola', 45, 30),
                (2, 'Pepsi Cola', 30, 30),
            ]
            
            # Mock successful AI API response
            with patch('planogram_optimizer.anthropic.Anthropic') as mock_anthropic:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.content = [Mock()]
                mock_response.content[0].text = json.dumps({
                    "recommendations": [
                        {"slot": "A1", "product_id": 1, "confidence": 0.9, "reasoning": "High velocity"},
                        {"slot": "A2", "product_id": 2, "confidence": 0.8, "reasoning": "Good performer"}
                    ],
                    "overall_reasoning": "Optimized for sales velocity"
                })
                
                mock_client.messages.create.return_value = mock_response
                mock_anthropic.return_value = mock_client
                
                optimizer = PlanogramOptimizer(self.api_key, self.db_path)
                result = optimizer.optimize_planogram(device_id=111, cabinet_index=0)
                
                # Verify AI integration
                self.assertIn('recommendations', result, "Should include AI recommendations")
                self.assertIn('reasoning', result, "Should include AI reasoning")
                self.assertFalse(result.get('fallback', True), "Should not be fallback mode")
                
                # Verify recommendations structure
                recommendations = result['recommendations']
                self.assertEqual(len(recommendations), 2, "Should have 2 recommendations")
                
                for rec in recommendations:
                    self.assertIn('slot', rec, "Recommendation should include slot")
                    self.assertIn('product_id', rec, "Recommendation should include product_id")
                    self.assertIn('confidence', rec, "Recommendation should include confidence")
                    self.assertGreaterEqual(rec['confidence'], 0.0, "Confidence should be >= 0")
                    self.assertLessEqual(rec['confidence'], 1.0, "Confidence should be <= 1")
                
                print("✓ AI API integration working correctly")
        
        # Test 2: AI API failure with fallback
        print("Testing AI API failure with fallback...")
        
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            # Mock sales data
            mock_cursor.fetchall.return_value = [
                (1, 'Coca Cola', 45, 30),
                (2, 'Pepsi Cola', 30, 30),
                (3, 'Sprite', 15, 30)
            ]
            
            # Mock AI API failure
            with patch('planogram_optimizer.anthropic.Anthropic') as mock_anthropic:
                mock_client = Mock()
                mock_client.messages.create.side_effect = Exception("API Error")
                mock_anthropic.return_value = mock_client
                
                optimizer = PlanogramOptimizer(self.api_key, self.db_path)
                result = optimizer.optimize_planogram(device_id=111, cabinet_index=0)
                
                # Verify fallback behavior
                self.assertIn('recommendations', result, "Should include fallback recommendations")
                self.assertTrue(result.get('fallback', False), "Should be in fallback mode")
                self.assertIn('reason', result, "Should explain fallback reason")
                
                # Fallback recommendations should be based on sales velocity
                recommendations = result['recommendations']
                self.assertGreater(len(recommendations), 0, "Should have fallback recommendations")
                
                # Should prioritize high-velocity products
                first_rec = recommendations[0]
                self.assertEqual(first_rec['product_id'], 1, "Should recommend highest velocity product first")
                
                print("✓ AI API fallback working correctly")
        
        # Test 3: No API key fallback
        print("Testing no API key fallback...")
        
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            # Mock sales data
            mock_cursor.fetchall.return_value = [
                (7, 'Chips', 60, 30),        # Highest velocity
                (1, 'Coca Cola', 45, 30),
                (2, 'Pepsi Cola', 30, 30)
            ]
            
            optimizer = PlanogramOptimizer(api_key=None, db_path=self.db_path)  # No API key
            result = optimizer.optimize_planogram(device_id=111, cabinet_index=0)
            
            # Should use rule-based optimization
            self.assertTrue(result.get('fallback', False), "Should be in fallback mode")
            self.assertIn('rule_based', result.get('reason', '').lower(), 
                         "Should explain rule-based fallback")
            
            # Should recommend highest velocity product first
            recommendations = result['recommendations']
            first_rec = recommendations[0]
            self.assertEqual(first_rec['product_id'], 7, "Should recommend Chips (highest velocity) first")
            
            print("✓ No API key fallback working correctly")
    
    def test_optimization_algorithm_logic(self):
        """
        Test the core optimization algorithm logic.
        
        This test focuses on the mathematical optimization logic
        independent of AI or external services.
        """
        print("\n=== Testing Optimization Algorithm Logic ===")
        
        with patch('sqlite3.connect') as mock_connect:
            mock_db = Mock()
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_db
            
            optimizer = PlanogramOptimizer(api_key=None, db_path=self.db_path)
            
            # Test 1: Velocity-based slot assignment
            print("Testing velocity-based slot assignment...")
            
            # Mock diverse product performance data
            products = [
                {'id': 1, 'name': 'Coca Cola', 'velocity': 2.5, 'margin': 0.40},
                {'id': 7, 'name': 'Chips', 'velocity': 3.0, 'margin': 0.60},      # Best overall
                {'id': 2, 'name': 'Pepsi Cola', 'velocity': 2.0, 'margin': 0.40},
                {'id': 12, 'name': 'Crackers', 'velocity': 0.5, 'margin': 0.50},   # Low velocity
                {'id': 9, 'name': 'Candy Bar', 'velocity': 1.5, 'margin': 0.80}    # High margin
            ]
            
            # Mock cabinet configuration (5x8 = 40 slots)
            cabinet_config = {'rows': 5, 'columns': 8, 'total_slots': 40}
            
            assignments = optimizer.calculate_optimal_assignments(products, cabinet_config)
            
            # Verify assignment logic
            self.assertIsInstance(assignments, list, "Assignments should be a list")
            self.assertLessEqual(len(assignments), 40, "Should not exceed cabinet capacity")
            
            # Prime slots (eye level, easy access) should get best products
            prime_slots = ['A1', 'A2', 'B1', 'B2']  # Assuming standard slot naming
            
            prime_assignments = [a for a in assignments if a['slot'] in prime_slots]
            if prime_assignments:
                # Check that high-velocity products get prime positions
                prime_products = [a['product_id'] for a in prime_assignments]
                self.assertIn(7, prime_products, "Chips (highest velocity) should get prime slot")
            
            print("✓ Velocity-based slot assignment logic correct")
            
            # Test 2: Capacity and space utilization
            print("Testing capacity and space utilization...")
            
            # All assignments should have valid slot positions
            for assignment in assignments:
                self.assertIn('slot', assignment, "Assignment should specify slot")
                self.assertIn('product_id', assignment, "Assignment should specify product")
                self.assertIn('quantity', assignment, "Assignment should specify quantity")
                self.assertGreater(assignment['quantity'], 0, "Quantity should be positive")
            
            # Should not assign same slot to multiple products
            assigned_slots = [a['slot'] for a in assignments]
            unique_slots = set(assigned_slots)
            self.assertEqual(len(assigned_slots), len(unique_slots), 
                           "Each slot should be assigned to only one product")
            
            print("✓ Capacity and space utilization logic correct")
            
            # Test 3: Profit optimization logic
            print("Testing profit optimization logic...")
            
            # Calculate expected profit for assignments
            total_expected_profit = 0
            for assignment in assignments:
                product = next(p for p in products if p['id'] == assignment['product_id'])
                expected_daily_sales = product['velocity'] * assignment['quantity']
                expected_profit = expected_daily_sales * product['margin']
                total_expected_profit += expected_profit
            
            self.assertGreater(total_expected_profit, 0, "Should generate positive expected profit")
            
            # High-margin products should get reasonable representation
            high_margin_products = [p['id'] for p in products if p['margin'] > 0.5]
            assigned_products = [a['product_id'] for a in assignments]
            
            high_margin_assigned = any(pid in assigned_products for pid in high_margin_products)
            self.assertTrue(high_margin_assigned, "Should assign some high-margin products")
            
            print("✓ Profit optimization logic working correctly")


if __name__ == '__main__':
    """
    Run the component unit testing examples.
    
    Usage:
    python COMPONENT_UNIT_TESTS.py                    # Run all unit tests
    python -m pytest COMPONENT_UNIT_TESTS.py         # Run with pytest
    python -m pytest COMPONENT_UNIT_TESTS.py::AuthManagerUnitTests::test_password_hashing_and_verification -v
    """
    
    print("="*80)
    print("CVD COMPONENT UNIT TESTING EXAMPLES")
    print("="*80)
    print()
    print("This module demonstrates comprehensive unit testing patterns for:")
    print("• AuthManager - Password hashing, authentication, session management")
    print("• ServiceOrderService - Business logic, validation, state transitions")
    print("• PlanogramOptimizer - AI integration, fallback behavior, optimization logic")
    print()
    print("Key testing concepts demonstrated:")
    print("• Isolated component testing with mocked dependencies")
    print("• Edge case and boundary condition testing")
    print("• Error handling and graceful degradation")
    print("• Business logic validation independent of external services")
    print("• Mock usage patterns for database and API interactions")
    print()
    print("Running tests with detailed output...")
    print("="*80)
    
    # Run tests with high verbosity
    unittest.main(verbosity=2, exit=False)
    
    print("="*80)
    print("COMPONENT UNIT TESTING EXAMPLES COMPLETED")
    print("="*80)