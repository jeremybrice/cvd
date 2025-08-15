# System Administration Tasks Cheat Sheet


## Metadata
- **ID**: 09_REFERENCE_CHEAT_SHEETS_ADMIN_TASKS
- **Type**: Reference
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #data-exchange #data-layer #database #debugging #device-management #dex-parser #documentation #integration #machine-learning #operations #optimization #performance #planogram #product-placement #reference #security #service-orders #troubleshooting #vending-machine
- **Intent**: Reference for System Administration Tasks Cheat Sheet
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/09-reference/cheat-sheets/
- **Category**: Cheat Sheets
- **Search Keywords**: ###, activity, admin, administration, cheat, check, clean, cleanup, common, data, database, device, dex, emergency, fixes

## User Management

### Create New User
```bash
# Via API
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -b admin_cookies.txt \
  -d '{
    "username": "newuser",
    "email": "user@company.com",
    "password": "SecurePass123",
    "role": "Manager"
  }'
```

### Reset User Password
```sql
-- Direct database method
sqlite3 cvd.db
UPDATE users 
SET password_hash = 'pbkdf2:sha256:600000$...' 
WHERE username = 'username';
```

### Toggle Admin Status
```bash
# Via API
curl -X POST http://localhost:5000/api/users/toggle-admin/{user_id} \
  -H "Content-Type: application/json" \
  -b admin_cookies.txt
```

### Lock/Unlock User Account
```sql
sqlite3 cvd.db
UPDATE users SET status = 'Locked' WHERE username = 'username';
UPDATE users SET status = 'Active' WHERE username = 'username';
```

## Database Administration

### Daily Backup
```bash
# Create timestamped backup
BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR
cp cvd.db "$BACKUP_DIR/cvd_$(date +%Y%m%d_%H%M%S).db"

# Compress backup
gzip "$BACKUP_DIR/cvd_$(date +%Y%m%d_%H%M%S).db"
```

### Database Maintenance
```sql
sqlite3 cvd.db
-- Reclaim space
VACUUM;

-- Update table statistics
ANALYZE;

-- Check database integrity
PRAGMA integrity_check;

-- View database size
.dbinfo

-- Show table sizes
SELECT 
  name as table_name,
  COUNT(*) as row_count
FROM sqlite_master 
WHERE type='table' 
  AND name NOT LIKE 'sqlite_%'
GROUP BY name;
```

### Data Retention Cleanup
```sql
sqlite3 cvd.db
-- Clean old audit logs (older than 90 days)
DELETE FROM audit_log 
WHERE created_at < date('now', '-90 days');

-- Clean old sessions
DELETE FROM sessions 
WHERE expires_at < datetime('now');

-- Archive old service visits
INSERT INTO service_visits_archive 
SELECT * FROM service_visits 
WHERE completed_at < date('now', '-1 year');

DELETE FROM service_visits 
WHERE completed_at < date('now', '-1 year');
```

## Security Tasks

### Monitor Failed Login Attempts
```sql
sqlite3 cvd.db
SELECT 
  username,
  COUNT(*) as failed_attempts,
  MAX(created_at) as last_attempt
FROM audit_log 
WHERE action = 'login_failed' 
  AND created_at > datetime('now', '-24 hours')
GROUP BY username
ORDER BY failed_attempts DESC;
```

### Check Privilege Escalation Attempts
```sql
sqlite3 cvd.db
SELECT 
  username,
  details,
  created_at
FROM audit_log 
WHERE action LIKE '%privilege%' 
  OR action LIKE '%unauthorized%'
ORDER BY created_at DESC 
LIMIT 20;
```

### Review User Activity
```sql
sqlite3 cvd.db
SELECT 
  u.username,
  a.action,
  a.details,
  a.created_at
FROM audit_log a
JOIN users u ON a.user_id = u.id
WHERE a.created_at > datetime('now', '-7 days')
ORDER BY a.created_at DESC 
LIMIT 50;
```

