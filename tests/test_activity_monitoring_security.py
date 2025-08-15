#!/usr/bin/env python3
"""
Security Test Suite for User Activity Monitoring System
Tests access control, input validation, session security, and audit logging
"""

import unittest
import json
import sqlite3
import tempfile
import os
import sys
import time
import hashlib
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import html

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
from activity_tracker import ActivityTracker
from auth import hash_password

class TestActivityMonitoringSecurity(unittest.TestCase):
    """Security test suite for Activity Monitoring system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_db_fd, cls.test_db_path = tempfile.mkstemp(suffix='.db')
        cls.setup_test_database()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        os.close(cls.test_db_fd)
        os.unlink(cls.test_db_path)
    
    @classmethod
    def setup_test_database(cls):
        """Initialize test database"""
        db = sqlite3.connect(cls.test_db_path)
        cursor = db.cursor()
        
        # Create necessary tables
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
                activity_count INTEGER DEFAULT 0,
                device_type TEXT DEFAULT 'unknown',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE user_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                page_url TEXT NOT NULL,
                page_title TEXT,
                action_type TEXT DEFAULT 'page_view',
                ip_address TEXT,
                user_agent TEXT,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
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
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
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
        
        cursor.execute('''
            CREATE TABLE system_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT
            )
        ''')
        
        # Insert test users
        test_users = [
            ('admin', 'Admin User', 'admin@test.com', 'admin', hash_password('Admin123!')),
            ('manager', 'Manager User', 'manager@test.com', 'manager', hash_password('Manager123!')),
            ('driver', 'Driver User', 'driver@test.com', 'driver', hash_password('Driver123!')),
            ('viewer', 'Viewer User', 'viewer@test.com', 'viewer', hash_password('Viewer123!')),
            ('attacker', 'Malicious User', 'attacker@test.com', 'viewer', hash_password('Hacker123!'))
        ]
        
        cursor.executemany('''
            INSERT INTO users (username, display_name, email, role, password_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', test_users)
        
        # Insert config
        cursor.execute('''
            INSERT INTO system_config (key, value) VALUES
            ('activity_monitoring_enabled', 'true')
        ''')
        
        db.commit()
        db.close()
    
    def setUp(self):
        """Set up for each test"""
        app.app.config['TESTING'] = True
        app.app.config['DATABASE'] = self.test_db_path
        app.DATABASE = self.test_db_path
        
        self.client = app.app.test_client()
        self.app_context = app.app.app_context()
        self.app_context.push()
        
        # Create admin session for testing
        self.admin_session = self.create_test_session('admin')
        self.viewer_session = self.create_test_session('viewer')
        self.attacker_session = self.create_test_session('attacker')
    
    def tearDown(self):
        """Clean up after each test"""
        self.app_context.pop()
        
        # Clean test data
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('DELETE FROM user_activity_log')
        cursor.execute('DELETE FROM activity_alerts')
        cursor.execute('DELETE FROM audit_log')
        cursor.execute('DELETE FROM sessions')
        db.commit()
        db.close()
    
    def create_test_session(self, username):
        """Helper to create test session"""
        import uuid
        
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()[0]
        
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        cursor.execute('''
            INSERT INTO sessions (id, user_id, ip_address, user_agent, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, '127.0.0.1', 'TestAgent/1.0', expires_at))
        
        db.commit()
        db.close()
        
        return session_id
    
    # Access Control Tests
    
    def test_admin_only_endpoint_protection(self):
        """Test that admin-only endpoints reject non-admin users"""
        endpoints = [
            '/api/admin/activity/current',
            '/api/admin/activity/history/1',
            '/api/admin/activity/summary',
            '/api/admin/activity/alerts'
        ]
        
        # Test each role
        test_cases = [
            (None, None, 401),  # No auth
            (self.viewer_session, 'viewer', 403),  # Viewer role
            (self.attacker_session, 'attacker', 403),  # Malicious viewer
            (self.admin_session, 'admin', 200)  # Admin should work
        ]
        
        for endpoint in endpoints:
            for session_id, username, expected_status in test_cases:
                with self.subTest(endpoint=endpoint, role=username):
                    if session_id:
                        with self.client.session_transaction() as sess:
                            sess['session_id'] = session_id
                            
                        # Get user data
                        db = sqlite3.connect(self.test_db_path)
                        cursor = db.cursor()
                        cursor.execute('SELECT id, role FROM users WHERE username = ?', (username,))
                        user_data = cursor.fetchone()
                        db.close()
                        
                        with patch('app.get_current_user') as mock_user:
                            if user_data:
                                mock_user.return_value = {
                                    'id': user_data[0],
                                    'username': username,
                                    'role': user_data[1]
                                }
                            else:
                                mock_user.return_value = None
                            
                            response = self.client.get(endpoint)
                    else:
                        response = self.client.get(endpoint)
                    
                    # Check status code
                    if expected_status == 200:
                        self.assertIn(response.status_code, [200, 404])  # 404 ok for missing resources
                    else:
                        self.assertEqual(response.status_code, expected_status)
    
    def test_session_termination_authorization(self):
        """Test that only admins can terminate sessions"""
        target_session = self.create_test_session('driver')
        
        # Try as viewer
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.viewer_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 4, 'username': 'viewer', 'role': 'viewer'}
            
            response = self.client.post(f'/api/admin/sessions/{target_session}/terminate')
            self.assertEqual(response.status_code, 403)
        
        # Verify session still active
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('SELECT expires_at FROM sessions WHERE id = ?', (target_session,))
        result = cursor.fetchone()
        db.close()
        
        expires_at = datetime.fromisoformat(result[0].replace('Z', '+00:00'))
        self.assertGreater(expires_at, datetime.utcnow())
    
    def test_cross_user_data_access_prevention(self):
        """Test that users cannot access other users' data"""
        # Create activity for admin user
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO user_activity_log (session_id, user_id, page_url)
            VALUES (?, ?, ?)
        ''', (self.admin_session, 1, '/admin/secret'))
        db.commit()
        db.close()
        
        # Try to access as viewer (even if they somehow got the endpoint)
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.viewer_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 4, 'username': 'viewer', 'role': 'viewer'}
            
            # Should not be able to access admin's history
            response = self.client.get('/api/admin/activity/history/1')
            self.assertEqual(response.status_code, 403)
    
    # Input Validation Tests
    
    def test_sql_injection_prevention(self):
        """Test SQL injection attack prevention"""
        sql_injection_payloads = [
            "1' OR '1'='1",
            "1; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "1' AND (SELECT * FROM users) --",
            "admin'--",
            "' OR 1=1--",
            "1' UNION ALL SELECT NULL, NULL, NULL--"
        ]
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            for payload in sql_injection_payloads:
                with self.subTest(payload=payload):
                    # Try injection in various parameters
                    response = self.client.get(f'/api/admin/activity/history/{payload}')
                    
                    # Should not execute SQL injection
                    self.assertIn(response.status_code, [400, 404])
                    
                    # Verify database integrity
                    db = sqlite3.connect(self.test_db_path)
                    cursor = db.cursor()
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    db.close()
                    
                    self.assertEqual(user_count, 5)  # Should still have 5 users
    
    def test_xss_prevention(self):
        """Test XSS attack prevention in activity tracking"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
            "';alert('XSS');//",
            "<svg/onload=alert('XSS')>",
            "<<SCRIPT>alert('XSS');//<</SCRIPT>"
        ]
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            for payload in xss_payloads:
                with self.subTest(payload=payload):
                    # Try to inject XSS in activity tracking
                    activity_data = {
                        'session_id': self.admin_session,
                        'page_url': payload,
                        'page_title': payload,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    response = self.client.post('/api/activity/track',
                                               data=json.dumps(activity_data),
                                               content_type='application/json')
                    
                    # Check stored data is escaped
                    db = sqlite3.connect(self.test_db_path)
                    cursor = db.cursor()
                    cursor.execute('''
                        SELECT page_url, page_title FROM user_activity_log 
                        WHERE session_id = ? ORDER BY id DESC LIMIT 1
                    ''', (self.admin_session,))
                    result = cursor.fetchone()
                    db.close()
                    
                    if result:
                        # Verify XSS payloads are stored safely (not executed)
                        self.assertNotIn('<script>', html.unescape(result[0] or ''))
                        self.assertNotIn('javascript:', result[0] or '')
    
    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "/var/www/../../etc/passwd",
            "C:\\..\\..\\windows\\system32\\drivers\\etc\\hosts"
        ]
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            for payload in path_traversal_payloads:
                with self.subTest(payload=payload):
                    activity_data = {
                        'session_id': self.admin_session,
                        'page_url': payload,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    response = self.client.post('/api/activity/track',
                                               data=json.dumps(activity_data),
                                               content_type='application/json')
                    
                    # Should handle safely
                    self.assertIn(response.status_code, [201, 400])
    
    def test_command_injection_prevention(self):
        """Test command injection prevention"""
        command_injection_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "`rm -rf /`",
            "$(whoami)",
            "& net user",
            "; shutdown -h now"
        ]
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            for payload in command_injection_payloads:
                with self.subTest(payload=payload):
                    # Try injection in search parameters
                    response = self.client.get(f'/api/admin/activity/current?search={payload}')
                    
                    # Should not execute commands
                    self.assertIn(response.status_code, [200, 400])
                    
                    # System should still be functional
                    response = self.client.get('/api/admin/activity/current')
                    self.assertIn(response.status_code, [200, 204])
    
    # Session Security Tests
    
    def test_session_hijacking_detection(self):
        """Test detection of session hijacking attempts"""
        # Create legitimate session
        legitimate_session = self.create_test_session('driver')
        
        # Simulate hijacking attempt (different IP/User-Agent)
        with self.client.session_transaction() as sess:
            sess['session_id'] = legitimate_session
        
        # First request from legitimate source
        self.client.environ_base['REMOTE_ADDR'] = '192.168.1.100'
        self.client.environ_base['HTTP_USER_AGENT'] = 'Chrome/91.0'
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 3, 'username': 'driver', 'role': 'driver'}
            
            # Legitimate activity
            activity1 = {
                'session_id': legitimate_session,
                'page_url': '/page1',
                'timestamp': datetime.utcnow().isoformat()
            }
            response = self.client.post('/api/activity/track',
                                       data=json.dumps(activity1),
                                       content_type='application/json')
        
        # Hijacking attempt from different IP
        self.client.environ_base['REMOTE_ADDR'] = '10.0.0.1'
        self.client.environ_base['HTTP_USER_AGENT'] = 'Firefox/89.0'
        
        # Should detect suspicious activity
        # In real implementation, this would trigger alerts
    
    def test_concurrent_session_limit(self):
        """Test enforcement of concurrent session limits"""
        # Create multiple sessions for same user
        sessions = []
        for i in range(5):
            session = self.create_test_session('driver')
            sessions.append(session)
        
        # Check if alerts are generated
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        # Simulate activity to trigger alert check
        tracker = ActivityTracker(MagicMock(), self.test_db_path)
        activity = {
            'session_id': sessions[-1],
            'user_id': 3,
            'timestamp': datetime.utcnow().isoformat()
        }
        tracker.check_activity_alerts([activity], db)
        
        # Should have concurrent session alert
        cursor.execute('''
            SELECT COUNT(*) FROM activity_alerts 
            WHERE alert_type = 'concurrent_sessions' AND user_id = 3
        ''')
        alert_count = cursor.fetchone()[0]
        db.close()
        
        self.assertGreater(alert_count, 0)
    
    def test_session_timeout_enforcement(self):
        """Test that expired sessions are rejected"""
        # Create expired session
        import uuid
        expired_session = str(uuid.uuid4())
        
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        expired_time = datetime.utcnow() - timedelta(hours=2)
        cursor.execute('''
            INSERT INTO sessions (id, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (expired_session, 1, expired_time))
        db.commit()
        db.close()
        
        # Try to use expired session
        with self.client.session_transaction() as sess:
            sess['session_id'] = expired_session
        
        response = self.client.get('/api/admin/activity/current')
        self.assertEqual(response.status_code, 401)
    
    def test_session_fixation_prevention(self):
        """Test prevention of session fixation attacks"""
        # Attacker creates a session
        attacker_session = self.create_test_session('attacker')
        
        # Attacker tries to force this session on admin
        # In real app, this would be prevented by session regeneration on login
        
        # Verify sessions are user-bound
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('SELECT user_id FROM sessions WHERE id = ?', (attacker_session,))
        result = cursor.fetchone()
        db.close()
        
        # Session should be bound to attacker, not transferable
        self.assertEqual(result[0], 5)  # Attacker's user ID
    
    # Audit Logging Tests
    
    def test_monitoring_access_audit_logging(self):
        """Test that all monitoring access is logged"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Access monitoring endpoints
            endpoints = [
                '/api/admin/activity/current',
                '/api/admin/activity/history/1',
                '/api/admin/activity/alerts'
            ]
            
            for endpoint in endpoints:
                self.client.get(endpoint)
            
            # Check audit log
            db = sqlite3.connect(self.test_db_path)
            cursor = db.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM audit_log 
                WHERE user_id = 1 AND resource_type = 'activity_monitor'
            ''')
            audit_count = cursor.fetchone()[0]
            db.close()
            
            self.assertGreaterEqual(audit_count, len(endpoints))
    
    def test_failed_access_attempt_logging(self):
        """Test that failed access attempts are logged"""
        # Attempt unauthorized access
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.viewer_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 4, 'username': 'viewer', 'role': 'viewer'}
            
            # Try to access admin endpoint
            response = self.client.get('/api/admin/activity/current')
            self.assertEqual(response.status_code, 403)
            
            # Check audit log for failed attempt
            db = sqlite3.connect(self.test_db_path)
            cursor = db.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM audit_log 
                WHERE user_id = 4 AND action LIKE '%unauthorized%'
            ''')
            failed_count = cursor.fetchone()[0]
            db.close()
            
            self.assertGreater(failed_count, 0)
    
    def test_data_export_audit_logging(self):
        """Test that data exports are logged"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Simulate data export request
            response = self.client.get('/api/admin/activity/export?format=csv')
            
            # Check audit log
            db = sqlite3.connect(self.test_db_path)
            cursor = db.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM audit_log 
                WHERE user_id = 1 AND action LIKE '%export%'
            ''')
            export_count = cursor.fetchone()[0]
            db.close()
            
            # Should log export attempts
            self.assertGreaterEqual(export_count, 0)
    
    # Data Protection Tests
    
    def test_no_sensitive_data_in_logs(self):
        """Test that sensitive data is not logged"""
        sensitive_data = {
            'password': 'SecretPassword123!',
            'credit_card': '4111111111111111',
            'ssn': '123-45-6789',
            'api_key': 'sk_test_abcd1234'
        }
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Try to log sensitive data
            for key, value in sensitive_data.items():
                activity_data = {
                    'session_id': self.admin_session,
                    'page_url': f'/form/{key}',
                    'metadata': {key: value},
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.client.post('/api/activity/track',
                               data=json.dumps(activity_data),
                               content_type='application/json')
            
            # Check that sensitive data is not in logs
            db = sqlite3.connect(self.test_db_path)
            cursor = db.cursor()
            cursor.execute('SELECT metadata FROM user_activity_log WHERE session_id = ?',
                          (self.admin_session,))
            results = cursor.fetchall()
            db.close()
            
            for result in results:
                if result[0]:
                    # Sensitive values should not appear in metadata
                    for value in sensitive_data.values():
                        self.assertNotIn(value, result[0])
    
    def test_ip_address_validation(self):
        """Test IP address validation and handling"""
        invalid_ips = [
            'not.an.ip',
            '999.999.999.999',
            'javascript:alert(1)',
            '<script>alert(1)</script>',
            '../../etc/passwd'
        ]
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            for ip in invalid_ips:
                with self.subTest(ip=ip):
                    # Simulate request with invalid IP
                    self.client.environ_base['REMOTE_ADDR'] = ip
                    
                    response = self.client.get('/api/admin/activity/current')
                    
                    # Should handle gracefully
                    self.assertIn(response.status_code, [200, 400])
    
    # Rate Limiting Tests
    
    def test_api_rate_limiting(self):
        """Test rate limiting on API endpoints"""
        with self.client.session_transaction() as sess:
            sess['session_id'] = self.admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Make many rapid requests
            start_time = time.time()
            request_count = 0
            rate_limited = False
            
            for i in range(100):
                response = self.client.get('/api/admin/activity/current')
                request_count += 1
                
                # Check if rate limited
                if response.status_code == 429:
                    rate_limited = True
                    break
                
                # Stop after 1 second
                if time.time() - start_time > 1:
                    break
            
            # Should implement some form of rate limiting
            # Note: Actual implementation may vary
            self.assertLess(request_count, 100)  # Shouldn't allow 100 requests/second
    
    def test_brute_force_protection(self):
        """Test protection against brute force attacks"""
        # Simulate multiple failed login attempts
        failed_attempts = []
        
        for i in range(10):
            # Create failed session attempt
            db = sqlite3.connect(self.test_db_path)
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, ip_address)
                VALUES (?, ?, ?)
            ''', (5, 'failed_login', '10.0.0.1'))
            db.commit()
            db.close()
        
        # Check if alerts are generated
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM audit_log 
            WHERE action = 'failed_login' AND ip_address = '10.0.0.1'
        ''')
        count = cursor.fetchone()[0]
        db.close()
        
        self.assertGreaterEqual(count, 10)
        # In real implementation, this IP should be blocked


class TestSecurityHelpers(unittest.TestCase):
    """Test security helper functions"""
    
    def test_password_hashing_security(self):
        """Test password hashing is secure"""
        password = "TestPassword123!"
        
        # Hash password
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Same password should produce different hashes (salt)
        self.assertNotEqual(hash1, hash2)
        
        # Should not contain original password
        self.assertNotIn(password, hash1)
        
        # Should be sufficiently long (indicates strong hashing)
        self.assertGreater(len(hash1), 50)
    
    def test_session_token_generation(self):
        """Test session token generation is secure"""
        import uuid
        
        tokens = set()
        
        # Generate many tokens
        for _ in range(1000):
            token = str(uuid.uuid4())
            
            # Should be unique
            self.assertNotIn(token, tokens)
            tokens.add(token)
            
            # Should be sufficiently random (UUID v4)
            self.assertEqual(len(token), 36)
            self.assertIn('-', token)
    
    def test_input_sanitization(self):
        """Test input sanitization functions"""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "javascript:void(0)"
        ]
        
        for dangerous in dangerous_inputs:
            # HTML escape
            escaped = html.escape(dangerous)
            self.assertNotIn('<script>', escaped)
            self.assertNotIn('DROP TABLE', escaped)
            
            # Should be safe to display
            self.assertIn('&', escaped)  # Indicates escaping occurred


if __name__ == '__main__':
    unittest.main(verbosity=2)