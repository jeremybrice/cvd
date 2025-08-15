#!/usr/bin/env python3
"""
Test script for user soft delete endpoints
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_endpoints():
    """Test the soft delete endpoints"""
    
    print("Testing user soft delete endpoints...")
    
    # Test get users endpoint
    try:
        response = requests.get(f'{BASE_URL}/api/users')
        print(f"GET /api/users: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {len(data.get('users', []))} users")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Error connecting to server: {e}")
        print("  Make sure Flask app is running on port 5000")
        return False
    
    # Test user lifecycle metrics
    try:
        response = requests.get(f'{BASE_URL}/api/metrics/user-lifecycle')
        print(f"GET /api/metrics/user-lifecycle: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  User counts: {data.get('user_counts', {})}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("Endpoint testing complete!")
    return True

if __name__ == '__main__':
    success = test_endpoints()
    if not success:
        print("\nTo run full tests, start the Flask app first:")
        print("python app.py")
        exit(1)