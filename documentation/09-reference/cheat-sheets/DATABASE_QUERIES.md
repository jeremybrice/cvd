# Database Queries Cheat Sheet


## Metadata
- **ID**: 09_REFERENCE_CHEAT_SHEETS_DATABASE_QUERIES
- **Type**: Reference
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #data-exchange #data-layer #database #device-management #dex-parser #documentation #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #reference #reporting #route-management #security #service-orders #vending-machine
- **Intent**: Reference for Database Queries Cheat Sheet
- **Audience**: system administrators, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/09-reference/cheat-sheets/
- **Category**: Cheat Sheets
- **Search Keywords**: ###, *use, ---, analysis, backup, cabinet, cheat, checks, data, database, device, dex, driver, export, information

## Connection & Basic Operations

### Connect to Database
```bash
# Interactive session
sqlite3 cvd.db

# Execute single query
sqlite3 cvd.db "SELECT COUNT(*) FROM users;"

# Execute from file
sqlite3 cvd.db < queries.sql

# Output formats
sqlite3 -header -csv cvd.db "SELECT * FROM users;"
sqlite3 -header -column cvd.db "SELECT * FROM users LIMIT 5;"
```

### Schema Information
```sql
-- View all tables
.tables

-- View table schema
.schema devices
.schema

-- View table info
PRAGMA table_info(devices);

-- View indexes
.indexes devices
SELECT * FROM sqlite_master WHERE type='index';

-- Database statistics
.dbinfo
```

## User Management Queries

### User Information
```sql
-- List all users
SELECT id, username, email, role, status, created_at 
FROM users 
ORDER BY created_at DESC;

-- Active users only
SELECT username, role, email 
FROM users 
WHERE status = 'Active';

-- Users by role
SELECT role, COUNT(*) as count 
FROM users 
GROUP BY role;

-- Recent logins
SELECT u.username, MAX(a.created_at) as last_login
FROM users u
LEFT JOIN audit_log a ON u.id = a.user_id 
WHERE a.action = 'login'
GROUP BY u.id
ORDER BY last_login DESC;
```

### Session Management
```sql
-- Active sessions
SELECT 
  u.username,
  s.session_id,
  s.created_at,
  s.expires_at,
  CASE WHEN s.expires_at > datetime('now') THEN 'Active' ELSE 'Expired' END as status
FROM sessions s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC;

-- Clean expired sessions
DELETE FROM sessions WHERE expires_at < datetime('now');

-- Session count by user
SELECT u.username, COUNT(s.id) as active_sessions
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id AND s.expires_at > datetime('now')
GROUP BY u.id;
```

## Device Management Queries

### Device Information
```sql
-- All active devices
SELECT 
  d.id,
  d.name,
  d.status,
  l.address,
  COUNT(cc.id) as cabinet_count
FROM devices d
LEFT JOIN locations l ON d.location_id = l.id
LEFT JOIN cabinet_configurations cc ON d.id = cc.device_id
WHERE d.deleted_at IS NULL
GROUP BY d.id
ORDER BY d.name;

-- Devices by status
SELECT status, COUNT(*) as count 
FROM devices 
WHERE deleted_at IS NULL
GROUP BY status;

-- Device with cabinet details
SELECT 
  d.name as device_name,
  cc.cabinet_number,
  ct.name as cabinet_type,
  cc.model_name,
  cc.capacity
FROM devices d
JOIN cabinet_configurations cc ON d.id = cc.device_id
JOIN cabinet_types ct ON cc.cabinet_type_id = ct.id
WHERE d.deleted_at IS NULL
ORDER BY d.name, cc.cabinet_number;
```

### Location Analysis
```sql
-- Devices per location
SELECT 
  l.address,
  l.city,
  l.state,
  COUNT(d.id) as device_count
FROM locations l
LEFT JOIN devices d ON l.id = d.location_id AND d.deleted_at IS NULL
GROUP BY l.id
ORDER BY device_count DESC;

-- Devices on routes
SELECT 
  r.name as route_name,
  COUNT(d.id) as device_count
FROM routes r
LEFT JOIN devices d ON r.id = d.route_id AND d.deleted_at IS NULL
GROUP BY r.id
ORDER BY device_count DESC;
```

