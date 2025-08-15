#!/usr/bin/env python3
"""
Test script for Activity Monitor Enhancement API endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/admin/activity"

# Test credentials (using admin)
LOGIN_URL = f"{BASE_URL}/api/auth/login"
CREDENTIALS = {
    "username": "admin",
    "password": "admin"
}

def login():
    """Login and get session"""
    session = requests.Session()
    response = session.post(LOGIN_URL, json=CREDENTIALS)
    if response.status_code == 200:
        print("✓ Login successful")
        return session
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_trends_endpoint(session):
    """Test /api/admin/activity/trends endpoint"""
    print("\n--- Testing Trends Endpoint ---")
    
    from datetime import datetime, timedelta
    
    # Test with date parameters
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "metrics": "active_users,page_views"
    }
    
    response = session.get(f"{API_BASE}/trends", params=params)
    print(f"GET /trends (7 days): {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Response time: {response.elapsed.total_seconds():.3f}s")
        print(f"  Data keys: {list(data.get('data', {}).keys())}")
        
        # Test with different date range
        start_date_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        params2 = {
            "start_date": start_date_30,
            "end_date": end_date,
            "metrics": "active_users,page_views,api_calls,avg_session"
        }
        response2 = session.get(f"{API_BASE}/trends", params=params2)
        print(f"GET /trends (30 days, all metrics): {response2.status_code}")
        print(f"  Response time: {response2.elapsed.total_seconds():.3f}s")
        
        return response.status_code == 200 and response2.status_code == 200
    else:
        print(f"  Error: {response.text}")
        return False

def test_export_endpoint(session):
    """Test /api/admin/activity/export endpoint"""
    print("\n--- Testing Export Endpoint ---")
    
    from datetime import datetime, timedelta
    
    # Test CSV export with date parameters
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    params = {
        "format": "csv",
        "start_date": start_date,
        "end_date": end_date
    }
    response = session.get(f"{API_BASE}/export", params=params)
    print(f"GET /export (CSV): {response.status_code}")
    
    if response.status_code == 200:
        print(f"  Response time: {response.elapsed.total_seconds():.3f}s")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Content size: {len(response.content)} bytes")
        
        # Test JSON export
        params["format"] = "json"
        response2 = session.get(f"{API_BASE}/export", params=params)
        print(f"GET /export (JSON): {response2.status_code}")
        print(f"  Response time: {response2.elapsed.total_seconds():.3f}s")
        
        return True
    else:
        print(f"  Error: {response.text}")
        return False

def test_health_endpoint(session):
    """Test /api/admin/activity/health endpoint"""
    print("\n--- Testing Health Endpoint ---")
    
    response = session.get(f"{API_BASE}/health")
    print(f"GET /health: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Response time: {response.elapsed.total_seconds():.3f}s")
        print(f"  Status: {data.get('status')}")
        print(f"  Database: {data.get('database')}")
        print(f"  Timestamp: {data.get('timestamp')}")
        return True
    else:
        print(f"  Error: {response.text}")
        return False

def test_current_users_endpoint(session):
    """Test /api/admin/activity/current endpoint"""
    print("\n--- Testing Current Users Endpoint ---")
    
    response = session.get(f"{API_BASE}/current")
    print(f"GET /current: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Response time: {response.elapsed.total_seconds():.3f}s")
        summary = data.get('data', {}).get('summary', {})
        print(f"  Total active: {summary.get('total_active', 0)}")
        print(f"  Total sessions: {len(data.get('data', {}).get('sessions', []))}")
        return True
    else:
        print(f"  Error: {response.text}")
        return False

def test_user_history_endpoint(session):
    """Test /api/admin/activity/history/<user_id> endpoint"""
    print("\n--- Testing User History Endpoint ---")
    
    # First get users to find an ID
    users_response = session.get(f"{BASE_URL}/api/users")
    if users_response.status_code == 200:
        users = users_response.json().get('users', [])
        if users:
            user_id = users[0]['id']
            username = users[0]['username']
            
            response = session.get(f"{API_BASE}/history/{user_id}")
            print(f"GET /history/{user_id} (user: {username}): {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Response time: {response.elapsed.total_seconds():.3f}s")
                activities = data.get('data', {}).get('activities', [])
                print(f"  Total activities: {len(activities)}")
                if activities:
                    print(f"  Latest activity: {activities[0].get('action_type', 'Unknown')}")
                return True
            else:
                print(f"  Error: {response.text}")
                return False
    
    print("  Could not test - no users found")
    return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Activity Monitor Enhancement API Tests")
    print("=" * 50)
    
    # Login
    session = login()
    if not session:
        print("\nCannot proceed without authentication")
        return
    
    # Run tests
    results = []
    results.append(("Trends", test_trends_endpoint(session)))
    results.append(("Export", test_export_endpoint(session)))
    results.append(("Health", test_health_endpoint(session)))
    results.append(("Current Users", test_current_users_endpoint(session)))
    results.append(("User History", test_user_history_endpoint(session)))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is ready.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check backend implementation.")

if __name__ == "__main__":
    main()