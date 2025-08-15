# ADR-002: SQLite Database Selection


## Metadata
- **ID**: 03_ARCHITECTURE_DECISIONS_ADR_002_SQLITE_DATABASE
- **Type**: Architecture
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #architecture #authentication #data-exchange #data-layer #database #debugging #deployment #device-management #devops #dex-parser #integration #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #quality-assurance #reporting #security #service-orders #system-design #technical #testing #troubleshooting #vending-machine
- **Intent**: Architecture for ADR-002: SQLite Database Selection
- **Audience**: system administrators, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/03-architecture/decisions/
- **Category**: Decisions
- **Search Keywords**: ###, 2024-07-15, 3.x, accepted, acid, administration, adr, advantages, backup, benefits, cabinet, characteristics, comfortable, complex, compliance

**Status**: Accepted  
**Date**: 2024-07-15  
**Deciders**: Development Team  
**Technical Story**: Selection of database technology for CVD data persistence

## Context

The CVD system requires a reliable database solution to store and manage:

- User accounts and authentication sessions
- Vending machine device inventory (1000+ devices)
- Planogram configurations with complex slot relationships
- Service orders and operational workflows
- Sales analytics and performance metrics
- DEX file processing results
- Audit logs and activity tracking
- Knowledge base content and metadata

Key requirements include:

- **Zero-administration deployment** for field installations
- **Single-file distribution** for easy backup and migration
- **ACID compliance** for financial and operational data
- **Complex relational queries** for analytics and reporting
- **Good performance** for read-heavy workloads
- **Embedded deployment** without external database servers
- **Long-term scalability** within SQLite capabilities

Database options considered:

1. **SQLite** - Embedded, serverless database
2. **Other relational databases** - Full-featured server-based solutions
3. **MySQL** - Popular relational database
4. **MongoDB** - Document-oriented NoSQL database

## Decision

We have chosen **SQLite 3.x** as the primary database for the CVD system.

## Rationale

### SQLite Advantages for CVD Use Case

1. **Zero Administration**
   ```bash
   # No database server setup required
   # Single file contains entire database
   ls -la cvd.db
   # -rw-r--r-- 1 user user 15728640 Jul 15 10:30 cvd.db
   ```

2. **Deployment Simplicity**
   - Single file backup: `cp cvd.db cvd_backup_$(date +%Y%m%d).db`
   - No network configuration or user management
   - Works offline and in isolated environments
   - Perfect for edge deployments in retail locations

3. **Performance Characteristics**
   ```sql
   -- Excellent for read-heavy workloads
   EXPLAIN QUERY PLAN 
   SELECT d.*, l.name as location_name 
   FROM devices d 
   JOIN locations l ON d.location_id = l.id 
   WHERE d.deleted_at IS NULL;
   
   -- Uses indexes effectively for fleet queries
   ```

4. **ACID Compliance**
   - Full ACID properties ensure data integrity
   - WAL mode for improved concurrency
   - Atomic transactions for service order processing

5. **Rich SQL Feature Set**
   ```sql
   -- Complex analytics queries supported
   WITH device_metrics AS (
       SELECT device_id, 
              COUNT(*) as slot_count,
              AVG(CASE WHEN quantity = 0 THEN 1 ELSE 0 END) as sold_out_rate
       FROM planogram_slots ps
       JOIN planograms p ON ps.planogram_id = p.id
       GROUP BY device_id
   )
   SELECT d.asset, dm.sold_out_rate
   FROM devices d
   JOIN device_metrics dm ON d.id = dm.device_id;
   ```

### Comparison with Alternatives

#### Server-Based Databases
**Advantages**:
- Better concurrent write performance
- Advanced features (JSON, arrays, full-text search)
- Horizontal scaling capabilities
- Enterprise support and tooling

**Disadvantages**:
- Requires database server installation and management
- Network configuration and security setup
- More complex deployment and backup procedures
- Overkill for current scale (< 10,000 devices)

#### MySQL
**Advantages**:
- Wide industry adoption
- Good performance at scale
- Extensive tooling ecosystem

**Disadvantages**:
- Server installation and management required
- Complex configuration for optimal performance
- Licensing considerations for commercial use
- Similar complexity to server-based databases without additional benefits

#### MongoDB
**Advantages**:
- Flexible document schema
- Good for rapid prototyping
- Horizontal scaling built-in

**Disadvantages**:
- No ACID guarantees for multi-document transactions
- Complex queries require aggregation pipelines
- Poor fit for relational data (devices -> cabinets -> slots)
- NoSQL overhead for structured operational data

## Implementation Details

### Database Configuration
```python
# Connection with WAL mode for better concurrency
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent access
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA foreign_keys=ON')
    return db
```

