---
title: "[System/Feature] Troubleshooting Guide"
category: "Troubleshooting"
tags: ["troubleshooting", "[system-area]", "support", "diagnostic"]
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
version: "1.0"
author: "Support Team"
audience: "all"
difficulty: "beginner"
prerequisites: ["Basic understanding of [system/feature]", "System access permissions"]
estimated_time: "5-30 minutes"
description: "Comprehensive troubleshooting guide for [system/feature] issues with step-by-step solutions and diagnostic procedures"
related_docs: ["../user-guides/system-user-guide.md", "../development/installation-guide.md", "../api/api-reference.md"]
---

# [System/Feature] Troubleshooting Guide

## Overview

Comprehensive troubleshooting guide for resolving common issues with [System/Feature]. This guide provides step-by-step solutions, diagnostic procedures, and preventive measures to help users quickly identify and resolve problems.

### How to Use This Guide
1. **Identify Symptoms**: Match your issue with the symptoms described
2. **Follow Diagnostic Steps**: Run through the suggested diagnostic procedures
3. **Apply Solutions**: Implement the recommended solutions in order
4. **Verify Resolution**: Confirm the issue is resolved
5. **Document Findings**: Record what worked for future reference

### When to Contact Support
- Issue persists after following all troubleshooting steps
- System shows signs of data corruption or security compromise
- Multiple users are affected simultaneously
- Error messages indicate critical system failures

## Quick Reference

### Emergency Procedures
| Issue Type | Immediate Action | Next Steps |
|------------|------------------|------------|
| System Down | Check service status | Restart services, check logs |
| Data Loss | Stop all operations | Restore from backup |
| Security Breach | Disconnect from network | Contact security team |
| Performance Critical | Enable debug logging | Monitor resource usage |

### Common Error Codes
| Code | Description | Quick Fix |
|------|-------------|-----------|
| ERR_AUTH_001 | Authentication failure | Clear cookies, re-login |
| ERR_DB_001 | Database connection lost | Check database service |
| ERR_API_001 | API endpoint unavailable | Verify service status |
| ERR_NET_001 | Network connectivity issue | Check internet connection |

## System Diagnostics

### Health Check Procedures

#### System Status Check
```bash
# Check service status
systemctl status cvd-backend
systemctl status cvd-frontend

# Check process status
ps aux | grep python
ps aux | grep http.server

# Check port availability
netstat -tulpn | grep :5000
netstat -tulpn | grep :8000
```

#### Database Health Check
```bash
# Check database file
ls -la instance/cvd.db
sqlite3 instance/cvd.db ".tables"

# Test database connectivity
sqlite3 instance/cvd.db "SELECT COUNT(*) FROM users;"
```

#### Network Connectivity Check
```bash
# Test local connectivity
curl -I http://localhost:5000/api/health
curl -I http://localhost:8000/

# Test external dependencies
ping 8.8.8.8
curl -I https://api.example.com/status
```

#### Log Analysis
```bash
# Check application logs
tail -f logs/app.log
tail -f logs/error.log

# Check system logs
sudo journalctl -u cvd-backend -f
sudo journalctl -u cvd-frontend -f
```

### Performance Diagnostics

#### System Resource Check
```bash
# CPU and memory usage
top -p $(pgrep -f "python|http.server")
htop

# Disk space
df -h
du -sh instance/

# Network traffic
iftop
netstat -i
```

#### Database Performance
```sql
-- Check database size
SELECT 
    name,
    COUNT(*) as record_count
FROM sqlite_master 
WHERE type='table'
GROUP BY name;

-- Identify slow queries
PRAGMA optimize;
EXPLAIN QUERY PLAN SELECT * FROM devices WHERE status = 'active';
```

## Common Issues and Solutions

### Issue 1: Authentication Problems

#### Symptoms
- Users cannot log in with correct credentials
- "Invalid username or password" error messages
- Authentication tokens expiring immediately
- Users logged out unexpectedly

#### Diagnostic Steps
1. **Verify User Account**
   ```sql
   -- Check if user exists
   SELECT username, email, role, created_at 
   FROM users 
   WHERE username = '[username]';
   
   -- Check password hash (don't display the hash)
   SELECT username, password IS NOT NULL as has_password 
   FROM users 
   WHERE username = '[username]';
   ```

2. **Check Session Management**
   ```sql
   -- Check active sessions
   SELECT user_id, created_at, expires_at
   FROM sessions
   WHERE user_id = [user_id];
   ```

3. **Review Authentication Logs**
   ```bash
   # Check for authentication errors
   grep "authentication" logs/app.log
   grep "login" logs/app.log | tail -10
   ```

#### Solutions

