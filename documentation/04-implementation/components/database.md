# Database Layer Component


## Metadata
- **ID**: 04_IMPLEMENTATION_COMPONENTS_DATABASE
- **Type**: Implementation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #code #data-exchange #data-layer #database #debugging #device-management #dex-parser #features #implementation #integration #logistics #machine-learning #operations #optimization #performance #planogram #product-placement #quality-assurance #route-management #service-orders #testing #troubleshooting #vending-machine
- **Intent**: Implementation for Database Layer Component
- **Audience**: developers, system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/04-implementation/components/
- **Category**: Components
- **Search Keywords**: ###, ####, application-level, backup, batch, boundaries, cabinet, check, commits, component, connection, constraints, cooler, database, debugging

## Overview

The database layer provides SQLite-based data persistence for the CVD application, implementing Flask's application context pattern for connection management, prepared statements for security, and comprehensive transaction handling. The layer supports both direct database operations and Flask-integrated request-scoped connections.

## Connection Management

### Flask Application Context Integration

#### Primary Connection Pattern
```python
def get_db():
    """Get database connection for current request context"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection at end of request"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
```

#### Connection Configuration
- **Database File**: `cvd.db` SQLite file in application root
- **Row Factory**: `sqlite3.Row` provides dict-like access to columns
- **Foreign Keys**: `PRAGMA foreign_keys = ON` enforced at application level
- **Request Scope**: One connection per HTTP request via Flask's `g` object

#### Context-Aware Connection Access
```python
# Within Flask request context
db = get_db()
cursor = db.cursor()

# Within auth.py or other modules
from flask import current_app

get_db = current_app.config.get('get_db')
if get_db:
    db = get_db()  # Use Flask's connection
else:
    db = sqlite3.connect(DATABASE)  # Direct connection
    db.row_factory = sqlite3.Row
```

### Direct Connection Pattern

#### Non-Flask Context Operations
```python
def cleanup_expired_sessions(self):
    """Remove expired sessions from database"""
    db = sqlite3.connect(self.db_path)
    cursor = db.cursor()
    
    deleted = cursor.execute('''
        DELETE FROM sessions WHERE expires_at < ?
    ''', (datetime.now(),)).rowcount
    
    db.commit()
    db.close()
    
    if deleted > 0:
        print(f'Cleaned up {deleted} expired sessions')
```

#### Connection Cleanup Patterns
```python
# Pattern 1: Context manager (recommended)
with closing(sqlite3.connect(DATABASE)) as db:
    cursor = db.cursor()
    # Operations here
    db.commit()

# Pattern 2: Try-finally
db = sqlite3.connect(DATABASE)
try:
    cursor = db.cursor()
    # Operations here
    db.commit()
finally:
    db.close()

# Pattern 3: Conditional cleanup
if db is None:
    db_path = current_app.config.get('DATABASE', 'cvd.db')
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    should_close = True
else:
    should_close = False

try:
    # Database operations
finally:
    if should_close:
        db.close()
```

## Query Patterns and Prepared Statements

### Parameterized Queries

#### Basic Parameter Binding
```python
# User validation with multiple parameters
user = cursor.execute('''
    SELECT u.id, u.username, u.email, u.role, u.is_active, u.is_deleted
    FROM users u
    JOIN sessions s ON s.user_id = u.id
    WHERE s.id = ? AND s.expires_at > ? AND u.is_active = 1 AND u.is_deleted = 0
''', (session_id, datetime.now())).fetchone()
```

#### Complex Query Patterns
```python
# Multi-table joins with filtering
devices = cursor.execute('''
    SELECT d.id, d.asset, d.cooler, d.model,
           l.name as location_name, l.address,
           dt.name as device_type_name,
           r.name as route_name
    FROM devices d
    LEFT JOIN locations l ON d.location_id = l.id
    LEFT JOIN device_types dt ON d.device_type_id = dt.id
    LEFT JOIN routes r ON d.route_id = r.id
    WHERE d.deleted_at IS NULL
    ORDER BY d.created_at DESC
''').fetchall()
```