## Planogram Queries

### Planogram Information
```sql
-- Planograms with device info
SELECT 
  p.id,
  d.name as device_name,
  p.cabinet_number,
  p.name as planogram_name,
  COUNT(ps.id) as slot_count
FROM planograms p
JOIN devices d ON p.device_id = d.id
LEFT JOIN planogram_slots ps ON p.id = ps.planogram_id
WHERE d.deleted_at IS NULL
GROUP BY p.id
ORDER BY d.name, p.cabinet_number;

-- Products in planograms
SELECT 
  d.name as device_name,
  p.cabinet_number,
  ps.slot_number,
  pr.name as product_name,
  ps.quantity,
  ps.par_level
FROM planograms p
JOIN devices d ON p.device_id = d.id
JOIN planogram_slots ps ON p.id = ps.planogram_id
JOIN products pr ON ps.product_id = pr.id
WHERE d.deleted_at IS NULL
ORDER BY d.name, p.cabinet_number, ps.slot_number;

-- Empty slots
SELECT 
  d.name as device_name,
  p.cabinet_number,
  ps.slot_number
FROM planograms p
JOIN devices d ON p.device_id = d.id
JOIN planogram_slots ps ON p.id = ps.planogram_id
WHERE ps.product_id IS NULL AND d.deleted_at IS NULL
ORDER BY d.name, p.cabinet_number, ps.slot_number;
```

### Product Analysis
```sql
-- Product usage across fleet
SELECT 
  pr.name as product_name,
  pr.category,
  COUNT(ps.id) as slot_count,
  AVG(ps.quantity) as avg_quantity,
  SUM(ps.quantity) as total_quantity
FROM products pr
LEFT JOIN planogram_slots ps ON pr.id = ps.product_id
GROUP BY pr.id
ORDER BY slot_count DESC;

-- Most popular products by location
SELECT 
  pr.name as product_name,
  COUNT(DISTINCT d.id) as device_count,
  SUM(ps.quantity) as total_slots
FROM products pr
JOIN planogram_slots ps ON pr.id = ps.product_id
JOIN planograms p ON ps.planogram_id = p.id
JOIN devices d ON p.device_id = d.id
WHERE d.deleted_at IS NULL
GROUP BY pr.id
ORDER BY device_count DESC;
```

## Service Order Queries

### Service Order Status
```sql
-- Service orders by status
SELECT 
  status,
  COUNT(*) as count,
  AVG(JULIANDAY(updated_at) - JULIANDAY(created_at)) as avg_days
FROM service_orders
GROUP BY status;

-- Pending orders
SELECT 
  so.id,
  d.name as device_name,
  l.address,
  so.priority,
  so.created_at
FROM service_orders so
JOIN devices d ON so.device_id = d.id
JOIN locations l ON d.location_id = l.id
WHERE so.status = 'Pending'
ORDER BY so.priority DESC, so.created_at;

-- Orders by driver
SELECT 
  u.username as driver,
  COUNT(so.id) as assigned_orders,
  COUNT(CASE WHEN so.status = 'Completed' THEN 1 END) as completed_orders
FROM users u
LEFT JOIN service_orders so ON u.id = so.assigned_to
WHERE u.role = 'Driver'
GROUP BY u.id;
```

