#!/usr/bin/env python3
"""
Test authentication flow
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_auth_flow():
    """Test the authentication flow"""
    session = requests.Session()
    
    print("="*50)
    print("Testing Authentication Flow")
    print("="*50)
    
    # Test 1: Access protected endpoint without auth
    print("\n1. Testing protected endpoint without authentication...")
    response = session.get(f"{BASE_URL}/devices")
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✓ Correctly rejected unauthorized request")
    else:
        print("✗ Expected 401, got:", response.status_code)
    
    # Test 2: Login with invalid credentials
    print("\n2. Testing login with invalid credentials...")
    response = session.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✓ Correctly rejected invalid credentials")
    else:
        print("✗ Expected 401, got:", response.status_code)
    
    # Test 3: Check if initial admin exists
    print("\n3. Checking for initial admin password file...")
    try:
        with open('initial_admin_password.txt', 'r') as f:
            content = f.read()
            print("✓ Found initial admin password file")
            # Extract password
            for line in content.split('\n'):
                if line.startswith('Password:'):
                    password = line.split(': ')[1].strip()
                    print(f"Admin password: {password}")
                    
                    # Test 4: Login with correct credentials
                    print("\n4. Testing login with correct credentials...")
                    response = session.post(f"{BASE_URL}/auth/login", json={
                        "username": "admin",
                        "password": password
                    })
                    print(f"Status: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print("✓ Login successful!")
                        print(f"User: {data['user']['username']} ({data['user']['role']})")
                        
                        # Test 5: Access protected endpoint with auth
                        print("\n5. Testing protected endpoint with authentication...")
                        response = session.get(f"{BASE_URL}/auth/current-user")
                        print(f"Status: {response.status_code}")
                        if response.status_code == 200:
                            print("✓ Successfully accessed protected endpoint")
                            print(f"Current user: {response.json()['user']}")
                        
                        # Test 6: Logout
                        print("\n6. Testing logout...")
                        response = session.post(f"{BASE_URL}/auth/logout")
                        print(f"Status: {response.status_code}")
                        if response.status_code == 200:
                            print("✓ Logout successful")
                            
                            # Test 7: Try to access protected endpoint after logout
                            print("\n7. Testing protected endpoint after logout...")
                            response = session.get(f"{BASE_URL}/auth/current-user")
                            print(f"Status: {response.status_code}")
                            if response.status_code == 401:
                                print("✓ Correctly rejected after logout")
                    else:
                        print("✗ Login failed:", response.json())
                    break
    except FileNotFoundError:
        print("✗ initial_admin_password.txt not found")
        print("Make sure the Flask app has been started at least once to create the admin user")

if __name__ == "__main__":
    test_auth_flow()