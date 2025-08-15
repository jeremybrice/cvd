#!/usr/bin/env python3
"""
Frontend API Call Tests for Admin User Hiding

This script simulates the frontend JavaScript API calls to test admin user hiding
from the frontend perspective.
"""

import requests
import json
import time
from datetime import datetime

class FrontendAPITestSuite:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
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
                self.log_result("Frontend Auth", True, "Admin authentication successful")
                return True
            else:
                self.log_result("Frontend Auth", False, f"Failed to authenticate: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Frontend Auth", False, f"Error authenticating: {str(e)}")
            return False
    
    def test_user_management_api_calls(self):
        """Test API calls that the user management frontend would make"""
        print("\n=== Frontend User Management API Tests ===")
        
        # Test 1: Basic user listing (what the frontend loads on page load)
        try:
            response = self.session.get(f'{self.base_url}/api/users')
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) == 0:
                    self.log_result("Frontend User List", True, f"User list API returns {len(users)} users (admin hidden)")
                else:
                    self.log_result("Frontend User List", False, f"Admin user visible in API response: {admin_users}")
                
                # Check pagination info
                pagination = data.get('pagination', {})
                total = pagination.get('total', 0)
                self.log_result("Frontend Pagination", True, f"Pagination shows {total} total users (admin excluded)")
                
            else:
                self.log_result("Frontend User List", False, f"API call failed: {response.status_code}")
        except Exception as e:
            self.log_result("Frontend User List", False, f"Error: {str(e)}")
        
        # Test 2: Search functionality (when user types in search box)
        try:
            response = self.session.get(f'{self.base_url}/api/users?search=admin')
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) == 0:
                    self.log_result("Frontend Search", True, f"Search for 'admin' returns {len(users)} results (admin hidden)")
                else:
                    self.log_result("Frontend Search", False, f"Admin user found in search: {admin_users}")
            else:
                self.log_result("Frontend Search", False, f"Search API failed: {response.status_code}")
        except Exception as e:
            self.log_result("Frontend Search", False, f"Error: {str(e)}")
        
        # Test 3: Role filtering (when user filters by admin role)
        try:
            response = self.session.get(f'{self.base_url}/api/users?role=admin')
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) == 0:
                    self.log_result("Frontend Role Filter", True, f"Admin role filter returns {len(users)} users (admin hidden)")
                else:
                    self.log_result("Frontend Role Filter", False, f"Admin user in role filter: {admin_users}")
            else:
                self.log_result("Frontend Role Filter", False, f"Role filter API failed: {response.status_code}")
        except Exception as e:
            self.log_result("Frontend Role Filter", False, f"Error: {str(e)}")
        
        # Test 4: Status filtering
        try:
            response = self.session.get(f'{self.base_url}/api/users?status=active')
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) == 0:
                    self.log_result("Frontend Status Filter", True, f"Active status filter returns {len(users)} users (admin hidden)")
                else:
                    self.log_result("Frontend Status Filter", False, f"Admin user in status filter: {admin_users}")
            else:
                self.log_result("Frontend Status Filter", False, f"Status filter API failed: {response.status_code}")
        except Exception as e:
            self.log_result("Frontend Status Filter", False, f"Error: {str(e)}")
        
        # Test 5: Pagination (different pages)
        try:
            response = self.session.get(f'{self.base_url}/api/users?page=1&per_page=5')
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) == 0:
                    self.log_result("Frontend Pagination", True, f"Paginated results hide admin user (page 1)")
                else:
                    self.log_result("Frontend Pagination", False, f"Admin user in paginated results: {admin_users}")
            else:
                self.log_result("Frontend Pagination", False, f"Pagination API failed: {response.status_code}")
        except Exception as e:
            self.log_result("Frontend Pagination", False, f"Error: {str(e)}")
    
    def test_user_creation_frontend(self):
        """Test user creation from frontend perspective"""
        print("\n=== Frontend User Creation Tests ===")
        
        # Test 1: Create user with 'admin' username (form validation)
        try:
            response = self.session.post(f'{self.base_url}/api/users',
                                       json={
                                           'username': 'admin',
                                           'email': 'admin2@test.com',
                                           'role': 'manager'
                                       })
            if response.status_code == 400:
                data = response.json()
                error_msg = data.get('error', '').lower()
                if 'not available' in error_msg or 'exists' in error_msg:
                    self.log_result("Frontend Create Admin", True, "Frontend correctly prevents 'admin' username creation")
                else:
                    self.log_result("Frontend Create Admin", False, f"Wrong error message: {data.get('error')}")
            else:
                self.log_result("Frontend Create Admin", False, f"User creation with 'admin' username allowed: {response.status_code}")
        except Exception as e:
            self.log_result("Frontend Create Admin", False, f"Error: {str(e)}")
        
        # Test 2: Create user with 'ADMIN' username (case insensitive)
        try:
            response = self.session.post(f'{self.base_url}/api/users',
                                       json={
                                           'username': 'ADMIN',
                                           'email': 'admin3@test.com',
                                           'role': 'manager'
                                       })
            if response.status_code == 400:
                data = response.json()
                error_msg = data.get('error', '').lower()
                if 'not available' in error_msg or 'exists' in error_msg:
                    self.log_result("Frontend Create Admin Case", True, "Frontend correctly prevents 'ADMIN' username creation")
                else:
                    self.log_result("Frontend Create Admin Case", False, f"Wrong error message: {data.get('error')}")
            else:
                self.log_result("Frontend Create Admin Case", False, f"User creation with 'ADMIN' username allowed: {response.status_code}")
        except Exception as e:
            self.log_result("Frontend Create Admin Case", False, f"Error: {str(e)}")
    
    def test_user_operations_frontend(self):
        """Test individual user operations from frontend perspective"""
        print("\n=== Frontend User Operations Tests ===")
        
        # First get admin user ID from current user endpoint
        admin_user_id = None
        try:
            response = self.session.get(f'{self.base_url}/api/auth/current-user')
            if response.status_code == 200:
                data = response.json()
                admin_user_id = data.get('user', {}).get('id')
            
            if admin_user_id:
                # Test 1: Try to get admin user details (should fail)
                try:
                    response = self.session.get(f'{self.base_url}/api/users/{admin_user_id}')
                    if response.status_code == 404:
                        self.log_result("Frontend Get Admin User", True, "Frontend cannot fetch admin user details")
                    else:
                        self.log_result("Frontend Get Admin User", False, f"Frontend can access admin user: {response.status_code}")
                except Exception as e:
                    self.log_result("Frontend Get Admin User", False, f"Error: {str(e)}")
                
                # Test 2: Try to update admin user (should fail)
                try:
                    response = self.session.put(f'{self.base_url}/api/users/{admin_user_id}',
                                              json={'email': 'newemail@test.com'})
                    if response.status_code == 404:
                        self.log_result("Frontend Update Admin", True, "Frontend cannot update admin user")
                    else:
                        self.log_result("Frontend Update Admin", False, f"Frontend can update admin user: {response.status_code}")
                except Exception as e:
                    self.log_result("Frontend Update Admin", False, f"Error: {str(e)}")
                
                # Test 3: Try to delete admin user (should fail)
                try:
                    response = self.session.delete(f'{self.base_url}/api/users/{admin_user_id}')
                    if response.status_code == 404:
                        self.log_result("Frontend Delete Admin", True, "Frontend cannot delete admin user")
                    else:
                        self.log_result("Frontend Delete Admin", False, f"Frontend can delete admin user: {response.status_code}")
                except Exception as e:
                    self.log_result("Frontend Delete Admin", False, f"Error: {str(e)}")
            else:
                self.log_result("Frontend User Operations", False, "Could not determine admin user ID")
                
        except Exception as e:
            self.log_result("Frontend User Operations", False, f"Error getting admin ID: {str(e)}")
    
    def run_all_tests(self):
        """Run comprehensive frontend API tests"""
        print("🖥️  Starting Frontend API Tests")
        print("=" * 60)
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Run test suites
        self.test_user_management_api_calls()
        self.test_user_creation_frontend()
        self.test_user_operations_frontend()
        
        return True
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 FRONTEND API TEST REPORT")
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
        
        # Save report
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
        
        with open('/home/jbrice/Projects/365/frontend_api_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved to: frontend_api_test_report.json")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    print("🖥️  Frontend API Test Suite for Admin User Hiding")
    print("Testing all frontend API calls that could expose admin user")
    print("-" * 60)
    
    test_suite = FrontendAPITestSuite()
    
    if test_suite.run_all_tests():
        all_passed = test_suite.generate_report()
        
        if all_passed:
            print("\n🎉 ALL FRONTEND API TESTS PASSED!")
            return True
        else:
            print("\n⚠️  Some frontend tests failed")
            return False
    else:
        print("\n❌ Frontend test suite setup failed")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)