#!/usr/bin/env python3
"""
Integration and Edge Case Tests for Admin User Hiding

This script tests complex scenarios, multi-user sessions, and edge cases
to ensure the admin hiding functionality works in all situations.
"""

import requests
import json
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import sys

class IntegrationTestSuite:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
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
    
    def test_multiple_admin_sessions(self):
        """Test multiple admin sessions simultaneously"""
        print("\n=== Multi-Session Admin Tests ===")
        
        def admin_session_test(session_id):
            """Test admin functionality in separate session"""
            session = requests.Session()
            
            try:
                # Authenticate
                response = session.post(f'{self.base_url}/api/auth/login',
                                      json={'username': 'admin', 'password': 'UU8fz433'})
                
                if response.status_code != 200:
                    return {'session': session_id, 'success': False, 'error': 'Auth failed'}
                
                # Test user listing
                users_response = session.get(f'{self.base_url}/api/users')
                if users_response.status_code != 200:
                    return {'session': session_id, 'success': False, 'error': 'User listing failed'}
                
                users_data = users_response.json()
                users = users_data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) > 0:
                    return {'session': session_id, 'success': False, 'error': f'Admin visible in session {session_id}'}
                
                return {'session': session_id, 'success': True, 'user_count': len(users)}
                
            except Exception as e:
                return {'session': session_id, 'success': False, 'error': str(e)}
        
        # Run multiple admin sessions concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(admin_session_test, i) for i in range(5)]
            results = [future.result() for future in futures]
        
        # Analyze results
        successful_sessions = [r for r in results if r['success']]
        failed_sessions = [r for r in results if not r['success']]
        
        if len(failed_sessions) == 0:
            self.log_result("Multiple Admin Sessions", True, 
                          f"All {len(successful_sessions)} admin sessions hide admin user")
        else:
            self.log_result("Multiple Admin Sessions", False,
                          f"{len(failed_sessions)} sessions failed", 
                          {'failed_sessions': failed_sessions})
    
    def test_mixed_role_sessions(self):
        """Test admin hiding across different user role sessions"""
        print("\n=== Mixed Role Session Tests ===")
        
        # First create test users of different roles
        admin_session = requests.Session()
        admin_session.post(f'{self.base_url}/api/auth/login',
                          json={'username': 'admin', 'password': 'UU8fz433'})
        
        test_users = [
            {'username': 'test_manager2', 'email': 'test_manager2@test.com', 'role': 'manager', 'password': 'test123'},
            {'username': 'test_driver', 'email': 'test_driver@test.com', 'role': 'driver', 'password': 'test123'},
            {'username': 'test_viewer', 'email': 'test_viewer@test.com', 'role': 'viewer', 'password': 'test123'}
        ]
        
        # Create test users
        for user in test_users:
            try:
                admin_session.post(f'{self.base_url}/api/users', json={
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role'],
                    'password': user['password']
                })
            except:
                pass  # User might already exist
        
        def test_role_session(user_info):
            """Test session for specific role"""
            session = requests.Session()
            
            try:
                # Authenticate as test user
                response = session.post(f'{self.base_url}/api/auth/login',
                                      json={'username': user_info['username'], 'password': user_info['password']})
                
                if response.status_code != 200:
                    return {'role': user_info['role'], 'success': False, 'error': 'Auth failed'}
                
                # Try to access user endpoints (should fail for non-admins)
                users_response = session.get(f'{self.base_url}/api/users')
                
                # Non-admin roles should not have access to user management
                if user_info['role'] != 'admin':
                    if users_response.status_code == 403:
                        return {'role': user_info['role'], 'success': True, 'message': 'Correctly blocked from user endpoints'}
                    else:
                        return {'role': user_info['role'], 'success': False, 'error': f'Non-admin got access: {users_response.status_code}'}
                else:
                    # Admin role should have access but admin user should be hidden
                    if users_response.status_code == 200:
                        users_data = users_response.json()
                        users = users_data.get('users', [])
                        admin_users = [u for u in users if u.get('username') == 'admin']
                        
                        if len(admin_users) == 0:
                            return {'role': user_info['role'], 'success': True, 'user_count': len(users)}
                        else:
                            return {'role': user_info['role'], 'success': False, 'error': 'Admin visible to admin user'}
                    else:
                        return {'role': user_info['role'], 'success': False, 'error': f'Admin access failed: {users_response.status_code}'}
                
            except Exception as e:
                return {'role': user_info['role'], 'success': False, 'error': str(e)}
        
        # Test each role
        for user_info in test_users:
            result = test_role_session(user_info)
            
            if result['success']:
                self.log_result(f"Role Session {result['role']}", True, result.get('message', 'Role session test passed'))
            else:
                self.log_result(f"Role Session {result['role']}", False, result.get('error', 'Role session test failed'))
    
    def test_edge_cases(self):
        """Test various edge cases"""
        print("\n=== Edge Case Tests ===")
        
        # Create admin session for testing
        admin_session = requests.Session()
        admin_session.post(f'{self.base_url}/api/auth/login',
                          json={'username': 'admin', 'password': 'UU8fz433'})
        
        # Test 1: Very large pagination request
        try:
            response = admin_session.get(f'{self.base_url}/api/users?page=1&per_page=1000')
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                admin_users = [u for u in users if u.get('username') == 'admin']
                
                if len(admin_users) == 0:
                    self.log_result("Large Pagination", True, f"Large pagination request hides admin ({len(users)} users)")
                else:
                    self.log_result("Large Pagination", False, f"Admin visible in large pagination: {admin_users}")
            else:
                self.log_result("Large Pagination", False, f"Large pagination failed: {response.status_code}")
        except Exception as e:
            self.log_result("Large Pagination", False, f"Error: {str(e)}")
        
        # Test 2: Special characters in search
        special_searches = ['admin%', 'admin*', 'admin_', 'ADMIN', 'Admin', 'aDmIn', '%admin%', '*admin*']
        
        for search_term in special_searches:
            try:
                response = admin_session.get(f'{self.base_url}/api/users?search={search_term}')
                if response.status_code == 200:
                    data = response.json()
                    users = data.get('users', [])
                    admin_users = [u for u in users if u.get('username') == 'admin']
                    
                    if len(admin_users) == 0:
                        self.log_result(f"Special Search '{search_term}'", True, "Admin hidden in special character search")
                    else:
                        self.log_result(f"Special Search '{search_term}'", False, f"Admin found: {admin_users}")
                else:
                    self.log_result(f"Special Search '{search_term}'", False, f"Search failed: {response.status_code}")
            except Exception as e:
                self.log_result(f"Special Search '{search_term}'", False, f"Error: {str(e)}")
        
        # Test 3: Multiple filter combinations
        filter_combinations = [
            {'role': 'admin', 'status': 'active'},
            {'role': 'admin', 'search': 'admin'},
            {'status': 'active', 'search': 'admin'},
            {'role': 'admin', 'status': 'active', 'search': 'admin'}
        ]
        
        for filters in filter_combinations:
            try:
                params = '&'.join([f'{k}={v}' for k, v in filters.items()])
                response = admin_session.get(f'{self.base_url}/api/users?{params}')
                
                if response.status_code == 200:
                    data = response.json()
                    users = data.get('users', [])
                    admin_users = [u for u in users if u.get('username') == 'admin']
                    
                    filter_str = ', '.join([f'{k}={v}' for k, v in filters.items()])
                    if len(admin_users) == 0:
                        self.log_result(f"Filter Combo ({filter_str})", True, "Admin hidden in combined filters")
                    else:
                        self.log_result(f"Filter Combo ({filter_str})", False, f"Admin found: {admin_users}")
                else:
                    self.log_result(f"Filter Combo", False, f"Combined filter failed: {response.status_code}")
            except Exception as e:
                self.log_result(f"Filter Combo", False, f"Error: {str(e)}")
    
    def test_session_persistence(self):
        """Test that admin hiding persists across session operations"""
        print("\n=== Session Persistence Tests ===")
        
        # Create a session and perform multiple operations
        session = requests.Session()
        
        try:
            # Authenticate
            response = session.post(f'{self.base_url}/api/auth/login',
                                  json={'username': 'admin', 'password': 'UU8fz433'})
            
            if response.status_code != 200:
                self.log_result("Session Persistence Setup", False, "Failed to authenticate")
                return
            
            # Perform multiple operations and check admin hiding each time
            operations = [
                ('Initial Load', lambda: session.get(f'{self.base_url}/api/users')),
                ('Search Operation', lambda: session.get(f'{self.base_url}/api/users?search=test')),
                ('Filter Operation', lambda: session.get(f'{self.base_url}/api/users?role=manager')),
                ('Pagination', lambda: session.get(f'{self.base_url}/api/users?page=2&per_page=5')),
                ('After User Creation', self.create_test_user_and_list),
                ('Final Check', lambda: session.get(f'{self.base_url}/api/users'))
            ]
            
            all_operations_passed = True
            
            for op_name, operation in operations:
                try:
                    if op_name == 'After User Creation':
                        response = operation(session)
                    else:
                        response = operation()
                    
                    if response.status_code == 200:
                        data = response.json()
                        users = data.get('users', [])
                        admin_users = [u for u in users if u.get('username') == 'admin']
                        
                        if len(admin_users) == 0:
                            self.log_result(f"Persistence {op_name}", True, f"Admin hidden after {op_name}")
                        else:
                            self.log_result(f"Persistence {op_name}", False, f"Admin visible after {op_name}: {admin_users}")
                            all_operations_passed = False
                    else:
                        self.log_result(f"Persistence {op_name}", False, f"Operation failed: {response.status_code}")
                        all_operations_passed = False
                        
                except Exception as e:
                    self.log_result(f"Persistence {op_name}", False, f"Error: {str(e)}")
                    all_operations_passed = False
            
            if all_operations_passed:
                self.log_result("Overall Persistence", True, "Admin hiding persists across all session operations")
            else:
                self.log_result("Overall Persistence", False, "Admin hiding failed in some operations")
                
        except Exception as e:
            self.log_result("Session Persistence", False, f"Error: {str(e)}")
    
    def create_test_user_and_list(self, session):
        """Helper function to create a user and then list users"""
        try:
            # Create a test user
            create_response = session.post(f'{self.base_url}/api/users', json={
                'username': f'test_user_{int(time.time())}',
                'email': f'test_{int(time.time())}@test.com',
                'role': 'viewer'
            })
            
            # List users after creation
            return session.get(f'{self.base_url}/api/users')
        except Exception:
            # Return a dummy response if creation fails
            return session.get(f'{self.base_url}/api/users')
    
    def test_stress_scenarios(self):
        """Test system under stress conditions"""
        print("\n=== Stress Test Scenarios ===")
        
        def rapid_requests_test():
            """Test rapid successive requests"""
            session = requests.Session()
            session.post(f'{self.base_url}/api/auth/login',
                        json={'username': 'admin', 'password': 'UU8fz433'})
            
            admin_found_count = 0
            total_requests = 20
            
            for i in range(total_requests):
                try:
                    response = session.get(f'{self.base_url}/api/users')
                    if response.status_code == 200:
                        data = response.json()
                        users = data.get('users', [])
                        admin_users = [u for u in users if u.get('username') == 'admin']
                        admin_found_count += len(admin_users)
                    time.sleep(0.1)  # Small delay
                except:
                    pass
            
            return admin_found_count == 0
        
        # Run rapid requests test
        try:
            if rapid_requests_test():
                self.log_result("Rapid Requests", True, "Admin hidden during 20 rapid successive requests")
            else:
                self.log_result("Rapid Requests", False, "Admin appeared during rapid requests")
        except Exception as e:
            self.log_result("Rapid Requests", False, f"Error: {str(e)}")
        
        # Test concurrent requests
        def concurrent_request_test():
            """Test concurrent requests from same session"""
            session = requests.Session()
            session.post(f'{self.base_url}/api/auth/login',
                        json={'username': 'admin', 'password': 'UU8fz433'})
            
            def make_request():
                try:
                    response = session.get(f'{self.base_url}/api/users')
                    if response.status_code == 200:
                        data = response.json()
                        users = data.get('users', [])
                        admin_users = [u for u in users if u.get('username') == 'admin']
                        return len(admin_users) == 0
                    return False
                except:
                    return False
            
            # Run 10 concurrent requests
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [future.result() for future in futures]
            
            return all(results)
        
        try:
            if concurrent_request_test():
                self.log_result("Concurrent Requests", True, "Admin hidden during 10 concurrent requests")
            else:
                self.log_result("Concurrent Requests", False, "Admin appeared during concurrent requests")
        except Exception as e:
            self.log_result("Concurrent Requests", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all integration and edge case tests"""
        print("🔗 Starting Integration and Edge Case Tests")
        print("=" * 60)
        
        self.test_multiple_admin_sessions()
        self.test_mixed_role_sessions()
        self.test_edge_cases()
        self.test_session_persistence()
        self.test_stress_scenarios()
        
        return True
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION & EDGE CASE TEST REPORT")
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
        
        # Save detailed report
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
        
        with open('/home/jbrice/Projects/365/integration_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: integration_test_report.json")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    print("🔗 Integration & Edge Case Test Suite")
    print("Testing complex scenarios and edge cases for admin user hiding")
    print("-" * 60)
    
    test_suite = IntegrationTestSuite()
    
    if test_suite.run_all_tests():
        all_passed = test_suite.generate_report()
        
        if all_passed:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            return True
        else:
            print("\n⚠️  Some integration tests failed")
            return False
    else:
        print("\n❌ Integration test suite setup failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)