### Service Performance
```sql
-- Average completion time by priority
SELECT 
  priority,
  COUNT(*) as total_orders,
  AVG(JULIANDAY(completed_at) - JULIANDAY(created_at)) as avg_days
FROM service_orders 
WHERE status = 'Completed'
GROUP BY priority;

-- Service frequency by device
SELECT 
  d.name as device_name,
  COUNT(so.id) as service_count,
  MAX(so.created_at) as last_service
FROM devices d
LEFT JOIN service_orders so ON d.id = so.device_id
WHERE d.deleted_at IS NULL
GROUP BY d.id
ORDER BY service_count DESC;

-- Pick list summary
SELECT 
  so.id as order_id,
  d.name as device_name,
  soc.cabinet_number,
  COUNT(soci.id) as item_count,
  SUM(soci.quantity_needed) as total_items
FROM service_orders so
JOIN devices d ON so.device_id = d.id
JOIN service_order_cabinets soc ON so.id = soc.service_order_id
JOIN service_order_cabinet_items soci ON soc.id = soci.service_order_cabinet_id
WHERE so.status IN ('Pending', 'Assigned')
GROUP BY so.id, soc.id
ORDER BY so.created_at;
```

## Analytics Queries

### Sales Analysis
```sql
-- Daily sales summary
SELECT 
  DATE(transaction_date) as date,
  COUNT(*) as transaction_count,
  SUM(amount) as total_revenue
FROM sales 
WHERE transaction_date >= date('now', '-30 days')
GROUP BY DATE(transaction_date)
ORDER BY date DESC;

-- Product performance
SELECT 
  pr.name as product_name,
  COUNT(s.id) as sales_count,
  SUM(s.quantity) as units_sold,
  SUM(s.amount) as revenue
FROM sales s
JOIN products pr ON s.product_id = pr.id
WHERE s.transaction_date >= date('now', '-30 days')
GROUP BY pr.id
ORDER BY revenue DESC;

-- Device performance
SELECT 
  d.name as device_name,
  l.city,
  COUNT(s.id) as sales_count,
  SUM(s.amount) as revenue
FROM devices d
JOIN locations l ON d.location_id = l.id
LEFT JOIN sales s ON d.id = s.device_id AND s.transaction_date >= date('now', '-30 days')
WHERE d.deleted_at IS NULL
GROUP BY d.id
ORDER BY revenue DESC NULLS LAST;
```

### DEX Data Analysis
```sql
-- DEX file processing status
SELECT 
  d.name as device_name,
  COUNT(dr.id) as file_count,
  MAX(dr.processed_at) as last_processed,
  AVG(dr.record_count) as avg_records
FROM devices d
LEFT JOIN dex_reads dr ON d.id = dr.device_id
WHERE d.deleted_at IS NULL
GROUP BY d.id
ORDER BY last_processed DESC;

-- Grid pattern analysis
SELECT 
  grid_pattern,
  COUNT(*) as occurrence_count,
  AVG(total_slots) as avg_slots
FROM dex_pa_records
WHERE grid_pattern IS NOT NULL
GROUP BY grid_pattern
ORDER BY occurrence_count DESC;
```

## Audit & Security Queries

### Activity Monitoring
```sql
-- Recent activity by user
SELECT 
  u.username,
  a.action,
  a.details,
  a.created_at
FROM audit_log a
LEFT JOIN users u ON a.user_id = u.id
WHERE a.created_at >= date('now', '-7 days')
ORDER BY a.created_at DESC
LIMIT 100;

-- Failed login attempts
SELECT 
  username,
  COUNT(*) as attempts,
  MAX(created_at) as last_attempt
FROM audit_log 
WHERE action = 'login_failed' 
  AND created_at >= date('now', '-24 hours')
GROUP BY username
ORDER BY attempts DESC;

-- Administrative actions
SELECT 
  u.username,
  a.action,
  a.details,
  a.created_at
FROM audit_log a
JOIN users u ON a.user_id = u.id
WHERE a.action IN ('user_created', 'user_updated', 'user_deleted', 'admin_toggled')
  AND a.created_at >= date('now', '-30 days')
ORDER BY a.created_at DESC;
```

