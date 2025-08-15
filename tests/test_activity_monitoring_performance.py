#!/usr/bin/env python3
"""
Performance Test Suite for User Activity Monitoring System
Tests tracking overhead, dashboard performance, scalability, and resource usage
"""

import unittest
import json
import sqlite3
import tempfile
import os
import sys
import time
import threading
import random
import psutil
import gc
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock
import statistics

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app
from activity_tracker import ActivityTracker
from auth import hash_password

class TestActivityMonitoringPerformance(unittest.TestCase):
    """Performance test suite for Activity Monitoring system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_db_fd, cls.test_db_path = tempfile.mkstemp(suffix='.db')
        cls.setup_test_database()
        cls.performance_results = {}
    
    @classmethod
    def tearDownClass(cls):
        """Clean up and report results"""
        os.close(cls.test_db_fd)
        os.unlink(cls.test_db_path)
        
        # Print performance summary
        print("\n" + "="*50)
        print("PERFORMANCE TEST RESULTS SUMMARY")
        print("="*50)
        for test_name, metrics in cls.performance_results.items():
            print(f"\n{test_name}:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value}")
    
    @classmethod
    def setup_test_database(cls):
        """Initialize test database with performance testing schema"""
        db = sqlite3.connect(cls.test_db_path)
        db.execute('PRAGMA journal_mode=WAL')  # Enable WAL for better concurrency
        db.execute('PRAGMA synchronous=NORMAL')
        db.execute('PRAGMA cache_size=10000')
        db.execute('PRAGMA temp_store=MEMORY')
        
        cursor = db.cursor()
        
        # Create all necessary tables
        cursor.executescript('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
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
            );
            
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
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            
            CREATE TABLE activity_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id INTEGER,
                session_id TEXT,
                description TEXT NOT NULL,
                metadata TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
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
            );
            
            CREATE TABLE system_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT
            );
            
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Performance-optimized indexes
            CREATE INDEX idx_sessions_user_expires ON sessions(user_id, expires_at);
            CREATE INDEX idx_sessions_last_activity ON sessions(last_activity DESC);
            CREATE INDEX idx_activity_user_time ON user_activity_log(user_id, timestamp DESC);
            CREATE INDEX idx_activity_session ON user_activity_log(session_id, timestamp DESC);
            CREATE INDEX idx_activity_timestamp ON user_activity_log(timestamp DESC);
            CREATE INDEX idx_activity_page ON user_activity_log(page_url);
            CREATE INDEX idx_alerts_status ON activity_alerts(status, created_at DESC);
            CREATE INDEX idx_alerts_user ON activity_alerts(user_id, created_at DESC);
            
            -- Create view for performance testing
            CREATE VIEW active_sessions_view AS
            SELECT 
                s.id as session_id,
                s.user_id,
                u.username,
                u.display_name,
                u.role,
                s.created_at as login_time,
                s.last_activity,
                s.last_page,
                s.activity_count,
                s.device_type,
                CASE
                    WHEN julianday('now') - julianday(s.last_activity) < 0.003472 THEN 'active'
                    WHEN julianday('now') - julianday(s.last_activity) < 0.010417 THEN 'idle'
                    ELSE 'warning'
                END as status
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.expires_at > datetime('now');
            
            INSERT INTO system_config (key, value) VALUES
            ('activity_monitoring_enabled', 'true'),
            ('activity_retention_days', '90'),
            ('activity_alert_concurrent_sessions_threshold', '2'),
            ('activity_alert_rapid_navigation_threshold', '20');
        ''')
        
        # Create test users for load testing
        test_users = []
        for i in range(100):
            username = f'user{i}'
            role = random.choice(['admin', 'manager', 'driver', 'viewer'])
            test_users.append((
                username,
                f'User {i}',
                f'{username}@test.com',
                hash_password(f'Pass{i}!'),
                role
            ))
        
        cursor.executemany('''
            INSERT INTO users (username, display_name, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        ''', test_users)
        
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
        
        # Clear any existing data
        self.cleanup_test_data()
    
    def tearDown(self):
        """Clean up after each test"""
        self.app_context.pop()
        gc.collect()  # Force garbage collection
    
    def cleanup_test_data(self):
        """Clean up test data between tests"""
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('DELETE FROM user_activity_log')
        cursor.execute('DELETE FROM activity_alerts')
        cursor.execute('DELETE FROM sessions')
        db.commit()
        db.close()
    
    def create_test_sessions(self, count):
        """Create multiple test sessions"""
        import uuid
        sessions = []
        
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        for i in range(count):
            session_id = str(uuid.uuid4())
            user_id = (i % 100) + 1  # Cycle through users
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            cursor.execute('''
                INSERT INTO sessions (id, user_id, ip_address, user_agent, expires_at, device_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, f'192.168.1.{i%255}', 'TestAgent/1.0', expires_at, 'desktop'))
            
            sessions.append((session_id, user_id))
        
        db.commit()
        db.close()
        
        return sessions
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure function execution time"""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        return (end - start) * 1000, result  # Return time in milliseconds
    
    # Tracking Overhead Tests
    
    def test_page_load_impact(self):
        """Test that activity tracking adds < 50ms to page loads"""
        print("\n[TEST] Measuring page load impact...")
        
        # Create test session
        import uuid
        session_id = str(uuid.uuid4())
        
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO sessions (id, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (session_id, 1, datetime.utcnow() + timedelta(hours=1)))
        db.commit()
        db.close()
        
        # Measure without tracking
        with self.client.session_transaction() as sess:
            sess['session_id'] = session_id
        
        times_without = []
        for _ in range(100):
            start = time.perf_counter()
            response = self.client.get('/api/health')  # Simple endpoint
            end = time.perf_counter()
            times_without.append((end - start) * 1000)
        
        avg_without = statistics.mean(times_without)
        
        # Initialize tracker
        tracker = ActivityTracker(app.app, self.test_db_path)
        
        # Measure with tracking
        times_with = []
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'user1', 'role': 'admin'}
            
            for _ in range(100):
                start = time.perf_counter()
                tracker.track_activity()  # Simulate tracking
                response = self.client.get('/api/health')
                end = time.perf_counter()
                times_with.append((end - start) * 1000)
        
        avg_with = statistics.mean(times_with)
        impact = avg_with - avg_without
        
        # Store results
        self.__class__.performance_results['page_load_impact'] = {
            'avg_without_tracking_ms': round(avg_without, 2),
            'avg_with_tracking_ms': round(avg_with, 2),
            'impact_ms': round(impact, 2),
            'requirement': '< 50ms',
            'passed': impact < 50
        }
        
        print(f"  Impact: {impact:.2f}ms (Requirement: < 50ms)")
        self.assertLess(impact, 50, f"Tracking impact {impact:.2f}ms exceeds 50ms limit")
    
    def test_activity_queue_throughput(self):
        """Test activity queue processing throughput"""
        print("\n[TEST] Measuring activity queue throughput...")
        
        tracker = ActivityTracker(app.app, self.test_db_path)
        
        # Generate test activities
        activities = []
        for i in range(1000):
            activities.append({
                'session_id': f'session_{i}',
                'user_id': (i % 100) + 1,
                'timestamp': datetime.utcnow().isoformat(),
                'page_url': f'/page/{i}',
                'action_type': 'page_view',
                'ip_address': f'192.168.1.{i%255}',
                'user_agent': 'TestAgent/1.0',
                'device_type': 'desktop'
            })
        
        # Measure queue processing
        start = time.perf_counter()
        
        for activity in activities:
            tracker.activity_queue.put_nowait(activity)
        
        # Process in batches
        batch_size = 100
        for i in range(0, len(activities), batch_size):
            batch = activities[i:i+batch_size]
            tracker.process_activity_batch(batch)
        
        end = time.perf_counter()
        
        total_time = (end - start) * 1000
        throughput = len(activities) / (total_time / 1000)
        
        self.__class__.performance_results['queue_throughput'] = {
            'activities_processed': len(activities),
            'total_time_ms': round(total_time, 2),
            'throughput_per_second': round(throughput, 0),
            'requirement': '> 100/s',
            'passed': throughput > 100
        }
        
        print(f"  Throughput: {throughput:.0f} activities/second")
        self.assertGreater(throughput, 100, "Queue throughput below 100 activities/second")
    
    # Dashboard Performance Tests
    
    def test_dashboard_initial_load_time(self):
        """Test dashboard loads in < 2 seconds with data"""
        print("\n[TEST] Measuring dashboard initial load time...")
        
        # Create test data
        sessions = self.create_test_sessions(100)
        
        # Create activity records
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        for session_id, user_id in sessions[:50]:  # Half the sessions have activity
            for j in range(10):  # 10 activities per session
                cursor.execute('''
                    INSERT INTO user_activity_log (session_id, user_id, page_url, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, user_id, f'/page/{j}', datetime.utcnow() - timedelta(minutes=j)))
        
        db.commit()
        db.close()
        
        # Create admin session
        admin_session = self.create_test_sessions(1)[0][0]
        
        with self.client.session_transaction() as sess:
            sess['session_id'] = admin_session
        
        with patch('app.get_current_user') as mock_user:
            mock_user.return_value = {'id': 1, 'username': 'admin', 'role': 'admin'}
            
            # Measure dashboard load time
            load_times = []
            
            for _ in range(10):
                start = time.perf_counter()
                response = self.client.get('/api/admin/activity/current')
                end = time.perf_counter()
                
                load_times.append((end - start) * 1000)
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
        
        avg_load_time = statistics.mean(load_times)
        max_load_time = max(load_times)
        
        self.__class__.performance_results['dashboard_load'] = {
            'avg_load_time_ms': round(avg_load_time, 2),
            'max_load_time_ms': round(max_load_time, 2),
            'sessions_loaded': 100,
            'requirement': '< 2000ms',
            'passed': max_load_time < 2000
        }
        
        print(f"  Average load time: {avg_load_time:.2f}ms")
        print(f"  Max load time: {max_load_time:.2f}ms")
        self.assertLess(max_load_time, 2000, "Dashboard load time exceeds 2 seconds")
    
    def test_concurrent_user_handling(self):
        """Test system handles 100+ concurrent users"""
        print("\n[TEST] Testing concurrent user handling...")
        
        # Create sessions for concurrent users
        sessions = self.create_test_sessions(150)
        
        # Simulate concurrent requests
        def make_request(session_info):
            session_id, user_id = session_info
            
            with app.app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['session_id'] = session_id
                
                with patch('app.get_current_user') as mock_user:
                    mock_user.return_value = {
                        'id': user_id,
                        'username': f'user{user_id}',
                        'role': 'admin'
                    }
                    
                    start = time.perf_counter()
                    response = client.get('/api/admin/activity/current')
                    end = time.perf_counter()
                    
                    return {
                        'status': response.status_code,
                        'time_ms': (end - start) * 1000,
                        'success': response.status_code == 200
                    }
        
        # Execute concurrent requests
        results = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(make_request, session) for session in sessions[:100]]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        successful = sum(1 for r in results if r['success'])
        avg_time = statistics.mean(r['time_ms'] for r in results)
        max_time = max(r['time_ms'] for r in results)
        
        self.__class__.performance_results['concurrent_users'] = {
            'total_users': 100,
            'successful_requests': successful,
            'avg_response_time_ms': round(avg_time, 2),
            'max_response_time_ms': round(max_time, 2),
            'success_rate': f'{(successful/100)*100:.1f}%',
            'passed': successful >= 95  # 95% success rate
        }
        
        print(f"  Successful requests: {successful}/100")
        print(f"  Average response time: {avg_time:.2f}ms")
        self.assertGreaterEqual(successful, 95, "Failed to handle 100 concurrent users")
    
    # Scalability Tests
    
    def test_large_dataset_performance(self):
        """Test performance with 10,000+ activity records"""
        print("\n[TEST] Testing large dataset performance...")
        
        # Create large dataset
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        # Batch insert for efficiency
        activities = []
        sessions = self.create_test_sessions(100)
        
        for i in range(10000):
            session_id, user_id = sessions[i % 100]
            activities.append((
                session_id,
                user_id,
                datetime.utcnow() - timedelta(minutes=i),
                f'/page/{i % 50}',
                'page_view',
                f'192.168.1.{i % 255}'
            ))
        
        cursor.executemany('''
            INSERT INTO user_activity_log 
            (session_id, user_id, timestamp, page_url, action_type, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', activities)
        
        db.commit()
        
        # Test query performance
        query_times = []
        
        # Test various queries
        queries = [
            "SELECT COUNT(*) FROM user_activity_log",
            "SELECT * FROM user_activity_log WHERE user_id = 1 ORDER BY timestamp DESC LIMIT 100",
            "SELECT page_url, COUNT(*) as count FROM user_activity_log GROUP BY page_url ORDER BY count DESC LIMIT 10",
            "SELECT * FROM active_sessions_view"
        ]
        
        for query in queries:
            start = time.perf_counter()
            cursor.execute(query)
            cursor.fetchall()
            end = time.perf_counter()
            query_times.append((end - start) * 1000)
        
        db.close()
        
        avg_query_time = statistics.mean(query_times)
        max_query_time = max(query_times)
        
        self.__class__.performance_results['large_dataset'] = {
            'total_records': 10000,
            'avg_query_time_ms': round(avg_query_time, 2),
            'max_query_time_ms': round(max_query_time, 2),
            'requirement': '< 500ms',
            'passed': max_query_time < 500
        }
        
        print(f"  Records: 10,000")
        print(f"  Average query time: {avg_query_time:.2f}ms")
        self.assertLess(max_query_time, 500, "Query performance degraded with large dataset")
    
    def test_alert_evaluation_performance(self):
        """Test alert evaluation completes < 500ms"""
        print("\n[TEST] Testing alert evaluation performance...")
        
        tracker = ActivityTracker(app.app, self.test_db_path)
        
        # Create test data for alert conditions
        sessions = self.create_test_sessions(10)
        
        # Create activities that trigger alerts
        activities = []
        for i in range(25):  # Rapid navigation scenario
            activities.append({
                'session_id': sessions[0][0],
                'user_id': sessions[0][1],
                'timestamp': datetime.utcnow().isoformat(),
                'page_url': f'/page/{i}'
            })
        
        # Measure alert evaluation time
        db = sqlite3.connect(self.test_db_path)
        
        eval_times = []
        for _ in range(10):
            start = time.perf_counter()
            tracker.check_activity_alerts(activities, db)
            end = time.perf_counter()
            eval_times.append((end - start) * 1000)
        
        db.close()
        
        avg_eval_time = statistics.mean(eval_times)
        max_eval_time = max(eval_times)
        
        self.__class__.performance_results['alert_evaluation'] = {
            'activities_evaluated': len(activities),
            'avg_eval_time_ms': round(avg_eval_time, 2),
            'max_eval_time_ms': round(max_eval_time, 2),
            'requirement': '< 500ms',
            'passed': max_eval_time < 500
        }
        
        print(f"  Average evaluation time: {avg_eval_time:.2f}ms")
        self.assertLess(max_eval_time, 500, "Alert evaluation exceeds 500ms")
    
    # Resource Usage Tests
    
    def test_memory_usage(self):
        """Test memory usage remains reasonable"""
        print("\n[TEST] Testing memory usage...")
        
        process = psutil.Process()
        
        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create tracker and load data
        tracker = ActivityTracker(app.app, self.test_db_path)
        sessions = self.create_test_sessions(1000)
        
        # Generate and process activities
        for i in range(5000):
            activity = {
                'session_id': sessions[i % 1000][0],
                'user_id': sessions[i % 1000][1],
                'timestamp': datetime.utcnow().isoformat(),
                'page_url': f'/page/{i}',
                'action_type': 'page_view',
                'ip_address': '127.0.0.1',
                'user_agent': 'TestAgent',
                'device_type': 'desktop'
            }
            tracker.update_session_cache(activity['session_id'], activity)
        
        # Measure memory after load
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - baseline_memory
        
        # Clean up
        tracker.shutdown()
        gc.collect()
        
        self.__class__.performance_results['memory_usage'] = {
            'baseline_mb': round(baseline_memory, 2),
            'peak_mb': round(peak_memory, 2),
            'increase_mb': round(memory_increase, 2),
            'sessions_cached': 1000,
            'requirement': '< 100MB increase',
            'passed': memory_increase < 100
        }
        
        print(f"  Memory increase: {memory_increase:.2f}MB")
        self.assertLess(memory_increase, 100, "Memory usage exceeds 100MB")
    
    def test_database_growth_rate(self):
        """Test database growth rate with activity data"""
        print("\n[TEST] Testing database growth rate...")
        
        # Get initial database size
        initial_size = os.path.getsize(self.test_db_path) / 1024 / 1024  # MB
        
        # Add activity data
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        sessions = self.create_test_sessions(100)
        
        # Add 1000 activity records
        for i in range(1000):
            session_id, user_id = sessions[i % 100]
            cursor.execute('''
                INSERT INTO user_activity_log 
                (session_id, user_id, page_url, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                user_id,
                f'/page/{i}',
                datetime.utcnow(),
                json.dumps({'test': 'data' * 10})  # Some metadata
            ))
        
        db.commit()
        db.close()
        
        # Get final size
        final_size = os.path.getsize(self.test_db_path) / 1024 / 1024  # MB
        growth = final_size - initial_size
        growth_per_record = (growth * 1024) / 1000  # KB per record
        
        self.__class__.performance_results['database_growth'] = {
            'initial_size_mb': round(initial_size, 2),
            'final_size_mb': round(final_size, 2),
            'growth_mb': round(growth, 2),
            'records_added': 1000,
            'kb_per_record': round(growth_per_record, 2),
            'daily_estimate_mb': round(growth_per_record * 100000 / 1024, 2),  # 100k records/day
            'passed': growth_per_record < 2  # Less than 2KB per record
        }
        
        print(f"  Growth: {growth:.2f}MB for 1000 records")
        print(f"  Per record: {growth_per_record:.2f}KB")
        self.assertLess(growth_per_record, 2, "Database growth exceeds 2KB per record")
    
    def test_cleanup_job_performance(self):
        """Test data cleanup job performance"""
        print("\n[TEST] Testing cleanup job performance...")
        
        # Create old data to clean up
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        old_date = datetime.utcnow() - timedelta(days=100)
        
        # Insert old activities
        for i in range(5000):
            cursor.execute('''
                INSERT INTO user_activity_log 
                (session_id, user_id, page_url, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (f'old_session_{i}', 1, f'/old/{i}', old_date))
        
        db.commit()
        
        # Measure cleanup time
        tracker = ActivityTracker(app.app, self.test_db_path)
        
        start = time.perf_counter()
        tracker.cleanup_old_data()
        end = time.perf_counter()
        
        cleanup_time = (end - start) * 1000
        
        # Verify cleanup worked
        cursor.execute('SELECT COUNT(*) FROM user_activity_log WHERE timestamp < ?', (old_date + timedelta(days=1),))
        remaining = cursor.fetchone()[0]
        
        db.close()
        
        self.__class__.performance_results['cleanup_job'] = {
            'records_cleaned': 5000,
            'cleanup_time_ms': round(cleanup_time, 2),
            'remaining_old_records': remaining,
            'requirement': '< 5000ms',
            'passed': cleanup_time < 5000 and remaining == 0
        }
        
        print(f"  Cleanup time: {cleanup_time:.2f}ms for 5000 records")
        self.assertLess(cleanup_time, 5000, "Cleanup job too slow")
        self.assertEqual(remaining, 0, "Cleanup job failed to remove old records")
    
    def test_index_effectiveness(self):
        """Test that database indexes improve query performance"""
        print("\n[TEST] Testing index effectiveness...")
        
        # Create test data
        sessions = self.create_test_sessions(100)
        
        db = sqlite3.connect(self.test_db_path)
        cursor = db.cursor()
        
        # Add activity data
        for i in range(5000):
            session_id, user_id = sessions[i % 100]
            cursor.execute('''
                INSERT INTO user_activity_log 
                (session_id, user_id, page_url, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user_id, f'/page/{i % 20}', 
                 datetime.utcnow() - timedelta(minutes=i)))
        
        db.commit()
        
        # Test queries that should use indexes
        indexed_queries = [
            ("SELECT * FROM user_activity_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (1,)),
            ("SELECT * FROM user_activity_log WHERE session_id = ?", (sessions[0][0],)),
            ("SELECT * FROM sessions WHERE last_activity > ?", (datetime.utcnow() - timedelta(hours=1),)),
            ("SELECT * FROM activity_alerts WHERE status = ? ORDER BY created_at DESC", ('pending',))
        ]
        
        query_times = []
        
        for query, params in indexed_queries:
            # Warm up cache
            cursor.execute(query, params)
            cursor.fetchall()
            
            # Measure
            start = time.perf_counter()
            cursor.execute(query, params)
            cursor.fetchall()
            end = time.perf_counter()
            
            query_times.append((end - start) * 1000)
        
        # Test without indexes (simulate)
        cursor.execute("EXPLAIN QUERY PLAN " + indexed_queries[0][0], indexed_queries[0][1])
        plan = cursor.fetchall()
        
        db.close()
        
        avg_indexed_time = statistics.mean(query_times)
        uses_index = any('USING INDEX' in str(row) for row in plan)
        
        self.__class__.performance_results['index_effectiveness'] = {
            'avg_indexed_query_ms': round(avg_indexed_time, 2),
            'uses_indexes': uses_index,
            'queries_tested': len(indexed_queries),
            'requirement': '< 10ms avg',
            'passed': avg_indexed_time < 10 and uses_index
        }
        
        print(f"  Average indexed query time: {avg_indexed_time:.2f}ms")
        print(f"  Indexes being used: {uses_index}")
        self.assertLess(avg_indexed_time, 10, "Indexed queries too slow")
        self.assertTrue(uses_index, "Queries not using indexes")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)