#### Dynamic Query Building
```python
# Sales filtering with optional parameters
def get_sales_with_filters(device_id=None, product_id=None, start_date=None, end_date=None):
    query = '''
        SELECT s.*, d.asset as device_asset, p.name as product_name
        FROM sales s
        JOIN devices d ON s.device_id = d.id
        JOIN products p ON s.product_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if device_id:
        query += ' AND s.device_id = ?'
        params.append(device_id)
    if product_id:
        query += ' AND s.product_id = ?'
        params.append(product_id)
    if start_date:
        query += ' AND s.created_at >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND s.created_at <= ?'
        params.append(end_date)
    
    query += ' ORDER BY s.created_at DESC'
    
    return cursor.execute(query, params).fetchall()
```

### Bulk Operations

#### Batch Insert Pattern
```python
# Planogram slots bulk creation
def create_all_planogram_slots(planogram_id, rows, cols, cursor):
    slot_data = []
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            slot_position = f"{row:02d}{col:02d}"
            slot_data.append((planogram_id, slot_position))
    
    cursor.executemany('''
        INSERT INTO planogram_slots (planogram_id, slot_position)
        VALUES (?, ?)
    ''', slot_data)
```

#### Batch Update Pattern
```python
# Service order cabinet updates
def update_service_order_cabinets(updates):
    cursor.executemany('''
        UPDATE service_order_cabinets 
        SET status = ?, completed_at = ?, notes = ?
        WHERE id = ?
    ''', updates)
```

## Transaction Handling

### Flask Request Transaction Pattern

#### Automatic Transaction Scope
```python
@app.route('/api/devices', methods=['POST'])
@auth_manager.require_role(['admin', 'manager'])
def create_device():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Multiple related operations
        device_id = cursor.execute('''
            INSERT INTO devices (asset, cooler, location_id, model, device_type_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (asset, cooler, location_id, model, device_type_id)).lastrowid
        
        # Create cabinet configurations
        for cabinet in cabinet_configurations:
            cursor.execute('''
                INSERT INTO cabinet_configurations 
                (device_id, cabinet_type_id, model_name, is_parent, cabinet_index, rows, columns)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (device_id, cabinet['cabinet_type_id'], cabinet['model_name'], 
                  cabinet['is_parent'], cabinet['cabinet_index'], 
                  cabinet['rows'], cabinet['columns']))
        
        db.commit()
        return jsonify({'success': True, 'device_id': device_id})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
```

#### Explicit Transaction Control
```python
def migrate_planogram_data(device_mappings):
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Begin explicit transaction
        cursor.execute('BEGIN TRANSACTION')
        
        for device_mapping in device_mappings:
            # Create planogram
            planogram_id = cursor.execute('''
                INSERT INTO planograms (cabinet_id, planogram_key)
                VALUES (?, ?)
            ''', (device_mapping['cabinet_id'], device_mapping['planogram_key'])).lastrowid
            
            # Create slots
            create_all_planogram_slots(planogram_id, rows, cols, cursor)
            
            # Update slot data
            for slot_data in device_mapping['slots']:
                cursor.execute('''
                    UPDATE planogram_slots 
                    SET product_id = ?, quantity = ?, capacity = ?, par_level = ?
                    WHERE planogram_id = ? AND slot_position = ?
                ''', (slot_data['product_id'], slot_data['quantity'],
                      slot_data['capacity'], slot_data['par_level'],
                      planogram_id, slot_data['position']))
        
        # Explicit commit
        cursor.execute('COMMIT')
        return {'success': True, 'migrated_count': len(device_mappings)}
        
    except Exception as e:
        # Explicit rollback
        cursor.execute('ROLLBACK')
        raise e
```

### Session Management Transactions

#### Session Creation with Context
```python
def create_session(self, user_id, db=None):
    """Create a new session for user"""
    from flask import current_app
    
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=8)
    
    # Use provided db connection or get from Flask context
    if db is None:
        db = current_app.config.get('get_db')()
    
    cursor = db.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (id, user_id, expires_at, ip_address, user_agent,
                            last_activity, activity_count, device_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, user_id, expires_at, 
          request.remote_addr, user_agent,
          datetime.now(), 0, device_type))
    
    # Don't commit here, let the caller handle it
    return session_id
```

