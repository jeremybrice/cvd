#!/usr/bin/env python3
"""
Test script for Activity Trends API endpoints
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin"}

def login():
    """Login and get session cookie"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=ADMIN_CREDENTIALS
    )
    
    if response.status_code == 200:
        print("✓ Login successful")
        return response.cookies
    else:
        print(f"✗ Login failed: {response.text}")
        return None

def test_trends_endpoint(cookies):
    """Test the trends API endpoint"""
    # Test with last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "metrics": "unique_users,total_sessions,total_page_views"
    }
    
    print(f"\nTesting trends API with date range: {start_date} to {end_date}")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/activity/trends",
        params=params,
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Trends API returned successfully")
        print(f"  - Cached: {data.get('cached', False)}")
        print(f"  - Cache TTL: {data.get('cache_ttl', 0)} seconds")
        
        if 'data' in data and 'summary' in data['data']:
            summary = data['data']['summary']
            for metric, stats in summary.items():
                print(f"  - {metric}:")
                print(f"    * Average: {stats.get('average', 0)}")
                print(f"    * Trend: {stats.get('trend', 'unknown')}")
                if 'trend_analysis' in stats:
                    print(f"    * Direction: {stats['trend_analysis'].get('direction')}")
                    print(f"    * Confidence: {stats['trend_analysis'].get('confidence')}")
        
        return True
    else:
        print(f"✗ Trends API failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_export_endpoint(cookies):
    """Test the export API endpoint"""
    # Test CSV export
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "metrics": "unique_users,total_sessions",
        "format": "csv"
    }
    
    print(f"\nTesting export API (CSV) with date range: {start_date} to {end_date}")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/activity/export",
        params=params,
        cookies=cookies
    )
    
    if response.status_code == 200:
        print(f"✓ Export API returned successfully")
        print(f"  - Content-Type: {response.headers.get('Content-Type')}")
        print(f"  - Content-Length: {len(response.content)} bytes")
        
        # Show first few lines of CSV
        lines = response.text.split('\n')[:5]
        print("  - First few lines:")
        for line in lines:
            if line:
                print(f"    {line}")
        
        return True
    else:
        print(f"✗ Export API failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_health_endpoint(cookies):
    """Test the health check endpoint"""
    print("\nTesting health check API")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/activity/health",
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Health check returned successfully")
        print(f"  - Status: {data.get('status')}")
        
        if 'checks' in data:
            for check_name, check_data in data['checks'].items():
                print(f"  - {check_name}: {check_data.get('status', 'unknown')}")
        
        return True
    else:
        print(f"✗ Health check failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_cache_stats_endpoint(cookies):
    """Test the cache statistics endpoint"""
    print("\nTesting cache statistics API")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/activity/cache/stats",
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Cache stats returned successfully")
        
        if 'stats' in data:
            stats = data['stats']
            print(f"  - Cache size: {stats.get('size', 0)}/{stats.get('max_size', 0)}")
            print(f"  - Hit rate: {stats.get('hit_rate', 0)}%")
            print(f"  - Hits: {stats.get('hits', 0)}")
            print(f"  - Misses: {stats.get('misses', 0)}")
        
        return True
    else:
        print(f"✗ Cache stats failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Activity Trends API Test Suite")
    print("=" * 60)
    
    # Login first
    cookies = login()
    if not cookies:
        print("\n✗ Cannot proceed without authentication")
        return
    
    # Run tests
    tests_passed = 0
    tests_total = 4
    
    if test_trends_endpoint(cookies):
        tests_passed += 1
    
    if test_export_endpoint(cookies):
        tests_passed += 1
    
    if test_health_endpoint(cookies):
        tests_passed += 1
    
    if test_cache_stats_endpoint(cookies):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("✓ All tests passed!")
    else:
        print(f"✗ {tests_total - tests_passed} test(s) failed")
    
    print("=" * 60)

if __name__ == "__main__":
    main()