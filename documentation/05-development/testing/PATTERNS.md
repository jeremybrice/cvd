# CVD Testing Patterns


## Metadata
- **ID**: 05_DEVELOPMENT_TESTING_PATTERNS
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #coding #data-exchange #data-layer #database #debugging #development #device-management #dex-parser #driver-app #integration #logistics #machine-learning #metrics #mobile #operations #optimization #performance #planogram #product-placement #pwa #quality-assurance #reporting #route-management #security #service-orders #testing #troubleshooting #vending-machine #workflows
- **Intent**: This document defines standardized testing patterns, utilities, and conventions for the CVD application
- **Audience**: system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/testing/
- **Category**: Testing
- **Search Keywords**: ###, api, cabinet, connection, cooler, cvd, data, database, device, dex, driver, factory, fixtures, mocking, order

## Overview

This document defines standardized testing patterns, utilities, and conventions for the CVD application. These patterns ensure consistency, maintainability, and effectiveness across the test suite while leveraging the existing testing infrastructure.

## Table of Contents

1. [Fixture Patterns](#fixture-patterns)
2. [Mock Strategies](#mock-strategies)
3. [Test Data Factories](#test-data-factories)
4. [Assertion Patterns](#assertion-patterns)
5. [Test Organization](#test-organization)
6. [Authentication Testing](#authentication-testing)
7. [API Testing Patterns](#api-testing-patterns)

## Fixture Patterns

### Database Testing Fixtures

**SQLite Test Database Pattern**:
```python
class DatabaseTestCase(unittest.TestCase):
    """Base class for database-dependent tests"""
    
    def setUp(self):
        """Create isolated test database"""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        
        # Initialize schema
        self.init_database_schema()
        # Load reference data
        self.load_reference_data()
        
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def init_database_schema(self):
        """Initialize database schema for testing"""
        schema_sql = self.get_test_schema()
        self.db.executescript(schema_sql)
        self.db.commit()
    
    def get_test_schema(self):
        """Return minimal schema required for tests"""
        return """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer',
                deleted_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                asset TEXT UNIQUE,
                device_type_id INTEGER,
                location_id INTEGER,
                active BOOLEAN DEFAULT 1,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE service_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            );
            
            CREATE TABLE service_order_cabinets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_order_id INTEGER NOT NULL,
                device_id INTEGER NOT NULL,
                cabinet_index INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (service_order_id) REFERENCES service_orders (id),
                FOREIGN KEY (device_id) REFERENCES devices (id)
            );
            
            -- Add indexes for performance
            CREATE INDEX idx_users_username ON users(username);
            CREATE INDEX idx_devices_name ON devices(name);
            CREATE INDEX idx_service_orders_status ON service_orders(status);
        """
    
    def load_reference_data(self):
        """Load standard reference data for tests"""
        cursor = self.db.cursor()
        
        # Standard device types
        cursor.executemany("""
            INSERT OR IGNORE INTO device_types (id, name, max_cabinets)
            VALUES (?, ?, ?)
        """, [
            (1, 'Single Door Cooler', 1),
            (2, 'Double Door Cooler', 2),
            (3, 'Triple Cabinet Unit', 3)
        ])
        
        # Standard cabinet types
        cursor.executemany("""
            INSERT OR IGNORE INTO cabinet_types (id, name, default_rows, default_columns)
            VALUES (?, ?, ?, ?)
        """, [
            (1, 'Beverage Cooler', 5, 8),
            (2, 'Snack Cabinet', 6, 10),
            (3, 'Combo Unit', 5, 6)
        ])
        
        # Standard products (12 system products as per CVD spec)
        cursor.executemany("""
            INSERT OR IGNORE INTO products (id, name, category, default_price)
            VALUES (?, ?, ?, ?)
        """, [
            (1, 'Coca Cola', 'Beverages', 1.50),
            (2, 'Pepsi Cola', 'Beverages', 1.50),
            (3, 'Sprite', 'Beverages', 1.50),
            (4, 'Orange Soda', 'Beverages', 1.50),
            (5, 'Water Bottle', 'Beverages', 1.00),
            (6, 'Energy Drink', 'Beverages', 2.50),
            (7, 'Chips - Original', 'Snacks', 1.75),
            (8, 'Chips - BBQ', 'Snacks', 1.75),
            (9, 'Candy Bar', 'Candy', 1.25),
            (10, 'Chocolate', 'Candy', 1.50),
            (11, 'Cookies', 'Snacks', 2.00),
            (12, 'Crackers', 'Snacks', 1.50)
        ])
        
        self.db.commit()
```

**Flask Application Test Fixture**:
```python
class FlaskTestCase(DatabaseTestCase):
    """Base class for Flask application tests"""
    
    def setUp(self):
        """Set up Flask test client with test database"""
        super().setUp()
        
        # Configure test app
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
            'SECRET_KEY': 'test-secret-key',
            'WTF_CSRF_ENABLED': False  # Disable CSRF for testing
        })
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test users
        self.create_test_users()
    
    def tearDown(self):
        """Clean up Flask application context"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
        super().tearDown()
    
    def create_test_users(self):
        """Create standard test users for authentication testing"""
        from auth import hash_password
        
        test_users = [
            ('admin', hash_password('admin'), 'admin'),
            ('manager', hash_password('manager'), 'manager'), 
            ('driver', hash_password('driver'), 'driver'),
            ('viewer', hash_password('viewer'), 'viewer')
        ]
        
        cursor = self.db.cursor()
        cursor.executemany("""
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        """, test_users)
        self.db.commit()
```

### Service-Specific Fixtures

**Service Order Test Fixtures**:
```python
class ServiceOrderTestMixin:
    """Mixin providing service order test fixtures"""
    
    def create_test_route(self, name="Test Route"):
        """Create a test route for service orders"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO routes (name, description, active)
            VALUES (?, ?, 1)
        """, (name, f"Test route: {name}"))
        return cursor.lastrowid
    
    def create_test_device(self, name="Test Device", device_type_id=1, active=True):
        """Create a test device with cabinet configuration"""
        cursor = self.db.cursor()
        
        # Create device
        cursor.execute("""
            INSERT INTO devices (name, device_type_id, active, asset)
            VALUES (?, ?, ?, ?)
        """, (name, device_type_id, active, f"ASSET_{name.replace(' ', '_').upper()}"))
        device_id = cursor.lastrowid
        
        # Create cabinet configurations based on device type
        max_cabinets = {1: 1, 2: 2, 3: 3}.get(device_type_id, 1)
        
        for cabinet_index in range(max_cabinets):
            cursor.execute("""
                INSERT INTO cabinet_configurations 
                (device_id, cabinet_index, cabinet_type_id, rows, columns)
                VALUES (?, ?, ?, ?, ?)
            """, (device_id, cabinet_index, 1, 5, 8))
        
        self.db.commit()
        return device_id
    
    def create_service_order(self, route_id, cabinet_selections, created_by=1):
        """Create service order with cabinet selections"""
        cursor = self.db.cursor()
        
        # Create main service order
        cursor.execute("""
            INSERT INTO service_orders (route_id, created_by, status)
            VALUES (?, ?, 'pending')
        """, (route_id, created_by))
        order_id = cursor.lastrowid
        
        # Add cabinet selections
        for selection in cabinet_selections:
            cursor.execute("""
                INSERT INTO service_order_cabinets 
                (service_order_id, device_id, cabinet_index, status)
                VALUES (?, ?, ?, 'pending')
            """, (order_id, selection['deviceId'], selection['cabinetIndex']))
        
        self.db.commit()
        return order_id
```

## Mock Strategies

### External Service Mocking

**AI Service Mocking Pattern**:
```python
class AIMockingMixin:
    """Mixin providing AI service mocking utilities"""
    
    def mock_anthropic_success(self, recommendations_data):
        """Mock successful Anthropic API response"""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps({
            "recommendations": recommendations_data,
            "reasoning": "Test AI reasoning",
            "confidence_score": 0.85
        })
        
        return patch('planogram_optimizer.anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            yield mock_client
    
    def mock_anthropic_failure(self, error_type="rate_limit"):
        """Mock Anthropic API failure scenarios"""
        error_map = {
            "rate_limit": Exception("Rate limit exceeded"),
            "api_key": Exception("Invalid API key"),
            "timeout": Exception("Request timeout"),
            "server_error": Exception("Internal server error")
        }
        
        return patch('planogram_optimizer.anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.side_effect = error_map[error_type]
            mock_anthropic.return_value = mock_client
            yield mock_client
    
    def assert_ai_fallback_used(self, result):
        """Assert that AI fallback logic was used"""
        self.assertIn('fallback', result)
        self.assertTrue(result['fallback'])
        self.assertIn('reason', result)
```

**Database Connection Mocking**:
```python
class DatabaseMockingMixin:
    """Mixin providing database mocking utilities"""
    
    def mock_database_error(self, error_type="operational"):
        """Mock database errors for error handling tests"""
        error_map = {
            "operational": sqlite3.OperationalError("Database is locked"),
            "integrity": sqlite3.IntegrityError("Constraint failed"),
            "programming": sqlite3.ProgrammingError("SQL syntax error")
        }
        
        return patch('sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_conn.cursor.side_effect = error_map[error_type]
            mock_connect.return_value = mock_conn
            yield mock_connect
    
    def mock_transaction_rollback(self):
        """Mock transaction rollback scenarios"""
        return patch('sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            
            # Configure cursor to raise error on specific operation
            mock_cursor.execute.side_effect = [None, sqlite3.IntegrityError("Rollback")]
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            yield mock_conn
```

### HTTP Request Mocking

**API Request Mocking Pattern**:
```python
class HTTPMockingMixin:
    """Mixin providing HTTP request mocking utilities"""
    
    def mock_external_api_success(self, endpoint, response_data):
        """Mock successful external API responses"""
        return patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = response_data
            mock_get.return_value = mock_response
            yield mock_response
    
    def mock_external_api_timeout(self, endpoint):
        """Mock API timeout scenarios"""
        return patch('requests.get') as mock_get:
            mock_get.side_effect = requests.Timeout("Request timeout")
            yield mock_get
    
    def mock_authentication_service(self, valid_tokens=None):
        """Mock authentication service responses"""
        valid_tokens = valid_tokens or {'admin-token': 'admin', 'user-token': 'user'}
        
        def mock_auth_response(request):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if token in valid_tokens:
                return (200, {}, json.dumps({'user': valid_tokens[token], 'valid': True}))
            else:
                return (401, {}, json.dumps({'error': 'Invalid token'}))
        
        return patch('requests.post', side_effect=mock_auth_response)
```

## Test Data Factories

### User Data Factory

```python
class UserFactory:
    """Factory for creating test user data"""
    
    @staticmethod
    def create(username=None, role='viewer', password='password', deleted=False):
        """Create user data with sensible defaults"""
        from faker import Faker
        from auth import hash_password
        
        fake = Faker()
        
        if username is None:
            username = fake.user_name()
        
        return {
            'username': username,
            'password_hash': hash_password(password),
            'role': role,
            'deleted_at': fake.date_time_this_year() if deleted else None,
            'created_at': fake.date_time_this_year()
        }
    
    @staticmethod
    def create_admin(username='test_admin'):
        """Create admin user"""
        return UserFactory.create(username=username, role='admin')
    
    @staticmethod
    def create_manager(username='test_manager'):
        """Create manager user"""
        return UserFactory.create(username=username, role='manager')
    
    @staticmethod
    def create_driver(username='test_driver'):
        """Create driver user"""
        return UserFactory.create(username=username, role='driver')
    
    @staticmethod
    def create_batch(count=5, role='viewer'):
        """Create multiple users with specified role"""
        return [UserFactory.create(role=role) for _ in range(count)]
```

### Device Data Factory

```python
class DeviceFactory:
    """Factory for creating test device data"""
    
    @staticmethod
    def create(name=None, device_type_id=1, location_id=1, active=True):
        """Create device data with cabinet configurations"""
        from faker import Faker
        
        fake = Faker()
        
        if name is None:
            name = f"{fake.company()} {fake.random_element(['Cooler', 'Unit', 'Station'])}"
        
        # Generate unique asset number
        asset = f"ASSET_{fake.random_int(10000, 99999)}"
        
        device_data = {
            'name': name,
            'asset': asset,
            'device_type_id': device_type_id,
            'location_id': location_id,
            'active': active,
            'created_at': fake.date_time_this_year()
        }
        
        # Add cabinet configurations based on device type
        max_cabinets = {1: 1, 2: 2, 3: 3}.get(device_type_id, 1)
        device_data['cabinets'] = []
        
        for cabinet_index in range(max_cabinets):
            cabinet_data = {
                'cabinet_index': cabinet_index,
                'cabinet_type_id': fake.random_element([1, 2, 3]),
                'rows': fake.random_int(4, 8),
                'columns': fake.random_int(6, 10),
                'modelName': fake.random_element(['CoolMax Pro', 'FreshKeep 2000', 'ChillMaster'])
            }
            device_data['cabinets'].append(cabinet_data)
        
        return device_data
    
    @staticmethod
    def create_cooler(name=None):
        """Create single-door cooler device"""
        return DeviceFactory.create(name=name, device_type_id=1)
    
    @staticmethod
    def create_combo_unit(name=None):
        """Create multi-cabinet combo unit"""
        return DeviceFactory.create(name=name, device_type_id=3)
    
    @staticmethod
    def create_inactive(name=None):
        """Create inactive device"""
        return DeviceFactory.create(name=name, active=False)
```

### Sales Data Factory

```python
class SalesDataFactory:
    """Factory for creating realistic sales test data"""
    
    @staticmethod
    def create_sales_period(device_id, start_date, end_date, daily_transaction_range=(5, 20)):
        """Create sales data for a specific period"""
        from faker import Faker
        from datetime import timedelta
        import random
        
        fake = Faker()
        sales_data = []
        
        current_date = start_date
        while current_date <= end_date:
            # Random number of transactions per day
            daily_transactions = random.randint(*daily_transaction_range)
            
            for _ in range(daily_transactions):
                # Random product (1-12 as per CVD spec)
                product_id = random.randint(1, 12)
                quantity = random.randint(1, 3)
                
                # Price varies by product category
                base_prices = {
                    range(1, 7): 1.50,   # Beverages
                    range(7, 12): 1.75,  # Snacks
                    12: 1.50             # Crackers
                }
                
                price = 1.50  # Default
                for product_range, base_price in base_prices.items():
                    if product_id in product_range:
                        price = base_price
                        break
                
                # Add some price variation (±10%)
                price *= random.uniform(0.9, 1.1)
                
                sales_record = {
                    'device_id': device_id,
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': round(price, 2),
                    'total_amount': round(price * quantity, 2),
                    'transaction_time': fake.date_time_between(current_date, current_date + timedelta(hours=23)),
                    'payment_method': random.choice(['cash', 'card', 'mobile'])
                }
                sales_data.append(sales_record)
            
            current_date += timedelta(days=1)
        
        return sales_data
    
    @staticmethod
    def create_peak_sales_day(device_id, date, peak_products=None):
        """Create high-volume sales data for specific products"""
        peak_products = peak_products or [1, 2, 7, 9]  # Popular items
        sales_data = []
        
        for product_id in peak_products:
            # High sales volume for peak products
            quantity = random.randint(10, 25)
            
            sales_record = {
                'device_id': device_id,
                'product_id': product_id,
                'quantity': quantity,
                'transaction_time': date,
                'notes': 'Peak sales simulation'
            }
            sales_data.append(sales_record)
        
        return sales_data
```

## Assertion Patterns

### Custom Assertion Mixins

```python
class CVDAssertionMixin:
    """Custom assertions for CVD-specific testing"""
    
    def assertServiceOrderValid(self, service_order):
        """Assert service order has valid structure"""
        required_fields = ['id', 'route_id', 'status', 'created_at', 'cabinets']
        
        for field in required_fields:
            self.assertIn(field, service_order, f"Service order missing required field: {field}")
        
        # Validate status
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        self.assertIn(service_order['status'], valid_statuses,
                     f"Invalid service order status: {service_order['status']}")
        
        # Validate cabinets structure
        self.assertIsInstance(service_order['cabinets'], list,
                             "Service order cabinets must be a list")
        
        for cabinet in service_order['cabinets']:
            self.assertCabinetSelectionValid(cabinet)
    
    def assertCabinetSelectionValid(self, cabinet):
        """Assert cabinet selection has valid structure"""
        required_fields = ['device_id', 'cabinet_index', 'status']
        
        for field in required_fields:
            self.assertIn(field, cabinet, f"Cabinet selection missing required field: {field}")
        
        # Validate cabinet index
        self.assertGreaterEqual(cabinet['cabinet_index'], 0,
                               "Cabinet index must be non-negative")
        self.assertLessEqual(cabinet['cabinet_index'], 2,
                            "Cabinet index must be 0-2 for CVD system")
    
    def assertUserHasRole(self, user, expected_role):
        """Assert user has expected role"""
        valid_roles = ['admin', 'manager', 'driver', 'viewer']
        
        self.assertIn('role', user, "User missing role field")
        self.assertIn(user['role'], valid_roles, f"Invalid user role: {user['role']}")
        self.assertEqual(user['role'], expected_role,
                        f"Expected role {expected_role}, got {user['role']}")
    
    def assertAPIResponseValid(self, response, expected_status=200):
        """Assert API response has valid structure"""
        self.assertEqual(response.status_code, expected_status,
                        f"Expected status {expected_status}, got {response.status_code}")
        
        if response.status_code == 200:
            # Response should be valid JSON
            try:
                data = response.get_json()
                self.assertIsNotNone(data, "Response body should contain valid JSON")
            except Exception as e:
                self.fail(f"Response does not contain valid JSON: {e}")
    
    def assertDatabaseIntegrityMaintained(self):
        """Assert database referential integrity is maintained"""
        cursor = self.db.cursor()
        
        # Check for orphaned service order cabinets
        cursor.execute("""
            SELECT COUNT(*) FROM service_order_cabinets soc
            LEFT JOIN service_orders so ON soc.service_order_id = so.id
            WHERE so.id IS NULL
        """)
        orphaned_cabinets = cursor.fetchone()[0]
        self.assertEqual(orphaned_cabinets, 0, "Found orphaned service order cabinets")
        
        # Check for orphaned planogram slots
        cursor.execute("""
            SELECT COUNT(*) FROM planogram_slots ps
            LEFT JOIN planograms p ON ps.planogram_id = p.id
            WHERE p.id IS NULL
        """)
        orphaned_slots = cursor.fetchone()[0]
        self.assertEqual(orphaned_slots, 0, "Found orphaned planogram slots")
    
    def assertAIRecommendationValid(self, recommendation):
        """Assert AI recommendation has valid structure"""
        required_fields = ['slot', 'product_id', 'confidence']
        
        for field in required_fields:
            self.assertIn(field, recommendation,
                         f"AI recommendation missing required field: {field}")
        
        # Validate confidence score
        confidence = recommendation['confidence']
        self.assertGreaterEqual(confidence, 0.0, "Confidence score must be >= 0.0")
        self.assertLessEqual(confidence, 1.0, "Confidence score must be <= 1.0")
        
        # Validate product_id
        product_id = recommendation['product_id']
        self.assertGreaterEqual(product_id, 1, "Product ID must be >= 1")
        self.assertLessEqual(product_id, 12, "Product ID must be <= 12 (system products)")
```

### Performance Assertion Patterns

```python
class PerformanceAssertionMixin:
    """Performance-related assertions"""
    
    def assertResponseTimeAcceptable(self, response_time, max_time, operation_name):
        """Assert response time meets performance requirements"""
        self.assertLess(response_time, max_time,
                       f"{operation_name} took {response_time:.3f}s, exceeds limit of {max_time}s")
    
    def assertMemoryUsageAcceptable(self, memory_before, memory_after, max_growth_mb):
        """Assert memory usage growth is within acceptable limits"""
        memory_growth = (memory_after - memory_before) / (1024 * 1024)  # Convert to MB
        self.assertLess(memory_growth, max_growth_mb,
                       f"Memory growth {memory_growth:.2f}MB exceeds limit of {max_growth_mb}MB")
    
    def assertConcurrentRequestsSuccessful(self, success_count, total_requests, min_success_rate):
        """Assert concurrent requests meet minimum success rate"""
        success_rate = success_count / total_requests
        self.assertGreaterEqual(success_rate, min_success_rate,
                               f"Success rate {success_rate:.2%} below minimum {min_success_rate:.2%}")
```

## Test Organization

### Base Test Classes Hierarchy

```python
class CVDTestCase(unittest.TestCase):
    """Base test case with common CVD testing utilities"""
    
    def setUp(self):
        """Common setup for all CVD tests"""
        self.maxDiff = None  # Show full diff for assertion failures
        
    def debug_print(self, message, data=None):
        """Print debug information during test development"""
        if os.getenv('TEST_DEBUG', 'false').lower() == 'true':
            print(f"DEBUG: {message}")
            if data:
                print(f"DATA: {json.dumps(data, indent=2, default=str)}")

class CVDDatabaseTestCase(CVDTestCase, DatabaseTestCase, CVDAssertionMixin):
    """Base class for database-dependent tests"""
    pass

class CVDAPITestCase(CVDDatabaseTestCase, FlaskTestCase, HTTPMockingMixin):
    """Base class for API endpoint tests"""
    
    def authenticate_as(self, role='admin'):
        """Authenticate test client as specific role"""
        response = self.client.post('/api/auth/login', json={
            'username': role,
            'password': role
        })
        self.assertEqual(response.status_code, 200)
        return response.get_json()
    
    def assert_requires_authentication(self, endpoint, method='GET'):
        """Assert endpoint requires authentication"""
        # Test without authentication
        if method == 'GET':
            response = self.client.get(endpoint)
        elif method == 'POST':
            response = self.client.post(endpoint, json={})
        elif method == 'PUT':
            response = self.client.put(endpoint, json={})
        elif method == 'DELETE':
            response = self.client.delete(endpoint)
        
        self.assertEqual(response.status_code, 401,
                        f"Endpoint {endpoint} should require authentication")
    
    def assert_requires_role(self, endpoint, required_role, method='GET'):
        """Assert endpoint requires specific role"""
        # Test with insufficient role
        lower_roles = {
            'admin': [],
            'manager': ['viewer', 'driver'],
            'driver': ['viewer'],
            'viewer': []
        }
        
        for insufficient_role in lower_roles.get(required_role, []):
            self.authenticate_as(insufficient_role)
            
            if method == 'GET':
                response = self.client.get(endpoint)
            elif method == 'POST':
                response = self.client.post(endpoint, json={})
            
            self.assertEqual(response.status_code, 403,
                            f"Endpoint {endpoint} should deny {insufficient_role} access")

class CVDAITestCase(CVDDatabaseTestCase, AIMockingMixin):
    """Base class for AI feature tests"""
    
    def setUp(self):
        """Set up AI testing environment"""
        super().setUp()
        
        # Create test sales data for AI analysis
        self.create_ai_test_data()
    
    def create_ai_test_data(self):
        """Create realistic sales data for AI testing"""
        from datetime import datetime, timedelta
        
        # Create devices
        device_id = self.create_test_device("AI Test Device")
        
        # Create historical sales data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        sales_data = SalesDataFactory.create_sales_period(
            device_id, start_date, end_date
        )
        
        cursor = self.db.cursor()
        for sale in sales_data:
            cursor.execute("""
                INSERT INTO sales 
                (device_id, product_id, quantity, unit_price, total_amount, transaction_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sale['device_id'], sale['product_id'], sale['quantity'],
                  sale['unit_price'], sale['total_amount'], sale['transaction_time']))
        
        self.db.commit()
```

### Test Method Naming Conventions

```python
class TestNamingExamples(CVDTestCase):
    """Examples of proper test method naming"""
    
    # Unit test naming: test_<method>_<condition>_<expected_result>
    def test_create_service_order_valid_data_returns_order_with_id(self):
        """Test service order creation with valid input data"""
        pass
    
    def test_create_service_order_invalid_route_raises_value_error(self):
        """Test service order creation with invalid route ID"""
        pass
    
    def test_authenticate_user_valid_credentials_returns_user_data(self):
        """Test user authentication with correct credentials"""
        pass
    
    def test_authenticate_user_invalid_password_returns_none(self):
        """Test user authentication with incorrect password"""
        pass
    
    # Integration test naming: test_<workflow>_<scenario>_<expected_outcome>
    def test_service_order_workflow_complete_cycle_updates_all_statuses(self):
        """Test complete service order workflow from creation to completion"""
        pass
    
    def test_planogram_optimization_with_sales_data_returns_valid_recommendations(self):
        """Test planogram optimization with historical sales data"""
        pass
    
    # Performance test naming: test_<operation>_performance_<metric>_<threshold>
    def test_device_listing_performance_response_under_300ms(self):
        """Test device listing API response time"""
        pass
    
    def test_concurrent_service_orders_performance_95_percent_success_rate(self):
        """Test service order creation under concurrent load"""
        pass
    
    # Security test naming: test_<security_concern>_<attack_vector>_<protection_verified>
    def test_sql_injection_malicious_input_prevented_by_parameterization(self):
        """Test SQL injection protection in user authentication"""
        pass
    
    def test_unauthorized_access_cross_role_requests_denied_by_rbac(self):
        """Test role-based access control prevents privilege escalation"""
        pass
```

## Authentication Testing

### Authentication Flow Testing Patterns

```python
class AuthenticationTestMixin:
    """Mixin providing authentication testing utilities"""
    
    def test_login_success_flow(self, username='admin', password='admin'):
        """Test successful login flow"""
        response = self.client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Verify response structure
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('user', data)
        
        # Verify user data
        user = data['user']
        self.assertEqual(user['username'], username)
        self.assertIn('role', user)
        
        # Verify session cookie is set
        cookies = [cookie for cookie in self.client.cookie_jar]
        session_cookie = next((c for c in cookies if c.name == 'session'), None)
        self.assertIsNotNone(session_cookie, "Session cookie not set after login")
        
        return data
    
    def test_login_failure_flow(self, username='admin', password='wrong'):
        """Test failed login flow"""
        response = self.client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
        
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        
        # Verify failure response
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        
        # Verify no session cookie is set
        cookies = [cookie for cookie in self.client.cookie_jar]
        session_cookies = [c for c in cookies if c.name == 'session']
        self.assertEqual(len(session_cookies), 0, "Session cookie set after failed login")
    
    def test_logout_flow(self):
        """Test logout flow"""
        # First login
        self.test_login_success_flow()
        
        # Then logout
        response = self.client.post('/api/auth/logout')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Verify session is invalidated
        current_user_response = self.client.get('/api/auth/current-user')
        self.assertEqual(current_user_response.status_code, 401)
    
    def test_session_persistence(self):
        """Test session persists across requests"""
        # Login
        self.test_login_success_flow()
        
        # Make authenticated request
        response = self.client.get('/api/auth/current-user')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'admin')
    
    def test_role_based_access_patterns(self):
        """Test role-based access control patterns"""
        role_endpoints = {
            'admin': ['/api/users', '/api/admin/settings', '/api/devices', '/api/service-orders'],
            'manager': ['/api/devices', '/api/service-orders', '/api/analytics'],
            'driver': ['/api/service-orders', '/api/devices'],
            'viewer': ['/api/devices', '/api/analytics']
        }
        
        restricted_endpoints = {
            'admin': [],
            'manager': ['/api/admin/settings'],
            'driver': ['/api/users', '/api/admin/settings'],
            'viewer': ['/api/users', '/api/admin/settings', '/api/service-orders']
        }
        
        for role in role_endpoints:
            # Test authorized endpoints
            self.authenticate_as(role)
            
            for endpoint in role_endpoints[role]:
                response = self.client.get(endpoint)
                self.assertNotEqual(response.status_code, 403,
                                  f"{role} should have access to {endpoint}")
            
            # Test restricted endpoints
            for endpoint in restricted_endpoints[role]:
                response = self.client.get(endpoint)
                self.assertEqual(response.status_code, 403,
                               f"{role} should not have access to {endpoint}")
```

### Session Security Testing

```python
class SessionSecurityTestMixin:
    """Mixin providing session security testing utilities"""
    
    def test_session_cookie_security_flags(self):
        """Test session cookie has proper security flags"""
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin'
        })
        
        # Check Set-Cookie header
        set_cookie_header = response.headers.get('Set-Cookie', '')
        
        # Security flags that should be present
        security_flags = ['HttpOnly', 'SameSite']
        
        for flag in security_flags:
            self.assertIn(flag, set_cookie_header,
                         f"Session cookie missing {flag} flag")
    
    def test_session_timeout_enforcement(self):
        """Test session timeout is properly enforced"""
        # Login
        self.authenticate_as('admin')
        
        # Mock time advancement beyond session timeout
        with patch('time.time', return_value=time.time() + 3601):  # 1 hour + 1 second
            response = self.client.get('/api/auth/current-user')
            self.assertEqual(response.status_code, 401,
                           "Session should expire after timeout period")
    
    def test_concurrent_session_handling(self):
        """Test handling of multiple concurrent sessions"""
        # Create multiple clients (simulate multiple browsers)
        client1 = self.app.test_client()
        client2 = self.app.test_client()
        
        # Login with both clients
        login_data = {'username': 'admin', 'password': 'admin'}
        response1 = client1.post('/api/auth/login', json=login_data)
        response2 = client2.post('/api/auth/login', json=login_data)
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Both sessions should be valid
        current_user1 = client1.get('/api/auth/current-user')
        current_user2 = client2.get('/api/auth/current-user')
        
        self.assertEqual(current_user1.status_code, 200)
        self.assertEqual(current_user2.status_code, 200)
        
        # Logout from one session shouldn't affect the other
        client1.post('/api/auth/logout')
        
        current_user1 = client1.get('/api/auth/current-user')
        current_user2 = client2.get('/api/auth/current-user')
        
        self.assertEqual(current_user1.status_code, 401)
        self.assertEqual(current_user2.status_code, 200)
```

## API Testing Patterns

### RESTful API Testing Utilities

```python
class RESTAPITestMixin:
    """Mixin providing RESTful API testing utilities"""
    
    def test_crud_operations(self, endpoint, resource_data, update_data=None):
        """Test complete CRUD operations for a resource"""
        
        # CREATE
        create_response = self.client.post(endpoint, json=resource_data)
        self.assertIn(create_response.status_code, [200, 201],
                     f"CREATE failed for {endpoint}")
        
        created_resource = create_response.get_json()
        resource_id = created_resource['id']
        
        # READ (single resource)
        read_response = self.client.get(f"{endpoint}/{resource_id}")
        self.assertEqual(read_response.status_code, 200,
                        f"READ failed for {endpoint}/{resource_id}")
        
        read_resource = read_response.get_json()
        for key, value in resource_data.items():
            if key in read_resource:
                self.assertEqual(read_resource[key], value,
                               f"READ data mismatch for {key}")
        
        # READ (list resources)
        list_response = self.client.get(endpoint)
        self.assertEqual(list_response.status_code, 200,
                        f"LIST failed for {endpoint}")
        
        resource_list = list_response.get_json()
        self.assertIsInstance(resource_list, list,
                             "LIST should return an array")
        
        # Verify created resource is in list
        resource_ids = [r['id'] for r in resource_list]
        self.assertIn(resource_id, resource_ids,
                     "Created resource not found in list")
        
        # UPDATE (if update_data provided)
        if update_data:
            update_response = self.client.put(f"{endpoint}/{resource_id}", 
                                            json=update_data)
            self.assertEqual(update_response.status_code, 200,
                           f"UPDATE failed for {endpoint}/{resource_id}")
            
            # Verify update
            updated_resource = update_response.get_json()
            for key, value in update_data.items():
                if key in updated_resource:
                    self.assertEqual(updated_resource[key], value,
                                   f"UPDATE data mismatch for {key}")
        
        # DELETE
        delete_response = self.client.delete(f"{endpoint}/{resource_id}")
        self.assertEqual(delete_response.status_code, 200,
                        f"DELETE failed for {endpoint}/{resource_id}")
        
        # Verify resource is deleted (or soft-deleted)
        verify_response = self.client.get(f"{endpoint}/{resource_id}")
        self.assertEqual(verify_response.status_code, 404,
                        "Resource should not be accessible after deletion")
    
    def test_pagination_parameters(self, endpoint):
        """Test API pagination parameters"""
        # Create multiple resources for pagination testing
        for i in range(25):  # Create more than typical page size
            self.client.post(endpoint, json=self.get_sample_resource_data(i))
        
        # Test default pagination
        response = self.client.get(endpoint)
        data = response.get_json()
        
        if isinstance(data, dict) and 'items' in data:
            # Paginated response structure
            self.assertIn('total', data)
            self.assertIn('page', data)
            self.assertIn('per_page', data)
            self.assertLessEqual(len(data['items']), data['per_page'])
        
        # Test custom page size
        response = self.client.get(f"{endpoint}?per_page=10")
        data = response.get_json()
        
        if isinstance(data, dict) and 'items' in data:
            self.assertLessEqual(len(data['items']), 10)
    
    def test_filtering_parameters(self, endpoint, filter_params):
        """Test API filtering parameters"""
        for param_name, param_value in filter_params.items():
            response = self.client.get(f"{endpoint}?{param_name}={param_value}")
            self.assertEqual(response.status_code, 200,
                           f"Filtering by {param_name} failed")
            
            data = response.get_json()
            if isinstance(data, list):
                # Simple list response
                for item in data:
                    if param_name in item:
                        self.assertEqual(str(item[param_name]), str(param_value),
                                       f"Filter {param_name} not applied correctly")
    
    def test_sorting_parameters(self, endpoint, sort_fields):
        """Test API sorting parameters"""
        for field in sort_fields:
            # Test ascending sort
            response = self.client.get(f"{endpoint}?sort={field}&order=asc")
            self.assertEqual(response.status_code, 200,
                           f"Ascending sort by {field} failed")
            
            # Test descending sort
            response = self.client.get(f"{endpoint}?sort={field}&order=desc")
            self.assertEqual(response.status_code, 200,
                           f"Descending sort by {field} failed")
```

### Error Handling Testing

```python
class APIErrorTestMixin:
    """Mixin providing API error handling testing utilities"""
    
    def test_invalid_json_handling(self, endpoint):
        """Test handling of invalid JSON in request body"""
        response = self.client.post(endpoint, 
                                  data='{"invalid": json}',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400,
                        "Should return 400 for invalid JSON")
        
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('json', data['error'].lower())
    
    def test_missing_required_fields(self, endpoint, required_fields):
        """Test handling of missing required fields"""
        for field in required_fields:
            incomplete_data = {f: 'test' for f in required_fields if f != field}
            
            response = self.client.post(endpoint, json=incomplete_data)
            self.assertEqual(response.status_code, 400,
                           f"Should return 400 when {field} is missing")
            
            data = response.get_json()
            self.assertIn('error', data)
            self.assertIn(field, data['error'])
    
    def test_invalid_field_types(self, endpoint, field_types):
        """Test handling of invalid field types"""
        for field, expected_type in field_types.items():
            invalid_data = {field: 'invalid_type' if expected_type != str else 123}
            
            response = self.client.post(endpoint, json=invalid_data)
            self.assertEqual(response.status_code, 400,
                           f"Should return 400 for invalid {field} type")
    
    def test_resource_not_found(self, endpoint):
        """Test handling of non-existent resource requests"""
        response = self.client.get(f"{endpoint}/99999")
        self.assertEqual(response.status_code, 404,
                        "Should return 404 for non-existent resource")
        
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('not found', data['error'].lower())
    
    def test_rate_limiting(self, endpoint, max_requests=100):
        """Test API rate limiting (if implemented)"""
        # Make rapid requests to test rate limiting
        responses = []
        for _ in range(max_requests + 10):
            response = self.client.get(endpoint)
            responses.append(response.status_code)
            
            # Break early if rate limit hit
            if response.status_code == 429:
                break
        
        # If rate limiting is implemented, should get 429 responses
        rate_limited = any(status == 429 for status in responses)
        
        if rate_limited:
            self.assertIn(429, responses, "Rate limiting should return 429 status")
```

These comprehensive testing patterns provide a solid foundation for maintaining consistent, effective tests across the CVD application. They emphasize practical utility, maintainability, and alignment with the existing Flask/SQLite/iframe architecture while supporting the specific needs of AI features, PWA functionality, and role-based access control.