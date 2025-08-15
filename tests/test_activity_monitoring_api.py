#!/usr/bin/env python3
"""
Backend API Test Suite for User Activity Monitoring System
Tests all API endpoints, middleware functionality, and data operations
"""

import unittest
import json
import sqlite3
import tempfile
import os
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
import threading
import queue

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to test
import app
from activity_tracker import ActivityTracker
from auth import hash_password, verify_password

class TestActivityMonitoringAPI(unittest.TestCase):
    """Test suite for Activity Monitoring API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.test_db_fd, cls.test_db_path = tempfile.mkstemp(suffix='.db')
        cls.setup_test_database()
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        os.close(cls.test_db_fd)
        os.unlink(cls.test_db_path)
    
    @classmethod
    def setup_test_database(cls):
        """Initialize test database with schema and test data"""
        db = sqlite3.connect(cls.test_db_path)
        cursor = db.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sessions table with activity monitoring fields
        cursor.execute('''
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_page TEXT,
                last_api_endpoint TEXT,
                activity_count INTEGER DEFAULT 0,
                device_type TEXT DEFAULT 'unknown',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create activity monitoring tables
        cursor.execute('''
            CREATE TABLE user_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                page_url TEXT NOT NULL,
                page_title TEXT,
                action_type TEXT DEFAULT 'page_view',
                duration_ms INTEGER,
                referrer TEXT,
                ip_address TEXT,
                user_agent TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE activity_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id INTEGER,
                session_id TEXT,
                description TEXT NOT NULL,
                metadata TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged_at TIMESTAMP,
                acknowledged_by INTEGER,
                resolved_at TIMESTAMP,
                resolved_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (acknowledged_by) REFERENCES users(id),
                FOREIGN KEY (resolved_by) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE activity_summary_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                unique_users INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                total_page_views INTEGER DEFAULT 0,
                total_api_calls INTEGER DEFAULT 0,
                avg_session_duration_seconds INTEGER DEFAULT 0,
                peak_concurrent_users INTEGER DEFAULT 0,
                peak_hour INTEGER,
                top_pages TEXT,
                user_distribution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE system_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX idx_sessions_user_expires ON sessions(user_id, expires_at)')
        cursor.execute('CREATE INDEX idx_sessions_last_activity ON sessions(last_activity DESC)')
        cursor.execute('CREATE INDEX idx_activity_user_time ON user_activity_log(user_id, timestamp DESC)')
        cursor.execute('CREATE INDEX idx_activity_session ON user_activity_log(session_id, timestamp DESC)')
        cursor.execute('CREATE INDEX idx_alerts_status ON activity_alerts(status, created_at DESC)')
        
        # Insert test configuration
        cursor.execute('''
            INSERT INTO system_config (key, value, description) VALUES
            ('activity_monitoring_enabled', 'true', 'Enable activity monitoring'),
            ('activity_retention_days', '90', 'Days to retain activity logs'),
            ('activity_alert_concurrent_sessions_threshold', '2', 'Max concurrent sessions'),
            ('activity_alert_rapid_navigation_threshold', '20', 'Max pages per minute')
        ''')
        
        # Insert test users
        test_users = [
            ('admin', 'Admin User', 'admin@test.com', 'admin', hash_password('admin123')),
            ('manager', 'Manager User', 'manager@test.com', 'manager', hash_password('manager123')),
            ('driver', 'Driver User', 'driver@test.com', 'driver', hash_password('driver123')),
            ('viewer', 'Viewer User', 'viewer@test.com', 'viewer', hash_password('viewer123'))
        ]
        
        cursor.executemany('''
            INSERT INTO users (username, display_name, email, role, password_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', test_users)
        
        db.commit()
        db.close()
    
    def setUp(self):
        """Set up test client and app context for each test"""
        app.app.config['TESTING'] = True
        app.app.config['DATABASE'] = self.test_db_path
        app.DATABASE = self.test_db_path
        
        self.client = app.app.test_client()
        self.app_context = app.app.app_context()
        self.app_context.push()
        
        # Initialize activity tracker
        self.tracker = ActivityTracker(app.app, self.test_db_path)
        
        # Create test session for admin user
        self.admin_session = self.create_test_session('admin')
        
    def tearDown(self):
        """Clean up after each test"""
        self.app_context.pop()
        
        # Clean up test data
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('DELETE FROM user_activity_log')
        cursor.execute('DELETE FROM activity_alerts')
        cursor.execute('DELETE FROM sessions')
        db.commit()
        db.close()
    
    def create_test_session(self, username):
        """Helper to create a test session"""
        import uuid
        
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        # Get user ID
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()[0]
        
        # Create session
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        cursor.execute('''
            INSERT INTO sessions (id, user_id, ip_address, user_agent, expires_at, device_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, user_id, '127.0.0.1', 'TestAgent/1.0', expires_at, 'desktop'))
        
        db.commit()
        db.close()
        
        return session_id
    
    def create_test_activity(self, session_id, user_id, page_url='/test', count=1):
        """Helper to create test activity records"""
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        for i in range(count):
            timestamp = datetime.utcnow() - timedelta(minutes=i)
            cursor.execute('''
                INSERT INTO user_activity_log 
                (session_id, user_id, timestamp, page_url, action_type, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, timestamp, f'{page_url}/{i}', 'page_view', '127.0.0.1'))
        
        db.commit()
        db.close()
    
    # Test Activity Tracking Middleware
    
    def test_activity_tracking_middleware_initialization(self):
        """Test that activity tracker initializes correctly"""
        self.assertIsNotNone(self.tracker)
        self.assertIsNotNone(self.tracker.activity_queue)
        self.assertTrue(self.tracker.is_running)
        self.assertEqual(self.tracker.db_path, self.test_db_path)
    
    def test_should_skip_tracking(self):
        """Test path exclusion logic"""
        # Should skip static files
        self.assertTrue(self.tracker.should_skip_tracking('/static/css/style.css'))
        self.assertTrue(self.tracker.should_skip_tracking('/favicon.ico'))
        self.assertTrue(self.tracker.should_skip_tracking('/api/activity/track'))
        
        # Should not skip regular pages
        self.assertFalse(self.tracker.should_skip_tracking('/pages/home.html'))
        self.assertFalse(self.tracker.should_skip_tracking('/api/devices'))
    
    def test_device_type_detection(self):
        """Test device type detection from user agent"""
        # Mobile detection
        mobile_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        self.assertEqual(self.tracker.get_device_type(mobile_agent), 'mobile')
        
        # Tablet detection
        tablet_agent = 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)'
        self.assertEqual(self.tracker.get_device_type(tablet_agent), 'tablet')
        
        # Desktop detection
        desktop_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'
        self.assertEqual(self.tracker.get_device_type(desktop_agent), 'desktop')
        
        # Bot detection
        bot_agent = 'Googlebot/2.1 (+http://www.google.com/bot.html)'
        self.assertEqual(self.tracker.get_device_type(bot_agent), 'bot')
    
    def test_activity_queue_processing(self):
        """Test that activities are queued and processed"""
        # Create activity data
        activity_data = {
            'session_id': self.admin_session,
            'user_id': 1,
            'timestamp': datetime.utcnow().isoformat(),
            'page_url': '/test/page',
            'action_type': 'page_view',
            'ip_address': '127.0.0.1',
            'user_agent': 'TestAgent/1.0',
            'device_type': 'desktop'
        }
        
        # Queue activity
        self.tracker.activity_queue.put(activity_data)
        
        # Process batch
        self.tracker.process_activity_batch([activity_data])
        
        # Verify activity was logged
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM user_activity_log WHERE session_id = ?', 
                      (self.admin_session,))
        count = cursor.fetchone()[0]
        db.close()
        
        self.assertEqual(count, 1)
    
    # Test Dashboard API Endpoints
    
    def test_get_current_sessions_admin_only(self):
        """Test that current sessions endpoint requires admin role"""
        # Test without authentication
        response = self.client.get('/api/admin/activity/current')
        self.assertEqual(response.status_code, 401)
        
        # Test with non-admin user
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.create_test_session('viewer')
            sess['user_id'] = 4  # viewer user
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 4, 'username': 'viewer', 'role': 'viewer'}
            response = self.client.get('/api/admin/activity/current')
            self.assertEqual(response.status_code, 403)
    
    def test_get_current_sessions_success(self):
        """Test successful retrieval of current sessions"""
        # Set up admin session
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Create some test sessions
            self.create_test_session('manager')
            self.create_test_session('driver')
            
            response = self.client.get('/api/admin/activity/current')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('sessions', data['data'])
            self.assertIn('summary', data['data'])
            self.assertGreaterEqual(len(data['data']['sessions']), 3)  # admin, manager, driver
    
    def test_get_current_sessions_with_filters(self):
        """Test session filtering and sorting"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Test role filter
            response = self.client.get('/api/admin/activity/current?role_filter=admin')
            data = json.loads(response.data)
            self.assertTrue(all(s['role'] == 'admin' for s in data['data']['sessions']))
            
            # Test sorting
            response = self.client.get('/api/admin/activity/current?sort=username&order=asc')
            data = json.loads(response.data)
            usernames = [s['username'] for s in data['data']['sessions']]
            self.assertEqual(usernames, sorted(usernames))
    
    def test_track_activity_endpoint(self):
        """Test activity tracking endpoint"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            activity_data = {
                'session_id': self.admin_session,
                'page_url': '/pages/test.html',
                'page_title': 'Test Page',
                'action_type': 'page_view',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = self.client.post('/api/activity/track',
                                       data=json.dumps(activity_data),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
    
    def test_get_user_history(self):
        """Test user activity history retrieval"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Create test activity
            self.create_test_activity(self.admin_session, 1, '/pages/test', 5)
            
            response = self.client.get('/api/admin/activity/history/1')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['user']['id'], 1)
            self.assertGreaterEqual(len(data['data']['activities']), 5)
    
    def test_get_activity_summary(self):
        """Test activity summary generation"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Create test data
            self.create_test_activity(self.admin_session, 1, '/pages/home', 10)
            
            response = self.client.get('/api/admin/activity/summary?period=day')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('metrics', data['data'])
            self.assertIn('top_pages', data['data'])
    
    # Test Alert Management
    
    def test_alert_generation_concurrent_sessions(self):
        """Test alert generation for concurrent sessions"""
        # Create multiple sessions for same user
        session1 = self.create_test_session('admin')
        session2 = self.create_test_session('admin')
        session3 = self.create_test_session('admin')
        
        # Create activity to trigger alert check
        activity = {
            'session_id': session3,
            'user_id': 1,
            'timestamp': datetime.utcnow().isoformat(),
            'page_url': '/test'
        }
        
        db = sqlite3.connect(self.test_db_path)
        self.tracker.check_activity_alerts([activity], db)
        
        # Check if alert was created
        cursor = db.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM activity_alerts 
            WHERE alert_type = 'concurrent_sessions' AND user_id = 1
        ''')
        count = cursor.fetchone()[0]
        db.close()
        
        self.assertGreater(count, 0)
    
    def test_alert_generation_rapid_navigation(self):
        """Test alert generation for rapid navigation"""
        # Create many activities in short time
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        for i in range(25):  # More than threshold of 20
            cursor.execute('''
                INSERT INTO user_activity_log 
                (session_id, user_id, timestamp, page_url, action_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.admin_session, 1, datetime.utcnow(), f'/page{i}', 'page_view'))
        
        db.commit()
        
        # Check alerts
        activity = {
            'session_id': self.admin_session,
            'user_id': 1,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.tracker.check_activity_alerts([activity], db)
        
        cursor.execute('''
            SELECT COUNT(*) FROM activity_alerts 
            WHERE alert_type = 'rapid_navigation' AND user_id = 1
        ''')
        count = cursor.fetchone()[0]
        db.close()
        
        self.assertGreater(count, 0)
    
    def test_get_alerts(self):
        """Test alert retrieval endpoint"""
        # Create test alert
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO activity_alerts 
            (alert_type, severity, user_id, session_id, description)
            VALUES (?, ?, ?, ?, ?)
        ''', ('test_alert', 'warning', 1, self.admin_session, 'Test alert'))
        db.commit()
        db.close()
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            response = self.client.get('/api/admin/activity/alerts')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertGreaterEqual(len(data['data']['alerts']), 1)
    
    def test_acknowledge_alert(self):
        """Test alert acknowledgment"""
        # Create test alert
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO activity_alerts 
            (alert_type, severity, user_id, session_id, description)
            VALUES (?, ?, ?, ?, ?)
        ''', ('test_alert', 'warning', 1, self.admin_session, 'Test alert'))
        alert_id = cursor.lastrowid
        db.commit()
        db.close()
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            response = self.client.post(f'/api/admin/activity/alerts/{alert_id}/acknowledge')
            self.assertEqual(response.status_code, 200)
            
            # Verify alert was acknowledged
            db = sqlite3.connect(self.test_db_path)
            cursor = db.cursor()
            cursor.execute('SELECT status, acknowledged_by FROM activity_alerts WHERE id = ?', 
                          (alert_id,))
            result = cursor.fetchone()
            db.close()
            
            self.assertEqual(result[0], 'acknowledged')
            self.assertEqual(result[1], 1)
    
    # Test Session Management
    
    def test_terminate_session(self):
        """Test session termination endpoint"""
        # Create session to terminate
        target_session = self.create_test_session('driver')
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            response = self.client.post(f'/api/admin/sessions/{target_session}/terminate')
            self.assertEqual(response.status_code, 200)
            
            # Verify session was terminated
            db = sqlite3.connect(self.test_db_path)
            cursor = db.cursor()
            cursor.execute('SELECT expires_at FROM sessions WHERE id = ?', (target_session,))
            result = cursor.fetchone()
            db.close()
            
            # Session should be expired
            expires_at = datetime.fromisoformat(result[0].replace('Z', '+00:00'))
            self.assertLess(expires_at, datetime.utcnow())
    
    # Test Data Validation
    
    def test_invalid_timestamp_handling(self):
        """Test handling of invalid timestamps"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Invalid timestamp format
            activity_data = {
                'session_id': self.admin_session,
                'page_url': '/test',
                'timestamp': 'invalid-timestamp'
            }
            
            response = self.client.post('/api/activity/track',
                                       data=json.dumps(activity_data),
                                       content_type='application/json')
            
            # Should handle gracefully
            self.assertIn(response.status_code, [400, 201])  # May validate or use current time
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Missing page_url
            activity_data = {
                'session_id': self.admin_session,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = self.client.post('/api/activity/track',
                                       data=json.dumps(activity_data),
                                       content_type='application/json')
            
            self.assertEqual(response.status_code, 400)
    
    # Test Performance Requirements
    
    def test_response_time_dashboard_api(self):
        """Test that dashboard API responds within 500ms"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Create test data
            for i in range(50):
                self.create_test_session(f'user{i}')
            
            start_time = time.time()
            response = self.client.get('/api/admin/activity/current')
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            self.assertLess((end_time - start_time) * 1000, 500)  # Less than 500ms
    
    def test_batch_processing_performance(self):
        """Test batch processing of activity records"""
        # Create large batch
        batch = []
        for i in range(100):
            batch.append({
                'session_id': self.admin_session,
                'user_id': 1,
                'timestamp': datetime.utcnow().isoformat(),
                'page_url': f'/page{i}',
                'action_type': 'page_view',
                'ip_address': '127.0.0.1',
                'user_agent': 'TestAgent/1.0',
                'device_type': 'desktop'
            })
        
        start_time = time.time()
        self.tracker.process_activity_batch(batch)
        end_time = time.time()
        
        # Should process 100 records quickly
        self.assertLess(end_time - start_time, 1.0)  # Less than 1 second
        
        # Verify all records were inserted
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM user_activity_log WHERE session_id = ?',
                      (self.admin_session,))
        count = cursor.fetchone()[0]
        db.close()
        
        self.assertEqual(count, 100)
    
    # Test Audit Logging
    
    def test_audit_logging_for_monitoring_access(self):
        """Test that monitoring access is logged"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
            sess['user_id'] = 1
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Access monitoring endpoint
            response = self.client.get('/api/admin/activity/current')
            
            # Check audit log
            db = sqlite3.connect(self.test_db_path)
            cursor = db.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM audit_log 
                WHERE user_id = 1 AND resource_type = 'activity_monitor'
            ''')
            count = cursor.fetchone()[0]
            db.close()
            
            # Should have audit entry
            self.assertGreater(count, 0)


class TestActivityTrackerUnit(unittest.TestCase):
    """Unit tests for ActivityTracker class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_db_fd, self.test_db_path = tempfile.mkstemp(suffix='.db')
        TestActivityMonitoringAPI.setup_test_database.__func__(self)
        
        # Create mock app
        self.mock_app = MagicMock()
        self.mock_app.logger = MagicMock()
        
        # Initialize tracker with test database
        self.tracker = ActivityTracker(self.mock_app, self.test_db_path)
    
    def tearDown(self):
        """Clean up test environment"""
        self.tracker.shutdown()
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
    def test_cache_management(self):
        """Test in-memory cache functionality"""
        # Add to cache
        self.tracker.update_session_cache('session1', {
            'user_id': 1,
            'timestamp': datetime.utcnow().isoformat(),
            'page_url': '/test',
            'device_type': 'desktop'
        })
        
        self.assertIn('session1', self.tracker.cache)
        
        # Test cache cleanup
        # Artificially age the cache entry
        self.tracker.cache['session1']['updated_at'] = time.time() - 100
        self.tracker._cleanup_cache()
        
        # Old entry should be removed
        self.assertNotIn('session1', self.tracker.cache)
    
    def test_config_cache_refresh(self):
        """Test configuration cache refresh"""
        # Initial config load
        value = self.tracker.get_config('activity_monitoring_enabled')
        self.assertEqual(value, 'true')
        
        # Force cache expiry
        self.tracker.config_cache_time = 0
        
        # Should refresh on next access
        value = self.tracker.get_config('activity_monitoring_enabled')
        self.assertEqual(value, 'true')
        self.assertGreater(self.tracker.config_cache_time, 0)
    
    def test_background_worker_thread(self):
        """Test background worker thread operation"""
        # Verify worker thread is running
        self.assertIsNotNone(self.tracker.worker_thread)
        self.assertTrue(self.tracker.worker_thread.is_alive())
        
        # Queue some activities
        for i in range(5):
            self.tracker.activity_queue.put({
                'session_id': f'session{i}',
                'user_id': 1,
                'timestamp': datetime.utcnow().isoformat(),
                'page_url': f'/page{i}',
                'action_type': 'page_view',
                'ip_address': '127.0.0.1',
                'user_agent': 'TestAgent',
                'device_type': 'desktop'
            })
        
        # Give worker time to process
        time.sleep(2)
        
        # Check that queue was processed
        self.assertEqual(self.tracker.activity_queue.qsize(), 0)
    
    def test_cleanup_scheduler(self):
        """Test cleanup scheduler thread"""
        # Verify cleanup thread is running
        self.assertIsNotNone(self.tracker.cleanup_thread)
        self.assertTrue(self.tracker.cleanup_thread.is_alive())
        
        # Add old data to test cleanup
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        old_date = datetime.utcnow() - timedelta(days=100)
        cursor.execute('''
            INSERT INTO user_activity_log 
            (session_id, user_id, timestamp, page_url)
            VALUES (?, ?, ?, ?)
        ''', ('old_session', 1, old_date, '/old_page'))
        
        db.commit()
        db.close()
        
        # Run cleanup
        self.tracker.cleanup_old_data()
        
        # Verify old data was removed
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM user_activity_log WHERE session_id = ?',
                      ('old_session',))
        count = cursor.fetchone()[0]
        db.close()
        
        self.assertEqual(count, 0)
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown of tracker"""
        # Create new tracker for shutdown test
        tracker = ActivityTracker(self.mock_app, self.test_db_path)
        
        # Verify it's running
        self.assertTrue(tracker.is_running)
        
        # Shutdown
        tracker.shutdown()
        
        # Verify shutdown
        self.assertFalse(tracker.is_running)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)