## ACID Properties Implementation

### Atomicity
- **Transaction Boundaries**: Explicit BEGIN/COMMIT/ROLLBACK for complex operations
- **Error Handling**: Comprehensive rollback on exceptions
- **Batch Operations**: Multiple related operations in single transactions

### Consistency
- **Foreign Key Constraints**: `PRAGMA foreign_keys = ON` enforces referential integrity
- **Check Constraints**: Database-level validation where appropriate
- **Application-Level Validation**: Business rules enforced before database operations

```sql
-- Foreign key constraint example
FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
```

### Isolation
- **SQLite Default**: Serializable isolation level
- **Connection Scope**: One connection per request prevents interference
- **Lock Handling**: SQLite's automatic locking mechanism

### Durability
- **Immediate Commits**: Changes committed to disk immediately
- **WAL Mode**: Write-Ahead Logging for better concurrency
- **Backup Strategy**: Regular database backups for recovery

## Soft Delete Implementation Pattern

### Soft Delete Schema Design
```sql
-- Devices table with soft delete support
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset TEXT UNIQUE NOT NULL,
    cooler TEXT NOT NULL,
    -- ... other columns
    deleted_at TIMESTAMP,
    deleted_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Soft Delete Query Patterns
```python
# Standard query excluding soft-deleted records
active_devices = cursor.execute('''
    SELECT * FROM devices 
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
''').fetchall()

# Include soft-deleted records for admin views
all_devices = cursor.execute('''
    SELECT *, 
           CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END as is_deleted
    FROM devices 
    ORDER BY created_at DESC
''').fetchall()

# Soft delete operation
cursor.execute('''
    UPDATE devices 
    SET deleted_at = ?, deleted_by = ?, updated_at = ?
    WHERE id = ?
''', (datetime.now(), current_user_id, datetime.now(), device_id))
```

### Soft Delete Recovery
```python
# Restore soft-deleted record
def restore_device(device_id, restored_by):
    cursor.execute('''
        UPDATE devices 
        SET deleted_at = NULL, deleted_by = NULL, updated_at = ?
        WHERE id = ?
    ''', (datetime.now(), device_id))
    
    # Log restoration event
    log_audit_event(
        user_id=restored_by,
        action='DEVICE_RESTORED',
        resource_type='device',
        resource_id=device_id
    )