##### Solution 1: Reset User Password
```bash
# Using admin interface
python -c "
from app import app, db
from models import User
with app.app_context():
    user = User.query.filter_by(username='[username]').first()
    if user:
        user.set_password('[new_password]')
        db.session.commit()
        print('Password updated successfully')
    else:
        print('User not found')
"
```

##### Solution 2: Clear User Sessions
```sql
-- Clear all sessions for user
DELETE FROM sessions WHERE user_id = [user_id];

-- Clear expired sessions
DELETE FROM sessions WHERE expires_at < datetime('now');
```

##### Solution 3: Verify Configuration
```python
# Check auth configuration
print("SECRET_KEY set:", bool(os.getenv('SECRET_KEY')))
print("SESSION_TIMEOUT:", os.getenv('SESSION_TIMEOUT', 3600))
```

### Issue 2: Database Connection Errors

#### Symptoms
- "Database is locked" error messages
- Connection timeout errors
- Data not saving or loading
- SQLite database corruption warnings

#### Diagnostic Steps
1. **Check Database File**
   ```bash
   # Verify database file exists and is readable
   ls -la instance/cvd.db
   file instance/cvd.db
   
   # Check database integrity
   sqlite3 instance/cvd.db "PRAGMA integrity_check;"
   ```

2. **Test Database Connection**
   ```python
   # Test connection from Python
   import sqlite3
   try:
       conn = sqlite3.connect('instance/cvd.db')
       cursor = conn.cursor()
       cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
       tables = cursor.fetchall()
       print(f"Found {len(tables)} tables")
       conn.close()
   except Exception as e:
       print(f"Database connection error: {e}")
   ```

3. **Check File Permissions**
   ```bash
   # Check permissions
   ls -la instance/
   whoami
   groups
   ```

#### Solutions

##### Solution 1: Fix Database Permissions
```bash
# Fix file permissions
chmod 664 instance/cvd.db
chmod 755 instance/

# Fix ownership (if needed)
chown $(whoami):$(whoami) instance/cvd.db
```

##### Solution 2: Repair Database Corruption
```bash
# Backup current database
cp instance/cvd.db instance/cvd.db.backup

# Attempt repair
sqlite3 instance/cvd.db ".recover" > temp_db.sql
sqlite3 instance/cvd_repaired.db < temp_db.sql

# Verify repair
sqlite3 instance/cvd_repaired.db "PRAGMA integrity_check;"

# Replace if successful
mv instance/cvd.db instance/cvd.db.corrupted
mv instance/cvd_repaired.db instance/cvd.db
```

##### Solution 3: Restart with Clean Database
```bash
# Backup existing database
cp instance/cvd.db instance/cvd.db.$(date +%Y%m%d_%H%M%S)

# Initialize fresh database
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
```

### Issue 3: API Endpoint Failures

#### Symptoms
- API returns 500 Internal Server Error
- Endpoints returning unexpected data formats
- CORS errors in browser console
- Slow API response times

#### Diagnostic Steps
1. **Test API Endpoints**
   ```bash
   # Test authentication endpoint
   curl -X POST http://localhost:5000/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin"}'
   
   # Test device listing
   curl -H "Authorization: Bearer [token]" \
        http://localhost:5000/api/devices
   ```

2. **Check API Logs**
   ```bash
   # Filter API-specific logs
   grep "api/" logs/app.log | tail -20
   grep "ERROR" logs/app.log | tail -10
   ```

3. **Verify Service Status**
   ```bash
   # Check if backend is running
   curl -I http://localhost:5000/api/health
   
   # Check response time
   time curl -s http://localhost:5000/api/devices > /dev/null
   ```

#### Solutions

##### Solution 1: Restart Backend Service
```bash
# Stop current process
pkill -f "python app.py"

# Start fresh
cd /path/to/cvd
source venv/bin/activate
python app.py
```

##### Solution 2: Fix CORS Configuration
```python
# In app.py, ensure CORS is properly configured
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:8000"])
```

##### Solution 3: Debug Specific Endpoint
```python
# Add debug logging to problematic endpoint
import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/api/problematic-endpoint', methods=['GET'])
def problematic_endpoint():
    try:
        logging.debug("Entering problematic_endpoint")
        # ... existing code ...
        logging.debug("Exiting problematic_endpoint successfully")
        return result
    except Exception as e:
        logging.error(f"Error in problematic_endpoint: {e}")
        raise
```

### Issue 4: Frontend Loading Problems

#### Symptoms
- Blank white screen in browser
- JavaScript errors in browser console
- Components not rendering correctly
- CSS styles not applying

#### Diagnostic Steps
1. **Check Browser Console**
   - Open Developer Tools (F12)
   - Look for JavaScript errors in Console tab
   - Check Network tab for failed resource loads
   - Verify no CORS errors