### Security Monitoring
```sql
-- Privilege escalation attempts
SELECT 
  u.username,
  a.action,
  a.details,
  a.ip_address,
  a.created_at
FROM audit_log a
LEFT JOIN users u ON a.user_id = u.id
WHERE (a.action LIKE '%privilege%' OR a.action LIKE '%unauthorized%')
  AND a.created_at >= date('now', '-7 days')
ORDER BY a.created_at DESC;

-- Suspicious activity patterns
SELECT 
  ip_address,
  COUNT(DISTINCT user_id) as user_count,
  COUNT(*) as request_count
FROM audit_log 
WHERE created_at >= datetime('now', '-1 hour')
GROUP BY ip_address
HAVING request_count > 100
ORDER BY request_count DESC;
```

## Maintenance Queries

### Data Cleanup
```sql
-- Old audit logs (older than 90 days)
SELECT COUNT(*) FROM audit_log 
WHERE created_at < date('now', '-90 days');

DELETE FROM audit_log 
WHERE created_at < date('now', '-90 days');

-- Expired sessions
SELECT COUNT(*) FROM sessions 
WHERE expires_at < datetime('now');

DELETE FROM sessions 
WHERE expires_at < datetime('now');

-- Soft-deleted devices (older than 30 days)
SELECT COUNT(*) FROM devices 
WHERE deleted_at IS NOT NULL 
  AND deleted_at < date('now', '-30 days');
```

### Data Integrity Checks
```sql
-- Orphaned records
SELECT 'planogram_slots without planogram' as issue, COUNT(*) as count
FROM planogram_slots ps
LEFT JOIN planograms p ON ps.planogram_id = p.id
WHERE p.id IS NULL

UNION ALL

SELECT 'planograms without device', COUNT(*)
FROM planograms p
LEFT JOIN devices d ON p.device_id = d.id
WHERE d.id IS NULL

UNION ALL

SELECT 'service_orders without device', COUNT(*)
FROM service_orders so
LEFT JOIN devices d ON so.device_id = d.id
WHERE d.id IS NULL;

-- Referential integrity
SELECT 
  'devices with invalid location' as issue,
  COUNT(*) as count
FROM devices d
LEFT JOIN locations l ON d.location_id = l.id
WHERE d.location_id IS NOT NULL AND l.id IS NULL;
```

## Performance Queries

### Query Performance Analysis
```sql
-- Enable timing
.timer ON

-- Explain query plan
EXPLAIN QUERY PLAN 
SELECT d.*, l.address 
FROM devices d 
LEFT JOIN locations l ON d.location_id = l.id 
WHERE d.status = 'Active';

-- Table statistics
SELECT 
  name,
  (SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name=t.name) as index_count
FROM sqlite_master t
WHERE type='table' AND name NOT LIKE 'sqlite_%';
```

### Database Statistics
```sql
-- Table row counts
SELECT 
  'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL SELECT 'devices', COUNT(*) FROM devices
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'planograms', COUNT(*) FROM planograms
UNION ALL SELECT 'service_orders', COUNT(*) FROM service_orders
UNION ALL SELECT 'audit_log', COUNT(*) FROM audit_log
ORDER BY row_count DESC;

-- Database size by table
SELECT 
  name,
  COUNT(*) as records,
  SUM(LENGTH(sql)) as schema_size
FROM sqlite_master 
WHERE type='table'
GROUP BY name;
```

## Useful Functions & Techniques

### Date/Time Functions
```sql
-- Current timestamp
SELECT datetime('now') as current_time;

-- Date arithmetic
SELECT 
  date('now') as today,
  date('now', '-7 days') as week_ago,
  date('now', '+30 days') as month_from_now;

-- Format dates
SELECT 
  strftime('%Y-%m-%d %H:%M:%S', created_at) as formatted_date
FROM users;
```

### JSON Operations (if using JSON columns)
```sql
-- Extract JSON values (if applicable)
SELECT 
  json_extract(details, '$.action') as action_detail
FROM audit_log 
WHERE json_valid(details);
```

### Backup & Export
```sql
-- Export table to CSV
.headers ON
.mode csv
.output devices_export.csv
SELECT * FROM devices WHERE deleted_at IS NULL;
.output stdout

-- Backup specific tables
.backup backup.db

-- Restore from backup
.restore backup.db
```

---

*Use `.help` in sqlite3 for additional commands and options.*