### Lock Suspicious Accounts
```sql
sqlite3 cvd.db
-- Find accounts with many failed logins
SELECT username FROM audit_log 
WHERE action = 'login_failed' 
  AND created_at > datetime('now', '-1 hour')
GROUP BY username 
HAVING COUNT(*) > 5;

-- Lock the accounts
UPDATE users 
SET status = 'Locked' 
WHERE username IN (
  SELECT username FROM audit_log 
  WHERE action = 'login_failed' 
    AND created_at > datetime('now', '-1 hour')
  GROUP BY username 
  HAVING COUNT(*) > 5
);
```

## System Monitoring

### Check System Health
```bash
# Backend health check
curl -f http://localhost:5000/api/auth/current-user > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Backend: Healthy"
else
  echo "❌ Backend: Down"
fi

# Frontend health check
curl -f http://localhost:8000/ > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Frontend: Healthy"
else
  echo "❌ Frontend: Down"
fi

# Database health check
sqlite3 cvd.db "SELECT 1;" > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Database: Accessible"
else
  echo "❌ Database: Inaccessible"
fi
```

### Monitor Active Sessions
```sql
sqlite3 cvd.db
SELECT 
  u.username,
  s.session_id,
  s.created_at,
  s.expires_at,
  CASE 
    WHEN s.expires_at > datetime('now') THEN 'Active'
    ELSE 'Expired'
  END as status
FROM sessions s
JOIN users u ON s.user_id = u.id
ORDER BY s.created_at DESC;
```

### Check Device Status
```sql
sqlite3 cvd.db
SELECT 
  status,
  COUNT(*) as count
FROM devices 
WHERE deleted_at IS NULL
GROUP BY status;
```

### Review Service Orders
```sql
sqlite3 cvd.db
SELECT 
  status,
  COUNT(*) as count,
  AVG(JULIANDAY(updated_at) - JULIANDAY(created_at)) as avg_days
FROM service_orders 
WHERE created_at > date('now', '-30 days')
GROUP BY status;
```

## Performance Optimization

### Add Database Indexes
```sql
sqlite3 cvd.db
-- Commonly queried indexes
CREATE INDEX IF NOT EXISTS idx_devices_status 
ON devices(status) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_service_orders_status 
ON service_orders(status);

CREATE INDEX IF NOT EXISTS idx_audit_log_date 
ON audit_log(created_at);

CREATE INDEX IF NOT EXISTS idx_sessions_expires 
ON sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_planogram_slots_planogram 
ON planogram_slots(planogram_id);
```

### Optimize Database Queries
```sql
sqlite3 cvd.db
-- View query execution plans
EXPLAIN QUERY PLAN 
SELECT * FROM devices 
WHERE status = 'Active' AND deleted_at IS NULL;

-- Enable query profiling
.timer ON
SELECT COUNT(*) FROM audit_log;
.timer OFF
```

### Clean Up Unused Data
```sql
sqlite3 cvd.db
-- Remove soft-deleted devices older than 30 days
DELETE FROM devices 
WHERE deleted_at IS NOT NULL 
  AND deleted_at < date('now', '-30 days');

-- Clean up orphaned planogram slots
DELETE FROM planogram_slots 
WHERE planogram_id NOT IN (SELECT id FROM planograms);

-- Clean up expired sessions
DELETE FROM sessions 
WHERE expires_at < datetime('now');
```

## Configuration Management

### Environment Settings Check
```bash
# Check critical environment variables
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET}" "${ANTHROPIC_API_KEY:-NOT SET}"
echo "SESSION_SECRET: ${SESSION_SECRET:+SET}" "${SESSION_SECRET:-NOT SET}"
echo "FLASK_ENV: ${FLASK_ENV:-development}"
echo "FLASK_DEBUG: ${FLASK_DEBUG:-0}"

# Verify file permissions
ls -la cvd.db
ls -la *.py
ls -la pages/
```