2. **Verify File Serving**
   ```bash
   # Test static file serving
   curl -I http://localhost:8000/index.html
   curl -I http://localhost:8000/api.js
   curl -I http://localhost:8000/styles/main.css
   ```

3. **Check File Structure**
   ```bash
   # Verify all required files exist
   ls -la index.html
   ls -la api.js
   ls -la pages/
   ls -la styles/
   ```

#### Solutions

##### Solution 1: Clear Browser Cache
```javascript
// In browser console, force refresh
location.reload(true);

// Or clear specific cache
if ('caches' in window) {
    caches.keys().then(names => {
        names.forEach(name => caches.delete(name));
    });
}
```

##### Solution 2: Restart Frontend Server
```bash
# Stop current server
pkill -f "http.server"

# Start fresh server
cd /path/to/cvd
python -m http.server 8000
```

##### Solution 3: Fix File Paths
```javascript
// Check and fix relative paths in HTML files
// Ensure imports use correct paths:
<script src="/api.js"></script>  // Absolute path
<script src="api.js"></script>   // Relative path
```

### Issue 5: Device Management Issues

#### Symptoms
- Cannot add new devices
- Device configurations not saving
- Planogram data not loading
- Service order generation failures

#### Diagnostic Steps
1. **Check Database Tables**
   ```sql
   -- Verify device data
   SELECT COUNT(*) FROM devices WHERE deleted = 0;
   SELECT COUNT(*) FROM cabinet_configurations;
   SELECT COUNT(*) FROM planograms;
   
   -- Check for orphaned records
   SELECT d.name, COUNT(cc.id) as cabinet_count
   FROM devices d
   LEFT JOIN cabinet_configurations cc ON d.id = cc.device_id
   WHERE d.deleted = 0
   GROUP BY d.id, d.name;
   ```

2. **Test Device API**
   ```bash
   # Test device creation
   curl -X POST http://localhost:5000/api/devices \
        -H "Authorization: Bearer [token]" \
        -H "Content-Type: application/json" \
        -d '{"name":"Test Device","location_id":1}'
   ```

3. **Check Business Logic**
   ```python
   # Test device service directly
   from device_service import DeviceService
   service = DeviceService()
   result = service.create_device({
       'name': 'Test Device',
       'location_id': 1
   })
   print(result)
   ```

#### Solutions

##### Solution 1: Fix Data Integrity
```sql
-- Clean up orphaned cabinet configurations
DELETE FROM cabinet_configurations 
WHERE device_id NOT IN (SELECT id FROM devices WHERE deleted = 0);

-- Reset auto-increment counters
DELETE FROM sqlite_sequence WHERE name IN ('devices', 'cabinet_configurations');
```

##### Solution 2: Rebuild Device Indexes
```sql
-- Rebuild database indexes
REINDEX;
PRAGMA optimize;

-- Update statistics
ANALYZE;
```

##### Solution 3: Restore Default Data
```python
# Restore system products and device types
from app import app, db
from models import Product, DeviceType, CabinetType

with app.app_context():
    # Restore default products if missing
    if Product.query.count() == 0:
        default_products = [
            {'name': 'Coca Cola', 'price': 1.50, 'category': 'Beverages'},
            {'name': 'Pepsi', 'price': 1.50, 'category': 'Beverages'},
            # ... add other default products
        ]
        for product_data in default_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print("Default products restored")
```

## Error Code Reference

### Authentication Errors (ERR_AUTH_xxx)
- **ERR_AUTH_001**: Invalid credentials
- **ERR_AUTH_002**: Account locked
- **ERR_AUTH_003**: Session expired
- **ERR_AUTH_004**: Insufficient permissions

### Database Errors (ERR_DB_xxx)
- **ERR_DB_001**: Connection failure
- **ERR_DB_002**: Query execution error
- **ERR_DB_003**: Data integrity violation
- **ERR_DB_004**: Database locked

### API Errors (ERR_API_xxx)
- **ERR_API_001**: Endpoint not found
- **ERR_API_002**: Invalid request format
- **ERR_API_003**: Rate limit exceeded
- **ERR_API_004**: Service unavailable

### System Errors (ERR_SYS_xxx)
- **ERR_SYS_001**: Configuration error
- **ERR_SYS_002**: Resource exhaustion
- **ERR_SYS_003**: Permission denied
- **ERR_SYS_004**: Service initialization failure

## Performance Troubleshooting

### Slow Response Times

#### Diagnostic Steps
1. **Measure Response Times**
   ```bash
   # Test API response times
   time curl -s http://localhost:5000/api/devices > /dev/null
   
   # Monitor with continuous testing
   while true; do
       time curl -s http://localhost:5000/api/devices > /dev/null
       sleep 5
   done
   ```

