# CVD Performance Tuning Runbook


## Metadata
- **ID**: 05_DEVELOPMENT_DEPLOYMENT_RUNBOOKS_PERFORMANCE_TUNING
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #coding #data-exchange #data-layer #database #debugging #deployment #development #device-management #devops #dex-parser #integration #logistics #machine-learning #metrics #operations #optimization #performance #planogram #product-placement #quality-assurance #reporting #route-management #security #service-orders #testing #troubleshooting #vending-machine #workflows
- **Intent**: This runbook provides comprehensive procedures for optimizing CVD (Vision Device Configuration) system performance
- **Audience**: system administrators, managers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/deployment/runbooks/
- **Category**: Runbooks
- **Search Keywords**: (95th, 1.0, 1024, 2024-01-01, 2024-04-01, <100ms, <500ms, <80%, >99.5%, ^/api/., api, approver, args,, cpu, cvd

## Overview

This runbook provides comprehensive procedures for optimizing CVD (Vision Device Configuration) system performance. It covers database optimization, application tuning, system resource optimization, and scaling strategies for the Flask/SQLite architecture.

### Scope
- Database performance optimization (SQLite)
- Application server tuning (Flask/Gunicorn)
- System resource optimization
- Caching strategies
- Network and SSL optimization
- AI services performance tuning

### Performance Targets
- **API Response Time**: <500ms (95th percentile)
- **Database Query Time**: <100ms (95th percentile)
- **Page Load Time**: <2 seconds
- **System Uptime**: >99.5%
- **Memory Usage**: <80%
- **CPU Usage**: <70% (sustained)

## Performance Assessment

### System Performance Baseline

```bash
#!/bin/bash
echo "=== CVD PERFORMANCE BASELINE ASSESSMENT ==="

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="/opt/cvd/logs/performance_baseline_${TIMESTAMP}.log"

log_performance() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$REPORT_FILE"
}

log_performance "Starting performance baseline assessment..."

# 1. Application Response Time Testing
log_performance "=== Application Response Time ==="
for endpoint in "/health" "/api/devices" "/api/planograms" "/api/users"; do
    log_performance "Testing endpoint: $endpoint"
    
    # Test 10 requests and calculate average
    TOTAL_TIME=0
    for i in {1..10}; do
        RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:5000$endpoint" 2>/dev/null || echo "999")
        TOTAL_TIME=$(echo "$TOTAL_TIME + $RESPONSE_TIME" | bc)
        sleep 1
    done
    
    AVG_TIME=$(echo "scale=3; $TOTAL_TIME / 10" | bc)
    log_performance "Average response time for $endpoint: ${AVG_TIME}s"
done

# 2. Database Performance Testing
log_performance "=== Database Performance ==="
DATABASE_PATH="/opt/cvd/data/cvd.db"

# Test basic queries
QUERIES=(
    "SELECT COUNT(*) FROM users"
    "SELECT COUNT(*) FROM devices"
    "SELECT COUNT(*) FROM service_orders"
    "SELECT COUNT(*) FROM planograms"
)

for query in "${QUERIES[@]}"; do
    START_TIME=$(date +%s.%N)
    RESULT=$(sqlite3 "$DATABASE_PATH" "$query" 2>/dev/null || echo "ERROR")
    END_TIME=$(date +%s.%N)
    DURATION=$(echo "$END_TIME - $START_TIME" | bc)
    log_performance "Query: '$query' - Result: $RESULT - Time: ${DURATION}s"
done

# Database statistics
DB_SIZE=$(stat -c%s "$DATABASE_PATH" 2>/dev/null | awk '{print int($1/1024/1024)"MB"}')
log_performance "Database size: $DB_SIZE"

# Check database pragmas
log_performance "Database configuration:"
for pragma in "page_size" "cache_size" "journal_mode" "synchronous" "temp_store"; do
    VALUE=$(sqlite3 "$DATABASE_PATH" "PRAGMA $pragma;" 2>/dev/null || echo "unknown")
    log_performance "PRAGMA $pragma: $VALUE"
done

# 3. System Resource Assessment
log_performance "=== System Resources ==="

# CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
log_performance "CPU usage: $CPU_USAGE"

# Memory usage
MEMORY_USAGE=$(free | awk '/Mem:/ {printf "%.1f%%", $3/$2 * 100.0}')
MEMORY_AVAILABLE=$(free -h | awk '/Mem:/ {print $7}')
log_performance "Memory usage: $MEMORY_USAGE (Available: $MEMORY_AVAILABLE)"

# Disk usage
DISK_USAGE=$(df /opt/cvd | awk 'NR==2 {print $5}')
DISK_AVAILABLE=$(df -h /opt/cvd | awk 'NR==2 {print $4}')
log_performance "Disk usage: $DISK_USAGE (Available: $DISK_AVAILABLE)"

# I/O statistics
if command -v iostat >/dev/null 2>&1; then
    IO_STATS=$(iostat -x 1 1 | grep -A1 "Device" | tail -n1)
    log_performance "I/O stats: $IO_STATS"
fi

# 4. Application Process Analysis
log_performance "=== Application Processes ==="

# Gunicorn processes
GUNICORN_PROCESSES=$(ps aux | grep gunicorn | grep -v grep | wc -l)
log_performance "Gunicorn processes: $GUNICORN_PROCESSES"

# Memory usage per process
ps aux --sort=-%mem | grep -E "(gunicorn|python.*app)" | grep -v grep | while read line; do
    PROCESS_INFO=$(echo "$line" | awk '{print $11 " - CPU: " $3 "% Memory: " $4 "% RSS: " $6 "KB"}')
    log_performance "Process: $PROCESS_INFO"
done

# 5. Network Performance
log_performance "=== Network Performance ==="

# Test SSL handshake time
if command -v openssl >/dev/null 2>&1; then
    SSL_TIME=$(curl -w "@-" -o /dev/null -s "https://your-domain.com/health" <<< 'time_namelookup: %{time_namelookup}s\ntime_connect: %{time_connect}s\ntime_appconnect: %{time_appconnect}s\ntime_pretransfer: %{time_pretransfer}s\ntime_total: %{time_total}s\n')
    log_performance "SSL/Network timing:"
    echo "$SSL_TIME" | while read line; do log_performance "  $line"; done
fi

# 6. AI Services Performance (if configured)
if [ -n "$ANTHROPIC_API_KEY" ]; then
    log_performance "=== AI Services Performance ==="
    
    # Test AI response time (mock request)
    START_TIME=$(date +%s.%N)
    # This would need to be adjusted based on your AI implementation
    log_performance "AI services configured - manual testing required"
    END_TIME=$(date +%s.%N)
fi

log_performance "Performance baseline assessment completed"
echo "Performance report saved to: $REPORT_FILE"
```

### Performance Monitoring Script

```bash
#!/bin/bash
echo "=== CVD CONTINUOUS PERFORMANCE MONITORING ==="

MONITOR_DURATION=${1:-300}  # Default 5 minutes
INTERVAL=30  # Check every 30 seconds
LOG_FILE="/opt/cvd/logs/performance_monitor.log"

log_monitor() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_monitor "Starting continuous monitoring for ${MONITOR_DURATION} seconds..."

END_TIME=$(($(date +%s) + MONITOR_DURATION))

while [ $(date +%s) -lt $END_TIME ]; do
    # Application response time
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:5000/health 2>/dev/null || echo "999")
    
    # System resources
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//' | cut -d'%' -f1)
    MEMORY=$(free | awk '/Mem:/ {printf "%.1f", $3/$2 * 100.0}')
    
    # Database query time
    DB_START=$(date +%s.%N)
    sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM users;" >/dev/null 2>&1
    DB_END=$(date +%s.%N)
    DB_TIME=$(echo "$DB_END - $DB_START" | bc)
    
    # Log metrics
    log_monitor "Response: ${RESPONSE_TIME}s | CPU: ${CPU}% | Memory: ${MEMORY}% | DB: ${DB_TIME}s"
    
    # Alert on performance issues
    if (( $(echo "$RESPONSE_TIME > 2.0" | bc -l) )); then
        log_monitor "ALERT: High response time detected: ${RESPONSE_TIME}s"
    fi
    
    if (( $(echo "$CPU > 80" | bc -l) )); then
        log_monitor "ALERT: High CPU usage detected: ${CPU}%"
    fi
    
    if (( $(echo "$MEMORY > 85" | bc -l) )); then
        log_monitor "ALERT: High memory usage detected: ${MEMORY}%"
    fi
    
    sleep $INTERVAL
done

log_monitor "Continuous monitoring completed"
```

## Database Optimization

### SQLite Performance Tuning

```bash
#!/bin/bash
echo "=== CVD DATABASE PERFORMANCE OPTIMIZATION ==="

DATABASE_PATH="/opt/cvd/data/cvd.db"
BACKUP_PATH="/opt/cvd/backups/pre_optimization_$(date +%Y%m%d_%H%M%S).db"
LOG_FILE="/opt/cvd/logs/db_optimization.log"

log_db() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_db "Starting database optimization..."

# Create backup before optimization
log_db "Creating backup before optimization..."
sqlite3 "$DATABASE_PATH" ".backup $BACKUP_PATH"
log_db "Backup created: $BACKUP_PATH"

# Stop application to prevent database locks
log_db "Stopping CVD service for optimization..."
sudo systemctl stop cvd

# 1. Analyze current database performance
log_db "=== Current Database Analysis ==="

# Database size and page information
DB_SIZE=$(stat -c%s "$DATABASE_PATH")
PAGE_SIZE=$(sqlite3 "$DATABASE_PATH" "PRAGMA page_size;")
PAGE_COUNT=$(sqlite3 "$DATABASE_PATH" "PRAGMA page_count;")
FREELIST_COUNT=$(sqlite3 "$DATABASE_PATH" "PRAGMA freelist_count;")

log_db "Database size: $(($DB_SIZE / 1024 / 1024))MB"
log_db "Page size: $PAGE_SIZE bytes"
log_db "Page count: $PAGE_COUNT"
log_db "Free pages: $FREELIST_COUNT"

# Current pragma settings
log_db "Current PRAGMA settings:"
for pragma in "journal_mode" "synchronous" "cache_size" "temp_store" "mmap_size"; do
    VALUE=$(sqlite3 "$DATABASE_PATH" "PRAGMA $pragma;")
    log_db "  $pragma: $VALUE"
done

# 2. Apply performance optimizations
log_db "=== Applying Database Optimizations ==="

# Set optimal PRAGMA settings
log_db "Configuring optimal PRAGMA settings..."

sqlite3 "$DATABASE_PATH" << 'EOF'
-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- Set synchronous to NORMAL for better performance (vs FULL)
PRAGMA synchronous = NORMAL;

-- Increase cache size to 64MB (from default ~2MB)
PRAGMA cache_size = -65536;

-- Use memory for temporary tables
PRAGMA temp_store = MEMORY;

-- Enable memory-mapped I/O (256MB)
PRAGMA mmap_size = 268435456;

-- Set auto_vacuum to INCREMENTAL for better space management
PRAGMA auto_vacuum = INCREMENTAL;

-- Optimize page size for better performance (if rebuilding)
-- PRAGMA page_size = 4096;
EOF

# Verify new settings
log_db "New PRAGMA settings:"
for pragma in "journal_mode" "synchronous" "cache_size" "temp_store" "mmap_size"; do
    VALUE=$(sqlite3 "$DATABASE_PATH" "PRAGMA $pragma;")
    log_db "  $pragma: $VALUE"
done

# 3. Analyze table structure and create indexes
log_db "=== Index Optimization ==="

# Get current indexes
CURRENT_INDEXES=$(sqlite3 "$DATABASE_PATH" "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
log_db "Current indexes:"
echo "$CURRENT_INDEXES" | while read line; do
    log_db "  $line"
done

# Create performance indexes based on common queries
log_db "Creating performance indexes..."

sqlite3 "$DATABASE_PATH" << 'EOF'
-- Index for device queries
CREATE INDEX IF NOT EXISTS idx_devices_soft_deleted ON devices(soft_deleted);
CREATE INDEX IF NOT EXISTS idx_devices_last_communication ON devices(last_communication);

-- Index for user authentication
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires);

-- Index for service orders
CREATE INDEX IF NOT EXISTS idx_service_orders_status ON service_orders(status);
CREATE INDEX IF NOT EXISTS idx_service_orders_created_at ON service_orders(created_at);
CREATE INDEX IF NOT EXISTS idx_service_orders_driver_id ON service_orders(driver_id);

-- Index for planograms
CREATE INDEX IF NOT EXISTS idx_planograms_device_id ON planograms(device_id);
CREATE INDEX IF NOT EXISTS idx_planogram_slots_planogram_id ON planogram_slots(planogram_id);

-- Index for sales data (if exists)
CREATE INDEX IF NOT EXISTS idx_sales_device_id_date ON sales(device_id, date);

-- Index for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
EOF

log_db "Performance indexes created"

# 4. Database maintenance operations
log_db "=== Database Maintenance ==="

# Analyze all tables for query optimization
log_db "Analyzing tables for query optimization..."
sqlite3 "$DATABASE_PATH" "ANALYZE;"

# Reclaim free space
log_db "Reclaiming free space..."
if [ "$FREELIST_COUNT" -gt 0 ]; then
    sqlite3 "$DATABASE_PATH" "PRAGMA incremental_vacuum;"
    NEW_FREELIST=$(sqlite3 "$DATABASE_PATH" "PRAGMA freelist_count;")
    log_db "Free pages reduced from $FREELIST_COUNT to $NEW_FREELIST"
fi

# Optimize database structure
log_db "Optimizing database structure..."
sqlite3 "$DATABASE_PATH" "PRAGMA optimize;"

# 5. Verify optimization results
log_db "=== Optimization Results ==="

NEW_DB_SIZE=$(stat -c%s "$DATABASE_PATH")
SIZE_CHANGE=$((NEW_DB_SIZE - DB_SIZE))
PERCENT_CHANGE=$(echo "scale=2; ($SIZE_CHANGE * 100) / $DB_SIZE" | bc)

log_db "Size change: $SIZE_CHANGE bytes (${PERCENT_CHANGE}%)"
log_db "New database size: $(($NEW_DB_SIZE / 1024 / 1024))MB"

# Test query performance
log_db "Testing query performance..."
QUERIES=(
    "SELECT COUNT(*) FROM users"
    "SELECT COUNT(*) FROM devices WHERE soft_deleted = 0"
    "SELECT COUNT(*) FROM service_orders WHERE status = 'pending'"
)

for query in "${QUERIES[@]}"; do
    START_TIME=$(date +%s.%N)
    RESULT=$(sqlite3 "$DATABASE_PATH" "$query")
    END_TIME=$(date +%s.%N)
    DURATION=$(echo "scale=4; $END_TIME - $START_TIME" | bc)
    log_db "Query performance: '$query' -> ${DURATION}s (result: $RESULT)"
done

# Start application service
log_db "Starting CVD service..."
sudo systemctl start cvd

# Wait for service to start
sleep 15

# Verify application is working
if systemctl is-active cvd >/dev/null && curl -f http://localhost:5000/health >/dev/null 2>&1; then
    log_db "Application started successfully after optimization"
    echo "Database optimization completed successfully"
else
    log_db "ERROR: Application failed to start after optimization"
    
    # Restore from backup
    log_db "Restoring from backup..."
    sudo systemctl stop cvd
    cp "$BACKUP_PATH" "$DATABASE_PATH"
    sudo systemctl start cvd
    
    log_db "Database restored from backup"
    exit 1
fi

log_db "Database optimization completed successfully"
```

### Database Query Optimization

```bash
#!/bin/bash
echo "=== CVD DATABASE QUERY ANALYSIS ==="

DATABASE_PATH="/opt/cvd/data/cvd.db"
LOG_FILE="/opt/cvd/logs/query_analysis.log"

log_query() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_query "Starting database query analysis..."

# Enable query planning output
sqlite3 "$DATABASE_PATH" "PRAGMA query_only = ON;"

# Analyze common application queries
COMMON_QUERIES=(
    "SELECT * FROM users WHERE username = 'admin'"
    "SELECT * FROM devices WHERE soft_deleted = 0"
    "SELECT COUNT(*) FROM service_orders WHERE status = 'pending'"
    "SELECT * FROM planograms WHERE device_id = 1"
    "SELECT * FROM audit_log WHERE user_id = 1 ORDER BY timestamp DESC LIMIT 10"
)

log_query "=== Query Execution Plan Analysis ==="

for query in "${COMMON_QUERIES[@]}"; do
    log_query "Analyzing query: $query"
    
    # Get query execution plan
    PLAN=$(sqlite3 "$DATABASE_PATH" "EXPLAIN QUERY PLAN $query" 2>/dev/null)
    log_query "Execution plan:"
    echo "$PLAN" | while read line; do
        log_query "  $line"
    done
    
    # Check for table scans (performance issue)
    if echo "$PLAN" | grep -q "SCAN TABLE"; then
        log_query "⚠️  WARNING: Query uses table scan - consider adding index"
    fi
    
    log_query "---"
done

# Disable query planning
sqlite3 "$DATABASE_PATH" "PRAGMA query_only = OFF;"

# Suggest missing indexes based on query patterns
log_query "=== Index Recommendations ==="

# Check for foreign key queries without indexes
FK_QUERIES=(
    "SELECT name FROM pragma_foreign_key_list('service_orders')"
    "SELECT name FROM pragma_foreign_key_list('planograms')" 
    "SELECT name FROM pragma_foreign_key_list('audit_log')"
)

for fk_query in "${FK_QUERIES[@]}"; do
    FKS=$(sqlite3 "$DATABASE_PATH" "$fk_query" 2>/dev/null)
    if [ -n "$FKS" ]; then
        log_query "Foreign keys found, checking for indexes: $FKS"
    fi
done

log_query "Query analysis completed"
```

## Application Server Optimization

### Gunicorn Configuration Tuning

```bash
#!/bin/bash
echo "=== CVD APPLICATION SERVER OPTIMIZATION ==="

LOG_FILE="/opt/cvd/logs/app_optimization.log"
CONFIG_DIR="/opt/cvd/config"

log_app() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_app "Starting application server optimization..."

# 1. Analyze current configuration
log_app "=== Current Configuration Analysis ==="

# Get current Gunicorn configuration
CURRENT_WORKERS=$(ps aux | grep gunicorn | grep -v grep | wc -l)
log_app "Current Gunicorn workers: $CURRENT_WORKERS"

# System resources
CPU_CORES=$(nproc)
MEMORY_GB=$(free -g | awk '/Mem:/ {print $2}')
log_app "System resources: ${CPU_CORES} CPU cores, ${MEMORY_GB}GB RAM"

# Calculate optimal worker count
OPTIMAL_WORKERS=$(((CPU_CORES * 2) + 1))
if [ $OPTIMAL_WORKERS -gt 8 ]; then
    OPTIMAL_WORKERS=8  # Cap at 8 workers
fi

log_app "Recommended workers: $OPTIMAL_WORKERS (formula: (CPU * 2) + 1)"

# 2. Create optimized Gunicorn configuration
log_app "Creating optimized Gunicorn configuration..."

cat > "$CONFIG_DIR/gunicorn.conf.py" << EOF
# Optimized Gunicorn configuration for CVD

import multiprocessing
import os

# Server socket
bind = "unix:/opt/cvd/app/cvd.sock"
backlog = 2048

# Worker processes
workers = $OPTIMAL_WORKERS
worker_class = "sync"
worker_connections = 1000
max_requests = 1200
max_requests_jitter = 50
preload_app = True

# Worker timeouts
timeout = 120
keepalive = 5

# Process naming
proc_name = "cvd-app"

# Logging
errorlog = "/opt/cvd/logs/gunicorn_error.log"
loglevel = "info"
accesslog = "/opt/cvd/logs/gunicorn_access.log"
access_log_format = '%h %l %u %t "%r" %s %b "%{Referer}i" "%{User-Agent}i" %D'

# Process management
daemon = False
pidfile = "/opt/cvd/app/cvd.pid"
user = "cvdapp"
group = "www-data"
tmp_upload_dir = None

# SSL (if terminating SSL at application level)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Performance tuning
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance

# Preload application for better memory usage
def on_starting(server):
    server.log.info("Server is starting")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)
EOF

log_app "Gunicorn configuration created: $CONFIG_DIR/gunicorn.conf.py"

# 3. Update systemd service to use new configuration
log_app "Updating systemd service configuration..."

cat > "/tmp/cvd.service.new" << EOF
[Unit]
Description=CVD Flask Application
After=network.target

[Service]
Type=notify
User=cvdapp
Group=www-data
WorkingDirectory=/opt/cvd/app
Environment=PATH=/opt/cvd/app/venv/bin
EnvironmentFile=/opt/cvd/config/.env
ExecStart=/opt/cvd/app/venv/bin/gunicorn --config /opt/cvd/config/gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cvd

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/cvd/data /opt/cvd/logs /opt/cvd/backups
ProtectHome=true

# Performance settings
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
EOF

# Backup current service file
cp /etc/systemd/system/cvd.service /opt/cvd/backups/cvd.service.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null

# Install new service configuration
sudo cp /tmp/cvd.service.new /etc/systemd/system/cvd.service
sudo systemctl daemon-reload

log_app "Systemd service configuration updated"

# 4. Apply Flask application optimizations
log_app "=== Flask Application Optimizations ==="

# Create optimized Flask configuration
cat > "$CONFIG_DIR/flask_optimization.py" << 'EOF'
# Flask optimization settings for CVD

import os
from datetime import timedelta

class OptimizedConfig:
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security optimizations
    SECRET_KEY = os.environ.get('SESSION_SECRET')
    WTF_CSRF_TIME_LIMIT = None
    
    # JSON optimization
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Request handling
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    
    # Database optimization
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    } if 'postgresql' in os.environ.get('DATABASE_URL', '') else {}
    
    # Caching (if using Flask-Caching)
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
EOF

log_app "Flask optimization configuration created"

# 5. Apply Python optimizations
log_app "=== Python Runtime Optimizations ==="

# Update environment variables for Python optimization
cat >> "$CONFIG_DIR/.env" << 'EOF'

# Python optimization
PYTHONOPTIMIZE=1
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1

# Gunicorn optimization
GUNICORN_CMD_ARGS="--config /opt/cvd/config/gunicorn.conf.py"
EOF

log_app "Python optimization environment variables added"

# 6. Restart and verify optimization
log_app "=== Applying Optimizations ==="

log_app "Restarting CVD service with new configuration..."
sudo systemctl restart cvd

# Wait for service to start
sleep 20

# Verify service is running with new configuration
if systemctl is-active cvd >/dev/null; then
    NEW_WORKERS=$(ps aux | grep gunicorn | grep -v grep | wc -l)
    log_app "Service restarted successfully with $NEW_WORKERS workers"
    
    # Test application performance
    log_app "Testing application performance..."
    for i in {1..5}; do
        RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:5000/health)
        log_app "Response time test $i: ${RESPONSE_TIME}s"
    done
    
    # Check memory usage
    MEMORY_USAGE=$(ps aux --sort=-%mem | grep gunicorn | grep -v grep | head -n1 | awk '{print $4}')
    log_app "Master process memory usage: ${MEMORY_USAGE}%"
    
else
    log_app "ERROR: Service failed to start with new configuration"
    
    # Rollback to previous configuration
    log_app "Rolling back to previous configuration..."
    sudo cp /opt/cvd/backups/cvd.service.backup.* /etc/systemd/system/cvd.service 2>/dev/null
    sudo systemctl daemon-reload
    sudo systemctl start cvd
    
    exit 1
fi

log_app "Application server optimization completed successfully"
```

### Caching Implementation

```bash
#!/bin/bash
echo "=== CVD CACHING OPTIMIZATION ==="

LOG_FILE="/opt/cvd/logs/caching_optimization.log"

log_cache() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_cache "Starting caching optimization implementation..."

# 1. Install Redis for caching (if not installed)
if ! command -v redis-cli >/dev/null 2>&1; then
    log_cache "Installing Redis for caching..."
    
    # For Ubuntu/Debian
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y redis-server
    # For RHEL/CentOS
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y redis
    fi
    
    # Configure Redis for production
    sudo tee -a /etc/redis/redis.conf << 'EOF'

# Performance optimizations
maxmemory 256mb
maxmemory-policy allkeys-lru
tcp-keepalive 300
timeout 0

# Persistence optimization
save 900 1
save 300 10
save 60 10000
EOF
    
    sudo systemctl enable redis
    sudo systemctl start redis
    
    log_cache "Redis installed and configured"
fi

# 2. Create caching layer for CVD
log_cache "Creating application caching layer..."

cat > /opt/cvd/app/cache_manager.py << 'EOF'
"""
CVD Caching Manager
Provides application-level caching for performance optimization.
"""

import redis
import json
import time
import hashlib
from functools import wraps
from typing import Any, Optional

class CacheManager:
    def __init__(self, redis_url='redis://localhost:6379/0'):
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            print(f"Redis not available, caching disabled: {e}")
            self.enabled = False
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            key_parts.append(hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest())
        return ':'.join(key_parts)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception:
            pass
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL."""
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled:
            return False
        
        try:
            return self.redis_client.delete(key) > 0
        except Exception:
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception:
            pass
        return 0

# Global cache manager instance
cache = CacheManager()

def cached(ttl: int = 300, prefix: str = 'cvd'):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._make_key(f"{prefix}:{func.__name__}", *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Add cache control methods
        wrapper.cache_key = lambda *args, **kwargs: cache._make_key(f"{prefix}:{func.__name__}", *args, **kwargs)
        wrapper.invalidate = lambda *args, **kwargs: cache.delete(wrapper.cache_key(*args, **kwargs))
        wrapper.clear_all = lambda: cache.clear_pattern(f"{prefix}:{func.__name__}:*")
        
        return wrapper
    return decorator

# Application-specific cache helpers
class CVDCache:
    @staticmethod
    def cache_user_data(user_id: int, data: dict, ttl: int = 1800):
        """Cache user-specific data."""
        cache.set(f"user:{user_id}", data, ttl)
    
    @staticmethod
    def get_user_data(user_id: int):
        """Get cached user data."""
        return cache.get(f"user:{user_id}")
    
    @staticmethod
    def invalidate_user(user_id: int):
        """Invalidate all user-related cache."""
        cache.clear_pattern(f"*user:{user_id}*")
    
    @staticmethod
    def cache_device_list(device_list: list, ttl: int = 600):
        """Cache device list."""
        cache.set("devices:active", device_list, ttl)
    
    @staticmethod
    def get_device_list():
        """Get cached device list."""
        return cache.get("devices:active")
    
    @staticmethod
    def invalidate_devices():
        """Invalidate device-related cache."""
        cache.clear_pattern("devices:*")
    
    @staticmethod
    def cache_planogram(device_id: int, planogram_data: dict, ttl: int = 3600):
        """Cache planogram data."""
        cache.set(f"planogram:{device_id}", planogram_data, ttl)
    
    @staticmethod
    def get_planogram(device_id: int):
        """Get cached planogram."""
        return cache.get(f"planogram:{device_id}")
    
    @staticmethod
    def invalidate_planogram(device_id: int):
        """Invalidate planogram cache."""
        cache.delete(f"planogram:{device_id}")
EOF

# 3. Implement browser caching optimization
log_cache "Implementing browser caching optimization..."

cat > /tmp/nginx_caching.conf << 'EOF'
# Browser caching optimization for CVD static assets

# Static assets with versioning - cache for 1 year
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # Enable compression for text-based assets
    gzip_vary on;
    gzip_comp_level 6;
}

# API responses - short cache for GET requests
location ~* ^/api/.* {
    # Only cache GET requests
    set $no_cache 0;
    if ($request_method != GET) {
        set $no_cache 1;
    }
    
    # Don't cache authenticated requests
    if ($http_authorization) {
        set $no_cache 1;
    }
    
    # Cache control headers
    expires 5m;
    add_header Cache-Control "public, max-age=300";
    add_header X-Cache-Status $upstream_cache_status;
}

# HTML pages - minimal caching
location ~* \.(html|htm)$ {
    expires 5m;
    add_header Cache-Control "public, max-age=300, must-revalidate";
}

# Dynamic content - no cache
location / {
    expires off;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
    add_header Pragma "no-cache";
}
EOF

log_cache "Nginx caching configuration created"

# 4. Update Flask application to use caching
log_cache "Integrating caching with Flask application..."

cat > /tmp/app_caching_integration.py << 'EOF'
# Add this to your main app.py file

from cache_manager import cached, CVDCache

# Example: Cache device list endpoint
@app.route('/api/devices')
@cached(ttl=600, prefix='api')  # Cache for 10 minutes
def get_devices():
    # Your existing device fetching logic
    pass

# Example: Cache user profile
@app.route('/api/user/<int:user_id>')
@cached(ttl=1800, prefix='api')  # Cache for 30 minutes
def get_user_profile(user_id):
    # Your existing user profile logic
    pass

# Example: Invalidate cache on updates
@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    # Your update logic here
    
    # Invalidate related caches
    CVDCache.invalidate_devices()
    cache.clear_pattern(f"api:get_device:{device_id}:*")
    
    return jsonify({'status': 'updated'})
EOF

log_cache "Flask caching integration examples created"

# 5. Test caching implementation
log_cache "Testing caching implementation..."

# Test Redis connectivity
if redis-cli ping | grep -q "PONG"; then
    log_cache "✅ Redis connectivity verified"
    
    # Test cache operations
    redis-cli set test_key "test_value" EX 60 >/dev/null
    TEST_VALUE=$(redis-cli get test_key)
    
    if [ "$TEST_VALUE" = "test_value" ]; then
        log_cache "✅ Redis cache operations verified"
        redis-cli del test_key >/dev/null
    else
        log_cache "❌ Redis cache operations failed"
    fi
else
    log_cache "❌ Redis connectivity failed"
fi

# 6. Monitor cache performance
log_cache "Setting up cache monitoring..."

cat > /opt/cvd/scripts/cache_monitor.sh << 'EOF'
#!/bin/bash
# Monitor Redis cache performance

echo "=== Redis Cache Statistics ==="
redis-cli info memory | grep -E "(used_memory|used_memory_peak|used_memory_human)"
redis-cli info stats | grep -E "(total_commands_processed|keyspace_hits|keyspace_misses)"

# Calculate hit rate
HITS=$(redis-cli info stats | grep keyspace_hits | cut -d: -f2)
MISSES=$(redis-cli info stats | grep keyspace_misses | cut -d: -f2)
TOTAL=$((HITS + MISSES))

if [ $TOTAL -gt 0 ]; then
    HIT_RATE=$(echo "scale=2; ($HITS * 100) / $TOTAL" | bc)
    echo "Cache hit rate: ${HIT_RATE}%"
fi

echo "=== Top Cache Keys ==="
redis-cli --scan --pattern "*" | head -n 10

echo "=== Cache Key Count by Prefix ==="
for prefix in user device planogram api; do
    COUNT=$(redis-cli --scan --pattern "${prefix}:*" | wc -l)
    echo "${prefix}: $COUNT keys"
done
EOF

chmod +x /opt/cvd/scripts/cache_monitor.sh

log_cache "Cache monitoring script created: /opt/cvd/scripts/cache_monitor.sh"

log_cache "Caching optimization implementation completed"
echo "To complete the implementation:"
echo "1. Update your Flask app.py to import and use the caching decorators"
echo "2. Update Nginx configuration with the caching rules"
echo "3. Restart services: sudo systemctl restart cvd nginx redis"
echo "4. Monitor cache performance with: /opt/cvd/scripts/cache_monitor.sh"
```

## System Resource Optimization

### Memory Optimization

```bash
#!/bin/bash
echo "=== CVD MEMORY OPTIMIZATION ==="

LOG_FILE="/opt/cvd/logs/memory_optimization.log"

log_memory() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_memory "Starting memory optimization..."

# 1. Analyze current memory usage
log_memory "=== Current Memory Analysis ==="

# System memory information
TOTAL_MEMORY=$(free -m | awk '/Mem:/ {print $2}')
USED_MEMORY=$(free -m | awk '/Mem:/ {print $3}')
AVAILABLE_MEMORY=$(free -m | awk '/Mem:/ {print $7}')
MEMORY_PERCENT=$(echo "scale=1; ($USED_MEMORY * 100) / $TOTAL_MEMORY" | bc)

log_memory "Total memory: ${TOTAL_MEMORY}MB"
log_memory "Used memory: ${USED_MEMORY}MB (${MEMORY_PERCENT}%)"
log_memory "Available memory: ${AVAILABLE_MEMORY}MB"

# Process memory usage
log_memory "Top memory-consuming processes:"
ps aux --sort=-%mem | head -n 10 | while read line; do
    log_memory "  $line"
done

# CVD application memory usage
CVD_MEMORY=$(ps aux | grep -E "(gunicorn|python.*app)" | grep -v grep | awk '{sum += $6} END {print sum/1024 " MB"}')
log_memory "CVD application memory usage: $CVD_MEMORY"

# 2. System memory optimization
log_memory "=== System Memory Optimization ==="

# Optimize swap settings
CURRENT_SWAPPINESS=$(cat /proc/sys/vm/swappiness)
log_memory "Current swappiness: $CURRENT_SWAPPINESS"

if [ "$CURRENT_SWAPPINESS" -gt 10 ]; then
    log_memory "Optimizing swappiness for server workload..."
    echo 'vm.swappiness = 10' | sudo tee -a /etc/sysctl.conf
    sudo sysctl vm.swappiness=10
    log_memory "Swappiness set to 10"
fi

# Optimize memory allocation
echo 'vm.overcommit_memory = 1' | sudo tee -a /etc/sysctl.conf
echo 'vm.max_map_count = 262144' | sudo tee -a /etc/sysctl.conf

# Apply memory optimizations
sudo sysctl -p

# 3. Application memory optimization
log_memory "=== Application Memory Optimization ==="

# Update Python memory optimization settings
cat >> /opt/cvd/config/.env << 'EOF'

# Python memory optimization
PYTHONMALLOC=malloc
PYTHONMALLOCSTATS=1

# Garbage collection optimization
PYTHONGC=1
EOF

# Create memory monitoring script
cat > /opt/cvd/scripts/memory_monitor.py << 'EOF'
#!/usr/bin/env python3
"""
CVD Memory Monitor
Monitors application memory usage and provides optimization insights.
"""

import psutil
import time
import gc
import sys
import os

def get_process_memory():
    """Get memory usage for CVD processes."""
    cvd_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent', 'cmdline']):
        try:
            if ('gunicorn' in proc.info['name'] or 
                'python' in proc.info['name'] and 'app.py' in ' '.join(proc.info['cmdline'])):
                
                cvd_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                    'memory_percent': proc.info['memory_percent']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return cvd_processes

def analyze_memory_usage():
    """Analyze system and application memory usage."""
    # System memory
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    print(f"System Memory Usage:")
    print(f"  Total: {memory.total / 1024 / 1024:.1f} MB")
    print(f"  Available: {memory.available / 1024 / 1024:.1f} MB")
    print(f"  Used: {memory.used / 1024 / 1024:.1f} MB ({memory.percent:.1f}%)")
    print(f"  Swap: {swap.used / 1024 / 1024:.1f} MB / {swap.total / 1024 / 1024:.1f} MB")
    
    # CVD processes
    cvd_processes = get_process_memory()
    total_cvd_memory = sum(proc['memory_mb'] for proc in cvd_processes)
    
    print(f"\nCVD Application Memory:")
    print(f"  Total: {total_cvd_memory:.1f} MB")
    
    for proc in cvd_processes:
        print(f"  PID {proc['pid']} ({proc['name']}): {proc['memory_mb']:.1f} MB ({proc['memory_percent']:.1f}%)")
    
    # Memory recommendations
    print(f"\nRecommendations:")
    if memory.percent > 80:
        print("  - High memory usage detected - consider increasing system RAM")
    if total_cvd_memory > (memory.total / 1024 / 1024 * 0.5):
        print("  - CVD application using >50% of system memory - consider optimization")
    if swap.used > (swap.total * 0.1):
        print("  - Significant swap usage - system may need more RAM")

if __name__ == "__main__":
    analyze_memory_usage()
EOF

chmod +x /opt/cvd/scripts/memory_monitor.py

# 4. Configure memory limits for systemd service
log_memory "Configuring memory limits for CVD service..."

# Update systemd service with memory limits
MEMORY_LIMIT=$((TOTAL_MEMORY * 80 / 100))  # 80% of system memory
log_memory "Setting memory limit to ${MEMORY_LIMIT}MB"

# Add memory limit to systemd service
sudo sed -i '/\[Service\]/a MemoryMax='"${MEMORY_LIMIT}M" /etc/systemd/system/cvd.service
sudo systemctl daemon-reload

# 5. Python garbage collection optimization
log_memory "Optimizing Python garbage collection..."

cat > /opt/cvd/app/memory_optimization.py << 'EOF'
"""
CVD Memory Optimization
Runtime memory optimization for the CVD application.
"""

import gc
import threading
import time
import psutil
import os

class MemoryOptimizer:
    def __init__(self):
        self.gc_threshold = (700, 10, 10)  # More aggressive GC
        self.monitor_interval = 300  # Check every 5 minutes
        self.memory_threshold = 80  # Alert at 80% memory usage
        self.running = True
    
    def configure_gc(self):
        """Configure garbage collection for optimal performance."""
        # Set more aggressive garbage collection
        gc.set_threshold(*self.gc_threshold)
        
        # Enable automatic garbage collection
        gc.enable()
        
        print(f"Garbage collection configured: {gc.get_threshold()}")
    
    def monitor_memory(self):
        """Monitor memory usage and trigger cleanup when needed."""
        while self.running:
            try:
                # Get current memory usage
                memory = psutil.virtual_memory()
                process = psutil.Process(os.getpid())
                process_memory = process.memory_info().rss / 1024 / 1024
                
                # Check if memory usage is high
                if memory.percent > self.memory_threshold:
                    print(f"High memory usage detected: {memory.percent:.1f}%")
                    self.cleanup_memory()
                
                # Log memory stats
                if hasattr(self, '_last_log_time'):
                    if time.time() - self._last_log_time > 3600:  # Log every hour
                        print(f"Memory stats - System: {memory.percent:.1f}%, Process: {process_memory:.1f}MB")
                        self._last_log_time = time.time()
                else:
                    self._last_log_time = time.time()
                
            except Exception as e:
                print(f"Memory monitoring error: {e}")
            
            time.sleep(self.monitor_interval)
    
    def cleanup_memory(self):
        """Perform memory cleanup operations."""
        print("Performing memory cleanup...")
        
        # Force garbage collection
        collected = gc.collect()
        print(f"Garbage collection freed {collected} objects")
        
        # Clear any application caches if they exist
        try:
            # This would clear your application-specific caches
            # cache.clear()  # Uncomment if using caching
            pass
        except Exception as e:
            print(f"Cache cleanup error: {e}")
    
    def start_monitoring(self):
        """Start memory monitoring in background thread."""
        self.configure_gc()
        
        monitor_thread = threading.Thread(target=self.monitor_memory, daemon=True)
        monitor_thread.start()
        
        print("Memory optimization and monitoring started")
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self.running = False

# Global memory optimizer instance
memory_optimizer = MemoryOptimizer()

def initialize_memory_optimization():
    """Initialize memory optimization for the application."""
    memory_optimizer.start_monitoring()
EOF

log_memory "Memory optimization module created"

# 6. Test memory optimization
log_memory "Testing memory optimization..."

# Run memory analysis
python3 /opt/cvd/scripts/memory_monitor.py | while read line; do
    log_memory "$line"
done

# Restart CVD service with new memory settings
log_memory "Restarting CVD service with memory optimizations..."
sudo systemctl restart cvd

# Wait for service to start
sleep 20

# Verify service is running
if systemctl is-active cvd >/dev/null; then
    NEW_MEMORY=$(ps aux | grep -E "(gunicorn|python.*app)" | grep -v grep | awk '{sum += $6} END {print sum/1024 " MB"}')
    log_memory "Service restarted - New memory usage: $NEW_MEMORY"
    
    # Test application response
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:5000/health)
    log_memory "Response time after optimization: ${RESPONSE_TIME}s"
else
    log_memory "ERROR: Service failed to start with memory optimizations"
    exit 1
fi

log_memory "Memory optimization completed successfully"
echo "Memory optimization applied. Monitor with: python3 /opt/cvd/scripts/memory_monitor.py"
```

### CPU and I/O Optimization

```bash
#!/bin/bash
echo "=== CVD CPU AND I/O OPTIMIZATION ==="

LOG_FILE="/opt/cvd/logs/cpu_io_optimization.log"

log_cpu_io() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_cpu_io "Starting CPU and I/O optimization..."

# 1. Analyze current CPU and I/O performance
log_cpu_io "=== Current Performance Analysis ==="

# CPU information
CPU_CORES=$(nproc)
CPU_MODEL=$(grep "model name" /proc/cpuinfo | head -n1 | cut -d: -f2 | xargs)
log_cpu_io "CPU: $CPU_MODEL ($CPU_CORES cores)"

# Current load average
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')
log_cpu_io "Load average:$LOAD_AVG"

# I/O statistics
if command -v iostat >/dev/null 2>&1; then
    IO_STATS=$(iostat -x 1 1 | grep -A 20 "Device")
    log_cpu_io "I/O statistics:"
    echo "$IO_STATS" | while read line; do
        log_cpu_io "  $line"
    done
fi

# 2. CPU optimization
log_cpu_io "=== CPU Optimization ==="

# Set CPU governor for performance
if [ -f "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor" ]; then
    CURRENT_GOVERNOR=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
    log_cpu_io "Current CPU governor: $CURRENT_GOVERNOR"
    
    # Set to performance governor for better response times
    echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor >/dev/null
    log_cpu_io "CPU governor set to performance"
fi

# Optimize CPU affinity for CVD processes
log_cpu_io "Optimizing CPU affinity..."

# Create CPU affinity script
cat > /opt/cvd/scripts/cpu_affinity.sh << 'EOF'
#!/bin/bash
# Set CPU affinity for CVD processes

# Get CVD process PIDs
CVD_PIDS=$(ps aux | grep -E "(gunicorn|python.*app)" | grep -v grep | awk '{print $2}')

if [ -n "$CVD_PIDS" ]; then
    CPU_COUNT=$(nproc)
    
    # Distribute processes across all cores
    CPU_MASK="0-$((CPU_COUNT-1))"
    
    for pid in $CVD_PIDS; do
        if [ -d "/proc/$pid" ]; then
            taskset -cp $CPU_MASK $pid 2>/dev/null
            echo "Set CPU affinity for PID $pid to cores $CPU_MASK"
        fi
    done
else
    echo "No CVD processes found"
fi
EOF

chmod +x /opt/cvd/scripts/cpu_affinity.sh
/opt/cvd/scripts/cpu_affinity.sh | while read line; do log_cpu_io "$line"; done

# 3. I/O optimization
log_cpu_io "=== I/O Optimization ==="

# Optimize I/O scheduler
BLOCK_DEVICE=$(df /opt/cvd | tail -1 | awk '{print $1}' | sed 's/[0-9]*$//')
DEVICE_NAME=$(basename "$BLOCK_DEVICE")

if [ -f "/sys/block/$DEVICE_NAME/queue/scheduler" ]; then
    CURRENT_SCHEDULER=$(cat /sys/block/$DEVICE_NAME/queue/scheduler | grep -o '\[.*\]' | tr -d '[]')
    log_cpu_io "Current I/O scheduler: $CURRENT_SCHEDULER"
    
    # Set to deadline scheduler for better database performance
    echo deadline | sudo tee /sys/block/$DEVICE_NAME/queue/scheduler >/dev/null
    log_cpu_io "I/O scheduler set to deadline"
fi

# Optimize I/O queue depth
if [ -f "/sys/block/$DEVICE_NAME/queue/nr_requests" ]; then
    echo 256 | sudo tee /sys/block/$DEVICE_NAME/queue/nr_requests >/dev/null
    log_cpu_io "I/O queue depth set to 256"
fi

# 4. File system optimization
log_cpu_io "=== File System Optimization ==="

# Get file system type
FS_TYPE=$(df -T /opt/cvd | tail -1 | awk '{print $2}')
log_cpu_io "File system type: $FS_TYPE"

# Create optimized mount options
case "$FS_TYPE" in
    "ext4")
        MOUNT_OPTIONS="defaults,noatime,data=writeback,barrier=0,nobh,errors=remount-ro"
        ;;
    "xfs")
        MOUNT_OPTIONS="defaults,noatime,largeio,inode64,swalloc"
        ;;
    *)
        MOUNT_OPTIONS="defaults,noatime"
        ;;
esac

log_cpu_io "Recommended mount options for $FS_TYPE: $MOUNT_OPTIONS"

# 5. Database I/O optimization
log_cpu_io "=== Database I/O Optimization ==="

# Check if database is on SSD or HDD
DISK_INFO=$(lsblk -d -o NAME,ROTA | grep "$DEVICE_NAME")
if echo "$DISK_INFO" | grep -q " 0"; then
    STORAGE_TYPE="SSD"
    # SSD optimizations
    echo 1 | sudo tee /sys/block/$DEVICE_NAME/queue/rotational >/dev/null
    echo 0 | sudo tee /sys/block/$DEVICE_NAME/queue/add_random >/dev/null
else
    STORAGE_TYPE="HDD"
    # HDD optimizations
    echo 8 | sudo tee /sys/block/$DEVICE_NAME/queue/read_ahead_kb >/dev/null
fi

log_cpu_io "Storage type detected: $STORAGE_TYPE"

# SQLite-specific I/O optimization
cat > /opt/cvd/scripts/sqlite_io_optimization.py << 'EOF'
#!/usr/bin/env python3
"""
SQLite I/O Optimization
Apply I/O-specific optimizations to SQLite database.
"""

import sqlite3
import os

def optimize_sqlite_io(db_path):
    """Apply I/O optimizations to SQLite database."""
    print(f"Optimizing SQLite I/O for: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # I/O optimization pragmas
    optimizations = [
        ("synchronous", "NORMAL"),      # Balance between safety and speed
        ("journal_mode", "WAL"),        # Write-Ahead Logging for better concurrency
        ("wal_autocheckpoint", "1000"), # Checkpoint every 1000 pages
        ("cache_size", "-65536"),       # 64MB cache
        ("temp_store", "MEMORY"),       # Store temp tables in memory
        ("mmap_size", "268435456"),     # 256MB memory-mapped I/O
    ]
    
    current_settings = {}
    new_settings = {}
    
    for pragma, value in optimizations:
        # Get current value
        cursor.execute(f"PRAGMA {pragma};")
        current = cursor.fetchone()[0] if cursor.rowcount > 0 else "unknown"
        current_settings[pragma] = current
        
        # Set new value
        cursor.execute(f"PRAGMA {pragma} = {value};")
        
        # Verify new value
        cursor.execute(f"PRAGMA {pragma};")
        new_value = cursor.fetchone()[0]
        new_settings[pragma] = new_value
    
    conn.close()
    
    print("I/O Optimization Results:")
    for pragma in current_settings:
        print(f"  {pragma}: {current_settings[pragma]} -> {new_settings[pragma]}")
    
    return True

if __name__ == "__main__":
    db_path = "/opt/cvd/data/cvd.db"
    if os.path.exists(db_path):
        optimize_sqlite_io(db_path)
    else:
        print(f"Database not found: {db_path}")
EOF

chmod +x /opt/cvd/scripts/sqlite_io_optimization.py

# Apply SQLite I/O optimizations
sudo systemctl stop cvd
python3 /opt/cvd/scripts/sqlite_io_optimization.py | while read line; do log_cpu_io "$line"; done
sudo systemctl start cvd

# 6. Process priority optimization
log_cpu_io "=== Process Priority Optimization ==="

# Create process priority script
cat > /opt/cvd/scripts/process_priority.sh << 'EOF'
#!/bin/bash
# Optimize process priorities for CVD

# Get CVD process PIDs
CVD_PIDS=$(ps aux | grep -E "(gunicorn|python.*app)" | grep -v grep | awk '{print $2}')

if [ -n "$CVD_PIDS" ]; then
    for pid in $CVD_PIDS; do
        if [ -d "/proc/$pid" ]; then
            # Set higher priority (lower nice value)
            renice -n -5 $pid 2>/dev/null
            
            # Set I/O priority for better disk access
            ionice -c 1 -n 4 -p $pid 2>/dev/null
            
            echo "Optimized priority for PID $pid"
        fi
    done
else
    echo "No CVD processes found"
fi
EOF

chmod +x /opt/cvd/scripts/process_priority.sh
/opt/cvd/scripts/process_priority.sh | while read line; do log_cpu_io "$line"; done

# 7. Create performance monitoring script
log_cpu_io "Creating performance monitoring script..."

cat > /opt/cvd/scripts/performance_monitor.sh << 'EOF'
#!/bin/bash
# Monitor CPU and I/O performance for CVD

echo "=== CVD Performance Monitor ==="
echo "Timestamp: $(date)"

echo -e "\n=== CPU Usage ==="
top -bn1 | grep "Cpu(s)" | awk '{print "CPU Usage: " $2}'
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"

echo -e "\n=== CVD Process Performance ==="
ps aux --sort=-%cpu | grep -E "(gunicorn|python.*app)" | grep -v grep | head -5 | \
    awk '{printf "PID %s: CPU %.1f%% MEM %.1f%% CMD %s\n", $2, $3, $4, $11}'

echo -e "\n=== I/O Statistics ==="
if command -v iostat >/dev/null 2>&1; then
    iostat -x 1 1 | grep -A 5 "Device"
fi

echo -e "\n=== Database I/O ==="
lsof /opt/cvd/data/cvd.db 2>/dev/null | wc -l | xargs echo "Database connections:"

echo -e "\n=== Memory Usage ==="
free -h | grep -E "(Mem|Swap)"

echo -e "\n=== Network Connections ==="
netstat -an | grep :5000 | wc -l | xargs echo "Active connections:"

echo "=== End Performance Monitor ==="
EOF

chmod +x /opt/cvd/scripts/performance_monitor.sh

# 8. Test performance optimization
log_cpu_io "Testing performance optimization..."

# Wait for service to stabilize
sleep 30

# Run performance test
/opt/cvd/scripts/performance_monitor.sh | while read line; do log_cpu_io "$line"; done

# Test application response times
log_cpu_io "Testing application response times..."
for i in {1..5}; do
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:5000/health)
    log_cpu_io "Response time test $i: ${RESPONSE_TIME}s"
done

log_cpu_io "CPU and I/O optimization completed successfully"
echo "Performance monitoring available at: /opt/cvd/scripts/performance_monitor.sh"
```

## Scaling and Load Management

### Load Testing and Capacity Planning

```bash
#!/bin/bash
echo "=== CVD LOAD TESTING AND CAPACITY PLANNING ==="

LOG_FILE="/opt/cvd/logs/load_testing.log"

log_load() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_load "Starting load testing and capacity planning..."

# Install load testing tools if not available
if ! command -v ab >/dev/null 2>&1; then
    log_load "Installing Apache Bench for load testing..."
    sudo apt-get update && sudo apt-get install -y apache2-utils
fi

# Create load testing script
cat > /opt/cvd/scripts/load_test.sh << 'EOF'
#!/bin/bash
# CVD Load Testing Script

TEST_URL="http://localhost:5000/health"
RESULTS_DIR="/opt/cvd/logs/load_tests"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$RESULTS_DIR"

echo "=== CVD Load Testing ==="
echo "Target URL: $TEST_URL"
echo "Test started: $(date)"

# Test scenarios
declare -A test_scenarios=(
    ["light"]="10 50"      # 10 requests, 50 concurrent
    ["moderate"]="100 20"   # 100 requests, 20 concurrent
    ["heavy"]="500 50"      # 500 requests, 50 concurrent
    ["stress"]="1000 100"   # 1000 requests, 100 concurrent
)

for scenario in "${!test_scenarios[@]}"; do
    params=(${test_scenarios[$scenario]})
    requests=${params[0]}
    concurrency=${params[1]}
    
    echo -e "\n=== Running $scenario test ($requests requests, $concurrency concurrent) ==="
    
    # Record system state before test
    echo "Pre-test system state:" > "$RESULTS_DIR/${scenario}_${TIMESTAMP}.log"
    free -m >> "$RESULTS_DIR/${scenario}_${TIMESTAMP}.log"
    uptime >> "$RESULTS_DIR/${scenario}_${TIMESTAMP}.log"
    
    # Run load test
    ab -n "$requests" -c "$concurrency" -g "$RESULTS_DIR/${scenario}_${TIMESTAMP}.gnuplot" \
       -e "$RESULTS_DIR/${scenario}_${TIMESTAMP}.csv" \
       "$TEST_URL" > "$RESULTS_DIR/${scenario}_${TIMESTAMP}.txt" 2>&1
    
    # Record system state after test
    echo -e "\nPost-test system state:" >> "$RESULTS_DIR/${scenario}_${TIMESTAMP}.log"
    free -m >> "$RESULTS_DIR/${scenario}_${TIMESTAMP}.log"
    uptime >> "$RESULTS_DIR/${scenario}_${TIMESTAMP}.log"
    
    # Extract key metrics
    if [ -f "$RESULTS_DIR/${scenario}_${TIMESTAMP}.txt" ]; then
        echo "Results for $scenario test:"
        grep -E "(Requests per second|Time per request|Transfer rate)" "$RESULTS_DIR/${scenario}_${TIMESTAMP}.txt"
        grep -E "(failed|errors)" "$RESULTS_DIR/${scenario}_${TIMESTAMP}.txt" || echo "No errors detected"
    fi
    
    # Wait between tests
    sleep 30
done

echo -e "\n=== Load Testing Completed ==="
echo "Results saved in: $RESULTS_DIR"
EOF

chmod +x /opt/cvd/scripts/load_test.sh

# Run load tests
log_load "Executing load tests..."
/opt/cvd/scripts/load_test.sh | while read line; do log_load "$line"; done

# Analyze load test results
cat > /opt/cvd/scripts/analyze_load_test.py << 'EOF'
#!/usr/bin/env python3
"""
CVD Load Test Analysis
Analyze load test results and provide capacity recommendations.
"""

import os
import re
import glob
import statistics
from datetime import datetime

def parse_ab_results(file_path):
    """Parse Apache Bench results file."""
    results = {}
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract key metrics
    patterns = {
        'requests_per_second': r'Requests per second:\s+([0-9.]+)',
        'time_per_request_mean': r'Time per request:\s+([0-9.]+)',
        'time_per_request_concurrent': r'Time per request:\s+[0-9.]+.*\(mean, across all concurrent requests\)',
        'transfer_rate': r'Transfer rate:\s+([0-9.]+)',
        'failed_requests': r'Failed requests:\s+([0-9]+)',
        'total_requests': r'Complete requests:\s+([0-9]+)',
        'concurrency_level': r'Concurrency Level:\s+([0-9]+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            try:
                results[key] = float(match.group(1))
            except ValueError:
                results[key] = match.group(1)
    
    return results

def analyze_capacity():
    """Analyze load test results and provide capacity recommendations."""
    results_dir = "/opt/cvd/logs/load_tests"
    
    if not os.path.exists(results_dir):
        print("No load test results found")
        return
    
    # Find all result files
    result_files = glob.glob(f"{results_dir}/*_*.txt")
    
    if not result_files:
        print("No load test result files found")
        return
    
    print("=== CVD Load Test Analysis ===")
    print(f"Analyzed {len(result_files)} test results\n")
    
    scenario_results = {}
    
    for file_path in result_files:
        filename = os.path.basename(file_path)
        scenario = filename.split('_')[0]
        
        results = parse_ab_results(file_path)
        
        if scenario not in scenario_results:
            scenario_results[scenario] = []
        
        scenario_results[scenario].append(results)
    
    # Analyze results by scenario
    for scenario, tests in scenario_results.items():
        print(f"=== {scenario.upper()} Load Test Results ===")
        
        if not tests:
            continue
        
        # Average metrics across runs
        avg_rps = statistics.mean([t.get('requests_per_second', 0) for t in tests])
        avg_response_time = statistics.mean([t.get('time_per_request_mean', 0) for t in tests])
        total_failed = sum([t.get('failed_requests', 0) for t in tests])
        total_requests = sum([t.get('total_requests', 0) for t in tests])
        
        print(f"  Average Requests/Second: {avg_rps:.2f}")
        print(f"  Average Response Time: {avg_response_time:.2f} ms")
        print(f"  Failed Requests: {total_failed}/{total_requests}")
        print(f"  Success Rate: {((total_requests - total_failed) / total_requests * 100):.1f}%")
        
        # Performance assessment
        if avg_rps < 10:
            performance = "Poor"
        elif avg_rps < 50:
            performance = "Fair"
        elif avg_rps < 100:
            performance = "Good"
        else:
            performance = "Excellent"
        
        print(f"  Performance Rating: {performance}")
        print()
    
    # Capacity recommendations
    print("=== Capacity Planning Recommendations ===")
    
    # Estimate concurrent user capacity
    best_rps = max([statistics.mean([t.get('requests_per_second', 0) for t in tests]) 
                    for tests in scenario_results.values() if tests])
    
    # Assume each user makes 1 request every 30 seconds
    estimated_users = int(best_rps * 30)
    
    print(f"Estimated concurrent user capacity: ~{estimated_users} users")
    print(f"Peak requests per second: {best_rps:.1f}")
    
    # Resource recommendations
    if best_rps < 20:
        print("\nRecommendations:")
        print("- Consider increasing Gunicorn worker count")
        print("- Implement caching to reduce database load")
        print("- Optimize database queries and indexes")
    elif best_rps < 50:
        print("\nRecommendations:")
        print("- Current performance is adequate for small to medium loads")
        print("- Monitor memory usage during peak times")
        print("- Consider load balancing for higher availability")
    else:
        print("\nRecommendations:")
        print("- Performance is good for current architecture")
        print("- Monitor for sustained load scenarios")
        print("- Plan for horizontal scaling if growth continues")

if __name__ == "__main__":
    analyze_capacity()
EOF

chmod +x /opt/cvd/scripts/analyze_load_test.py

# Analyze results
log_load "Analyzing load test results..."
python3 /opt/cvd/scripts/analyze_load_test.py | while read line; do log_load "$line"; done

log_load "Load testing and capacity planning completed"
```

---

**Runbook Version**: 1.0  
**Last Updated**: 2024-01-01  
**Next Review Date**: 2024-04-01  
**Owner**: DevOps Team  
**Approver**: Operations Manager

**Performance Targets:**
- API Response Time: <500ms (95th percentile)
- Database Query Time: <100ms (95th percentile)
- Memory Usage: <80%
- CPU Usage: <70% (sustained)

**Monitoring Schedule:**
- Performance baseline: Monthly
- Load testing: Quarterly
- Resource optimization: As needed