### Update System Configuration
```sql
sqlite3 cvd.db
-- Update company settings (if table exists)
UPDATE company_settings 
SET value = 'New Company Name' 
WHERE key = 'company_name';

-- Set system maintenance mode
INSERT OR REPLACE INTO system_config 
VALUES ('maintenance_mode', 'true', datetime('now'));
```

## Backup & Recovery

### Full System Backup
```bash
#!/bin/bash
# Create backup directory
BACKUP_DIR="system_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Copy database
cp cvd.db "$BACKUP_DIR/"

# Copy application files
cp *.py "$BACKUP_DIR/"
cp -r pages/ "$BACKUP_DIR/"
cp -r documentation/ "$BACKUP_DIR/"

# Copy configuration
cp requirements.txt "$BACKUP_DIR/"

# Create archive
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "✅ Backup created: $BACKUP_DIR.tar.gz"
```

### Database Recovery
```bash
# Stop application first
pkill -f "python app.py"

# Restore from backup
cp backup/cvd_20250101_120000.db cvd.db

# Verify integrity
sqlite3 cvd.db "PRAGMA integrity_check;"

# Restart application
python app.py &
```

### Emergency Reset
```bash
# CAUTION: This will reset all data
# Create final backup
cp cvd.db emergency_backup_$(date +%Y%m%d_%H%M%S).db

# Remove database
rm cvd.db

# Restart application (will recreate with init_db)
python app.py &

# Reset admin password
sqlite3 cvd.db "
UPDATE users 
SET password_hash = 'pbkdf2:sha256:600000\$salt\$hash' 
WHERE username = 'admin';
"
```

## Log Management

### View Recent Activity
```sql
sqlite3 cvd.db
-- Last 24 hours activity
SELECT 
  u.username,
  a.action,
  a.details,
  a.created_at
FROM audit_log a
LEFT JOIN users u ON a.user_id = u.id
WHERE a.created_at > datetime('now', '-24 hours')
ORDER BY a.created_at DESC
LIMIT 100;
```

### Generate Reports
```bash
# Daily activity report
sqlite3 cvd.db -header -csv "
SELECT 
  DATE(created_at) as date,
  action,
  COUNT(*) as count
FROM audit_log 
WHERE created_at > date('now', '-7 days')
GROUP BY DATE(created_at), action
ORDER BY date DESC, count DESC;
" > daily_activity_report.csv

# User activity summary
sqlite3 cvd.db -header -csv "
SELECT 
  u.username,
  u.role,
  COUNT(a.id) as total_actions,
  MAX(a.created_at) as last_activity
FROM users u
LEFT JOIN audit_log a ON u.id = a.user_id
WHERE a.created_at > date('now', '-30 days')
GROUP BY u.id
ORDER BY total_actions DESC;
" > user_activity_summary.csv
```

## Troubleshooting Commands

### Check Process Status
```bash
# Find running processes
ps aux | grep -E "(python|http\.server)" | grep -v grep

# Check port usage
netstat -tulpn | grep -E ":(5000|8000)"

# Memory usage
free -h
df -h

# Check system load
uptime
```

### Common Fixes
```bash
# Restart services
pkill -f "python app.py"
pkill -f "http.server"
python app.py &
python -m http.server 8000 &

# Clear browser data (command line)
# Chrome/Chromium
rm -rf ~/.config/google-chrome/Default/Local\ Storage/
# Firefox  
rm -rf ~/.mozilla/firefox/*/storage/

# Reset file permissions
chmod 644 cvd.db
chmod 755 *.py
chmod -R 755 pages/
```

### Emergency Contacts & Escalation
```bash
# System status check script
#!/bin/bash
echo "=== CVD System Status ==="
echo "Date: $(date)"
echo "Backend: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/auth/current-user)"
echo "Frontend: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)"
echo "Database: $(sqlite3 cvd.db 'SELECT COUNT(*) FROM users;' 2>/dev/null && echo 'OK' || echo 'ERROR')"
echo "Disk Usage: $(df -h . | tail -1 | awk '{print $5}')"
echo "=========================="
```

---

*Run these commands with appropriate privileges. Always backup before making changes.*