# Database Patterns


## Metadata
- **ID**: 03_ARCHITECTURE_PATTERNS_DATABASE_PATTERNS
- **Type**: Architecture
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #architecture #authentication #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #driver-app #integration #logistics #machine-learning #mobile #operations #optimization #performance #planogram #product-placement #pwa #route-management #security #service-orders #system-design #technical #troubleshooting #vending-machine
- **Intent**: Architecture for Database Patterns
- **Audience**: system administrators, managers, end users, architects
- **Related**: BEST_PRACTICES.md, API_PATTERNS.md, SECURITY_PATTERNS.md, migrations.md
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/03-architecture/patterns/
- **Category**: Patterns
- **Search Keywords**: 1.0, 2025-08-12, always, application, appropriate, args,, audit, cabinet, compliance, connection, context:, cvd, cvd:, data, database

**Document Version:** 1.0  
**Last Updated:** 2025-08-12  
**Status:** Complete

## Introduction

This document outlines the database design patterns, data access strategies, and persistence best practices implemented in the CVD system. These patterns ensure data integrity, performance, and maintainability across all database operations.

## Table of Contents

1. [Database Architecture Overview](#database-architecture-overview)
2. [Soft Delete Pattern](#soft-delete-pattern)
3. [Audit Trail Pattern](#audit-trail-pattern)
4. [Transaction Management](#transaction-management)
5. [Entity Relationship Patterns](#entity-relationship-patterns)
6. [Indexing Strategies](#indexing-strategies)
7. [Data Validation Patterns](#data-validation-patterns)
8. [Migration Patterns](#migration-patterns)
9. [Connection Management](#connection-management)
10. [Performance Optimization](#performance-optimization)

## Database Architecture Overview

### Technology Stack
- **Database Engine**: SQLite (development/small deployments)
- **ORM**: Native SQL with Python DB-API
- **Connection Management**: Flask application context
- **Migration Strategy**: Version-controlled SQL migrations

### Schema Organization

**CVD Database Structure:**
```
Core Entities:
├── users                     # User accounts and authentication
├── devices                   # Vending machine registry  
├── cabinet_configurations    # Device cabinet specifications
├── planograms               # Planogram configurations
├── planogram_slots          # Individual slot configurations
├── products                 # Product catalog
└── service_orders          # Service order management

Supporting Tables:
├── locations               # Geographic locations
├── routes                 # Service routes
├── device_types          # Device type definitions
├── cabinet_types         # Cabinet type specifications
├── sessions             # User session management
└── audit_log           # System audit trail
```

## Soft Delete Pattern

### Implementation Strategy

**Pattern Purpose:**
- Preserve referential integrity
- Enable data recovery
- Maintain historical accuracy
- Support compliance requirements

**Implementation in CVD:**
```sql
-- Users table with soft delete columns
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete columns
    is_deleted BOOLEAN DEFAULT 0,
    deleted_at TIMESTAMP NULL,
    deleted_by INTEGER NULL,
    
    FOREIGN KEY (deleted_by) REFERENCES users(id)
);

-- Devices table soft delete
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location_id INTEGER,
    route_id INTEGER,
    device_type_id INTEGER,
    serial_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete implementation
    deleted BOOLEAN DEFAULT 0,
    deleted_at TIMESTAMP,
    deleted_by TEXT,
    
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (route_id) REFERENCES routes(id),
    FOREIGN KEY (device_type_id) REFERENCES device_types(id)
);
```

### Query Patterns

**Standard Query Implementation:**
```python
# Repository pattern for soft delete queries
class SoftDeleteMixin:
    @staticmethod
    def get_active_records(table_name, conditions=None):
        """Get non-deleted records"""
        base_query = f"SELECT * FROM {table_name} WHERE deleted = 0"
        
        if conditions:
            base_query += f" AND {conditions}"
            
        return db.execute(base_query).fetchall()
    
    @staticmethod
    def soft_delete(table_name, record_id, deleted_by=None):
        """Perform soft delete"""
        update_query = f"""
            UPDATE {table_name} 
            SET deleted = 1, deleted_at = ?, deleted_by = ?
            WHERE id = ?
        """
        db.execute(update_query, (datetime.now(), deleted_by, record_id))
    
    @staticmethod
    def restore_record(table_name, record_id):
        """Restore soft deleted record"""
        update_query = f"""
            UPDATE {table_name}
            SET deleted = 0, deleted_at = NULL, deleted_by = NULL
            WHERE id = ?
        """
        db.execute(update_query, (record_id,))

# API implementation
@app.route('/api/users')
def get_users():
    users = db.execute('SELECT * FROM users WHERE is_deleted = 0').fetchall()
    return jsonify([dict(user) for user in users])

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_role(['admin'])
def delete_user(user_id):
    # Soft delete implementation
    db.execute('''
        UPDATE users 
        SET is_deleted = 1, deleted_at = ?, deleted_by = ?
        WHERE id = ?
    ''', (datetime.now(), g.current_user['id'], user_id))
    
    db.commit()
    
    # Log audit event
    log_audit_event(g.current_user['id'], 'user_deleted', 
                   'user', user_id, f'Soft deleted user {user_id}')
    
    return jsonify({'message': 'User deleted successfully'})
```

### Indexing for Soft Delete

```sql
-- Optimize queries that filter by deleted status
CREATE INDEX idx_users_active_deleted ON users(is_active, is_deleted);
CREATE INDEX idx_devices_deleted ON devices(deleted);
CREATE INDEX idx_planograms_active ON planograms(deleted_at) WHERE deleted_at IS NULL;
```

## Audit Trail Pattern

### Implementation Strategy

**Audit Log Schema:**
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,           -- 'create', 'update', 'delete', 'login', etc.
    resource_type TEXT,             -- 'user', 'device', 'planogram', etc.
    resource_id INTEGER,            -- ID of affected resource
    details TEXT,                   -- JSON details of change
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for audit queries
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
```

**Audit Logging Implementation:**
```python
def log_audit_event(user_id, action, resource_type=None, resource_id=None, 
                   details=None, ip_address=None):
    """Log audit event with comprehensive tracking"""
    if ip_address is None:
        ip_address = request.remote_addr if request else 'system'
    
    user_agent = request.headers.get('User-Agent') if request else 'system'
    
    # Prepare details as JSON
    details_json = json.dumps(details) if details and not isinstance(details, str) else details
    
    try:
        db = get_db()
        db.execute('''
            INSERT INTO audit_log 
            (user_id, action, resource_type, resource_id, details, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, action, resource_type, resource_id, details_json, 
              ip_address, user_agent))
        db.commit()
        
    except Exception as e:
        # Audit logging should not break application flow
        print(f"Audit logging error: {e}")

# Usage in API endpoints
@app.route('/api/users', methods=['POST'])
@require_role(['admin'])
def create_user():
    data = request.json
    
    # Create user logic
    cursor = db.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', (data['username'], data['email'], password_hash, data['role']))
    
    user_id = cursor.lastrowid
    db.commit()
    
    # Log audit event
    log_audit_event(
        user_id=g.current_user['id'],
        action='user_created',
        resource_type='user',
        resource_id=user_id,
        details={
            'username': data['username'],
            'role': data['role'],
            'created_by': g.current_user['username']
        }
    )
    
    return jsonify({'id': user_id, 'message': 'User created'})
```

### Session Tracking Pattern

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,                    -- Session token
    user_id INTEGER NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activity_count INTEGER DEFAULT 0,
    device_type TEXT,                       -- 'mobile', 'desktop', 'tablet'
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Session management indexes
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
CREATE INDEX idx_sessions_activity ON sessions(last_activity);
```

## Transaction Management

### Connection Management Pattern

**Flask Application Context:**
```python
from flask import g
import sqlite3

DATABASE = 'cvd.db'

def get_db():
    """Get database connection with proper configuration"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Enable column name access
        
        # Enable foreign key constraints
        g.db.execute('PRAGMA foreign_keys = ON')
        
        # Set journal mode for better concurrency
        g.db.execute('PRAGMA journal_mode = WAL')
        
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Transaction Patterns

**Service Layer Transaction Management:**
```python
class ServiceOrderService:
    @staticmethod
    def create_service_order(route_id, cabinet_selections, created_by=None):
        """Create service order with proper transaction handling"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Start transaction (implicit with sqlite3)
            db.execute('BEGIN')
            
            # Calculate pick list from cabinet selections
            pick_list = ServiceOrderService.calculate_pick_list(cabinet_selections)
            total_units = sum(item['quantity'] for item in pick_list)
            estimated_minutes = len(cabinet_selections) * 10
            
            # Create service order
            cursor.execute('''
                INSERT INTO service_orders 
                (route_id, driver_id, created_by, status, total_units, estimated_duration_minutes)
                VALUES (?, ?, ?, 'pending', ?, ?)
            ''', (route_id, None, created_by, total_units, estimated_minutes))
            
            order_id = cursor.lastrowid
            
            # Create cabinet entries and items
            for selection in cabinet_selections:
                # Get cabinet configuration
                cabinet_config = cursor.execute('''
                    SELECT id FROM cabinet_configurations
                    WHERE device_id = ? AND cabinet_index = ?
                ''', (selection['deviceId'], selection['cabinetIndex'])).fetchone()
                
                if not cabinet_config:
                    raise ValueError(f"Cabinet configuration not found")
                
                # Create service order cabinet entry
                cursor.execute('''
                    INSERT INTO service_order_cabinets
                    (service_order_id, cabinet_configuration_id)
                    VALUES (?, ?)
                ''', (order_id, cabinet_config['id']))
                
                service_order_cabinet_id = cursor.lastrowid
                
                # Create cabinet items
                products_needed = cursor.execute('''
                    SELECT ps.product_id, SUM(ps.par_level - ps.quantity) as quantity_needed
                    FROM planogram_slots ps
                    JOIN planograms p ON ps.planogram_id = p.id
                    WHERE p.cabinet_id = ? AND ps.product_id != 1
                    AND ps.par_level > ps.quantity
                    GROUP BY ps.product_id
                ''', (cabinet_config['id'],)).fetchall()
                
                for product in products_needed:
                    cursor.execute('''
                        INSERT INTO service_order_cabinet_items
                        (service_order_cabinet_id, product_id, quantity_needed)
                        VALUES (?, ?, ?)
                    ''', (service_order_cabinet_id, product['product_id'], 
                          product['quantity_needed']))
            
            # Commit transaction
            db.commit()
            
            # Log audit event
            log_audit_event(created_by, 'service_order_created', 'service_order', 
                          order_id, {'cabinet_count': len(cabinet_selections)})
            
            return {
                'orderId': order_id,
                'totalUnits': total_units,
                'estimatedMinutes': estimated_minutes,
                'pickList': pick_list
            }
            
        except Exception as e:
            # Rollback on error
            db.rollback()
            raise e
```

### Atomic Operations Pattern

```python
def atomic_operation(func):
    """Decorator for atomic database operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = get_db()
        try:
            db.execute('BEGIN')
            result = func(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise e
    return wrapper

@atomic_operation
def transfer_device_ownership(device_id, new_route_id, transferred_by):
    """Atomically transfer device to new route"""
    db = get_db()
    
    # Update device
    db.execute('''
        UPDATE devices 
        SET route_id = ?, updated_at = ?
        WHERE id = ?
    ''', (new_route_id, datetime.now(), device_id))
    
    # Log audit event
    log_audit_event(transferred_by, 'device_transferred', 'device', device_id,
                   {'new_route_id': new_route_id})
```

## Entity Relationship Patterns

### Foreign Key Relationships

**Referential Integrity Implementation:**
```sql
-- Cabinet configurations belong to devices
ALTER TABLE cabinet_configurations 
ADD CONSTRAINT fk_cabinet_device 
FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE;

-- Planograms belong to cabinets
ALTER TABLE planograms 
ADD CONSTRAINT fk_planogram_cabinet 
FOREIGN KEY (cabinet_id) REFERENCES cabinet_configurations(id) ON DELETE CASCADE;

-- Planogram slots belong to planograms
ALTER TABLE planogram_slots 
ADD CONSTRAINT fk_slot_planogram 
FOREIGN KEY (planogram_id) REFERENCES planograms(id) ON DELETE CASCADE;

-- Products can be referenced but not deleted if in use
ALTER TABLE planogram_slots 
ADD CONSTRAINT fk_slot_product 
FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL;
```

### Association Patterns

**Many-to-Many Relationships:**
```sql
-- Service order cabinets (association table)
CREATE TABLE service_order_cabinets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_order_id INTEGER NOT NULL,
    cabinet_configuration_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    completed_at TIMESTAMP,
    notes TEXT,
    
    FOREIGN KEY (service_order_id) REFERENCES service_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (cabinet_configuration_id) REFERENCES cabinet_configurations(id),
    UNIQUE(service_order_id, cabinet_configuration_id)
);

-- User role assignments (future enhancement)
CREATE TABLE user_roles (
    user_id INTEGER NOT NULL,
    role_name TEXT NOT NULL,
    assigned_by INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id),
    PRIMARY KEY (user_id, role_name)
);
```

## Indexing Strategies

### Performance Optimization Indexes

```sql
-- Primary lookup indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_devices_serial ON devices(serial_number);

-- Foreign key indexes
CREATE INDEX idx_cabinets_device ON cabinet_configurations(device_id);
CREATE INDEX idx_planograms_cabinet ON planograms(cabinet_id);
CREATE INDEX idx_slots_planogram ON planogram_slots(planogram_id);
CREATE INDEX idx_slots_product ON planogram_slots(product_id);

-- Composite indexes for common queries
CREATE INDEX idx_users_active_deleted ON users(is_active, is_deleted);
CREATE INDEX idx_devices_route_location ON devices(route_id, location_id);
CREATE INDEX idx_sessions_user_expires ON sessions(user_id, expires_at);

-- Audit trail indexes
CREATE INDEX idx_audit_user_action ON audit_log(user_id, action);
CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id);
CREATE INDEX idx_audit_created_at ON audit_log(created_at);

-- Partial indexes for soft delete
CREATE INDEX idx_active_users ON users(username) WHERE is_deleted = 0;
CREATE INDEX idx_active_devices ON devices(name) WHERE deleted = 0;
```

### Query Optimization Patterns

```python
def get_user_activity_summary(user_id, days=30):
    """Optimized query for user activity"""
    since_date = datetime.now() - timedelta(days=days)
    
    query = '''
        SELECT 
            action,
            COUNT(*) as action_count,
            MAX(created_at) as last_occurrence
        FROM audit_log 
        WHERE user_id = ? AND created_at >= ?
        GROUP BY action
        ORDER BY action_count DESC
    '''
    
    return db.execute(query, (user_id, since_date)).fetchall()

def get_device_utilization(route_id=None, location_id=None):
    """Optimized device utilization query"""
    conditions = ['d.deleted = 0']
    params = []
    
    if route_id:
        conditions.append('d.route_id = ?')
        params.append(route_id)
    
    if location_id:
        conditions.append('d.location_id = ?')
        params.append(location_id)
    
    query = f'''
        SELECT 
            d.id,
            d.name,
            COUNT(cc.id) as cabinet_count,
            l.name as location_name,
            r.name as route_name
        FROM devices d
        LEFT JOIN cabinet_configurations cc ON d.id = cc.device_id
        LEFT JOIN locations l ON d.location_id = l.id
        LEFT JOIN routes r ON d.route_id = r.id
        WHERE {' AND '.join(conditions)}
        GROUP BY d.id
        ORDER BY d.name
    '''
    
    return db.execute(query, params).fetchall()
```

## Data Validation Patterns

### Constraint-Based Validation

```sql
-- Enum constraints
CREATE TABLE users (
    role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
    -- other columns...
);

-- Range constraints
CREATE TABLE products (
    price DECIMAL(10,2) NOT NULL CHECK(price >= 0),
    -- other columns...
);

CREATE TABLE cabinet_configurations (
    rows INTEGER NOT NULL CHECK(rows > 0 AND rows <= 20),
    columns INTEGER NOT NULL CHECK(columns > 0 AND columns <= 20),
    -- other columns...
);
```

### Application-Level Validation

```python
def validate_planogram_slot(slot_data):
    """Validate planogram slot data"""
    errors = []
    
    # Quantity validation
    if 'quantity' in slot_data:
        quantity = slot_data['quantity']
        if not isinstance(quantity, int) or quantity < 0:
            errors.append('Quantity must be a non-negative integer')
    
    # Capacity validation
    if 'capacity' in slot_data and 'quantity' in slot_data:
        if slot_data['quantity'] > slot_data['capacity']:
            errors.append('Quantity cannot exceed capacity')
    
    # Par level validation
    if 'par_level' in slot_data and 'capacity' in slot_data:
        if slot_data['par_level'] > slot_data['capacity']:
            errors.append('Par level cannot exceed capacity')
    
    # Price validation
    if 'price' in slot_data:
        try:
            price = float(slot_data['price'])
            if price < 0:
                errors.append('Price must be non-negative')
        except (ValueError, TypeError):
            errors.append('Price must be a valid number')
    
    return errors
```

## Migration Patterns

### Schema Migration Strategy

**Migration File Structure:**
```
migrations/
├── 001_initial_schema.sql
├── 002_add_soft_delete_users.sql
├── 003_add_audit_logging.sql
├── 004_add_session_tracking.sql
└── 005_optimize_indexes.sql
```

**Migration Implementation:**
```python
import os
import sqlite3
from datetime import datetime

class DatabaseMigrator:
    def __init__(self, db_path, migrations_dir):
        self.db_path = db_path
        self.migrations_dir = migrations_dir
        self.ensure_migration_table()
    
    def ensure_migration_table(self):
        """Create migration tracking table"""
        with sqlite3.connect(self.db_path) as db:
            db.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def get_applied_migrations(self):
        """Get list of applied migrations"""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute('SELECT version FROM schema_migrations')
            return {row[0] for row in cursor.fetchall()}
    
    def get_pending_migrations(self):
        """Get list of pending migrations"""
        applied = self.get_applied_migrations()
        all_migrations = set()
        
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith('.sql'):
                all_migrations.add(filename)
        
        return sorted(all_migrations - applied)
    
    def apply_migration(self, migration_file):
        """Apply a single migration"""
        migration_path = os.path.join(self.migrations_dir, migration_file)
        
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        with sqlite3.connect(self.db_path) as db:
            try:
                db.executescript(migration_sql)
                db.execute('''
                    INSERT INTO schema_migrations (version)
                    VALUES (?)
                ''', (migration_file,))
                print(f"Applied migration: {migration_file}")
                
            except Exception as e:
                print(f"Failed to apply migration {migration_file}: {e}")
                raise
    
    def migrate(self):
        """Apply all pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("No pending migrations")
            return
        
        for migration in pending:
            self.apply_migration(migration)
        
        print(f"Applied {len(pending)} migrations")

# Usage
migrator = DatabaseMigrator('cvd.db', 'migrations')
migrator.migrate()
```

## Performance Optimization

### Query Performance Patterns

```python
# Use row factory for better performance
def get_db_optimized():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    
    # Enable query optimization
    db.execute('PRAGMA optimize')
    
    # Set cache size (in KB)
    db.execute('PRAGMA cache_size = 10000')  # 10MB cache
    
    return db

# Batch operations for better performance
def batch_update_planogram_slots(planogram_id, slot_updates):
    """Update multiple planogram slots efficiently"""
    db = get_db()
    
    # Use executemany for batch operations
    update_data = [
        (slot['quantity'], slot['par_level'], planogram_id, slot['position'])
        for slot in slot_updates
    ]
    
    db.executemany('''
        UPDATE planogram_slots 
        SET quantity = ?, par_level = ?
        WHERE planogram_id = ? AND slot_position = ?
    ''', update_data)
    
    db.commit()

# Connection pooling pattern (for future scaling)
class ConnectionPool:
    def __init__(self, database_path, pool_size=5):
        self.database_path = database_path
        self.pool_size = pool_size
        self.pool = []
        self._create_pool()
    
    def _create_pool(self):
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.database_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.pool.append(conn)
    
    def get_connection(self):
        if self.pool:
            return self.pool.pop()
        else:
            # Create new connection if pool is empty
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def return_connection(self, conn):
        if len(self.pool) < self.pool_size:
            self.pool.append(conn)
        else:
            conn.close()
```

## Implementation Guidelines

### Database Design Checklist

- [ ] **Referential Integrity**: Foreign keys properly defined
- [ ] **Soft Delete**: Implemented where data recovery is needed
- [ ] **Audit Trail**: Comprehensive logging for sensitive operations
- [ ] **Indexing**: Appropriate indexes for query performance
- [ ] **Validation**: Both constraint-based and application validation
- [ ] **Transactions**: Proper transaction handling for data consistency
- [ ] **Migration**: Version-controlled schema changes

### Best Practices

1. **Always use transactions** for multi-table operations
2. **Implement soft delete** for core business entities
3. **Create comprehensive audit trails** for compliance
4. **Optimize queries** with appropriate indexes
5. **Validate data** at both database and application levels
6. **Plan for schema evolution** with migration strategies
7. **Monitor performance** and optimize as needed

## Related Documentation

- [API Patterns](./API_PATTERNS.md) - API-database integration patterns
- [Security Patterns](./SECURITY_PATTERNS.md) - Database security patterns
- [Performance Patterns](../BEST_PRACTICES.md) - Database performance optimization
- [Migration Guide](../../04-implementation/backend/migrations.md) - Schema migration procedures

## References

- SQLite Documentation
- Database Design Patterns
- ACID Transaction Properties
- SQL Performance Tuning Best Practices