2. **Check Resource Usage**
   ```bash
   # Monitor system resources
   top -p $(pgrep -f "python|http.server")
   iostat 1 5
   vmstat 1 5
   ```

3. **Analyze Database Performance**
   ```sql
   -- Check for missing indexes
   PRAGMA index_list(devices);
   PRAGMA index_list(cabinet_configurations);
   
   -- Analyze query performance
   EXPLAIN QUERY PLAN 
   SELECT d.*, cc.* 
   FROM devices d 
   LEFT JOIN cabinet_configurations cc ON d.id = cc.device_id 
   WHERE d.deleted = 0;
   ```

#### Solutions
1. **Optimize Database Queries**
2. **Add Missing Indexes**
3. **Implement Query Caching**
4. **Increase System Resources**

### Memory Issues

#### Diagnostic Steps
1. **Monitor Memory Usage**
   ```bash
   # Check memory consumption
   ps -o pid,ppid,cmd,%mem,%cpu -p $(pgrep -f python)
   
   # Monitor memory over time
   while true; do
       ps -o pid,ppid,cmd,%mem -p $(pgrep -f python)
       sleep 10
   done
   ```

2. **Check for Memory Leaks**
   ```python
   # Add memory monitoring to application
   import psutil
   import gc
   
   def log_memory_usage():
       process = psutil.Process()
       memory_mb = process.memory_info().rss / 1024 / 1024
       print(f"Memory usage: {memory_mb:.2f} MB")
       print(f"GC collections: {gc.get_count()}")
   ```

#### Solutions
1. **Implement Proper Cleanup**
2. **Optimize Data Structures**
3. **Add Memory Limits**
4. **Restart Services Periodically**

## Prevention Strategies

### Regular Maintenance

#### Daily Tasks
- Monitor system logs for errors
- Check service status and uptime
- Verify backup completion
- Review performance metrics

#### Weekly Tasks
- Clean up temporary files and logs
- Update system packages
- Review user activity and permissions
- Test backup restoration procedures

#### Monthly Tasks
- Analyze performance trends
- Review and update documentation
- Conduct security audits
- Plan capacity upgrades

### Monitoring Setup

#### Log Monitoring
```bash
# Setup log rotation
sudo cat > /etc/logrotate.d/cvd << EOF
/path/to/cvd/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

#### Health Check Scripts
```bash
#!/bin/bash
# health_check.sh

# Check services
if ! curl -s http://localhost:5000/api/health > /dev/null; then
    echo "Backend service is down"
    exit 1
fi

if ! curl -s http://localhost:8000/ > /dev/null; then
    echo "Frontend service is down"
    exit 1
fi

# Check database
if ! sqlite3 instance/cvd.db "SELECT 1;" > /dev/null 2>&1; then
    echo "Database is not accessible"
    exit 1
fi

echo "All systems operational"
```

#### Automated Alerts
```bash
# Setup cron job for monitoring
crontab -e

# Add line:
*/5 * * * * /path/to/cvd/scripts/health_check.sh || mail -s "CVD System Alert" admin@example.com < /dev/null
```

## Recovery Procedures

### Data Recovery

#### From Database Backup
```bash
# Stop services
systemctl stop cvd-backend

# Restore database
cp backups/cvd.db.$(date +%Y%m%d) instance/cvd.db

# Verify integrity
sqlite3 instance/cvd.db "PRAGMA integrity_check;"

# Restart services
systemctl start cvd-backend
```

#### From System Backup
```bash
# Full system restore
tar -xzf backups/cvd-system-$(date +%Y%m%d).tar.gz -C /

# Restore permissions
chown -R cvd-user:cvd-group /path/to/cvd
chmod +x /path/to/cvd/*.py
```

### Disaster Recovery

#### Complete System Rebuild
1. **Prepare New Environment**
2. **Install Dependencies**
3. **Restore Configuration**
4. **Restore Data**
5. **Verify Functionality**
6. **Update DNS/Load Balancer**

## Contact Information

### Internal Support
- **Development Team**: dev-team@company.com
- **System Administrator**: sysadmin@company.com
- **Database Administrator**: dba@company.com

### External Support
- **Hosting Provider**: provider-support@hosting.com
- **Third-party Services**: Check individual service documentation

### Emergency Contacts
- **On-call Developer**: [phone number]
- **System Administrator**: [phone number]
- **Management Escalation**: [phone number]

---

**Document Version**: [Version number]
**Last Updated**: [Date]
**Next Review**: [Date + 3 months]
**Document Owner**: [Team/Person responsible]