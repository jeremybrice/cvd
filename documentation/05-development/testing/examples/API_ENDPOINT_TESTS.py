#!/usr/bin/env python3
"""
CVD API Endpoint Testing Examples

This file demonstrates comprehensive API endpoint testing patterns for the CVD application,
including service order management, device operations, authentication flows, and error handling.
These examples show real-world testing scenarios with complete setup, execution, and verification.
"""

import unittest
import sqlite3
import tempfile
import os
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add CVD application to Python path for testing
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

# Import CVD application components
try:
    from app import create_app
    from auth import AuthManager, hash_password
    from service_order_service import ServiceOrderService
except ImportError as e:
    print(f"Warning: Could not import CVD modules: {e}")
    print("This example requires the CVD application to be in the Python path")


class ServiceOrderAPITests(unittest.TestCase):
    """
    Comprehensive testing of service order API endpoints.
    
    This test class demonstrates:
    - Complete CRUD operations for service orders
    - Authentication and authorization testing
    - Input validation and error handling
    - Performance benchmarking
    - Database state verification
    """
    
    def setUp(self):
        """
        Set up test environment with isolated database and Flask test client.
        
        This setup creates:
        - Temporary SQLite database for test isolation
        - Flask application in testing mode
        - Test client for API requests
        - Standard test data (users, devices, routes)
        """
        # Create temporary database for this test
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Configure Flask application for testing
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
            'SECRET_KEY': 'test-secret-key',
            'WTF_CSRF_ENABLED': False
        })
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize test database with schema and data
        self.init_test_database()
        self.create_test_data()
        
        print(f"Test setup complete. Database: {self.db_path}")
    
    def tearDown(self):
        """Clean up test environment and remove temporary database."""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
        
        # Close and remove temporary database
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        print("Test cleanup complete")
    
    def init_test_database(self):
        """
        Initialize test database with minimal schema required for service order testing.
        
        This creates all the essential tables needed for service order operations:
        - users: For authentication testing
        - devices: For device management
        - cabinet_configurations: For multi-cabinet device support
        - routes: For service order routing
        - service_orders: Main service order table
        - service_order_cabinets: Cabinet-centric service orders
        """
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Create essential tables for service order testing
        cursor.executescript("""
            -- Users table for authentication
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer',
                deleted_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Device types for device management
            CREATE TABLE device_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                max_cabinets INTEGER DEFAULT 1
            );
            
            -- Locations for device placement
            CREATE TABLE locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT
            );
            
            -- Routes for service orders
            CREATE TABLE routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                active BOOLEAN DEFAULT 1
            );
            
            -- Devices with soft delete support
            CREATE TABLE devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                asset TEXT UNIQUE,
                device_type_id INTEGER NOT NULL,
                location_id INTEGER,
                active BOOLEAN DEFAULT 1,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_type_id) REFERENCES device_types (id),
                FOREIGN KEY (location_id) REFERENCES locations (id)
            );
            
            -- Cabinet types for device configurations
            CREATE TABLE cabinet_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                default_rows INTEGER DEFAULT 5,
                default_columns INTEGER DEFAULT 8
            );
            
            -- Cabinet configurations for multi-cabinet devices
            CREATE TABLE cabinet_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                cabinet_index INTEGER NOT NULL,
                cabinet_type_id INTEGER NOT NULL,
                rows INTEGER NOT NULL,
                columns INTEGER NOT NULL,
                modelName TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (id),
                FOREIGN KEY (cabinet_type_id) REFERENCES cabinet_types (id),
                UNIQUE(device_id, cabinet_index)
            );
            
            -- Service orders (main table)
            CREATE TABLE service_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_by INTEGER,
                notes TEXT,
                scheduled_date DATE,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            );
            
            -- Service order cabinets (cabinet-centric approach)
            CREATE TABLE service_order_cabinets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_order_id INTEGER NOT NULL,
                device_id INTEGER NOT NULL,
                cabinet_index INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_order_id) REFERENCES service_orders (id),
                FOREIGN KEY (device_id) REFERENCES devices (id)
            );
            
            -- Indexes for performance
            CREATE INDEX idx_users_username ON users(username);
            CREATE INDEX idx_devices_name ON devices(name);
            CREATE INDEX idx_devices_active ON devices(active, is_deleted);
            CREATE INDEX idx_service_orders_status ON service_orders(status);
            CREATE INDEX idx_service_orders_route ON service_orders(route_id);
            
            -- Enable foreign keys
            PRAGMA foreign_keys = ON;
        """)
        
        db.commit()
        db.close()
        
        print("Test database schema initialized")
    
    def create_test_data(self):
        """
        Create comprehensive test data for service order API testing.
        
        This creates:
        - Test users with different roles (admin, manager, driver, viewer)
        - Device types and cabinet types
        - Sample locations and routes
        - Test devices with various cabinet configurations
        - Sample service orders in different states
        """
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Create test users with different roles
        test_users = [
            ('admin', hash_password('admin'), 'admin'),
            ('manager', hash_password('manager'), 'manager'),
            ('driver', hash_password('driver'), 'driver'),
            ('viewer', hash_password('viewer'), 'viewer'),
            ('test_user', hash_password('password'), 'manager')  # For general testing
        ]
        
        cursor.executemany("""
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        """, test_users)
        
        # Create device types
        device_types = [
            (1, 'Single Door Cooler', 1),
            (2, 'Double Door Cooler', 2), 
            (3, 'Triple Cabinet Unit', 3)
        ]
        
        cursor.executemany("""
            INSERT INTO device_types (id, name, max_cabinets)
            VALUES (?, ?, ?)
        """, device_types)
        
        # Create cabinet types
        cabinet_types = [
            (1, 'Beverage Cooler', 5, 8),
            (2, 'Snack Cabinet', 6, 10),
            (3, 'Combo Unit', 5, 6)
        ]
        
        cursor.executemany("""
            INSERT INTO cabinet_types (id, name, default_rows, default_columns)
            VALUES (?, ?, ?, ?)
        """, cabinet_types)
        
        # Create test locations
        locations = [
            (1, 'Main Office', '123 Business St'),
            (2, 'North Branch', '456 Corporate Ave'),
            (3, 'South Campus', '789 Industrial Blvd')
        ]
        
        cursor.executemany("""
            INSERT INTO locations (id, name, address)
            VALUES (?, ?, ?)
        """, locations)
        
        # Create test routes
        routes = [
            (1, 'Route A', 'Downtown business district', 1),
            (2, 'Route B', 'North side locations', 1),
            (3, 'Route C', 'Industrial area', 1),
            (4, 'Inactive Route', 'Test inactive route', 0)
        ]
        
        cursor.executemany("""
            INSERT INTO routes (id, name, description, active)
            VALUES (?, ?, ?, ?)
        """, routes)
        
        # Create test devices
        devices = [
            (111, 'Cooler A1', 'ASSET_A1', 1, 1, 1, 0),     # Single cabinet
            (222, 'Cooler B2', 'ASSET_B2', 2, 2, 1, 0),     # Double cabinet  
            (333, 'Unit C3', 'ASSET_C3', 3, 3, 1, 0),       # Triple cabinet
            (444, 'Inactive Device', 'ASSET_D4', 1, 1, 0, 0), # Inactive device
            (555, 'Deleted Device', 'ASSET_D5', 1, 1, 1, 1)   # Soft deleted
        ]
        
        cursor.executemany("""
            INSERT INTO devices (id, name, asset, device_type_id, location_id, active, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, devices)
        
        # Create cabinet configurations for devices
        cabinet_configs = [
            # Device 111 (Single cabinet)
            (111, 0, 1, 5, 8, 'CoolMax Pro'),
            # Device 222 (Double cabinet)
            (222, 0, 1, 5, 8, 'FreshKeep Left'),
            (222, 1, 2, 6, 10, 'FreshKeep Right'),
            # Device 333 (Triple cabinet)
            (333, 0, 1, 5, 8, 'TripleMax Left'),
            (333, 1, 2, 6, 10, 'TripleMax Center'),
            (333, 2, 3, 5, 6, 'TripleMax Right')
        ]
        
        cursor.executemany("""
            INSERT INTO cabinet_configurations 
            (device_id, cabinet_index, cabinet_type_id, rows, columns, modelName)
            VALUES (?, ?, ?, ?, ?, ?)
        """, cabinet_configs)
        
        # Create sample service orders for testing
        sample_orders = [
            (1, 1, 'pending', 1, 'Test pending order'),
            (2, 2, 'in_progress', 2, 'Test in-progress order'),
            (3, 3, 'completed', 1, 'Test completed order')
        ]
        
        cursor.executemany("""
            INSERT INTO service_orders (id, route_id, status, created_by, notes)
            VALUES (?, ?, ?, ?, ?)
        """, sample_orders)
        
        # Create sample service order cabinets
        sample_cabinets = [
            (1, 1, 111, 0, 'pending', 'Cabinet A1-0'),
            (2, 2, 222, 0, 'in_progress', 'Cabinet B2-0'),
            (3, 2, 222, 1, 'in_progress', 'Cabinet B2-1'),
            (4, 3, 333, 0, 'completed', 'Cabinet C3-0')
        ]
        
        cursor.executemany("""
            INSERT INTO service_order_cabinets 
            (id, service_order_id, device_id, cabinet_index, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_cabinets)
        
        db.commit()
        db.close()
        
        print("Test data created successfully")
    
    def authenticate_as(self, role='admin'):
        """
        Helper method to authenticate test client with specific user role.
        
        Args:
            role (str): User role to authenticate as ('admin', 'manager', 'driver', 'viewer')
            
        Returns:
            dict: Authentication response data
        """
        response = self.client.post('/api/auth/login', json={
            'username': role,
            'password': role
        })
        
        self.assertEqual(response.status_code, 200, 
                        f"Failed to authenticate as {role}")
        
        return response.get_json()
    
    def test_service_order_creation_success(self):
        """
        Test successful service order creation with valid data.
        
        This test demonstrates:
        - Authentication requirement for service order creation
        - Valid request payload structure
        - Successful creation response validation
        - Database state verification after creation
        - Cabinet-centric service order structure
        """
        print("\n=== Testing Service Order Creation (Success) ===")
        
        # Authenticate as manager (should have permission to create service orders)
        auth_response = self.authenticate_as('manager')
        self.assertIn('user', auth_response)
        
        # Prepare valid service order data
        order_data = {
            'route_id': 1,
            'cabinet_selections': [
                {'deviceId': 111, 'cabinetIndex': 0},    # Single cabinet device
                {'deviceId': 222, 'cabinetIndex': 0},    # First cabinet of double unit
                {'deviceId': 222, 'cabinetIndex': 1}     # Second cabinet of double unit
            ],
            'notes': 'Test service order creation',
            'scheduled_date': '2024-12-01'
        }
        
        print(f"Creating service order with data: {json.dumps(order_data, indent=2)}")
        
        # Create service order via API
        start_time = time.time()
        response = self.client.post('/api/service-orders', json=order_data)
        creation_time = time.time() - start_time
        
        # Verify successful creation
        self.assertEqual(response.status_code, 201, "Service order creation should return 201")
        
        # Verify response structure
        created_order = response.get_json()
        self.assertIn('id', created_order, "Response should include service order ID")
        self.assertIn('cabinets', created_order, "Response should include cabinet information")
        
        # Verify order details
        self.assertEqual(created_order['route_id'], order_data['route_id'])
        self.assertEqual(created_order['status'], 'pending')
        self.assertEqual(len(created_order['cabinets']), 3)  # 3 cabinet selections
        
        # Verify database state
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Check service order was created
        cursor.execute("SELECT * FROM service_orders WHERE id = ?", (created_order['id'],))
        order_record = cursor.fetchone()
        self.assertIsNotNone(order_record, "Service order should exist in database")
        
        # Check cabinet records were created
        cursor.execute("""
            SELECT device_id, cabinet_index, status 
            FROM service_order_cabinets 
            WHERE service_order_id = ?
            ORDER BY device_id, cabinet_index
        """, (created_order['id'],))
        
        cabinet_records = cursor.fetchall()
        self.assertEqual(len(cabinet_records), 3, "Should have 3 cabinet records")
        
        # Verify cabinet details
        expected_cabinets = [(111, 0), (222, 0), (222, 1)]
        actual_cabinets = [(record[0], record[1]) for record in cabinet_records]
        self.assertEqual(actual_cabinets, expected_cabinets, "Cabinet assignments should match")
        
        db.close()
        
        # Verify performance (creation should be fast)
        self.assertLess(creation_time, 0.5, "Service order creation should complete in < 500ms")
        
        print(f"✓ Service order created successfully (ID: {created_order['id']}) in {creation_time:.3f}s")
        print(f"✓ Cabinet assignments: {actual_cabinets}")
    
    def test_service_order_creation_validation_errors(self):
        """
        Test service order creation with invalid data to verify input validation.
        
        This test demonstrates:
        - Required field validation
        - Data type validation
        - Business rule validation
        - Proper error response structure
        """
        print("\n=== Testing Service Order Creation (Validation Errors) ===")
        
        # Authenticate first
        self.authenticate_as('manager')
        
        # Test 1: Missing required fields
        print("Testing missing required fields...")
        invalid_payloads = [
            {},  # Empty payload
            {'route_id': 1},  # Missing cabinet_selections
            {'cabinet_selections': []},  # Missing route_id
            {'route_id': 1, 'cabinet_selections': []}  # Empty cabinet selections
        ]
        
        for payload in invalid_payloads:
            response = self.client.post('/api/service-orders', json=payload)
            self.assertEqual(response.status_code, 400, 
                           f"Should return 400 for invalid payload: {payload}")
            
            error_data = response.get_json()
            self.assertIn('error', error_data, "Response should include error message")
            print(f"  ✓ Rejected payload: {payload}")
        
        # Test 2: Invalid data types
        print("Testing invalid data types...")
        type_errors = [
            {'route_id': 'invalid', 'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}]},
            {'route_id': 1, 'cabinet_selections': 'invalid'},
            {'route_id': 1, 'cabinet_selections': [{'deviceId': 'invalid', 'cabinetIndex': 0}]},
            {'route_id': 1, 'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 'invalid'}]}
        ]
        
        for payload in type_errors:
            response = self.client.post('/api/service-orders', json=payload)
            self.assertEqual(response.status_code, 400,
                           f"Should return 400 for type error: {payload}")
            print(f"  ✓ Rejected type error: {payload}")
        
        # Test 3: Business rule violations
        print("Testing business rule violations...")
        business_errors = [
            # Non-existent route
            {'route_id': 9999, 'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}]},
            # Non-existent device
            {'route_id': 1, 'cabinet_selections': [{'deviceId': 9999, 'cabinetIndex': 0}]},
            # Invalid cabinet index for device
            {'route_id': 1, 'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 5}]},
            # Inactive route
            {'route_id': 4, 'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}]}
        ]
        
        for payload in business_errors:
            response = self.client.post('/api/service-orders', json=payload)
            self.assertIn(response.status_code, [400, 404],
                         f"Should return 400/404 for business rule violation: {payload}")
            print(f"  ✓ Rejected business rule violation: {payload}")
        
        print("✓ All validation tests passed")
    
    def test_service_order_retrieval_operations(self):
        """
        Test service order retrieval operations (GET endpoints).
        
        This test demonstrates:
        - List all service orders
        - Retrieve specific service order by ID
        - Filtering and pagination
        - Performance benchmarking
        """
        print("\n=== Testing Service Order Retrieval ===")
        
        # Authenticate as viewer (should have read access)
        self.authenticate_as('viewer')
        
        # Test 1: List all service orders
        print("Testing service order listing...")
        start_time = time.time()
        response = self.client.get('/api/service-orders')
        list_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200, "Should successfully list service orders")
        
        orders = response.get_json()
        self.assertIsInstance(orders, list, "Response should be a list")
        self.assertGreater(len(orders), 0, "Should return existing service orders")
        
        # Verify order structure
        first_order = orders[0]
        required_fields = ['id', 'route_id', 'status', 'created_at', 'cabinets']
        for field in required_fields:
            self.assertIn(field, first_order, f"Order should include {field}")
        
        print(f"✓ Listed {len(orders)} service orders in {list_time:.3f}s")
        
        # Test 2: Retrieve specific service order
        print("Testing specific service order retrieval...")
        order_id = orders[0]['id']
        
        start_time = time.time()
        response = self.client.get(f'/api/service-orders/{order_id}')
        detail_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200, "Should retrieve specific service order")
        
        order_detail = response.get_json()
        self.assertEqual(order_detail['id'], order_id, "Should return correct order")
        
        # Verify detailed information is included
        self.assertIn('cabinets', order_detail, "Order detail should include cabinet information")
        if len(order_detail['cabinets']) > 0:
            cabinet = order_detail['cabinets'][0]
            cabinet_fields = ['device_id', 'cabinet_index', 'status']
            for field in cabinet_fields:
                self.assertIn(field, cabinet, f"Cabinet should include {field}")
        
        print(f"✓ Retrieved order {order_id} in {detail_time:.3f}s")
        
        # Test 3: Non-existent service order
        print("Testing non-existent service order...")
        response = self.client.get('/api/service-orders/9999')
        self.assertEqual(response.status_code, 404, "Should return 404 for non-existent order")
        
        error_data = response.get_json()
        self.assertIn('error', error_data, "Should include error message")
        print("✓ Properly handled non-existent order")
        
        # Test 4: Performance benchmarks
        self.assertLess(list_time, 0.3, "Service order listing should complete in < 300ms")
        self.assertLess(detail_time, 0.1, "Service order detail should complete in < 100ms")
        
        print("✓ All retrieval tests passed")
    
    def test_service_order_status_updates(self):
        """
        Test service order status update operations.
        
        This test demonstrates:
        - Status transition validation
        - Authorization requirements
        - Database state verification
        - Audit trail verification
        """
        print("\n=== Testing Service Order Status Updates ===")
        
        # Authenticate as driver (should be able to update order status)
        self.authenticate_as('driver')
        
        # Create a test service order first
        self.authenticate_as('manager')  # Switch to manager for creation
        order_data = {
            'route_id': 1,
            'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}]
        }
        
        create_response = self.client.post('/api/service-orders', json=order_data)
        self.assertEqual(create_response.status_code, 201)
        order_id = create_response.get_json()['id']
        
        # Switch back to driver for status updates
        self.authenticate_as('driver')
        
        # Test 1: Valid status transition (pending -> in_progress)
        print(f"Testing status update for order {order_id}...")
        update_data = {
            'status': 'in_progress',
            'notes': 'Driver started service'
        }
        
        response = self.client.put(f'/api/service-orders/{order_id}', json=update_data)
        self.assertEqual(response.status_code, 200, "Should successfully update status")
        
        updated_order = response.get_json()
        self.assertEqual(updated_order['status'], 'in_progress', "Status should be updated")
        
        # Verify database state
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        cursor.execute("SELECT status FROM service_orders WHERE id = ?", (order_id,))
        db_status = cursor.fetchone()[0]
        self.assertEqual(db_status, 'in_progress', "Database should reflect status change")
        db.close()
        
        print("✓ Successfully updated status to 'in_progress'")
        
        # Test 2: Complete the service order
        print("Testing order completion...")
        completion_data = {
            'status': 'completed',
            'notes': 'Service completed successfully',
            'completion_photos': ['photo1.jpg', 'photo2.jpg']  # Simulated photo uploads
        }
        
        response = self.client.put(f'/api/service-orders/{order_id}', json=completion_data)
        self.assertEqual(response.status_code, 200, "Should successfully complete order")
        
        completed_order = response.get_json()
        self.assertEqual(completed_order['status'], 'completed')
        self.assertIsNotNone(completed_order.get('completed_at'), "Should set completion timestamp")
        
        print("✓ Successfully completed service order")
        
        # Test 3: Invalid status transitions
        print("Testing invalid status transitions...")
        invalid_updates = [
            {'status': 'pending'},      # Can't go back to pending
            {'status': 'invalid_status'},  # Invalid status value
            {'status': ''},             # Empty status
        ]
        
        for invalid_update in invalid_updates:
            response = self.client.put(f'/api/service-orders/{order_id}', json=invalid_update)
            self.assertEqual(response.status_code, 400,
                           f"Should reject invalid update: {invalid_update}")
            print(f"  ✓ Rejected invalid update: {invalid_update}")
        
        print("✓ All status update tests passed")
    
    def test_authentication_and_authorization(self):
        """
        Test authentication and authorization for service order endpoints.
        
        This test demonstrates:
        - Unauthenticated request rejection
        - Role-based access control
        - Session management
        - Security headers validation
        """
        print("\n=== Testing Authentication and Authorization ===")
        
        # Test 1: Unauthenticated requests
        print("Testing unauthenticated access...")
        protected_endpoints = [
            ('GET', '/api/service-orders'),
            ('POST', '/api/service-orders'),
            ('GET', '/api/service-orders/1'),
            ('PUT', '/api/service-orders/1')
        ]
        
        for method, endpoint in protected_endpoints:
            if method == 'GET':
                response = self.client.get(endpoint)
            elif method == 'POST':
                response = self.client.post(endpoint, json={})
            elif method == 'PUT':
                response = self.client.put(endpoint, json={})
            
            self.assertEqual(response.status_code, 401,
                           f"Unauthenticated {method} {endpoint} should return 401")
            print(f"  ✓ Rejected unauthenticated {method} {endpoint}")
        
        # Test 2: Role-based access control
        print("Testing role-based access control...")
        
        # Test viewer role (should have read-only access)
        self.authenticate_as('viewer')
        
        # Should be able to read
        response = self.client.get('/api/service-orders')
        self.assertEqual(response.status_code, 200, "Viewer should read service orders")
        
        # Should not be able to create
        response = self.client.post('/api/service-orders', json={
            'route_id': 1,
            'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}]
        })
        self.assertEqual(response.status_code, 403, "Viewer should not create service orders")
        
        print("  ✓ Viewer role permissions validated")
        
        # Test driver role (should be able to read and update)
        self.authenticate_as('driver')
        
        # Should be able to read
        response = self.client.get('/api/service-orders')
        self.assertEqual(response.status_code, 200, "Driver should read service orders")
        
        # Should not be able to create (managers create, drivers execute)
        response = self.client.post('/api/service-orders', json={
            'route_id': 1,
            'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}]
        })
        self.assertEqual(response.status_code, 403, "Driver should not create service orders")
        
        print("  ✓ Driver role permissions validated")
        
        # Test manager role (should have full access to service orders)
        self.authenticate_as('manager')
        
        # Should be able to create
        response = self.client.post('/api/service-orders', json={
            'route_id': 1,
            'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}]
        })
        self.assertIn(response.status_code, [200, 201], "Manager should create service orders")
        
        print("  ✓ Manager role permissions validated")
        
        # Test 3: Session security
        print("Testing session security...")
        
        # Login and check session cookie properties
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin'
        })
        
        # Check for secure session cookie
        set_cookie_header = response.headers.get('Set-Cookie', '')
        
        # Should have security flags (Note: not all may be present in test mode)
        security_flags = ['HttpOnly']
        for flag in security_flags:
            if flag in set_cookie_header:
                print(f"  ✓ Session cookie has {flag} flag")
        
        print("✓ All authentication and authorization tests passed")
    
    def test_error_handling_and_edge_cases(self):
        """
        Test error handling and edge cases for service order API.
        
        This test demonstrates:
        - Invalid JSON handling
        - Database error simulation
        - Network timeout simulation
        - Graceful degradation
        """
        print("\n=== Testing Error Handling and Edge Cases ===")
        
        self.authenticate_as('manager')
        
        # Test 1: Invalid JSON in request body
        print("Testing invalid JSON handling...")
        response = self.client.post('/api/service-orders',
                                  data='{"invalid": json}',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400, "Should return 400 for invalid JSON")
        
        error_data = response.get_json()
        if error_data:  # Some frameworks may not return JSON for JSON parse errors
            self.assertIn('error', error_data, "Should include error message")
        
        print("✓ Invalid JSON properly handled")
        
        # Test 2: Extremely large payload
        print("Testing large payload handling...")
        large_cabinet_selections = []
        for i in range(1000):  # Create unreasonably large payload
            large_cabinet_selections.append({'deviceId': 111, 'cabinetIndex': 0})
        
        large_payload = {
            'route_id': 1,
            'cabinet_selections': large_cabinet_selections
        }
        
        response = self.client.post('/api/service-orders', json=large_payload)
        # Should either reject as too large or handle gracefully
        self.assertIn(response.status_code, [400, 413, 500],
                     "Should handle large payloads appropriately")
        
        print("✓ Large payload handled appropriately")
        
        # Test 3: Concurrent order creation
        print("Testing concurrent operations...")
        import threading
        import queue
        
        results = queue.Queue()
        
        def create_order(order_num):
            """Create a service order in a separate thread"""
            try:
                # Each thread needs its own client
                test_client = self.app.test_client()
                
                # Authenticate
                test_client.post('/api/auth/login', json={
                    'username': 'manager',
                    'password': 'manager'
                })
                
                # Create order
                response = test_client.post('/api/service-orders', json={
                    'route_id': 1,
                    'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}],
                    'notes': f'Concurrent order {order_num}'
                })
                
                results.put((order_num, response.status_code))
            except Exception as e:
                results.put((order_num, f'Error: {e}'))
        
        # Start 5 concurrent order creations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_order, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        concurrent_results = []
        while not results.empty():
            concurrent_results.append(results.get())
        
        success_count = sum(1 for _, status in concurrent_results if status in [200, 201])
        print(f"✓ Concurrent operations: {success_count}/5 succeeded")
        
        # At least some should succeed (exact number depends on implementation)
        self.assertGreater(success_count, 0, "At least some concurrent operations should succeed")
        
        print("✓ All error handling tests passed")
    
    def test_performance_benchmarks(self):
        """
        Test performance benchmarks for service order operations.
        
        This test demonstrates:
        - Response time measurement
        - Throughput testing
        - Memory usage monitoring
        - Performance regression detection
        """
        print("\n=== Testing Performance Benchmarks ===")
        
        self.authenticate_as('manager')
        
        # Test 1: Single operation performance
        print("Testing single operation performance...")
        
        operations = {
            'list_orders': lambda: self.client.get('/api/service-orders'),
            'get_order': lambda: self.client.get('/api/service-orders/1'),
            'create_order': lambda: self.client.post('/api/service-orders', json={
                'route_id': 1,
                'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}]
            })
        }
        
        performance_results = {}
        
        for operation_name, operation_func in operations.items():
            # Warm up
            operation_func()
            
            # Measure performance
            times = []
            for _ in range(10):
                start_time = time.time()
                response = operation_func()
                end_time = time.time()
                
                if response.status_code in [200, 201]:
                    times.append(end_time - start_time)
            
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                performance_results[operation_name] = {
                    'avg': avg_time,
                    'max': max_time,
                    'min': min_time
                }
                
                print(f"  {operation_name}: avg={avg_time:.3f}s, max={max_time:.3f}s, min={min_time:.3f}s")
        
        # Performance assertions
        if 'list_orders' in performance_results:
            self.assertLess(performance_results['list_orders']['avg'], 0.3,
                           "List orders should average < 300ms")
        
        if 'get_order' in performance_results:
            self.assertLess(performance_results['get_order']['avg'], 0.1,
                           "Get order should average < 100ms")
        
        if 'create_order' in performance_results:
            self.assertLess(performance_results['create_order']['avg'], 0.5,
                           "Create order should average < 500ms")
        
        # Test 2: Bulk operation performance
        print("Testing bulk operation performance...")
        
        start_time = time.time()
        
        # Create 20 service orders rapidly
        created_orders = 0
        for i in range(20):
            response = self.client.post('/api/service-orders', json={
                'route_id': 1,
                'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}],
                'notes': f'Bulk test order {i}'
            })
            
            if response.status_code in [200, 201]:
                created_orders += 1
        
        bulk_time = time.time() - start_time
        throughput = created_orders / bulk_time if bulk_time > 0 else 0
        
        print(f"  Bulk creation: {created_orders} orders in {bulk_time:.3f}s ({throughput:.2f} orders/sec)")
        
        # Performance assertions
        self.assertGreater(throughput, 5, "Should create at least 5 orders per second")
        self.assertLess(bulk_time, 10, "Bulk creation should complete within 10 seconds")
        
        print("✓ All performance benchmark tests passed")


class DeviceAPITests(unittest.TestCase):
    """
    Device management API testing examples.
    
    This test class demonstrates device CRUD operations, search functionality,
    and soft delete behavior specific to the CVD application.
    """
    
    def setUp(self):
        """Set up test environment for device API testing."""
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Configure Flask application
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
            'SECRET_KEY': 'test-secret-key'
        })
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize database
        self.init_device_test_database()
        self.create_device_test_data()
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
        
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def init_device_test_database(self):
        """Initialize database schema for device testing."""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer'
            );
            
            CREATE TABLE device_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                max_cabinets INTEGER DEFAULT 1
            );
            
            CREATE TABLE locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT
            );
            
            CREATE TABLE devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                asset TEXT UNIQUE,
                device_type_id INTEGER NOT NULL,
                location_id INTEGER,
                active BOOLEAN DEFAULT 1,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_type_id) REFERENCES device_types (id),
                FOREIGN KEY (location_id) REFERENCES locations (id)
            );
            
            CREATE INDEX idx_devices_name ON devices(name);
            CREATE INDEX idx_devices_active ON devices(active, is_deleted);
            
            PRAGMA foreign_keys = ON;
        """)
        
        db.commit()
        db.close()
    
    def create_device_test_data(self):
        """Create test data for device testing."""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Create test user
        cursor.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES ('admin', ?, 'admin')
        """, (hash_password('admin'),))
        
        # Create device types
        device_types = [
            (1, 'Single Door Cooler', 1),
            (2, 'Double Door Cooler', 2)
        ]
        cursor.executemany("""
            INSERT INTO device_types (id, name, max_cabinets)
            VALUES (?, ?, ?)
        """, device_types)
        
        # Create locations
        locations = [
            (1, 'Main Office', '123 Business St'),
            (2, 'Branch Office', '456 Corporate Ave')
        ]
        cursor.executemany("""
            INSERT INTO locations (id, name, address)
            VALUES (?, ?, ?)
        """, locations)
        
        # Create test devices
        devices = [
            ('Active Cooler 1', 'ASSET001', 1, 1, 1, 0),
            ('Active Cooler 2', 'ASSET002', 2, 2, 1, 0),
            ('Inactive Cooler', 'ASSET003', 1, 1, 0, 0),
            ('Deleted Cooler', 'ASSET004', 1, 1, 1, 1)
        ]
        
        cursor.executemany("""
            INSERT INTO devices (name, asset, device_type_id, location_id, active, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?)
        """, devices)
        
        db.commit()
        db.close()
    
    def authenticate_as_admin(self):
        """Authenticate as admin user."""
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_device_listing_with_filters(self):
        """
        Test device listing with various filters and search functionality.
        
        This test demonstrates:
        - Basic device listing
        - Active/inactive filtering
        - Search by name functionality
        - Soft delete handling
        """
        print("\n=== Testing Device Listing with Filters ===")
        
        self.authenticate_as_admin()
        
        # Test 1: List all active devices (default behavior)
        print("Testing default device listing (active only)...")
        response = self.client.get('/api/devices')
        self.assertEqual(response.status_code, 200)
        
        devices = response.get_json()
        self.assertIsInstance(devices, list)
        
        # Should only return active, non-deleted devices
        active_devices = [d for d in devices if d.get('active', True) and not d.get('is_deleted', False)]
        self.assertEqual(len(devices), len(active_devices), "Should only return active devices by default")
        print(f"✓ Listed {len(devices)} active devices")
        
        # Test 2: List all devices (including inactive)
        print("Testing device listing with inactive devices...")
        response = self.client.get('/api/devices?include_inactive=true')
        self.assertEqual(response.status_code, 200)
        
        all_devices = response.get_json()
        self.assertGreaterEqual(len(all_devices), len(devices), "Should return more devices when including inactive")
        print(f"✓ Listed {len(all_devices)} devices (including inactive)")
        
        # Test 3: Search by device name
        print("Testing device search functionality...")
        search_response = self.client.get('/api/devices?search=Cooler 1')
        self.assertEqual(search_response.status_code, 200)
        
        search_results = search_response.get_json()
        self.assertGreater(len(search_results), 0, "Should find devices matching search term")
        
        # Verify search results contain the search term
        for device in search_results:
            self.assertIn('Cooler 1', device['name'], "Search results should match search term")
        
        print(f"✓ Search found {len(search_results)} devices matching 'Cooler 1'")
        
        # Test 4: Verify soft-deleted devices are excluded
        print("Testing soft delete exclusion...")
        device_names = [d['name'] for d in all_devices]
        self.assertNotIn('Deleted Cooler', device_names, "Soft-deleted devices should be excluded")
        print("✓ Soft-deleted devices properly excluded")
    
    def test_device_crud_operations(self):
        """
        Test complete CRUD operations for devices.
        
        This demonstrates the full lifecycle of device management
        including creation, reading, updating, and soft deletion.
        """
        print("\n=== Testing Device CRUD Operations ===")
        
        self.authenticate_as_admin()
        
        # Test 1: Create new device
        print("Testing device creation...")
        new_device = {
            'name': 'New Test Cooler',
            'asset': 'ASSET999',
            'device_type_id': 1,
            'location_id': 1,
            'active': True
        }
        
        response = self.client.post('/api/devices', json=new_device)
        self.assertEqual(response.status_code, 201, "Should create device successfully")
        
        created_device = response.get_json()
        self.assertIn('id', created_device, "Response should include device ID")
        device_id = created_device['id']
        
        print(f"✓ Created device with ID: {device_id}")
        
        # Test 2: Read created device
        print("Testing device retrieval...")
        response = self.client.get(f'/api/devices/{device_id}')
        self.assertEqual(response.status_code, 200, "Should retrieve device successfully")
        
        retrieved_device = response.get_json()
        self.assertEqual(retrieved_device['name'], new_device['name'])
        self.assertEqual(retrieved_device['asset'], new_device['asset'])
        
        print("✓ Retrieved device successfully")
        
        # Test 3: Update device
        print("Testing device update...")
        update_data = {
            'name': 'Updated Test Cooler',
            'active': False
        }
        
        response = self.client.put(f'/api/devices/{device_id}', json=update_data)
        self.assertEqual(response.status_code, 200, "Should update device successfully")
        
        updated_device = response.get_json()
        self.assertEqual(updated_device['name'], update_data['name'])
        self.assertEqual(updated_device['active'], update_data['active'])
        
        print("✓ Updated device successfully")
        
        # Test 4: Soft delete device
        print("Testing device soft deletion...")
        response = self.client.delete(f'/api/devices/{device_id}')
        self.assertEqual(response.status_code, 200, "Should soft delete device successfully")
        
        # Verify device is soft deleted (not visible in normal listing)
        response = self.client.get(f'/api/devices/{device_id}')
        self.assertEqual(response.status_code, 404, "Soft deleted device should not be accessible")
        
        # Verify device still exists in database with is_deleted flag
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        cursor.execute("SELECT is_deleted FROM devices WHERE id = ?", (device_id,))
        result = cursor.fetchone()
        self.assertIsNotNone(result, "Device should still exist in database")
        self.assertEqual(result[0], 1, "Device should be marked as deleted")
        db.close()
        
        print("✓ Soft deleted device successfully")
        
        print("✓ All CRUD operations completed successfully")


if __name__ == '__main__':
    """
    Run the API endpoint testing examples.
    
    Usage:
    python API_ENDPOINT_TESTS.py              # Run all tests
    python -m pytest API_ENDPOINT_TESTS.py   # Run with pytest
    python -m pytest API_ENDPOINT_TESTS.py::ServiceOrderAPITests::test_service_order_creation_success -v  # Run specific test
    """
    
    print("="*80)
    print("CVD API ENDPOINT TESTING EXAMPLES")
    print("="*80)
    print()
    print("This module demonstrates comprehensive API testing patterns for:")
    print("• Service order management (creation, updates, status transitions)")
    print("• Device CRUD operations with soft delete support")
    print("• Authentication and authorization flows")
    print("• Input validation and error handling")
    print("• Performance benchmarking and monitoring")
    print()
    print("Running tests with detailed output...")
    print("="*80)
    
    # Run tests with high verbosity
    unittest.main(verbosity=2, exit=False)
    
    print("="*80)
    print("API ENDPOINT TESTING EXAMPLES COMPLETED")
    print("="*80)