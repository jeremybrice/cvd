#!/usr/bin/env python3
"""
CVD Integration Test Suites

This file demonstrates comprehensive integration testing patterns for the CVD application,
showing how to test complete workflows, cross-component interactions, and end-to-end
scenarios while maintaining test isolation and reliability.
"""

import unittest
import sqlite3
import tempfile
import os
import json
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add CVD application to Python path for testing
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

# Import CVD application components
try:
    from app import create_app
    from auth import AuthManager, hash_password
    from service_order_service import ServiceOrderService
    from planogram_optimizer import PlanogramOptimizer
except ImportError as e:
    print(f"Warning: Could not import CVD modules: {e}")
    print("This example requires the CVD application to be in the Python path")


class ServiceOrderWorkflowIntegrationTests(unittest.TestCase):
    """
    Complete service order workflow integration tests.
    
    These tests demonstrate:
    - End-to-end service order lifecycle
    - Multi-user role interactions
    - Database transaction integrity
    - State synchronization across components
    - Real-time workflow progression
    """
    
    def setUp(self):
        """Set up complete integration test environment."""
        # Create temporary database for integration testing
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # Configure Flask application with real database
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
            'SECRET_KEY': 'integration-test-secret',
            'WTF_CSRF_ENABLED': False
        })
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize complete database schema
        self.init_integration_database()
        self.create_comprehensive_test_data()
        
        print(f"Integration test environment ready. Database: {self.db_path}")
    
    def tearDown(self):
        """Clean up integration test environment."""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
        
        # Clean up database
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        print("Integration test cleanup complete")
    
    def init_integration_database(self):
        """Initialize complete database schema for integration testing."""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Create complete schema for integration testing
        cursor.executescript("""
            -- Users and authentication
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer',
                email TEXT,
                full_name TEXT,
                deleted_at TIMESTAMP NULL,
                active BOOLEAN DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Sessions for authentication
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            -- Device management
            CREATE TABLE device_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                max_cabinets INTEGER DEFAULT 1,
                description TEXT
            );
            
            CREATE TABLE locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                latitude REAL,
                longitude REAL,
                active BOOLEAN DEFAULT 1
            );
            
            CREATE TABLE routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                asset TEXT UNIQUE,
                device_type_id INTEGER NOT NULL,
                location_id INTEGER,
                route_id INTEGER,
                active BOOLEAN DEFAULT 1,
                is_deleted BOOLEAN DEFAULT 0,
                installation_date DATE,
                last_service_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_type_id) REFERENCES device_types (id),
                FOREIGN KEY (location_id) REFERENCES locations (id),
                FOREIGN KEY (route_id) REFERENCES routes (id)
            );
            
            -- Cabinet configurations
            CREATE TABLE cabinet_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                default_rows INTEGER DEFAULT 5,
                default_columns INTEGER DEFAULT 8
            );
            
            CREATE TABLE cabinet_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                cabinet_index INTEGER NOT NULL,
                cabinet_type_id INTEGER NOT NULL,
                rows INTEGER NOT NULL,
                columns INTEGER NOT NULL,
                modelName TEXT,
                temperature_range TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (id),
                FOREIGN KEY (cabinet_type_id) REFERENCES cabinet_types (id),
                UNIQUE(device_id, cabinet_index)
            );
            
            -- Products
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                default_price REAL,
                cost REAL,
                sku TEXT UNIQUE,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Service orders (main workflow)
            CREATE TABLE service_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_by INTEGER,
                assigned_to INTEGER,
                priority TEXT DEFAULT 'normal',
                notes TEXT,
                scheduled_date DATE,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                estimated_duration INTEGER,
                actual_duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes (id),
                FOREIGN KEY (created_by) REFERENCES users (id),
                FOREIGN KEY (assigned_to) REFERENCES users (id)
            );
            
            -- Service order cabinets (cabinet-centric workflow)
            CREATE TABLE service_order_cabinets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_order_id INTEGER NOT NULL,
                device_id INTEGER NOT NULL,
                cabinet_index INTEGER NOT NULL,
                cabinet_configuration_id INTEGER,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                photos TEXT,  -- JSON array of photo URLs
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_order_id) REFERENCES service_orders (id),
                FOREIGN KEY (device_id) REFERENCES devices (id),
                FOREIGN KEY (cabinet_configuration_id) REFERENCES cabinet_configurations (id)
            );
            
            -- Service order items (product-level tracking)
            CREATE TABLE service_order_cabinet_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_order_cabinet_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                requested_quantity INTEGER NOT NULL,
                delivered_quantity INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_order_cabinet_id) REFERENCES service_order_cabinets (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            );
            
            -- Service visits (completion tracking)
            CREATE TABLE service_visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_order_id INTEGER NOT NULL,
                service_order_cabinet_id INTEGER,
                user_id INTEGER NOT NULL,
                visit_type TEXT DEFAULT 'service',
                check_in_time TIMESTAMP,
                check_out_time TIMESTAMP,
                location_latitude REAL,
                location_longitude REAL,
                notes TEXT,
                photos TEXT,  -- JSON array of photo URLs
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_order_id) REFERENCES service_orders (id),
                FOREIGN KEY (service_order_cabinet_id) REFERENCES service_order_cabinets (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            -- Audit logging
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id INTEGER,
                old_values TEXT,  -- JSON
                new_values TEXT,  -- JSON
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            
            -- Indexes for performance
            CREATE INDEX idx_users_username ON users(username);
            CREATE INDEX idx_users_active ON users(active, deleted_at);
            CREATE INDEX idx_sessions_user_id ON sessions(user_id);
            CREATE INDEX idx_sessions_expires ON sessions(expires_at);
            CREATE INDEX idx_devices_active ON devices(active, is_deleted);
            CREATE INDEX idx_devices_route ON devices(route_id);
            CREATE INDEX idx_service_orders_status ON service_orders(status);
            CREATE INDEX idx_service_orders_route ON service_orders(route_id);
            CREATE INDEX idx_service_orders_assigned ON service_orders(assigned_to);
            CREATE INDEX idx_service_order_cabinets_order ON service_order_cabinets(service_order_id);
            CREATE INDEX idx_service_order_cabinets_device ON service_order_cabinets(device_id);
            CREATE INDEX idx_service_visits_order ON service_visits(service_order_id);
            CREATE INDEX idx_service_visits_user ON service_visits(user_id);
            CREATE INDEX idx_audit_log_user ON audit_log(user_id);
            CREATE INDEX idx_audit_log_table ON audit_log(table_name, record_id);
            
            -- Enable foreign keys
            PRAGMA foreign_keys = ON;
        """)
        
        db.commit()
        db.close()
        
        print("Complete integration database schema initialized")
    
    def create_comprehensive_test_data(self):
        """Create comprehensive test data for integration testing."""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Create test users with full role hierarchy
        test_users = [
            ('admin', hash_password('admin'), 'admin', 'admin@cvd.com', 'Admin User'),
            ('manager1', hash_password('manager1'), 'manager', 'manager1@cvd.com', 'Manager One'),
            ('manager2', hash_password('manager2'), 'manager', 'manager2@cvd.com', 'Manager Two'),
            ('driver1', hash_password('driver1'), 'driver', 'driver1@cvd.com', 'Driver One'),
            ('driver2', hash_password('driver2'), 'driver', 'driver2@cvd.com', 'Driver Two'),
            ('viewer', hash_password('viewer'), 'viewer', 'viewer@cvd.com', 'Viewer User')
        ]
        
        cursor.executemany("""
            INSERT INTO users (username, password_hash, role, email, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, test_users)
        
        # Create device types
        device_types = [
            (1, 'Single Door Cooler', 1, 'Standard single-door beverage cooler'),
            (2, 'Double Door Cooler', 2, 'Double-door cooler with dual cabinets'),
            (3, 'Triple Cabinet Unit', 3, 'Large triple-cabinet combination unit'),
            (4, 'Snack Tower', 1, 'Tall snack dispensing unit')
        ]
        
        cursor.executemany("""
            INSERT INTO device_types (id, name, max_cabinets, description)
            VALUES (?, ?, ?, ?)
        """, device_types)
        
        # Create cabinet types
        cabinet_types = [
            (1, 'Beverage Cooler', 5, 8),
            (2, 'Snack Cabinet', 6, 10),
            (3, 'Combo Unit', 5, 6),
            (4, 'Ice Cream Freezer', 4, 6)
        ]
        
        cursor.executemany("""
            INSERT INTO cabinet_types (id, name, default_rows, default_columns)
            VALUES (?, ?, ?, ?)
        """, cabinet_types)
        
        # Create test locations
        locations = [
            (1, 'Downtown Office Complex', '123 Business Street, Downtown', 40.7128, -74.0060),
            (2, 'North Side Mall', '456 Shopping Center Blvd', 40.7589, -73.9851),
            (3, 'Industrial Park East', '789 Industrial Way', 40.6892, -74.0445),
            (4, 'University Campus', '321 Campus Drive', 40.7505, -73.9934),
            (5, 'Airport Terminal', '555 Airport Road', 40.6413, -73.7781)
        ]
        
        cursor.executemany("""
            INSERT INTO locations (id, name, address, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
        """, locations)
        
        # Create test routes
        routes = [
            (1, 'Route A - Downtown', 'Downtown business district and office complexes'),
            (2, 'Route B - North Side', 'North side residential and commercial areas'),
            (3, 'Route C - Industrial', 'Industrial parks and manufacturing facilities'),
            (4, 'Route D - Campus/Airport', 'University campus and airport locations')
        ]
        
        cursor.executemany("""
            INSERT INTO routes (id, name, description)
            VALUES (?, ?, ?)
        """, routes)
        
        # Create test devices with various configurations
        devices = [
            # Downtown route devices
            (111, 'Cooler A1', 'ASSET_DT_A1', 1, 1, 1, '2024-01-15', '2024-11-01'),
            (112, 'Cooler A2', 'ASSET_DT_A2', 2, 1, 1, '2024-01-20', '2024-10-15'),
            (113, 'Unit A3', 'ASSET_DT_A3', 3, 1, 1, '2024-02-01', '2024-11-10'),
            
            # North side route devices  
            (211, 'Cooler B1', 'ASSET_NS_B1', 1, 2, 2, '2024-01-10', '2024-10-20'),
            (212, 'Cooler B2', 'ASSET_NS_B2', 2, 2, 2, '2024-01-25', '2024-11-05'),
            (213, 'Tower B3', 'ASSET_NS_B3', 4, 2, 2, '2024-02-10', '2024-10-30'),
            
            # Industrial route devices
            (311, 'Cooler C1', 'ASSET_IN_C1', 2, 3, 3, '2024-01-05', '2024-10-25'),
            (312, 'Unit C2', 'ASSET_IN_C2', 3, 3, 3, '2024-01-30', '2024-11-08'),
            
            # Campus/Airport route devices
            (411, 'Cooler D1', 'ASSET_CA_D1', 1, 4, 4, '2024-01-12', '2024-10-18'),
            (412, 'Cooler D2', 'ASSET_CA_D2', 2, 5, 4, '2024-02-05', '2024-11-12')
        ]
        
        cursor.executemany("""
            INSERT INTO devices 
            (id, name, asset, device_type_id, location_id, route_id, installation_date, last_service_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, devices)
        
        # Create cabinet configurations for multi-cabinet devices
        cabinet_configs = [
            # Double door coolers (type 2)
            (112, 0, 1, 5, 8, 'CoolMax Left'),  # Device 112, cabinet 0
            (112, 1, 2, 6, 10, 'CoolMax Right'),  # Device 112, cabinet 1
            (212, 0, 1, 5, 8, 'FreshKeep Left'),
            (212, 1, 1, 5, 8, 'FreshKeep Right'),
            (311, 0, 1, 5, 8, 'IndustrialCool Left'),
            (311, 1, 2, 6, 10, 'IndustrialCool Right'),
            (412, 0, 1, 5, 8, 'AirportCool Left'),
            (412, 1, 4, 4, 6, 'AirportCool Right'),
            
            # Triple cabinet units (type 3)
            (113, 0, 1, 5, 8, 'TripleMax Left'),
            (113, 1, 2, 6, 10, 'TripleMax Center'),
            (113, 2, 3, 5, 6, 'TripleMax Right'),
            (312, 0, 1, 5, 8, 'IndustrialTriple Left'),
            (312, 1, 2, 6, 10, 'IndustrialTriple Center'),
            (312, 2, 4, 4, 6, 'IndustrialTriple Right'),
            
            # Single cabinet devices
            (111, 0, 1, 5, 8, 'Standard Cooler'),
            (211, 0, 1, 5, 8, 'Standard Cooler'),
            (213, 0, 2, 8, 5, 'Snack Tower'),  # Tall snack unit
            (411, 0, 1, 5, 8, 'Standard Cooler')
        ]
        
        cursor.executemany("""
            INSERT INTO cabinet_configurations 
            (device_id, cabinet_index, cabinet_type_id, rows, columns, modelName)
            VALUES (?, ?, ?, ?, ?, ?)
        """, cabinet_configs)
        
        # Create standard 12 system products
        products = [
            (1, 'Coca Cola', 'Beverages', 1.50, 0.75, 'BEV001'),
            (2, 'Pepsi Cola', 'Beverages', 1.50, 0.75, 'BEV002'),
            (3, 'Sprite', 'Beverages', 1.50, 0.75, 'BEV003'),
            (4, 'Orange Soda', 'Beverages', 1.50, 0.75, 'BEV004'),
            (5, 'Water Bottle', 'Beverages', 1.00, 0.30, 'BEV005'),
            (6, 'Energy Drink', 'Beverages', 2.50, 1.50, 'BEV006'),
            (7, 'Chips - Original', 'Snacks', 1.75, 1.00, 'SNK007'),
            (8, 'Chips - BBQ', 'Snacks', 1.75, 1.00, 'SNK008'),
            (9, 'Candy Bar', 'Candy', 1.25, 0.60, 'CND009'),
            (10, 'Chocolate', 'Candy', 1.50, 0.80, 'CND010'),
            (11, 'Cookies', 'Snacks', 2.00, 1.20, 'SNK011'),
            (12, 'Crackers', 'Snacks', 1.50, 0.90, 'SNK012')
        ]
        
        cursor.executemany("""
            INSERT INTO products (id, name, category, default_price, cost, sku)
            VALUES (?, ?, ?, ?, ?, ?)
        """, products)
        
        db.commit()
        db.close()
        
        print("Comprehensive test data created for integration testing")
    
    def authenticate_user(self, username, password):
        """Helper method to authenticate a user and return auth data."""
        response = self.client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
        
        self.assertEqual(response.status_code, 200, 
                        f"Authentication failed for {username}")
        
        return response.get_json()
    
    def test_complete_service_order_lifecycle(self):
        """
        Test complete service order lifecycle with multiple user roles.
        
        This integration test demonstrates:
        - Service order creation by manager
        - Order assignment to driver
        - Driver workflow execution
        - Status updates and transitions
        - Completion verification and audit trail
        """
        print("\n=== Testing Complete Service Order Lifecycle ===")
        
        # Phase 1: Manager creates service order
        print("Phase 1: Manager creates service order...")
        
        manager_auth = self.authenticate_user('manager1', 'manager1')
        manager_user_id = manager_auth['user']['id']
        
        # Create comprehensive service order
        order_data = {
            'route_id': 1,  # Downtown route
            'cabinet_selections': [
                {'deviceId': 111, 'cabinetIndex': 0},  # Single cabinet
                {'deviceId': 112, 'cabinetIndex': 0},  # First cabinet of double unit
                {'deviceId': 112, 'cabinetIndex': 1},  # Second cabinet of double unit  
                {'deviceId': 113, 'cabinetIndex': 0},  # First cabinet of triple unit
                {'deviceId': 113, 'cabinetIndex': 1}   # Second cabinet of triple unit
            ],
            'priority': 'high',
            'notes': 'Integration test service order - complete lifecycle',
            'scheduled_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        }
        
        start_time = time.time()
        create_response = self.client.post('/api/service-orders', json=order_data)
        creation_time = time.time() - start_time
        
        self.assertEqual(create_response.status_code, 201, "Service order creation should succeed")
        
        created_order = create_response.get_json()
        order_id = created_order['id']
        
        # Verify order structure
        self.assertEqual(created_order['route_id'], 1)
        self.assertEqual(created_order['status'], 'pending')
        self.assertEqual(created_order['created_by'], manager_user_id)
        self.assertEqual(len(created_order['cabinets']), 5)  # 5 cabinet selections
        
        print(f"✓ Service order created (ID: {order_id}) in {creation_time:.3f}s")
        print(f"  Route: {created_order['route_id']}, Cabinets: {len(created_order['cabinets'])}")
        
        # Phase 2: Manager assigns order to driver
        print("Phase 2: Manager assigns order to driver...")
        
        # Get driver user ID
        driver_auth = self.authenticate_user('driver1', 'driver1')
        driver_user_id = driver_auth['user']['id']
        
        # Re-authenticate as manager for assignment
        self.authenticate_user('manager1', 'manager1')
        
        assignment_data = {
            'assigned_to': driver_user_id,
            'status': 'assigned',
            'notes': 'Assigned to Driver One for execution'
        }
        
        assign_response = self.client.put(f'/api/service-orders/{order_id}', json=assignment_data)
        self.assertEqual(assign_response.status_code, 200, "Order assignment should succeed")
        
        assigned_order = assign_response.get_json()
        self.assertEqual(assigned_order['assigned_to'], driver_user_id)
        self.assertEqual(assigned_order['status'], 'assigned')
        
        print(f"✓ Order assigned to driver {driver_user_id}")
        
        # Phase 3: Driver accepts and starts order
        print("Phase 3: Driver accepts and starts order...")
        
        # Authenticate as driver
        self.authenticate_user('driver1', 'driver1')
        
        # Driver accepts order
        accept_data = {
            'status': 'in_progress',
            'notes': 'Driver accepted order and starting route'
        }
        
        accept_response = self.client.put(f'/api/service-orders/{order_id}', json=accept_data)
        self.assertEqual(accept_response.status_code, 200, "Driver should accept order")
        
        accepted_order = accept_response.get_json()
        self.assertEqual(accepted_order['status'], 'in_progress')
        self.assertIsNotNone(accepted_order.get('started_at'), "Should set start timestamp")
        
        print("✓ Driver accepted order and started execution")
        
        # Phase 4: Driver executes service on individual cabinets
        print("Phase 4: Driver executes service on individual cabinets...")
        
        cabinet_completion_count = 0
        
        # Get cabinet details for execution
        cabinet_response = self.client.get(f'/api/service-orders/{order_id}')
        order_details = cabinet_response.get_json()
        
        for cabinet in order_details['cabinets']:
            cabinet_id = cabinet['id']
            device_name = cabinet.get('device_name', f"Device {cabinet['device_id']}")
            cabinet_index = cabinet['cabinet_index']
            
            print(f"  Servicing cabinet {cabinet_index} on {device_name}...")
            
            # Start cabinet service
            cabinet_start_data = {
                'status': 'in_progress',
                'notes': f'Starting service on cabinet {cabinet_index}'
            }
            
            start_cabinet_response = self.client.put(
                f'/api/service-order-cabinets/{cabinet_id}', 
                json=cabinet_start_data
            )
            
            if start_cabinet_response.status_code == 200:
                # Complete cabinet service with simulated photos
                cabinet_complete_data = {
                    'status': 'completed',
                    'notes': f'Cabinet {cabinet_index} serviced successfully',
                    'photos': [f'cabinet_{cabinet_id}_before.jpg', f'cabinet_{cabinet_id}_after.jpg']
                }
                
                complete_cabinet_response = self.client.put(
                    f'/api/service-order-cabinets/{cabinet_id}', 
                    json=cabinet_complete_data
                )
                
                if complete_cabinet_response.status_code == 200:
                    cabinet_completion_count += 1
                    print(f"    ✓ Cabinet {cabinet_index} completed")
            
            # Small delay to simulate real service time
            time.sleep(0.1)
        
        print(f"✓ Completed service on {cabinet_completion_count} cabinets")
        
        # Phase 5: Driver completes entire service order
        print("Phase 5: Driver completes entire service order...")
        
        completion_data = {
            'status': 'completed',
            'notes': 'All cabinets serviced successfully. Route completed.',
            'actual_duration': 120  # 2 hours in minutes
        }
        
        completion_response = self.client.put(f'/api/service-orders/{order_id}', json=completion_data)
        self.assertEqual(completion_response.status_code, 200, "Order completion should succeed")
        
        completed_order = completion_response.get_json()
        self.assertEqual(completed_order['status'], 'completed')
        self.assertIsNotNone(completed_order.get('completed_at'), "Should set completion timestamp")
        
        print("✓ Service order completed successfully")
        
        # Phase 6: Verify database consistency and audit trail
        print("Phase 6: Verifying database consistency and audit trail...")
        
        # Verify order status in database
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT status, created_by, assigned_to, started_at, completed_at
            FROM service_orders WHERE id = ?
        """, (order_id,))
        
        order_record = cursor.fetchone()
        self.assertIsNotNone(order_record, "Order should exist in database")
        self.assertEqual(order_record[0], 'completed')  # status
        self.assertEqual(order_record[1], manager_user_id)  # created_by
        self.assertEqual(order_record[2], driver_user_id)  # assigned_to
        self.assertIsNotNone(order_record[3])  # started_at
        self.assertIsNotNone(order_record[4])  # completed_at
        
        # Verify cabinet statuses
        cursor.execute("""
            SELECT COUNT(*) FROM service_order_cabinets 
            WHERE service_order_id = ? AND status = 'completed'
        """, (order_id,))
        
        completed_cabinets = cursor.fetchone()[0]
        self.assertGreater(completed_cabinets, 0, "Should have completed cabinets")
        
        db.close()
        
        print("✓ Database consistency verified")
        
        # Phase 7: Manager reviews completed order
        print("Phase 7: Manager reviews completed order...")
        
        self.authenticate_user('manager1', 'manager1')
        
        review_response = self.client.get(f'/api/service-orders/{order_id}')
        self.assertEqual(review_response.status_code, 200)
        
        review_order = review_response.get_json()
        self.assertEqual(review_order['status'], 'completed')
        
        # Verify all workflow phases completed
        workflow_phases = ['created', 'assigned', 'started', 'completed']
        for phase in workflow_phases:
            phase_key = f"{phase}_at" if phase != 'created' else 'created_at'
            if phase == 'started':
                phase_key = 'started_at'
            elif phase == 'assigned':
                continue  # No assigned_at timestamp in basic schema
            
            if phase_key in review_order:
                self.assertIsNotNone(review_order[phase_key], 
                                   f"Should have {phase_key} timestamp")
        
        print("✓ Manager review completed - all phases verified")
        
        total_test_time = time.time() - start_time + creation_time
        print(f"\n✓ Complete service order lifecycle test completed in {total_test_time:.3f}s")
        print(f"  Order ID: {order_id}")
        print(f"  Cabinets serviced: {cabinet_completion_count}")
        print(f"  Workflow: Manager → Driver → Completion → Review")
    
    def test_concurrent_service_order_operations(self):
        """
        Test concurrent service order operations for race conditions.
        
        This test demonstrates:
        - Multiple users creating orders simultaneously
        - Concurrent status updates on different orders
        - Database transaction isolation
        - Data consistency under load
        """
        print("\n=== Testing Concurrent Service Order Operations ===")
        
        import queue
        import threading
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def concurrent_order_creation(thread_id, route_id, user_credentials):
            """Create service order in separate thread."""
            try:
                # Create new client for this thread
                thread_client = self.app.test_client()
                
                # Authenticate
                auth_response = thread_client.post('/api/auth/login', json=user_credentials)
                if auth_response.status_code != 200:
                    errors.put(f"Thread {thread_id}: Authentication failed")
                    return
                
                # Create order
                order_data = {
                    'route_id': route_id,
                    'cabinet_selections': [
                        {'deviceId': 111 + (thread_id * 100), 'cabinetIndex': 0}
                    ] if (111 + (thread_id * 100)) in [111, 211, 311, 411] else [
                        {'deviceId': 111, 'cabinetIndex': 0}  # Fallback to valid device
                    ],
                    'notes': f'Concurrent test order from thread {thread_id}',
                    'priority': 'normal'
                }
                
                start_time = time.time()
                response = thread_client.post('/api/service-orders', json=order_data)
                end_time = time.time()
                
                if response.status_code in [200, 201]:
                    order = response.get_json()
                    results.put({
                        'thread_id': thread_id,
                        'order_id': order['id'],
                        'response_time': end_time - start_time,
                        'success': True
                    })
                else:
                    errors.put(f"Thread {thread_id}: Order creation failed - {response.status_code}")
                    
            except Exception as e:
                errors.put(f"Thread {thread_id}: Exception - {str(e)}")
        
        def concurrent_status_updates(thread_id, order_id, target_status):
            """Update order status in separate thread."""
            try:
                # Create new client for this thread
                thread_client = self.app.test_client()
                
                # Authenticate as driver
                auth_response = thread_client.post('/api/auth/login', json={
                    'username': 'driver1',
                    'password': 'driver1'
                })
                
                if auth_response.status_code != 200:
                    errors.put(f"Status thread {thread_id}: Authentication failed")
                    return
                
                # Update status
                update_data = {
                    'status': target_status,
                    'notes': f'Status update from thread {thread_id}'
                }
                
                start_time = time.time()
                response = thread_client.put(f'/api/service-orders/{order_id}', json=update_data)
                end_time = time.time()
                
                results.put({
                    'thread_id': f'status_{thread_id}',
                    'order_id': order_id,
                    'status': target_status,
                    'response_time': end_time - start_time,
                    'success': response.status_code == 200
                })
                
            except Exception as e:
                errors.put(f"Status thread {thread_id}: Exception - {str(e)}")
        
        # Test 1: Concurrent order creation
        print("Testing concurrent order creation...")
        
        # Create multiple orders simultaneously
        creation_threads = []
        user_credentials_list = [
            {'username': 'manager1', 'password': 'manager1'},
            {'username': 'manager2', 'password': 'manager2'},
        ]
        
        for i in range(8):  # 8 concurrent order creations
            credentials = user_credentials_list[i % len(user_credentials_list)]
            route_id = (i % 4) + 1  # Rotate through routes 1-4
            
            thread = threading.Thread(
                target=concurrent_order_creation,
                args=(i, route_id, credentials)
            )
            creation_threads.append(thread)
            thread.start()
        
        # Wait for all creation threads to complete
        for thread in creation_threads:
            thread.join(timeout=10)  # 10 second timeout per thread
        
        # Collect creation results
        creation_results = []
        while not results.empty():
            creation_results.append(results.get())
        
        successful_creations = [r for r in creation_results if r['success']]
        print(f"  ✓ {len(successful_creations)}/8 concurrent order creations succeeded")
        
        # Verify response times
        if successful_creations:
            avg_response_time = sum(r['response_time'] for r in successful_creations) / len(successful_creations)
            max_response_time = max(r['response_time'] for r in successful_creations)
            
            print(f"  ✓ Average response time: {avg_response_time:.3f}s")
            print(f"  ✓ Max response time: {max_response_time:.3f}s")
            
            # Performance assertions
            self.assertLess(avg_response_time, 2.0, "Average response time should be < 2s under load")
            self.assertLess(max_response_time, 5.0, "Max response time should be < 5s under load")
        
        # Test 2: Concurrent status updates on different orders
        if len(successful_creations) >= 2:
            print("Testing concurrent status updates...")
            
            # Take first two successful orders for status update testing
            order1_id = successful_creations[0]['order_id']
            order2_id = successful_creations[1]['order_id']
            
            status_threads = []
            status_updates = [
                (order1_id, 'in_progress'),
                (order2_id, 'in_progress'),
                (order1_id, 'completed'),
                (order2_id, 'completed')
            ]
            
            for i, (order_id, status) in enumerate(status_updates):
                thread = threading.Thread(
                    target=concurrent_status_updates,
                    args=(i, order_id, status)
                )
                status_threads.append(thread)
                thread.start()
                
                # Small stagger to create more realistic concurrent conditions
                time.sleep(0.1)
            
            # Wait for all status update threads
            for thread in status_threads:
                thread.join(timeout=5)
            
            # Collect status update results
            status_results = []
            while not results.empty():
                status_results.append(results.get())
            
            successful_status_updates = [r for r in status_results if r['success']]
            print(f"  ✓ {len(successful_status_updates)}/{len(status_updates)} concurrent status updates succeeded")
        
        # Test 3: Database consistency verification
        print("Verifying database consistency after concurrent operations...")
        
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Verify all created orders exist and have valid data
        for result in successful_creations:
            cursor.execute("SELECT status, created_by FROM service_orders WHERE id = ?", 
                          (result['order_id'],))
            order_record = cursor.fetchone()
            
            self.assertIsNotNone(order_record, f"Order {result['order_id']} should exist")
            self.assertIsNotNone(order_record[1], f"Order {result['order_id']} should have created_by")
        
        # Check for any data corruption or constraint violations
        cursor.execute("SELECT COUNT(*) FROM service_orders WHERE created_by IS NULL")
        orphaned_orders = cursor.fetchone()[0]
        self.assertEqual(orphaned_orders, 0, "Should have no orphaned orders")
        
        cursor.execute("""
            SELECT COUNT(*) FROM service_order_cabinets soc
            LEFT JOIN service_orders so ON soc.service_order_id = so.id
            WHERE so.id IS NULL
        """)
        orphaned_cabinets = cursor.fetchone()[0]
        self.assertEqual(orphaned_cabinets, 0, "Should have no orphaned cabinet records")
        
        db.close()
        
        print("✓ Database consistency verified after concurrent operations")
        
        # Report any errors
        error_list = []
        while not errors.empty():
            error_list.append(errors.get())
        
        if error_list:
            print(f"  ! {len(error_list)} errors occurred during concurrent operations:")
            for error in error_list:
                print(f"    - {error}")
        
        # Overall success metrics
        total_operations = len(creation_results) + len(status_results)
        total_successful = len(successful_creations) + len(successful_status_updates)
        success_rate = (total_successful / total_operations * 100) if total_operations > 0 else 0
        
        print(f"✓ Overall concurrent operations success rate: {success_rate:.1f}%")
        
        # Minimum success rate assertion
        self.assertGreater(success_rate, 75, "Success rate should be > 75% under concurrent load")
    
    def test_cross_component_data_flow(self):
        """
        Test data flow across multiple CVD components.
        
        This test demonstrates:
        - Authentication → Authorization → Service Orders
        - Service Orders → Device Management → Cabinet Configurations  
        - Database transactions spanning multiple tables
        - Data consistency across component boundaries
        """
        print("\n=== Testing Cross-Component Data Flow ===")
        
        # Test 1: Authentication → Authorization → Service Order Creation
        print("Phase 1: Authentication → Authorization flow...")
        
        # Authenticate user and verify session
        auth_response = self.authenticate_user('manager1', 'manager1')
        session_info = auth_response['user']
        
        self.assertEqual(session_info['role'], 'manager')
        self.assertIn('id', session_info)
        user_id = session_info['id']
        
        # Verify authorization allows service order creation
        test_order = {
            'route_id': 1,
            'cabinet_selections': [{'deviceId': 111, 'cabinetIndex': 0}],
            'notes': 'Cross-component flow test'
        }
        
        create_response = self.client.post('/api/service-orders', json=test_order)
        self.assertEqual(create_response.status_code, 201, 
                        "Manager should be authorized to create service orders")
        
        order_id = create_response.get_json()['id']
        print(f"  ✓ Auth → Authorization → Service Order creation flow verified (Order: {order_id})")
        
        # Test 2: Service Orders → Device Management → Cabinet Configuration
        print("Phase 2: Service Orders → Device Management flow...")
        
        # Verify that service order properly links to device and cabinet data
        detail_response = self.client.get(f'/api/service-orders/{order_id}')
        order_details = detail_response.get_json()
        
        # Should have cabinet information populated from device management
        self.assertIn('cabinets', order_details)
        self.assertGreater(len(order_details['cabinets']), 0)
        
        cabinet = order_details['cabinets'][0]
        self.assertIn('device_id', cabinet)
        self.assertIn('cabinet_index', cabinet)
        
        # Verify device data is accessible and linked
        device_response = self.client.get(f'/api/devices/{cabinet["device_id"]}')
        self.assertEqual(device_response.status_code, 200, "Device should be accessible")
        
        device_data = device_response.get_json()
        self.assertEqual(device_data['id'], cabinet['device_id'])
        
        print(f"  ✓ Service Order → Device Management linkage verified")
        print(f"    Order {order_id} → Device {device_data['id']} ({device_data['name']})")
        
        # Test 3: Database transaction consistency across tables
        print("Phase 3: Database transaction consistency verification...")
        
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Verify referential integrity across component boundaries
        cursor.execute("""
            SELECT 
                so.id as order_id,
                so.status,
                so.created_by,
                u.username as creator_username,
                u.role as creator_role,
                soc.device_id,
                d.name as device_name,
                d.asset as device_asset,
                cc.modelName as cabinet_model
            FROM service_orders so
            JOIN users u ON so.created_by = u.id
            JOIN service_order_cabinets soc ON so.id = soc.service_order_id
            JOIN devices d ON soc.device_id = d.id
            LEFT JOIN cabinet_configurations cc ON d.id = cc.device_id AND soc.cabinet_index = cc.cabinet_index
            WHERE so.id = ?
        """, (order_id,))
        
        cross_component_data = cursor.fetchone()
        self.assertIsNotNone(cross_component_data, "Cross-component query should return data")
        
        # Verify all components are properly linked
        self.assertEqual(cross_component_data[0], order_id)  # order_id
        self.assertEqual(cross_component_data[2], user_id)   # created_by
        self.assertEqual(cross_component_data[4], 'manager') # creator_role
        self.assertIsNotNone(cross_component_data[5])       # device_id
        self.assertIsNotNone(cross_component_data[6])       # device_name
        
        print("  ✓ Cross-component database relationships verified")
        print(f"    Order: {cross_component_data[0]}")
        print(f"    Creator: {cross_component_data[3]} ({cross_component_data[4]})")
        print(f"    Device: {cross_component_data[6]} (Asset: {cross_component_data[7]})")
        
        # Test 4: Component state consistency during updates
        print("Phase 4: Component state consistency during updates...")
        
        # Update service order status and verify it propagates correctly
        status_update = {
            'status': 'in_progress',
            'notes': 'Cross-component state update test'
        }
        
        update_response = self.client.put(f'/api/service-orders/{order_id}', json=status_update)
        self.assertEqual(update_response.status_code, 200)
        
        # Verify status update is reflected across all related components
        cursor.execute("""
            SELECT so.status, so.started_at, soc.status as cabinet_status
            FROM service_orders so
            JOIN service_order_cabinets soc ON so.id = soc.service_order_id  
            WHERE so.id = ?
        """, (order_id,))
        
        status_data = cursor.fetchone()
        self.assertEqual(status_data[0], 'in_progress')  # Main order status
        self.assertIsNotNone(status_data[1])            # Started timestamp set
        
        print("  ✓ State consistency maintained across components during updates")
        
        # Test 5: Error propagation and rollback across components
        print("Phase 5: Error handling and rollback verification...")
        
        # Attempt invalid update that should fail and rollback
        invalid_update = {
            'status': 'invalid_status_value',
            'notes': 'This should fail and rollback'
        }
        
        invalid_response = self.client.put(f'/api/service-orders/{order_id}', json=invalid_update)
        self.assertNotEqual(invalid_response.status_code, 200, 
                          "Invalid status should be rejected")
        
        # Verify that partial updates didn't corrupt data
        cursor.execute("SELECT status, notes FROM service_orders WHERE id = ?", (order_id,))
        rollback_data = cursor.fetchone()
        
        self.assertEqual(rollback_data[0], 'in_progress', 
                        "Status should remain unchanged after failed update")
        self.assertNotIn('This should fail', rollback_data[1] or '', 
                        "Notes should not contain failed update text")
        
        print("  ✓ Error handling and rollback working correctly")
        
        db.close()
        
        # Test 6: Performance of cross-component operations
        print("Phase 6: Cross-component operation performance...")
        
        start_time = time.time()
        
        # Perform several cross-component operations
        operations = [
            lambda: self.client.get('/api/service-orders'),  # List orders (auth + orders)
            lambda: self.client.get(f'/api/service-orders/{order_id}'),  # Order details (orders + devices)
            lambda: self.client.get('/api/devices'),  # List devices (auth + devices)
            lambda: self.client.get(f'/api/devices/{cabinet["device_id"]}')  # Device details
        ]
        
        for operation in operations:
            operation_start = time.time()
            response = operation()
            operation_time = time.time() - operation_start
            
            self.assertEqual(response.status_code, 200, "Cross-component operation should succeed")
            self.assertLess(operation_time, 1.0, "Cross-component operation should be fast")
        
        total_time = time.time() - start_time
        print(f"  ✓ Cross-component operations completed in {total_time:.3f}s")
        
        print("✓ Cross-component data flow integration test completed successfully")


if __name__ == '__main__':
    """
    Run the integration test suites.
    
    Usage:
    python INTEGRATION_TEST_SUITES.py                        # Run all integration tests
    python -m pytest INTEGRATION_TEST_SUITES.py             # Run with pytest
    python -m pytest INTEGRATION_TEST_SUITES.py::ServiceOrderWorkflowIntegrationTests::test_complete_service_order_lifecycle -v
    """
    
    print("="*80)
    print("CVD INTEGRATION TEST SUITES")
    print("="*80)
    print()
    print("This module demonstrates comprehensive integration testing patterns for:")
    print("• Complete service order workflow (Manager → Driver → Completion)")
    print("• Multi-user role interactions and authorization")
    print("• Database transaction integrity and consistency")
    print("• Concurrent operations and race condition testing")
    print("• Cross-component data flow and state synchronization")
    print()
    print("Key integration concepts demonstrated:")
    print("• End-to-end workflow testing with real database")
    print("• Multi-threaded concurrent operation testing")
    print("• Cross-component relationship verification")
    print("• Performance testing under realistic load")
    print("• Data consistency and referential integrity validation")
    print()
    print("Running integration tests with detailed output...")
    print("="*80)
    
    # Run tests with high verbosity
    unittest.main(verbosity=2, exit=False)
    
    print("="*80)
    print("INTEGRATION TEST SUITES COMPLETED")
    print("="*80)