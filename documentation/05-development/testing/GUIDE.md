# CVD Testing Guide


## Metadata
- **ID**: 05_DEVELOPMENT_TESTING_GUIDE
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #coding #data-exchange #data-layer #database #debugging #deployment #development #device-management #devops #dex-parser #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #quality-assurance #reporting #route-management #security #service-orders #testing #troubleshooting #vending-machine #workflows
- **Intent**: This comprehensive testing guide covers all aspects of testing for the CVD (Vision Device Configuration) application
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/testing/
- **Category**: Testing
- **Search Keywords**: ###, ${result.error}, /__pycache__/, /migrations/, accuracy, add, arrange-act-assert, assertion, assertions, cabinet, changes, check, clear, code, comprehensive

## Overview

This comprehensive testing guide covers all aspects of testing for the CVD (Vision Device Configuration) application. The guide is based on analysis of the existing test suite and establishes patterns for unit testing, integration testing, frontend testing, and AI feature validation.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Organization](#test-organization)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [Frontend Testing](#frontend-testing)
6. [AI Feature Testing](#ai-feature-testing)
7. [Performance Testing](#performance-testing)
8. [Security Testing](#security-testing)
9. [Test Data Management](#test-data-management)
10. [Testing Tools and Frameworks](#testing-tools-and-frameworks)
11. [CI/CD Integration](#cicd-integration)

## Testing Philosophy

### Core Principles
- **Quality First**: Tests are first-class citizens, not afterthoughts
- **Fast Feedback**: Quick test execution for rapid development cycles
- **Reliable Results**: Tests should be deterministic and stable
- **Maintainable Code**: Tests should be as clean and readable as production code
- **Comprehensive Coverage**: Test all critical paths and edge cases

### Testing Pyramid Strategy
```
    ┌─────────────────────────────────────┐
    │         E2E Tests (Few)             │
    │     Browser, User Workflows         │
    ├─────────────────────────────────────┤
    │      Integration Tests (Some)       │
    │    API, Database, Components        │
    ├─────────────────────────────────────┤
    │        Unit Tests (Many)            │
    │   Functions, Classes, Modules       │
    └─────────────────────────────────────┘
```

### Test Categories
1. **Unit Tests**: Isolated component testing
2. **Integration Tests**: Component interaction testing
3. **System Tests**: End-to-end workflow testing
4. **Performance Tests**: Load and response time testing
5. **Security Tests**: Authentication and authorization testing
6. **AI Tests**: ML model accuracy and performance testing

## Test Organization

### Directory Structure
```
tests/
├── test_*.py              # Python unit tests
├── test-*.html            # Frontend test pages  
├── debug-*.html           # Debug and diagnostic tests
├── *-test-strategy.md     # Testing strategy documents
├── *-test-results.md      # Test execution reports
└── fixtures/              # Test data and fixtures
    ├── sample_data.sql
    ├── test_devices.json
    └── mock_responses.json
```

### Test File Naming Conventions
```python
# Unit tests: test_<module_name>.py
test_auth_flow.py
test_user_soft_delete.py
test_planogram_optimizer.py

# Integration tests: test_<feature>_integration.py
test_service_order_integration.py
test_api_integration.py

# Performance tests: test_<component>_performance.py
test_activity_monitoring_performance.py
test_knowledge_base_performance.py

# Security tests: test_<component>_security.py
test_activity_monitoring_security.py
test_auth_security.py

# Frontend tests: test-<feature>.html
test-service-order.html
test-device-selection.html
```

## Unit Testing

### Python Unit Tests

#### Standard Test Class Structure
```python
import unittest
import sqlite3
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Import application modules
from app import app
from auth import AuthManager
from service_order_service import ServiceOrderService

class TestServiceOrderService(unittest.TestCase):
    """Test cases for service order functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create temporary test database
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Initialize test database schema
        self.init_test_database()
        
        # Create test data
        self.create_test_data()
    
    def tearDown(self):
        """Clean up after each test"""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def init_test_database(self):
        """Initialize test database with minimal schema"""
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        
        # Create essential tables for testing
        cursor.executescript('''
            CREATE TABLE service_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE service_order_cabinets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_order_id INTEGER,
                device_id INTEGER,
                cabinet_index INTEGER,
                FOREIGN KEY (service_order_id) REFERENCES service_orders (id)
            );
        ''')
        
        db.commit()
        db.close()
    
    def create_test_data(self):
        """Create test data for use in tests"""
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        
        # Insert test service order
        cursor.execute('''
            INSERT INTO service_orders (route_id, status)
            VALUES (1, 'pending')
        ''')
        
        db.commit()
        db.close()
    
    def test_create_service_order(self):
        """Test service order creation with valid data"""
        cabinet_selections = [
            {'deviceId': 1, 'cabinetIndex': 0},
            {'deviceId': 2, 'cabinetIndex': 1}
        ]
        
        result = ServiceOrderService.create_service_order(
            route_id=1,
            cabinet_selections=cabinet_selections,
            created_by=1
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('id', result)
        self.assertIn('cabinets', result)
        self.assertEqual(len(result['cabinets']), 2)
    
    def test_create_service_order_invalid_data(self):
        """Test service order creation with invalid data"""
        with self.assertRaises(ValueError):
            ServiceOrderService.create_service_order(
                route_id=None,
                cabinet_selections=[],
                created_by=1
            )
    
    @patch('service_order_service.get_db')
    def test_database_error_handling(self, mock_get_db):
        """Test handling of database errors"""
        # Mock database to raise exception
        mock_db = Mock()
        mock_db.cursor.side_effect = sqlite3.OperationalError("Database error")
        mock_get_db.return_value = mock_db
        
        cabinet_selections = [{'deviceId': 1, 'cabinetIndex': 0}]
        
        with self.assertRaises(sqlite3.OperationalError):
            ServiceOrderService.create_service_order(
                route_id=1,
                cabinet_selections=cabinet_selections
            )
```

#### Authentication Testing Pattern
```python
class TestAuthManager(unittest.TestCase):
    """Test authentication and authorization functionality"""
    
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.auth_manager = AuthManager(app, app.config['DATABASE'])
        
        self.init_auth_database()
    
    def test_user_login_success(self):
        """Test successful user login"""
        response = self.client.post('/api/auth/login', 
            json={
                'username': 'admin',
                'password': 'admin'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('user', data)
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/auth/login', 
            json={
                'username': 'invalid',
                'password': 'wrong'
            }
        )
        
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data['success'])
    
    def test_role_based_access(self):
        """Test role-based access control"""
        # Login as regular user
        self.client.post('/api/auth/login', 
            json={'username': 'driver', 'password': 'driver'}
        )
        
        # Try to access admin-only endpoint
        response = self.client.get('/api/admin/users')
        self.assertEqual(response.status_code, 403)
```

### Running Unit Tests
```bash
# Run all unit tests
python -m pytest tests/test_*.py -v

# Run specific test file
python -m pytest tests/test_auth_flow.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run with detailed output
python -m pytest tests/ -v -s

# Run specific test method
python -m pytest tests/test_auth_flow.py::TestAuthManager::test_user_login_success -v
```

## Integration Testing

### API Integration Tests
```python
class TestAPIIntegration(unittest.TestCase):
    """Test API endpoints with real database interactions"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use real database for integration tests
        self.setup_integration_database()
    
    def test_service_order_workflow(self):
        """Test complete service order creation workflow"""
        # Step 1: Login as manager
        login_response = self.client.post('/api/auth/login', 
            json={'username': 'manager', 'password': 'manager'}
        )
        self.assertEqual(login_response.status_code, 200)
        
        # Step 2: Get available routes
        routes_response = self.client.get('/api/routes')
        self.assertEqual(routes_response.status_code, 200)
        routes = routes_response.get_json()
        self.assertGreater(len(routes), 0)
        
        # Step 3: Create service order
        order_data = {
            'route_id': routes[0]['id'],
            'cabinet_selections': [
                {'deviceId': 1, 'cabinetIndex': 0}
            ]
        }
        
        create_response = self.client.post('/api/service-orders', json=order_data)
        self.assertEqual(create_response.status_code, 201)
        
        # Step 4: Verify order was created
        order = create_response.get_json()
        self.assertIn('id', order)
        
        # Step 5: Retrieve created order
        get_response = self.client.get(f'/api/service-orders/{order["id"]}')
        self.assertEqual(get_response.status_code, 200)
        
        retrieved_order = get_response.get_json()
        self.assertEqual(retrieved_order['id'], order['id'])
```

### Database Integration Tests
```python
class TestDatabaseIntegration(unittest.TestCase):
    """Test database operations and constraints"""
    
    def test_foreign_key_constraints(self):
        """Test that foreign key constraints are enforced"""
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        
        # Try to insert service order cabinet with invalid service_order_id
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute('''
                INSERT INTO service_order_cabinets 
                (service_order_id, device_id, cabinet_index)
                VALUES (99999, 1, 0)
            ''')
            db.commit()
    
    def test_soft_delete_functionality(self):
        """Test soft delete operations"""
        # Create test user
        response = self.client.post('/api/users', json={
            'username': 'testuser',
            'password': 'password',
            'role': 'viewer'
        })
        self.assertEqual(response.status_code, 201)
        user_id = response.get_json()['id']
        
        # Soft delete user
        delete_response = self.client.delete(f'/api/users/{user_id}')
        self.assertEqual(delete_response.status_code, 200)
        
        # Verify user is soft deleted (not visible in normal queries)
        get_response = self.client.get(f'/api/users/{user_id}')
        self.assertEqual(get_response.status_code, 404)
        
        # Verify user still exists in database with deleted_at timestamp
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        result = cursor.execute(
            'SELECT deleted_at FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        self.assertIsNotNone(result[0])  # deleted_at should be set
```

## Frontend Testing

### HTML Test Pages
Frontend testing uses dedicated HTML test pages that can be loaded in browsers:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Service Order Frontend Test</title>
    <script src="/api.js"></script>
    <style>
        .test-result { padding: 10px; margin: 5px; border-radius: 3px; }
        .pass { background-color: #d4edda; color: #155724; }
        .fail { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>Service Order Frontend Test Suite</h1>
    <div id="test-results"></div>
    
    <script>
        class FrontendTestRunner {
            constructor() {
                this.results = [];
                this.output = document.getElementById('test-results');
            }
            
            async runTests() {
                console.log('Starting frontend tests...');
                
                // Test 1: API Client Initialization
                this.test('API Client Initialization', () => {
                    const api = new CVDApi();
                    return api !== null && typeof api.get === 'function';
                });
                
                // Test 2: Authentication Check
                await this.asyncTest('Authentication Check', async () => {
                    try {
                        const api = new CVDApi();
                        const response = await api.get('/auth/current-user');
                        return response !== null;
                    } catch (error) {
                        return error.message.includes('401'); // Expected for unauthenticated
                    }
                });
                
                // Test 3: Service Order API
                await this.asyncTest('Service Order API Structure', async () => {
                    try {
                        const api = new CVDApi();
                        const response = await api.get('/service-orders');
                        return Array.isArray(response) || response.error;
                    } catch (error) {
                        return true; // Any response structure is acceptable
                    }
                });
                
                this.displayResults();
            }
            
            test(name, testFunction) {
                try {
                    const result = testFunction();
                    this.results.push({ name, passed: result, error: null });
                } catch (error) {
                    this.results.push({ name, passed: false, error: error.message });
                }
            }
            
            async asyncTest(name, testFunction) {
                try {
                    const result = await testFunction();
                    this.results.push({ name, passed: result, error: null });
                } catch (error) {
                    this.results.push({ name, passed: false, error: error.message });
                }
            }
            
            displayResults() {
                this.results.forEach(result => {
                    const div = document.createElement('div');
                    div.className = `test-result ${result.passed ? 'pass' : 'fail'}`;
                    div.innerHTML = `
                        <strong>${result.name}</strong>: 
                        ${result.passed ? 'PASS' : 'FAIL'}
                        ${result.error ? ` - ${result.error}` : ''}
                    `;
                    this.output.appendChild(div);
                });
                
                const summary = document.createElement('div');
                const passed = this.results.filter(r => r.passed).length;
                const total = this.results.length;
                summary.innerHTML = `<h3>Results: ${passed}/${total} tests passed</h3>`;
                this.output.insertBefore(summary, this.output.firstChild);
            }
        }
        
        // Run tests when page loads
        document.addEventListener('DOMContentLoaded', () => {
            const runner = new FrontendTestRunner();
            runner.runTests();
        });
    </script>
</body>
</html>
```

### JavaScript Unit Testing Pattern
```javascript
// For pages with complex JavaScript logic
class ComponentTestSuite {
    constructor() {
        this.testResults = [];
    }
    
    // Test DOM manipulation
    testDOMOperations() {
        const testContainer = document.createElement('div');
        testContainer.innerHTML = '<button id="test-btn">Click me</button>';
        document.body.appendChild(testContainer);
        
        const button = document.getElementById('test-btn');
        button.click();
        
        // Verify expected DOM changes
        const result = button.textContent === 'Clicked!';
        
        // Clean up
        document.body.removeChild(testContainer);
        
        return result;
    }
    
    // Test API interactions
    async testAPIIntegration() {
        const api = new CVDApi();
        
        try {
            // Test with mock data
            const mockResponse = await api.post('/test-endpoint', {
                test: true
            });
            
            return mockResponse.success === true;
        } catch (error) {
            console.error('API test failed:', error);
            return false;
        }
    }
    
    // Test form validation
    testFormValidation() {
        const form = document.createElement('form');
        form.innerHTML = `
            <input type="text" name="username" required>
            <input type="password" name="password" required>
            <button type="submit">Submit</button>
        `;
        
        // Test empty form validation
        const isValid = form.checkValidity();
        return !isValid; // Should be false for empty required fields
    }
}
```

## AI Feature Testing

### AI Model Testing Pattern
```python
class TestPlanogramOptimizer(unittest.TestCase):
    """Test AI-powered planogram optimization"""
    
    def setUp(self):
        self.test_db = 'test_cvd.db'
        self.api_key = os.getenv('ANTHROPIC_API_KEY', 'test_key')
        self.optimizer = PlanogramOptimizer(self.api_key, self.test_db)
        
        self.setup_test_data()
    
    def setup_test_data(self):
        """Create comprehensive test data for AI testing"""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Create test sales data
        cursor.executescript('''
            INSERT INTO sales (device_id, product_id, quantity, timestamp)
            VALUES 
            (1, 1, 5, '2024-01-01'),
            (1, 2, 3, '2024-01-01'),
            (1, 1, 2, '2024-01-02');
            
            INSERT INTO planograms (device_id, cabinet_index, created_at)
            VALUES (1, 0, '2024-01-01');
        ''')
        
        conn.commit()
        conn.close()
    
    @patch('planogram_optimizer.anthropic.Anthropic')
    def test_optimization_with_mock_api(self, mock_anthropic):
        """Test optimization logic with mocked AI API"""
        # Mock AI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps({
            "recommendations": [
                {"slot": 1, "product_id": 1, "confidence": 0.9},
                {"slot": 2, "product_id": 2, "confidence": 0.8}
            ],
            "reasoning": "High-velocity products in prime positions"
        })
        
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Test optimization
        result = self.optimizer.optimize_planogram(device_id=1, cabinet_index=0)
        
        # Verify results
        self.assertIsInstance(result, dict)
        self.assertIn('recommendations', result)
        self.assertIn('reasoning', result)
        self.assertEqual(len(result['recommendations']), 2)
    
    def test_optimization_without_api_key(self):
        """Test fallback behavior when API key is not available"""
        optimizer_no_key = PlanogramOptimizer(api_key=None, db_path=self.test_db)
        
        result = optimizer_no_key.optimize_planogram(device_id=1, cabinet_index=0)
        
        # Should return rule-based recommendations
        self.assertIsInstance(result, dict)
        self.assertIn('recommendations', result)
        self.assertIn('fallback', result)
    
    def test_optimization_performance(self):
        """Test optimization response time requirements"""
        import time
        
        start_time = time.time()
        result = self.optimizer.optimize_planogram(device_id=1, cabinet_index=0)
        end_time = time.time()
        
        # Should complete within reasonable time (5 seconds for AI calls)
        self.assertLess(end_time - start_time, 5.0)
        self.assertIsInstance(result, dict)
```

### AI Accuracy Testing
```python
class TestAIAccuracy(unittest.TestCase):
    """Test AI prediction accuracy and confidence scores"""
    
    def test_recommendation_confidence_scores(self):
        """Verify that AI recommendations include confidence scores"""
        optimizer = PlanogramOptimizer(api_key="test_key")
        
        # Use historical test data with known outcomes
        result = optimizer.optimize_planogram(device_id=1, cabinet_index=0)
        
        for recommendation in result['recommendations']:
            self.assertIn('confidence', recommendation)
            self.assertGreaterEqual(recommendation['confidence'], 0.0)
            self.assertLessEqual(recommendation['confidence'], 1.0)
    
    def test_recommendation_business_logic(self):
        """Verify recommendations follow business rules"""
        optimizer = PlanogramOptimizer(api_key="test_key")
        result = optimizer.optimize_planogram(device_id=1, cabinet_index=0)
        
        # Test business rules
        for recommendation in result['recommendations']:
            # High-velocity products should get prime positions (slots 1-4)
            if recommendation['confidence'] > 0.8:
                self.assertLessEqual(recommendation['slot'], 4)
```

## Performance Testing

### Load Testing Pattern
```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class TestPerformance(unittest.TestCase):
    """Performance testing for critical operations"""
    
    def test_api_response_times(self):
        """Test API response time requirements"""
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            
            response = self.client.get('/api/devices')
            
            end_time = time.time()
            response_times.append(end_time - start_time)
            
            self.assertEqual(response.status_code, 200)
        
        # Average response time should be under 500ms
        avg_response_time = sum(response_times) / len(response_times)
        self.assertLess(avg_response_time, 0.5)
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        def make_request():
            response = self.client.get('/api/service-orders')
            return response.status_code == 200
        
        # Test with 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        self.assertTrue(all(results))
    
    def test_database_query_performance(self):
        """Test database query performance"""
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        
        start_time = time.time()
        
        # Execute complex query
        cursor.execute('''
            SELECT d.id, d.name, COUNT(so.id) as order_count
            FROM devices d
            LEFT JOIN service_order_cabinets soc ON d.id = soc.device_id
            LEFT JOIN service_orders so ON soc.service_order_id = so.id
            GROUP BY d.id, d.name
            ORDER BY order_count DESC
            LIMIT 100
        ''')
        
        results = cursor.fetchall()
        end_time = time.time()
        
        # Query should complete within 100ms
        self.assertLess(end_time - start_time, 0.1)
        self.assertGreater(len(results), 0)
```

## Security Testing

### Authentication and Authorization Testing
```python
class TestSecurity(unittest.TestCase):
    """Security testing for authentication and authorization"""
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection attacks"""
        malicious_input = "'; DROP TABLE users; --"
        
        response = self.client.post('/api/auth/login', json={
            'username': malicious_input,
            'password': 'password'
        })
        
        # Should not cause internal server error
        self.assertNotEqual(response.status_code, 500)
        
        # Verify users table still exists
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM users')
            result = cursor.fetchone()
            self.assertIsNotNone(result)
        except sqlite3.OperationalError:
            self.fail("SQL injection attack succeeded")
    
    def test_session_security(self):
        """Test session security measures"""
        # Login to create session
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin'
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify session cookie is secure
        cookie = response.headers.get('Set-Cookie', '')
        self.assertIn('HttpOnly', cookie)
        self.assertIn('SameSite', cookie)
    
    def test_role_based_access_control(self):
        """Test role-based access control enforcement"""
        # Test admin access
        self.client.post('/api/auth/login', json={
            'username': 'admin', 'password': 'admin'
        })
        
        admin_response = self.client.get('/api/admin/users')
        self.assertEqual(admin_response.status_code, 200)
        
        # Logout and login as regular user
        self.client.post('/api/auth/logout')
        self.client.post('/api/auth/login', json={
            'username': 'driver', 'password': 'driver'
        })
        
        # Same endpoint should be forbidden
        user_response = self.client.get('/api/admin/users')
        self.assertEqual(user_response.status_code, 403)
```

## Test Data Management

### Test Fixtures and Sample Data
```python
class TestDataManager:
    """Manage test data and fixtures"""
    
    @staticmethod
    def create_sample_users(db):
        """Create sample user data for testing"""
        cursor = db.cursor()
        
        users_data = [
            ('admin', 'admin_hash', 'admin', False),
            ('manager', 'manager_hash', 'manager', False),
            ('driver', 'driver_hash', 'driver', False),
            ('viewer', 'viewer_hash', 'viewer', False),
            ('deleted_user', 'hash', 'viewer', True)
        ]
        
        cursor.executemany('''
            INSERT INTO users (username, password_hash, role, deleted_at)
            VALUES (?, ?, ?, CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END)
        ''', users_data)
        
        db.commit()
    
    @staticmethod
    def create_sample_devices(db):
        """Create sample device data for testing"""
        cursor = db.cursor()
        
        cursor.executescript('''
            INSERT INTO device_types (id, name, max_cabinets)
            VALUES 
            (1, 'Single Door Cooler', 1),
            (2, 'Double Door Cooler', 2),
            (3, 'Triple Cabinet Unit', 3);
            
            INSERT INTO devices (name, device_type_id, location_id, active)
            VALUES 
            ('Cooler A1', 1, 1, 1),
            ('Cooler B2', 2, 1, 1),
            ('Unit C3', 3, 2, 1),
            ('Inactive Device', 1, 1, 0);
        ''')
        
        db.commit()
    
    @staticmethod
    def create_sample_sales_data(db):
        """Create realistic sales data for testing"""
        import random
        from datetime import datetime, timedelta
        
        cursor = db.cursor()
        
        # Generate sales data for last 30 days
        base_date = datetime.now() - timedelta(days=30)
        
        for device_id in range(1, 4):
            for day in range(30):
                date = base_date + timedelta(days=day)
                
                # Random number of sales per day per device
                for _ in range(random.randint(0, 10)):
                    product_id = random.randint(1, 12)
                    quantity = random.randint(1, 3)
                    
                    cursor.execute('''
                        INSERT INTO sales (device_id, product_id, quantity, timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (device_id, product_id, quantity, date))
        
        db.commit()
```

### Test Database Setup
```python
def setup_test_database():
    """Set up complete test database with sample data"""
    db_path = 'test_cvd.db'
    
    # Remove existing test database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new test database
    db = sqlite3.connect(db_path)
    
    # Apply schema
    with open('migrations/001_initial_schema.sql', 'r') as f:
        db.executescript(f.read())
    
    # Create test data
    TestDataManager.create_sample_users(db)
    TestDataManager.create_sample_devices(db)
    TestDataManager.create_sample_sales_data(db)
    
    db.close()
    
    return db_path
```

## Testing Tools and Frameworks

### Python Testing Stack
```bash
# Core testing framework
pytest==7.4.0              # Primary test runner
pytest-cov==4.1.0          # Coverage reporting
pytest-mock==3.11.1        # Mocking utilities
pytest-asyncio==0.21.1     # Async test support

# Additional testing tools
unittest-mock==1.0.1       # Extended mocking
factory-boy==3.3.0         # Test data factories
faker==19.3.0               # Fake data generation
responses==0.23.3           # HTTP request mocking

# Performance testing
pytest-benchmark==4.0.0    # Performance benchmarking
locust==2.16.1             # Load testing framework
```

### Test Configuration
```python
# conftest.py - pytest configuration
import pytest
import sqlite3
import tempfile
import os
from app import app

@pytest.fixture(scope="function")
def test_client():
    """Create test client for each test"""
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            # Initialize test database
            init_test_db()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture(scope="function") 
def test_db():
    """Create test database for each test"""
    db_fd, db_path = tempfile.mkstemp()
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    
    # Initialize schema
    init_test_db_schema(db)
    
    yield db
    
    db.close()
    os.close(db_fd)
    os.unlink(db_path)

def init_test_db():
    """Initialize test database schema"""
    # Database initialization logic
    pass

def init_test_db_schema(db):
    """Initialize database schema for testing"""
    # Schema initialization logic
    pass
```

### Test Runner Scripts
```bash
#!/bin/bash
# run_tests.sh - Comprehensive test runner

echo "Running CVD Test Suite"
echo "======================"

# Set test environment
export FLASK_ENV=testing
export TESTING=true

# Run Python unit tests with coverage
echo "Running Python unit tests..."
python -m pytest tests/test_*.py \
    --cov=. \
    --cov-report=html \
    --cov-report=term \
    -v

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/*integration*.py -v

# Run performance tests
echo "Running performance tests..."
python -m pytest tests/*performance*.py -v

# Run security tests  
echo "Running security tests..."
python -m pytest tests/*security*.py -v

# Generate test report
echo "Generating test report..."
python -m pytest tests/ \
    --html=reports/test_report.html \
    --self-contained-html

echo "Test suite complete. Reports available in reports/ directory."
```

## CI/CD Integration

### GitHub Actions Configuration (Example)
```yaml
# .github/workflows/test.yml
name: CVD Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: |
        python -m pytest tests/test_*.py --cov=. --cov-report=xml
    
    - name: Run integration tests
      run: |
        python -m pytest tests/*integration*.py -v
    
    - name: Run security tests
      run: |
        python -m pytest tests/*security*.py -v
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### Test Coverage Requirements
```ini
# .coveragerc - Coverage configuration
[run]
source = .
omit = 
    venv/*
    tests/*
    */__pycache__/*
    */migrations/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

## Best Practices Summary

### Test Writing Guidelines
1. **Clear Test Names**: Test names should describe what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
3. **One Assertion Per Test**: Focus each test on a single behavior
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Execution**: Keep tests fast to encourage frequent running

### Test Maintenance
1. **Update with Code Changes**: Keep tests in sync with production code
2. **Refactor Test Code**: Apply same quality standards to test code
3. **Remove Obsolete Tests**: Delete tests for removed functionality
4. **Regular Test Review**: Review test effectiveness and coverage

### Debugging Test Failures
1. **Use Descriptive Assertions**: Include helpful error messages
2. **Add Debug Output**: Use logging and print statements for complex tests
3. **Isolate Failures**: Run individual tests to isolate issues
4. **Check Test Environment**: Verify database state and configuration

This comprehensive testing guide provides the foundation for maintaining high code quality and reliability in the CVD application. Follow these patterns and practices to ensure robust, maintainable test coverage across all application components.