```

## Performance Optimization Strategies

### Index Strategy
```sql
-- Primary performance indexes
CREATE INDEX idx_devices_deleted_at ON devices(deleted_at);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sales_device_id ON sales(device_id);
CREATE INDEX idx_sales_created_at ON sales(created_at);
CREATE INDEX idx_planogram_slots_planogram_id ON planogram_slots(planogram_id);
```

### Query Optimization Patterns
```python
# Efficient pagination
def get_devices_paginated(page=1, per_page=50):
    offset = (page - 1) * per_page
    devices = cursor.execute('''
        SELECT * FROM devices 
        WHERE deleted_at IS NULL
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    
    total_count = cursor.execute('''
        SELECT COUNT(*) FROM devices WHERE deleted_at IS NULL
    ''').fetchone()[0]
    
    return devices, total_count

# Efficient joins for related data
def get_devices_with_details():
    return cursor.execute('''
        SELECT 
            d.id, d.asset, d.cooler, d.model,
            l.name as location_name,
            dt.name as device_type_name,
            COUNT(cc.id) as cabinet_count
        FROM devices d
        LEFT JOIN locations l ON d.location_id = l.id
        LEFT JOIN device_types dt ON d.device_type_id = dt.id
        LEFT JOIN cabinet_configurations cc ON d.id = cc.device_id
        WHERE d.deleted_at IS NULL
        GROUP BY d.id, d.asset, d.cooler, d.model, l.name, dt.name
        ORDER BY d.created_at DESC
    ''').fetchall()
```

### Connection Pooling and Resource Management

#### SQLite-Specific Optimizations
```python
# Database initialization with optimization
def init_db():
    with closing(sqlite3.connect(DATABASE)) as db:
        db.execute('PRAGMA foreign_keys = ON')
        db.execute('PRAGMA journal_mode = WAL')  # Write-Ahead Logging
        db.execute('PRAGMA synchronous = NORMAL')  # Faster writes
        db.execute('PRAGMA cache_size = -64000')  # 64MB cache
        db.execute('PRAGMA temp_store = MEMORY')  # Memory temp tables
        
        # Create schema and indexes
        create_tables(db)
        create_indexes(db)
```

#### Connection Reuse Patterns
```python
# Reuse Flask's connection for multiple operations
def complex_device_operation(device_data):
    db = get_db()  # Reuses request-scoped connection
    cursor = db.cursor()
    
    try:
        # Multiple operations using same connection
        device_id = create_device_record(cursor, device_data)
        create_cabinet_configurations(cursor, device_id, device_data['cabinets'])
        create_initial_planograms(cursor, device_id)
        
        db.commit()
        return device_id
        
    except Exception as e:
        db.rollback()
        raise e
```

## Database Migration Approach

### Schema Evolution Pattern
```python
def migrate_database_schema():
    """Apply database schema migrations"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check current schema version
        try:
            version = cursor.execute('''
                SELECT version FROM schema_version ORDER BY id DESC LIMIT 1
            ''').fetchone()
            current_version = version[0] if version else 0
        except sqlite3.OperationalError:
            # Schema version table doesn't exist, create it
            cursor.execute('''
                CREATE TABLE schema_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            current_version = 0
        
        # Apply migrations
        migrations = [
            (1, add_soft_delete_columns),
            (2, add_activity_monitoring_tables),
            (3, add_security_enhancement_columns),
            (4, add_knowledge_base_tables)
        ]
        
        for version, migration_func in migrations:
            if current_version < version:
                print(f'Applying migration {version}...')
                migration_func(cursor)
                cursor.execute('''
                    INSERT INTO schema_version (version) VALUES (?)
                ''', (version,))
                current_version = version
        
        db.commit()
        print(f'Database schema up to date (version {current_version})')
        
    except Exception as e:
        db.rollback()
        print(f'Migration failed: {e}')
        raise e
```

### Data Migration Patterns
```python
def migrate_planogram_data():
    """Migrate planogram data to new structure"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get existing planogram data
        old_planograms = cursor.execute('''
            SELECT * FROM legacy_planograms
        ''').fetchall()
        
        for planogram in old_planograms:
            # Create new planogram record
            new_id = cursor.execute('''
                INSERT INTO planograms (cabinet_id, planogram_key, updated_at)
                VALUES (?, ?, ?)
            ''', (planogram['cabinet_id'], planogram['key'], 
                  planogram['updated_at'])).lastrowid
            
            # Migrate slot data
            migrate_planogram_slots(cursor, planogram['id'], new_id)
        
        # Clean up old data after successful migration
        cursor.execute('DROP TABLE legacy_planograms')
        
        db.commit()
        print(f'Migrated {len(old_planograms)} planograms')
        
    except Exception as e:
        db.rollback()
        print(f'Planogram migration failed: {e}')
        raise e
```

## Error Handling and Logging

### Database Error Categories
```python
import sqlite3

def handle_database_error(e, operation_context):
    """Centralized database error handling"""
    if isinstance(e, sqlite3.IntegrityError):
        if 'UNIQUE constraint failed' in str(e):
            return {'error': 'Record already exists', 'type': 'duplicate'}, 409
        elif 'FOREIGN KEY constraint failed' in str(e):
            return {'error': 'Referenced record not found', 'type': 'reference'}, 400
        else:
            return {'error': 'Data integrity violation', 'type': 'integrity'}, 400
    
    elif isinstance(e, sqlite3.OperationalError):
        if 'database is locked' in str(e):
            return {'error': 'Database temporarily unavailable', 'type': 'lock'}, 503
        elif 'no such table' in str(e):
            return {'error': 'Database schema error', 'type': 'schema'}, 500
        else:
            return {'error': 'Database operation failed', 'type': 'operational'}, 500
    
    else:
        # Log unexpected errors
        print(f'Unexpected database error in {operation_context}: {e}')
        return {'error': 'Database error occurred', 'type': 'unknown'}, 500
```

### Query Debugging
```python
def execute_query_with_logging(cursor, query, params=None):
    """Execute query with debugging information"""
    import time
    
    start_time = time.time()
    try:
        if params:
            result = cursor.execute(query, params)
        else:
            result = cursor.execute(query)
        
        execution_time = time.time() - start_time
        
        # Log slow queries (> 100ms)
        if execution_time > 0.1:
            print(f'Slow query ({execution_time:.3f}s): {query[:100]}...')
        
        return result
        
    except Exception as e:
        print(f'Query failed: {query}')
        print(f'Parameters: {params}')
        print(f'Error: {e}')
        raise e
```

## Common Usage Patterns

### Repository Pattern Implementation
```python
class DeviceRepository:
    def __init__(self, db=None):
        self.db = db or get_db()
        self.cursor = self.db.cursor()
    
    def get_all_active(self):
        return self.cursor.execute('''
            SELECT * FROM devices WHERE deleted_at IS NULL
            ORDER BY created_at DESC
        ''').fetchall()
    
    def get_by_id(self, device_id):
        return self.cursor.execute('''
            SELECT * FROM devices WHERE id = ? AND deleted_at IS NULL
        ''', (device_id,)).fetchone()
    
    def create(self, device_data):
        return self.cursor.execute('''
            INSERT INTO devices (asset, cooler, location_id, model, device_type_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (device_data['asset'], device_data['cooler'],
              device_data['location_id'], device_data['model'],
              device_data['device_type_id'])).lastrowid
    
    def soft_delete(self, device_id, deleted_by):
        self.cursor.execute('''
            UPDATE devices 
            SET deleted_at = ?, deleted_by = ?, updated_at = ?
            WHERE id = ?
        ''', (datetime.now(), deleted_by, datetime.now(), device_id))
```

### Data Access Layer Pattern
```python
class DataAccessLayer:
    @staticmethod
    def dict_from_row(row):
        """Convert SQLite Row to dictionary"""
        if row is None:
            return None
        return {key: row[key] for key in row.keys()}
    
    @staticmethod
    def execute_scalar(cursor, query, params=None):
        """Execute query and return single value"""
        result = cursor.execute(query, params or ()).fetchone()
        return result[0] if result else None
    
    @staticmethod
    def execute_list(cursor, query, params=None):
        """Execute query and return list of dictionaries"""
        rows = cursor.execute(query, params or ()).fetchall()
        return [DataAccessLayer.dict_from_row(row) for row in rows]
```

## Testing Database Operations

### Test Database Setup
```python
import tempfile
import os

def setup_test_database():
    """Create temporary database for testing"""
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    
    # Create test database with schema
    with sqlite3.connect(db_path) as db:
        db.execute('PRAGMA foreign_keys = ON')
        # Initialize schema
        init_test_schema(db)
        # Insert test data
        insert_test_data(db)
    
    return db_path

def teardown_test_database(db_path):
    """Clean up test database"""
    if os.path.exists(db_path):
        os.unlink(db_path)
```

### Transaction Testing
```python
def test_transaction_rollback():
    """Test transaction rollback behavior"""
    db_path = setup_test_database()
    
    try:
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            
            # Count initial records
            initial_count = cursor.execute('SELECT COUNT(*) FROM devices').fetchone()[0]
            
            try:
                # Start transaction that will fail
                cursor.execute('BEGIN TRANSACTION')
                
                # Valid insert
                cursor.execute('''
                    INSERT INTO devices (asset, cooler, location_id, model, device_type_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('TEST001', 'Test Device', 1, 'Test Model', 1))
                
                # Invalid insert (duplicate asset)
                cursor.execute('''
                    INSERT INTO devices (asset, cooler, location_id, model, device_type_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('TEST001', 'Test Device 2', 1, 'Test Model', 1))
                
                cursor.execute('COMMIT')
                
            except sqlite3.IntegrityError:
                cursor.execute('ROLLBACK')
            
            # Verify rollback worked
            final_count = cursor.execute('SELECT COUNT(*) FROM devices').fetchone()[0]
            assert final_count == initial_count, "Transaction rollback failed"
    
    finally:
        teardown_test_database(db_path)
```