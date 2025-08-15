#!/usr/bin/env python3
"""
Test script to verify activity monitoring integration
"""

import sqlite3
import json
from datetime import datetime

def test_database_setup():
    """Test that all activity monitoring tables and views exist"""
    print("\n🔍 Testing Database Setup...")
    print("-" * 50)
    
    db = sqlite3.connect('cvd.db')
    cursor = db.cursor()
    
    # Check tables
    tables = [
        'user_activity_log',
        'activity_alerts',
        'activity_summary_daily',
        'system_config'
    ]
    
    for table in tables:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table,))
        
        if cursor.fetchone():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✓ Table {table}: exists ({count} records)")
        else:
            print(f"  ✗ Table {table}: missing")
            return False
    
    # Check views
    views = ['user_activity_current', 'active_sessions_view']
    
    for view in views:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name=?
        """, (view,))
        
        if cursor.fetchone():
            print(f"  ✓ View {view}: exists")
        else:
            print(f"  ✗ View {view}: missing")
            return False
    
    # Check session table columns
    cursor.execute("PRAGMA table_info(sessions)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = ['last_activity', 'last_page', 'activity_count', 'device_type']
    missing_columns = [col for col in required_columns if col not in columns]
    
    if missing_columns:
        print(f"  ✗ Missing columns in sessions table: {', '.join(missing_columns)}")
        return False
    else:
        print(f"  ✓ Sessions table has all required columns")
    
    db.close()
    return True

def test_configuration():
    """Test that activity monitoring configuration is set"""
    print("\n⚙️  Testing Configuration...")
    print("-" * 50)
    
    db = sqlite3.connect('cvd.db')
    cursor = db.cursor()
    
    # Check important config values
    configs = [
        'activity_monitoring_enabled',
        'activity_retention_days',
        'activity_session_idle_minutes'
    ]
    
    for config_key in configs:
        cursor.execute("""
            SELECT value FROM system_config WHERE key = ?
        """, (config_key,))
        
        result = cursor.fetchone()
        if result:
            print(f"  ✓ {config_key}: {result[0]}")
        else:
            print(f"  ✗ {config_key}: not found")
    
    db.close()
    return True

def test_active_sessions_view():
    """Test the active sessions view"""
    print("\n👥 Testing Active Sessions View...")
    print("-" * 50)
    
    db = sqlite3.connect('cvd.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    # Get active sessions
    sessions = cursor.execute("""
        SELECT * FROM active_sessions_view
        LIMIT 5
    """).fetchall()
    
    if sessions:
        print(f"  ✓ Found {len(sessions)} active session(s)")
        for session in sessions:
            print(f"    - User: {session['username']}, Role: {session['role']}, Status: {session['status']}")
    else:
        print("  ℹ No active sessions found (this is normal if no one is logged in)")
    
    db.close()
    return True

def test_api_endpoints():
    """Test that API endpoints are accessible"""
    print("\n🌐 Testing API Endpoints...")
    print("-" * 50)
    
    import requests
    
    # Test endpoints (without authentication for now)
    endpoints = [
        ('/api/health', 'GET'),
        ('/api/admin/activity/current', 'GET'),  # Will require auth
        ('/api/admin/activity/summary', 'GET'),  # Will require auth
    ]
    
    base_url = 'http://localhost:5000'
    
    for endpoint, method in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{endpoint}", timeout=2)
            else:
                response = requests.post(f"{base_url}{endpoint}", json={}, timeout=2)
            
            if response.status_code == 401:
                print(f"  ✓ {endpoint}: Protected (requires authentication)")
            elif response.status_code == 403:
                print(f"  ✓ {endpoint}: Protected (requires admin role)")
            elif response.status_code == 200:
                print(f"  ✓ {endpoint}: Accessible")
            else:
                print(f"  ⚠ {endpoint}: Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"  ⚠ Cannot connect to Flask server (ensure it's running on port 5000)")
            break
        except Exception as e:
            print(f"  ✗ {endpoint}: Error - {e}")
    
    return True

def create_test_activity():
    """Create some test activity data"""
    print("\n📝 Creating Test Activity Data...")
    print("-" * 50)
    
    db = sqlite3.connect('cvd.db')
    cursor = db.cursor()
    
    # Check if we have any test user
    cursor.execute("SELECT id, username FROM users WHERE username = 'admin'")
    user = cursor.fetchone()
    
    if not user:
        print("  ⚠ No admin user found to create test data")
        db.close()
        return False
    
    user_id = user[0]
    username = user[1]
    
    # Create a test session if needed
    cursor.execute("""
        SELECT id FROM sessions 
        WHERE user_id = ? AND expires_at > datetime('now')
        LIMIT 1
    """, (user_id,))
    
    session = cursor.fetchone()
    if session:
        session_id = session[0]
        print(f"  ℹ Using existing session for user '{username}'")
    else:
        print(f"  ℹ No active session for test data")
        db.close()
        return True
    
    # Add some test activity
    test_activities = [
        ('/pages/home-dashboard.html', 'page_view', 'Home Dashboard'),
        ('/api/devices', 'api_call', None),
        ('/pages/NSPT.html', 'page_view', 'Planogram Management'),
        ('/pages/service-orders.html', 'page_view', 'Service Orders')
    ]
    
    for url, action_type, title in test_activities:
        cursor.execute("""
            INSERT INTO user_activity_log 
            (session_id, user_id, page_url, page_title, action_type, 
             ip_address, user_agent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user_id, url, title, action_type,
              '127.0.0.1', 'Test Script/1.0', datetime.now()))
    
    db.commit()
    print(f"  ✓ Created {len(test_activities)} test activity records")
    
    # Update session activity count
    cursor.execute("""
        UPDATE sessions 
        SET activity_count = activity_count + ?,
            last_activity = ?,
            last_page = ?
        WHERE id = ?
    """, (len(test_activities), datetime.now(), 
          '/pages/service-orders.html', session_id))
    
    db.commit()
    db.close()
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("Activity Monitoring Integration Test")
    print("=" * 50)
    
    tests = [
        ("Database Setup", test_database_setup),
        ("Configuration", test_configuration),
        ("Active Sessions View", test_active_sessions_view),
        ("Test Activity Data", create_test_activity)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Restart the Flask application to enable activity tracking")
        print("2. Log in as an admin user")
        print("3. Navigate to /pages/admin/activity-monitor.html")
        print("4. Activity will be tracked automatically as users navigate")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
    print("=" * 50)

if __name__ == '__main__':
    main()