#!/usr/bin/env python3
"""
Comprehensive Test Suite for Admin User Hiding Functionality

This script tests all aspects of the admin user hiding implementation
to ensure the admin user is properly hidden and protected from all operations
while maintaining authentication capabilities.
"""

import requests
import json
import time
from datetime import datetime
import sys

class AdminHidingTestSuite:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.admin_session_cookies = None
        self.manager_session_cookies = None
        self.admin_user_id = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Print immediate feedback
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f'{self.base_url}/api/auth/login', 
                                       json={'username': 'admin', 'password': 'UU8fz433'})
            
            if response.status_code == 200:
                self.admin_session_cookies = self.session.cookies
                
                # Get current user to find admin user ID
                user_response = self.session.get(f'{self.base_url}/api/auth/current-user')
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    self.admin_user_id = user_data.get('user', {}).get('id')
                
                self.log_result("Admin Authentication", True, "Admin user successfully authenticated")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Failed to authenticate admin: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Error authenticating admin: {str(e)}")
            return False
    
    def create_test_manager(self):
        """Create a test manager user for testing"""
        try:
            # Ensure we're authenticated as admin
            if not self.admin_session_cookies:
                if not self.authenticate_admin():
                    return False
            
            test_manager_data = {
                'username': 'test_manager',
                'email': 'test_manager@test.com',
                'role': 'manager',
                'password': 'test123'
            }
            
            response = self.session.post(f'{self.base_url}/api/users', json=test_manager_data)
            
            if response.status_code in [201, 400]:  # 400 if already exists
                # Try to authenticate as the manager
                manager_session = requests.Session()
                auth_response = manager_session.post(f'{self.base_url}/api/auth/login',
                                                   json={'username': 'test_manager', 'password': 'test123'})
                
                if auth_response.status_code == 200:
                    self.manager_session_cookies = manager_session.cookies
                    self.log_result("Test Manager Creation", True, "Test manager user available and authenticated")
                    return True
                else:
                    self.log_result("Test Manager Creation", False, f"Could not authenticate test manager: {auth_response.status_code}")
                    return False
            else:
                self.log_result("Test Manager Creation", False, f"Failed to create test manager: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Test Manager Creation", False, f"Error creating test manager: {str(e)}")
            return False
    
    def test_user_listing_endpoints(self):
        """Test Phase 1.1: User listing endpoints"""
        print("\n=== Phase 1.1: User Listing Endpoints ===")
        
        # Test 1: GET /api/users - Verify admin not in response
        try:
            response = self.session.get(f'{self.base_url}/api/users')
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) == 0:
                    self.log_result("User List - Admin Hidden", True, "Admin user not present in user list")
                else:
                    self.log_result("User List - Admin Hidden", False, f"Admin user found in list: {admin_users}")
            else:
                self.log_result("User List - Admin Hidden", False, f"Failed to get users: {response.status_code}")
        except Exception as e:
            self.log_result("User List - Admin Hidden", False, f"Error: {str(e)}")
        
        # Test 2: GET /api/users with role filter
        try:
            response = self.session.get(f'{self.base_url}/api/users?role=admin')
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) == 0:
                    self.log_result("User List Filter - Admin Hidden", True, "Admin user not in role=admin filter")
                else:
                    self.log_result("User List Filter - Admin Hidden", False, f"Admin user found in role filter: {admin_users}")
            else:
                self.log_result("User List Filter - Admin Hidden", False, f"Failed to filter users: {response.status_code}")
        except Exception as e:
            self.log_result("User List Filter - Admin Hidden", False, f"Error: {str(e)}")
        
        # Test 3: GET /api/users with search
        try:
            response = self.session.get(f'{self.base_url}/api/users?search=admin')
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) == 0:
                    self.log_result("User Search - Admin Hidden", True, "Admin user not found in search")
                else:
                    self.log_result("User Search - Admin Hidden", False, f"Admin user found in search: {admin_users}")
            else:
                self.log_result("User Search - Admin Hidden", False, f"Failed to search users: {response.status_code}")
        except Exception as e:
            self.log_result("User Search - Admin Hidden", False, f"Error: {str(e)}")
    
    def test_individual_user_operations(self):
        """Test Phase 1.2: Individual user operations"""
        print("\n=== Phase 1.2: Individual User Operations ===")
        
        if not self.admin_user_id:
            self.log_result("Individual Operations Setup", False, "Admin user ID not available")
            return
        
        # Test 1: GET /api/users/{admin_id} - Should return 404
        try:
            response = self.session.get(f'{self.base_url}/api/users/{self.admin_user_id}')
            if response.status_code == 404:
                self.log_result("Get Admin User", True, "GET admin user correctly returns 404")
            else:
                self.log_result("Get Admin User", False, f"GET admin user returned: {response.status_code}")
        except Exception as e:
            self.log_result("Get Admin User", False, f"Error: {str(e)}")
        
        # Test 2: PUT /api/users/{admin_id} - Should return 404
        try:
            response = self.session.put(f'{self.base_url}/api/users/{self.admin_user_id}',
                                      json={'email': 'new_admin@test.com'})
            if response.status_code == 404:
                self.log_result("Update Admin User", True, "PUT admin user correctly returns 404")
            else:
                self.log_result("Update Admin User", False, f"PUT admin user returned: {response.status_code}")
        except Exception as e:
            self.log_result("Update Admin User", False, f"Error: {str(e)}")
        
        # Test 3: DELETE /api/users/{admin_id} - Should return 404
        try:
            response = self.session.delete(f'{self.base_url}/api/users/{self.admin_user_id}')
            if response.status_code == 404:
                self.log_result("Delete Admin User", True, "DELETE admin user correctly returns 404")
            else:
                self.log_result("Delete Admin User", False, f"DELETE admin user returned: {response.status_code}")
        except Exception as e:
            self.log_result("Delete Admin User", False, f"Error: {str(e)}")
    
    def test_user_creation_validation(self):
        """Test Phase 1.3: User creation validation"""
        print("\n=== Phase 1.3: User Creation Validation ===")
        
        # Test 1: Create user with username 'admin'
        try:
            response = self.session.post(f'{self.base_url}/api/users',
                                       json={'username': 'admin', 'email': 'admin2@test.com', 'role': 'manager'})
            if response.status_code == 400:
                data = response.json()
                if 'not available' in data.get('error', '').lower():
                    self.log_result("Create Admin Username", True, "Username 'admin' correctly rejected")
                else:
                    self.log_result("Create Admin Username", False, f"Wrong error message: {data.get('error')}")
            else:
                self.log_result("Create Admin Username", False, f"Username 'admin' not rejected: {response.status_code}")
        except Exception as e:
            self.log_result("Create Admin Username", False, f"Error: {str(e)}")
        
        # Test 2: Create user with username 'ADMIN' (case insensitive)
        try:
            response = self.session.post(f'{self.base_url}/api/users',
                                       json={'username': 'ADMIN', 'email': 'admin3@test.com', 'role': 'manager'})
            if response.status_code == 400:
                data = response.json()
                if 'not available' in data.get('error', '').lower():
                    self.log_result("Create Admin Username Case", True, "Username 'ADMIN' correctly rejected (case insensitive)")
                else:
                    self.log_result("Create Admin Username Case", False, f"Wrong error message: {data.get('error')}")
            else:
                self.log_result("Create Admin Username Case", False, f"Username 'ADMIN' not rejected: {response.status_code}")
        except Exception as e:
            self.log_result("Create Admin Username Case", False, f"Error: {str(e)}")
    
    def test_authentication_verification(self):
        """Test Phase 1.4: Authentication verification"""
        print("\n=== Phase 1.4: Authentication Verification ===")
        
        # Test 1: Admin can still login
        try:
            new_session = requests.Session()
            response = new_session.post(f'{self.base_url}/api/auth/login',
                                      json={'username': 'admin', 'password': 'UU8fz433'})
            if response.status_code == 200:
                self.log_result("Admin Login", True, "Admin can still authenticate successfully")
                
                # Test 2: GET current user as admin
                user_response = new_session.get(f'{self.base_url}/api/auth/current-user')
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    user_info = user_data.get('user', {})
                    if user_info.get('username') == 'admin':
                        self.log_result("Admin Current User", True, "Admin current-user endpoint works")
                    else:
                        self.log_result("Admin Current User", False, f"Wrong user data: {user_data}")
                else:
                    self.log_result("Admin Current User", False, f"Current user failed: {user_response.status_code}")
            else:
                self.log_result("Admin Login", False, f"Admin login failed: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Error: {str(e)}")
        
        # Test 3: Admin can access admin-only endpoints
        try:
            response = self.session.get(f'{self.base_url}/api/users')
            if response.status_code == 200:
                self.log_result("Admin Endpoint Access", True, "Admin can access admin-only endpoints")
            else:
                self.log_result("Admin Endpoint Access", False, f"Admin endpoint access failed: {response.status_code}")
        except Exception as e:
            self.log_result("Admin Endpoint Access", False, f"Error: {str(e)}")
    
    def test_bulk_operations(self):
        """Test Phase 1.5: Bulk operations"""
        print("\n=== Phase 1.5: Bulk Operations ===")
        
        # Test user count accuracy (should exclude admin)
        try:
            response = self.session.get(f'{self.base_url}/api/users')
            if response.status_code == 200:
                data = response.json()
                total_count = data.get('pagination', {}).get('total', 0)
                users = data.get('users', [])
                
                # Verify no admin user in results
                has_admin = any(u.get('username') == 'admin' for u in users)
                count_matches = len(users) <= total_count
                
                if not has_admin and count_matches:
                    self.log_result("User Count Accuracy", True, f"User count accurate: {total_count} (admin excluded)")
                else:
                    self.log_result("User Count Accuracy", False, f"Count issues: admin_present={has_admin}, count_match={count_matches}")
            else:
                self.log_result("User Count Accuracy", False, f"Failed to get user count: {response.status_code}")
        except Exception as e:
            self.log_result("User Count Accuracy", False, f"Error: {str(e)}")
    
    def test_manager_perspective(self):
        """Test from manager perspective (admin should still be hidden)"""
        print("\n=== Testing Manager Perspective ===")
        
        if not self.manager_session_cookies:
            self.log_result("Manager Perspective Setup", False, "Manager session not available")
            return
        
        # Create new session for manager
        manager_session = requests.Session()
        manager_session.cookies.update(self.manager_session_cookies)
        
        try:
            # Managers don't have user access, so test should fail with 403
            response = manager_session.get(f'{self.base_url}/api/users')
            if response.status_code == 403:
                self.log_result("Manager User Access", True, "Manager correctly blocked from user endpoints")
            else:
                self.log_result("Manager User Access", False, f"Manager got unexpected access: {response.status_code}")
        except Exception as e:
            self.log_result("Manager User Access", False, f"Error: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all test phases"""
        print("🧪 Starting Comprehensive Admin User Hiding Tests")
        print("=" * 60)
        
        # Setup phase
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        self.create_test_manager()  # Optional, continues if it fails
        
        # Run all test phases
        self.test_user_listing_endpoints()
        self.test_individual_user_operations()
        self.test_user_creation_validation()
        self.test_authentication_verification()
        self.test_bulk_operations()
        self.test_manager_perspective()
        
        return True
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            print("-" * 40)
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test_name']}: {result['message']}")
                    if result['details']:
                        print(f"   Details: {result['details']}")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test_name']}: {result['message']}")
        
        # Save detailed report to file
        report_data = {
            'test_run': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'results': self.test_results
        }
        
        with open('/home/jbrice/Projects/365/admin_hiding_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: admin_hiding_test_report.json")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    print("🚀 Admin User Hiding Functionality Test Suite")
    print("Testing comprehensive admin user hiding implementation")
    print("-" * 60)
    
    # Check if servers are running
    try:
        response = requests.get('http://localhost:5000/api/auth/current-user', timeout=5)
        print("✅ Backend server is running")
    except:
        print("❌ Backend server not accessible at http://localhost:5000")
        print("Please start the Flask backend with: python app.py")
        return False
    
    # Run tests
    test_suite = AdminHidingTestSuite()
    
    if test_suite.run_comprehensive_tests():
        all_passed = test_suite.generate_report()
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED - Admin user hiding implementation is working correctly!")
            return True
        else:
            print("\n⚠️  Some tests failed - Review the report above for issues")
            return False
    else:
        print("\n❌ Test suite setup failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)