### Schema Management
```sql
-- Comprehensive foreign key relationships
CREATE TABLE cabinet_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    cabinet_type_id INTEGER NOT NULL,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    FOREIGN KEY (cabinet_type_id) REFERENCES cabinet_types(id)
);

-- Strategic indexing for performance
CREATE INDEX idx_devices_asset ON devices(asset);
CREATE INDEX idx_cabinets_device ON cabinet_configurations(device_id);
CREATE INDEX idx_slots_product ON planogram_slots(product_id);
```

### Migration Strategy
```python
# Database migrations with version tracking
def apply_migration(migration_name, migration_sql):
    db = get_db()
    cursor = db.cursor()
    
    # Check if migration already applied
    existing = cursor.execute(
        'SELECT 1 FROM migrations WHERE name = ?', 
        (migration_name,)
    ).fetchone()
    
    if not existing:
        cursor.executescript(migration_sql)
        cursor.execute(
            'INSERT INTO migrations (name) VALUES (?)',
            (migration_name,)
        )
        db.commit()
```

### Performance Optimizations
```sql
-- Comprehensive indexing strategy
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_planograms_key ON planograms(planogram_key);  
CREATE INDEX idx_slots_cleared_at ON planogram_slots(cleared_at);
CREATE INDEX idx_service_orders_status ON service_orders(status);
CREATE INDEX idx_user_activity_timestamp ON user_activity_log(timestamp);

-- View for common queries
CREATE VIEW device_summary AS
SELECT d.id, d.asset, d.cooler, l.name as location_name,
       COUNT(cc.id) as cabinet_count,
       d.deleted_at IS NULL as is_active
FROM devices d
LEFT JOIN locations l ON d.location_id = l.id
LEFT JOIN cabinet_configurations cc ON d.id = cc.device_id
GROUP BY d.id;
```

## Consequences

### Positive

1. **Operational Simplicity**
   - Zero database administration overhead
   - Simple backup strategy (file copy)
   - No network security considerations
   - Reliable offline operation

2. **Development Velocity**
   - Instant local development setup
   - Easy test database creation and cleanup
   - Direct SQL debugging and optimization
   - Simple schema migrations

3. **Deployment Benefits**
   - Single-file deployment artifact
   - No external dependencies
   - Works in air-gapped environments
   - Easy containerization

4. **Cost Efficiency**
   - No database licensing costs
   - No dedicated database server resources
   - Minimal operational overhead

### Negative

1. **Concurrency Limitations**
   - Single writer at a time (mitigated by WAL mode)
   - Not suitable for high-concurrency write workloads
   - May require optimization for many simultaneous users

2. **Scaling Constraints**
   - Database size practical limit (~100GB recommended)
   - No built-in replication or clustering
   - Single point of failure

3. **Enterprise Features**
   - No advanced security features (row-level security)
   - Limited full-text search capabilities
   - No built-in backup/recovery tools

### Mitigation Strategies

1. **Connection Pool Management**
   ```python
   # Flask-g based connection management prevents connection leaks
   @app.teardown_appcontext
   def close_connection(exception):
       db = getattr(g, '_database', None)
       if db is not None:
           db.close()
   ```

2. **Regular Backup Strategy**
   ```bash
   # Automated backup script
   #!/bin/bash
   backup_dir="/backups/$(date +%Y%m%d_%H%M%S)"
   mkdir -p "$backup_dir"
   cp cvd.db "$backup_dir/cvd_backup.db"
   ```

3. **Future Scalability Considerations**
   ```python
   # Database abstraction layer for future migration
   class DatabaseAdapter:
       def __init__(self, db_type='sqlite'):
           self.db_type = db_type
           
       def get_devices(self):
           if self.db_type == 'sqlite':
               return self._get_devices_sqlite()
           # Future database types can be added here
               pass
   ```

## Performance Characteristics

### Benchmark Results (Development Environment)
```
Device List Query (1000 devices): ~50ms
Planogram Load (500 slots): ~25ms
Service Order Creation: ~15ms
Analytics Query (30-day sales): ~200ms
Database Size: 15MB (1000 devices, 1 year data)
```

### Scaling Thresholds
- **Comfortable**: < 5,000 devices, < 50 concurrent users
- **Monitor**: 5,000-10,000 devices, 50-100 concurrent users  
- **Migrate**: > 10,000 devices, > 100 concurrent users

## Migration Strategy

### When to Consider Alternative Solutions
1. **Performance**: Query response times > 1 second
2. **Scale**: > 10,000 devices or > 100 concurrent users
3. **Features**: Need for advanced analytics, replication, or clustering
4. **Compliance**: Enterprise security requirements

### Migration Path
```sql
-- Schema conversion script
-- SQLite syntax considerations for portability
-- INTEGER PRIMARY KEY AUTOINCREMENT → SERIAL PRIMARY KEY
-- BOOLEAN → BOOLEAN (with explicit true/false values)
-- TIMESTAMP DEFAULT CURRENT_TIMESTAMP → TIMESTAMP DEFAULT NOW()
```

This decision positions CVD for rapid deployment and operation while maintaining a clear upgrade path for future scaling needs.