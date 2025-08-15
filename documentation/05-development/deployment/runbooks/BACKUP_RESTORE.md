# CVD Backup and Restore Runbook


## Metadata
- **ID**: 05_DEVELOPMENT_DEPLOYMENT_RUNBOOKS_BACKUP_RESTORE
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #coding #data-layer #database #debugging #development #device-management #integration #machine-learning #operations #optimization #quality-assurance #service-orders #testing #troubleshooting #vending-machine #workflows
- **Intent**: This runbook provides comprehensive procedures for backing up and restoring the CVD (Vision Device Configuration) system
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/deployment/runbooks/
- **Category**: Runbooks
- **Search Keywords**: .db, 1.0, 2024-01-01, 2024-04-01, _\([0-9]\{8\}_[0-9]\{6\}\)., application, approver, backup, configuration, cvd, database, date, device, full, last

## Overview

This runbook provides comprehensive procedures for backing up and restoring the CVD (Vision Device Configuration) system. It covers database backups, application code backups, configuration backups, and complete system recovery procedures.

### Scope
- SQLite database backup and restore
- Application code and configuration backup
- Full system backup and recovery
- Automated backup verification
- Disaster recovery procedures

### Backup Schedule
- **Database**: Every 2 hours (automated)
- **Application**: Daily at 2 AM (automated)
- **Configuration**: After every change (manual)
- **Full System**: Weekly (automated)

## Backup Procedures

### Database Backup

#### Manual Database Backup

```bash
#!/bin/bash
echo "=== CVD DATABASE BACKUP ==="

# Set variables
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATABASE_PATH="/opt/cvd/data/cvd.db"
BACKUP_DIR="/opt/cvd/backups"
BACKUP_FILE="${BACKUP_DIR}/cvd_backup_${TIMESTAMP}.db"
LOG_FILE="/opt/cvd/logs/backup.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting database backup..."

# Verify source database exists and is accessible
if [ ! -f "$DATABASE_PATH" ]; then
    log_message "ERROR: Source database not found: $DATABASE_PATH"
    exit 1
fi

# Check if database is locked
if lsof "$DATABASE_PATH" >/dev/null 2>&1; then
    log_message "WARNING: Database has active connections - backup may be inconsistent"
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create SQLite backup using .backup command (online backup)
log_message "Creating database backup: $BACKUP_FILE"
if sqlite3 "$DATABASE_PATH" ".backup $BACKUP_FILE"; then
    log_message "Database backup created successfully"
else
    log_message "ERROR: Database backup failed"
    exit 1
fi

# Verify backup integrity
log_message "Verifying backup integrity..."
if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
    log_message "Backup integrity verified successfully"
else
    log_message "ERROR: Backup integrity check failed"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Get backup size and record count for verification
BACKUP_SIZE=$(stat -c%s "$BACKUP_FILE")
RECORD_COUNT=$(sqlite3 "$BACKUP_FILE" "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")

log_message "Backup completed - Size: $(($BACKUP_SIZE / 1024))KB, User records: $RECORD_COUNT"

# Compress backup to save space
gzip "$BACKUP_FILE"
log_message "Backup compressed: ${BACKUP_FILE}.gz"

echo "Database backup completed successfully"
```

#### Automated Database Backup Script

```bash
#!/bin/bash
# Automated database backup with rotation

BACKUP_DIR="/opt/cvd/backups"
DATABASE_PATH="/opt/cvd/data/cvd.db"
RETENTION_DAYS=30
MAX_BACKUPS=200

# Lock file to prevent overlapping backups
LOCK_FILE="/tmp/cvd_backup.lock"
if [ -f "$LOCK_FILE" ]; then
    echo "Backup already running (lock file exists)"
    exit 1
fi
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/cvd_auto_${TIMESTAMP}.db"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Create backup with error handling
if sqlite3 "$DATABASE_PATH" ".backup $BACKUP_FILE" 2>/dev/null; then
    # Verify backup
    if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" 2>/dev/null | grep -q "ok"; then
        # Compress backup
        gzip "$BACKUP_FILE"
        
        # Log success
        echo "$(date): Automated backup successful - ${BACKUP_FILE}.gz" >> /opt/cvd/logs/backup.log
        
        # Cleanup old backups
        find "$BACKUP_DIR" -name "cvd_auto_*.db.gz" -mtime +$RETENTION_DAYS -delete
        
        # Limit total number of backups
        ls -t "$BACKUP_DIR"/cvd_auto_*.db.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f 2>/dev/null
        
    else
        # Remove corrupted backup
        rm -f "$BACKUP_FILE"
        echo "$(date): ERROR - Backup integrity check failed" >> /opt/cvd/logs/backup.log
        exit 1
    fi
else
    echo "$(date): ERROR - Backup creation failed" >> /opt/cvd/logs/backup.log
    exit 1
fi
```

### Application Backup

#### Complete Application Backup

```bash
#!/bin/bash
echo "=== CVD APPLICATION BACKUP ==="

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/cvd/backups/app"
APP_BACKUP="${BACKUP_DIR}/cvd_app_${TIMESTAMP}.tar.gz"
CONFIG_BACKUP="${BACKUP_DIR}/cvd_config_${TIMESTAMP}.tar.gz"
LOG_FILE="/opt/cvd/logs/backup.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting application backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup application code (excluding venv and cache)
log_message "Backing up application code..."
tar -czf "$APP_BACKUP" \
    -C /opt/cvd/app \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='ai_cache.db' \
    . 2>/dev/null

if [ $? -eq 0 ]; then
    log_message "Application code backup completed: $APP_BACKUP"
else
    log_message "ERROR: Application code backup failed"
    exit 1
fi

# Backup configuration files
log_message "Backing up configuration..."
tar -czf "$CONFIG_BACKUP" \
    -C /opt/cvd \
    config/ \
    2>/dev/null

if [ $? -eq 0 ]; then
    log_message "Configuration backup completed: $CONFIG_BACKUP"
else
    log_message "ERROR: Configuration backup failed"
fi

# Backup system service files
SYSTEMD_BACKUP="${BACKUP_DIR}/cvd_systemd_${TIMESTAMP}.tar.gz"
tar -czf "$SYSTEMD_BACKUP" \
    -C /etc/systemd/system \
    cvd.service \
    2>/dev/null && log_message "Systemd service backup completed"

# Record current git version
cd /opt/cvd/app
if [ -d ".git" ]; then
    GIT_VERSION=$(git rev-parse HEAD 2>/dev/null)
    echo "$GIT_VERSION" > "${BACKUP_DIR}/git_version_${TIMESTAMP}.txt"
    log_message "Git version recorded: $GIT_VERSION"
fi

# Get backup sizes for verification
APP_SIZE=$(stat -c%s "$APP_BACKUP" 2>/dev/null | awk '{print int($1/1024/1024)"MB"}')
CONFIG_SIZE=$(stat -c%s "$CONFIG_BACKUP" 2>/dev/null | awk '{print int($1/1024/1024)"MB"}')

log_message "Application backup completed - App: $APP_SIZE, Config: $CONFIG_SIZE"

# Cleanup old application backups (keep last 14 days)
find "$BACKUP_DIR" -name "cvd_app_*.tar.gz" -mtime +14 -delete
find "$BACKUP_DIR" -name "cvd_config_*.tar.gz" -mtime +14 -delete

echo "Application backup completed successfully"
```

### Full System Backup

#### Complete System State Backup

```bash
#!/bin/bash
echo "=== CVD FULL SYSTEM BACKUP ==="

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_ROOT="/opt/cvd/backups/system"
SYSTEM_BACKUP="${BACKUP_ROOT}/cvd_system_${TIMESTAMP}"
LOG_FILE="/opt/cvd/logs/system_backup.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting full system backup..."

# Create backup directory structure
mkdir -p "$SYSTEM_BACKUP"/{database,application,config,system}

# 1. Database backup
log_message "Backing up database..."
sqlite3 /opt/cvd/data/cvd.db ".backup ${SYSTEM_BACKUP}/database/cvd.db"
gzip "${SYSTEM_BACKUP}/database/cvd.db"

# 2. Application backup
log_message "Backing up application..."
tar -czf "${SYSTEM_BACKUP}/application/app.tar.gz" \
    -C /opt/cvd/app \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    . 2>/dev/null

# 3. Configuration backup
log_message "Backing up configuration..."
# Application config
cp -r /opt/cvd/config "${SYSTEM_BACKUP}/config/"
# Nginx config
cp /etc/nginx/sites-available/cvd "${SYSTEM_BACKUP}/config/nginx-cvd.conf" 2>/dev/null
# Systemd service
cp /etc/systemd/system/cvd.service "${SYSTEM_BACKUP}/config/" 2>/dev/null

# 4. System information backup
log_message "Collecting system information..."
{
    echo "=== System Information ==="
    uname -a
    cat /etc/os-release
    
    echo -e "\n=== Installed Packages ==="
    dpkg -l | grep -E "(python|nginx|sqlite)" 2>/dev/null || rpm -qa | grep -E "(python|nginx|sqlite)"
    
    echo -e "\n=== System Services ==="
    systemctl status cvd --no-pager
    systemctl status nginx --no-pager
    
    echo -e "\n=== Network Configuration ==="
    ip addr show
    
    echo -e "\n=== Disk Usage ==="
    df -h
    
    echo -e "\n=== Memory Info ==="
    free -h
    
    echo -e "\n=== Current Processes ==="
    ps aux | grep -E "(python|nginx|gunicorn)" | grep -v grep
    
} > "${SYSTEM_BACKUP}/system/system_info.txt"

# 5. Create backup manifest
log_message "Creating backup manifest..."
{
    echo "CVD System Backup Manifest"
    echo "=========================="
    echo "Backup Date: $(date)"
    echo "Backup ID: $TIMESTAMP"
    echo "Hostname: $(hostname)"
    echo "System: $(uname -a)"
    echo ""
    echo "Backup Contents:"
    find "$SYSTEM_BACKUP" -type f -exec ls -lh {} \; | awk '{print $9 " (" $5 ")"}'
    echo ""
    echo "Database Record Counts:"
    sqlite3 /opt/cvd/data/cvd.db "SELECT 'Users: ' || COUNT(*) FROM users;" 2>/dev/null || echo "Users: Unable to count"
    sqlite3 /opt/cvd/data/cvd.db "SELECT 'Devices: ' || COUNT(*) FROM devices;" 2>/dev/null || echo "Devices: Unable to count"
    sqlite3 /opt/cvd/data/cvd.db "SELECT 'Service Orders: ' || COUNT(*) FROM service_orders;" 2>/dev/null || echo "Service Orders: Unable to count"
} > "${SYSTEM_BACKUP}/MANIFEST.txt"

# 6. Compress entire system backup
log_message "Compressing system backup..."
tar -czf "${BACKUP_ROOT}/cvd_system_${TIMESTAMP}.tar.gz" -C "$BACKUP_ROOT" "cvd_system_${TIMESTAMP}"
rm -rf "$SYSTEM_BACKUP"

# Verify compressed backup
if [ -f "${BACKUP_ROOT}/cvd_system_${TIMESTAMP}.tar.gz" ]; then
    BACKUP_SIZE=$(stat -c%s "${BACKUP_ROOT}/cvd_system_${TIMESTAMP}.tar.gz" | awk '{print int($1/1024/1024)"MB"}')
    log_message "System backup completed: cvd_system_${TIMESTAMP}.tar.gz ($BACKUP_SIZE)"
else
    log_message "ERROR: System backup failed"
    exit 1
fi

# Cleanup old system backups (keep last 4 weeks)
find "$BACKUP_ROOT" -name "cvd_system_*.tar.gz" -mtime +28 -delete

echo "Full system backup completed successfully"
```

## Restore Procedures

### Database Restore

#### Single Database Restore

```bash
#!/bin/bash
echo "=== CVD DATABASE RESTORE ==="

# Usage: ./restore_database.sh <backup_file>
BACKUP_FILE="$1"
DATABASE_PATH="/opt/cvd/data/cvd.db"
LOG_FILE="/opt/cvd/logs/restore.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Validate input
if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -la /opt/cvd/backups/*.db* 2>/dev/null | tail -n 10
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    log_message "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

log_message "Starting database restore from: $BACKUP_FILE"

# Create safety backup of current database
SAFETY_BACKUP="/opt/cvd/data/cvd.db.pre-restore.$(date +%Y%m%d_%H%M%S)"
if [ -f "$DATABASE_PATH" ]; then
    log_message "Creating safety backup: $SAFETY_BACKUP"
    cp "$DATABASE_PATH" "$SAFETY_BACKUP"
fi

# Stop application service
log_message "Stopping CVD service..."
sudo systemctl stop cvd

# Extract backup if compressed
RESTORE_FILE="$BACKUP_FILE"
if [[ "$BACKUP_FILE" == *.gz ]]; then
    RESTORE_FILE="/tmp/restore_$(basename "$BACKUP_FILE" .gz)"
    log_message "Extracting compressed backup..."
    gunzip -c "$BACKUP_FILE" > "$RESTORE_FILE"
fi

# Verify backup integrity before restore
log_message "Verifying backup integrity..."
if sqlite3 "$RESTORE_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
    log_message "Backup integrity verified"
else
    log_message "ERROR: Backup integrity check failed"
    sudo systemctl start cvd
    exit 1
fi

# Perform restore
log_message "Restoring database..."
cp "$RESTORE_FILE" "$DATABASE_PATH"

# Set correct permissions
chown cvdapp:www-data "$DATABASE_PATH"
chmod 644 "$DATABASE_PATH"

# Verify restored database
log_message "Verifying restored database..."
if sqlite3 "$DATABASE_PATH" "PRAGMA integrity_check;" | grep -q "ok"; then
    log_message "Database restore verification successful"
else
    log_message "ERROR: Restored database failed verification"
    
    # Restore original database
    if [ -f "$SAFETY_BACKUP" ]; then
        cp "$SAFETY_BACKUP" "$DATABASE_PATH"
        log_message "Original database restored due to verification failure"
    fi
    
    sudo systemctl start cvd
    exit 1
fi

# Start application service
log_message "Starting CVD service..."
sudo systemctl start cvd

# Wait for service to start
sleep 10

# Test application functionality
if systemctl is-active cvd >/dev/null && curl -f http://localhost:5000/health >/dev/null 2>&1; then
    log_message "Service started successfully and health check passed"
    
    # Log record counts for verification
    USER_COUNT=$(sqlite3 "$DATABASE_PATH" "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
    DEVICE_COUNT=$(sqlite3 "$DATABASE_PATH" "SELECT COUNT(*) FROM devices;" 2>/dev/null || echo "0")
    log_message "Restored database contains: $USER_COUNT users, $DEVICE_COUNT devices"
    
    echo "Database restore completed successfully"
else
    log_message "ERROR: Service failed to start or health check failed after restore"
    
    # Restore original database
    if [ -f "$SAFETY_BACKUP" ]; then
        sudo systemctl stop cvd
        cp "$SAFETY_BACKUP" "$DATABASE_PATH"
        sudo systemctl start cvd
        log_message "Original database restored due to service failure"
    fi
    
    exit 1
fi

# Cleanup
if [ "$RESTORE_FILE" != "$BACKUP_FILE" ]; then
    rm -f "$RESTORE_FILE"
fi

echo "Database restore completed successfully"
```

#### Point-in-Time Database Recovery

```bash
#!/bin/bash
echo "=== CVD POINT-IN-TIME RECOVERY ==="

# Usage: ./pit_recovery.sh "2024-01-01 12:00:00"
TARGET_TIME="$1"
BACKUP_DIR="/opt/cvd/backups"
LOG_FILE="/opt/cvd/logs/pit_recovery.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

if [ -z "$TARGET_TIME" ]; then
    echo "Usage: $0 \"YYYY-MM-DD HH:MM:SS\""
    echo "Available backup timeframes:"
    ls -la "$BACKUP_DIR"/*.db* | awk '{print $6, $7, $8, $9}' | tail -n 10
    exit 1
fi

log_message "Starting point-in-time recovery to: $TARGET_TIME"

# Convert target time to epoch for comparison
TARGET_EPOCH=$(date -d "$TARGET_TIME" +%s 2>/dev/null)
if [ $? -ne 0 ]; then
    log_message "ERROR: Invalid date format"
    exit 1
fi

# Find the most recent backup before target time
BEST_BACKUP=""
BEST_EPOCH=0

for backup in $(ls -1 "$BACKUP_DIR"/cvd_*_*.db* 2>/dev/null | sort); do
    # Extract timestamp from filename (format: cvd_backup_YYYYMMDD_HHMMSS.db)
    BACKUP_TIMESTAMP=$(basename "$backup" | sed 's/.*_\([0-9]\{8\}_[0-9]\{6\}\).*/\1/')
    
    # Convert to readable format
    BACKUP_DATE="${BACKUP_TIMESTAMP:0:8}"
    BACKUP_TIME="${BACKUP_TIMESTAMP:9:6}"
    BACKUP_READABLE="${BACKUP_DATE:0:4}-${BACKUP_DATE:4:2}-${BACKUP_DATE:6:2} ${BACKUP_TIME:0:2}:${BACKUP_TIME:2:2}:${BACKUP_TIME:4:2}"
    
    BACKUP_EPOCH=$(date -d "$BACKUP_READABLE" +%s 2>/dev/null)
    
    if [ $? -eq 0 ] && [ "$BACKUP_EPOCH" -le "$TARGET_EPOCH" ] && [ "$BACKUP_EPOCH" -gt "$BEST_EPOCH" ]; then
        BEST_BACKUP="$backup"
        BEST_EPOCH="$BACKUP_EPOCH"
    fi
done

if [ -z "$BEST_BACKUP" ]; then
    log_message "ERROR: No suitable backup found for target time $TARGET_TIME"
    exit 1
fi

BEST_READABLE=$(date -d "@$BEST_EPOCH" '+%Y-%m-%d %H:%M:%S')
log_message "Selected backup: $BEST_BACKUP (created: $BEST_READABLE)"

# Confirm the recovery
echo "WARNING: This will restore the database to $BEST_READABLE"
echo "Current data after this time will be lost!"
echo -n "Continue? (yes/NO): "
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_message "Point-in-time recovery cancelled by user"
    exit 0
fi

# Perform the restore using the database restore script
log_message "Executing database restore..."
./restore_database.sh "$BEST_BACKUP"

if [ $? -eq 0 ]; then
    log_message "Point-in-time recovery completed successfully"
    echo "Database restored to state as of: $BEST_READABLE"
else
    log_message "ERROR: Point-in-time recovery failed"
    exit 1
fi
```

### Application Restore

#### Complete Application Restore

```bash
#!/bin/bash
echo "=== CVD APPLICATION RESTORE ==="

# Usage: ./restore_application.sh <backup_file>
BACKUP_FILE="$1"
RESTORE_DIR="/opt/cvd/app"
LOG_FILE="/opt/cvd/logs/restore.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available application backups:"
    ls -la /opt/cvd/backups/app/cvd_app_*.tar.gz 2>/dev/null | tail -n 5
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    log_message "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

log_message "Starting application restore from: $BACKUP_FILE"

# Create safety backup of current application
SAFETY_BACKUP="/opt/cvd/backups/app/current_app_$(date +%Y%m%d_%H%M%S).tar.gz"
log_message "Creating safety backup of current application..."
tar -czf "$SAFETY_BACKUP" -C "$RESTORE_DIR" . 2>/dev/null

# Stop application service
log_message "Stopping CVD service..."
sudo systemctl stop cvd

# Create temporary restore directory
TEMP_RESTORE="/tmp/cvd_restore_$$"
mkdir -p "$TEMP_RESTORE"

# Extract backup
log_message "Extracting application backup..."
if tar -xzf "$BACKUP_FILE" -C "$TEMP_RESTORE"; then
    log_message "Backup extracted successfully"
else
    log_message "ERROR: Failed to extract backup"
    sudo systemctl start cvd
    rm -rf "$TEMP_RESTORE"
    exit 1
fi

# Backup current virtual environment and important runtime files
log_message "Preserving runtime environment..."
if [ -d "$RESTORE_DIR/venv" ]; then
    mv "$RESTORE_DIR/venv" "$TEMP_RESTORE/venv_current"
fi

# Restore application files
log_message "Restoring application files..."
rm -rf "$RESTORE_DIR"/*
cp -r "$TEMP_RESTORE"/* "$RESTORE_DIR/"

# Restore virtual environment if it was preserved
if [ -d "$TEMP_RESTORE/venv_current" ]; then
    mv "$TEMP_RESTORE/venv_current" "$RESTORE_DIR/venv"
    log_message "Virtual environment preserved"
else
    # Create new virtual environment
    log_message "Creating new virtual environment..."
    cd "$RESTORE_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Set correct permissions
chown -R cvdapp:www-data "$RESTORE_DIR"
chmod +x "$RESTORE_DIR/app.py"

# Start application service
log_message "Starting CVD service..."
sudo systemctl start cvd

# Wait for service to start and test
sleep 15

if systemctl is-active cvd >/dev/null && curl -f http://localhost:5000/health >/dev/null 2>&1; then
    log_message "Application restore completed successfully"
    echo "Application restored and running"
else
    log_message "ERROR: Application failed to start after restore"
    
    # Rollback to safety backup
    log_message "Rolling back to previous version..."
    sudo systemctl stop cvd
    rm -rf "$RESTORE_DIR"/*
    tar -xzf "$SAFETY_BACKUP" -C "$RESTORE_DIR"
    chown -R cvdapp:www-data "$RESTORE_DIR"
    sudo systemctl start cvd
    
    log_message "Rollback completed"
    exit 1
fi

# Cleanup
rm -rf "$TEMP_RESTORE"

echo "Application restore completed successfully"
```

### Full System Recovery

#### Disaster Recovery from System Backup

```bash
#!/bin/bash
echo "=== CVD DISASTER RECOVERY ==="

BACKUP_FILE="$1"
LOG_FILE="/opt/cvd/logs/disaster_recovery.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <system_backup_file>"
    echo "Available system backups:"
    ls -la /opt/cvd/backups/system/cvd_system_*.tar.gz 2>/dev/null | tail -n 5
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    log_message "ERROR: System backup file not found: $BACKUP_FILE"
    exit 1
fi

log_message "=== STARTING DISASTER RECOVERY ==="
log_message "Backup file: $BACKUP_FILE"
log_message "Recovery initiated by: $USER"

# Warn about the operation
echo "WARNING: This will completely restore the CVD system from backup"
echo "All current data and configuration will be replaced!"
echo -n "Continue with disaster recovery? (yes/NO): "
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_message "Disaster recovery cancelled by user"
    exit 0
fi

# Stop all services
log_message "Stopping all CVD services..."
sudo systemctl stop cvd
sudo systemctl stop nginx

# Extract system backup
TEMP_RESTORE="/tmp/cvd_disaster_recovery_$$"
mkdir -p "$TEMP_RESTORE"

log_message "Extracting system backup..."
if tar -xzf "$BACKUP_FILE" -C "$TEMP_RESTORE"; then
    log_message "System backup extracted successfully"
else
    log_message "ERROR: Failed to extract system backup"
    exit 1
fi

# Find the backup directory (should be cvd_system_TIMESTAMP)
BACKUP_DIR=$(find "$TEMP_RESTORE" -maxdepth 1 -type d -name "cvd_system_*" | head -n1)
if [ -z "$BACKUP_DIR" ]; then
    log_message "ERROR: Could not find backup directory in archive"
    rm -rf "$TEMP_RESTORE"
    exit 1
fi

log_message "Found backup directory: $BACKUP_DIR"

# Display backup manifest
if [ -f "$BACKUP_DIR/MANIFEST.txt" ]; then
    log_message "Backup manifest:"
    cat "$BACKUP_DIR/MANIFEST.txt" | tee -a "$LOG_FILE"
fi

# 1. Restore Database
log_message "Restoring database..."
if [ -f "$BACKUP_DIR/database/cvd.db.gz" ]; then
    gunzip -c "$BACKUP_DIR/database/cvd.db.gz" > /opt/cvd/data/cvd.db
    chown cvdapp:www-data /opt/cvd/data/cvd.db
    chmod 644 /opt/cvd/data/cvd.db
    log_message "Database restored"
else
    log_message "ERROR: Database backup not found in system backup"
    exit 1
fi

# 2. Restore Application
log_message "Restoring application..."
if [ -f "$BACKUP_DIR/application/app.tar.gz" ]; then
    rm -rf /opt/cvd/app/*
    tar -xzf "$BACKUP_DIR/application/app.tar.gz" -C /opt/cvd/app/
    
    # Recreate virtual environment
    cd /opt/cvd/app
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    chown -R cvdapp:www-data /opt/cvd/app
    chmod +x /opt/cvd/app/app.py
    log_message "Application restored"
else
    log_message "ERROR: Application backup not found in system backup"
    exit 1
fi

# 3. Restore Configuration
log_message "Restoring configuration..."
if [ -d "$BACKUP_DIR/config" ]; then
    # Application configuration
    if [ -d "$BACKUP_DIR/config/config" ]; then
        cp -r "$BACKUP_DIR/config/config"/* /opt/cvd/config/
        chown -R cvdapp:www-data /opt/cvd/config
    fi
    
    # Nginx configuration
    if [ -f "$BACKUP_DIR/config/nginx-cvd.conf" ]; then
        cp "$BACKUP_DIR/config/nginx-cvd.conf" /etc/nginx/sites-available/cvd
    fi
    
    # Systemd service
    if [ -f "$BACKUP_DIR/config/cvd.service" ]; then
        cp "$BACKUP_DIR/config/cvd.service" /etc/systemd/system/
        sudo systemctl daemon-reload
    fi
    
    log_message "Configuration restored"
fi

# 4. Verify system integrity
log_message "Verifying system integrity..."

# Check database integrity
if sqlite3 /opt/cvd/data/cvd.db "PRAGMA integrity_check;" | grep -q "ok"; then
    log_message "Database integrity verified"
else
    log_message "ERROR: Database integrity check failed"
    exit 1
fi

# Check application files
if [ -f "/opt/cvd/app/app.py" ] && [ -f "/opt/cvd/app/requirements.txt" ]; then
    log_message "Application files verified"
else
    log_message "ERROR: Critical application files missing"
    exit 1
fi

# 5. Start services
log_message "Starting services..."
sudo systemctl start nginx
sudo systemctl start cvd

# Wait for services to start
sleep 30

# 6. Verify system functionality
log_message "Verifying system functionality..."

# Check service status
if systemctl is-active cvd >/dev/null; then
    log_message "CVD service is running"
else
    log_message "ERROR: CVD service failed to start"
    exit 1
fi

if systemctl is-active nginx >/dev/null; then
    log_message "Nginx service is running"
else
    log_message "ERROR: Nginx service failed to start"
    exit 1
fi

# Check application health
if curl -f http://localhost:5000/health >/dev/null 2>&1; then
    log_message "Application health check passed"
else
    log_message "ERROR: Application health check failed"
    exit 1
fi

# Check database connectivity
USER_COUNT=$(sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
DEVICE_COUNT=$(sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM devices;" 2>/dev/null || echo "0")
log_message "Database connectivity verified - Users: $USER_COUNT, Devices: $DEVICE_COUNT"

# Cleanup
rm -rf "$TEMP_RESTORE"

log_message "=== DISASTER RECOVERY COMPLETED SUCCESSFULLY ==="
echo "System has been fully restored from backup"
echo "Please verify all functionality and update any time-sensitive configurations"

# Final system status
echo ""
echo "System Status:"
echo "- CVD Service: $(systemctl is-active cvd)"
echo "- Nginx Service: $(systemctl is-active nginx)"
echo "- Database Records: $USER_COUNT users, $DEVICE_COUNT devices"
echo "- Recovery completed at: $(date)"
```

## Backup Verification

### Automated Backup Testing

```bash
#!/bin/bash
echo "=== CVD BACKUP VERIFICATION ==="

BACKUP_DIR="/opt/cvd/backups"
LOG_FILE="/opt/cvd/logs/backup_verification.log"
TEST_DB="/tmp/backup_test_$$.db"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting backup verification process..."

# Test all recent backups
for backup in $(ls -t "$BACKUP_DIR"/*.db* 2>/dev/null | head -n 5); do
    log_message "Testing backup: $backup"
    
    # Extract if compressed
    if [[ "$backup" == *.gz ]]; then
        gunzip -c "$backup" > "$TEST_DB"
    else
        cp "$backup" "$TEST_DB"
    fi
    
    # Test database integrity
    if sqlite3 "$TEST_DB" "PRAGMA integrity_check;" | grep -q "ok"; then
        log_message "✅ Integrity check passed: $(basename "$backup")"
    else
        log_message "❌ Integrity check failed: $(basename "$backup")"
        continue
    fi
    
    # Test basic queries
    USER_COUNT=$(sqlite3 "$TEST_DB" "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "ERROR")
    DEVICE_COUNT=$(sqlite3 "$TEST_DB" "SELECT COUNT(*) FROM devices;" 2>/dev/null || echo "ERROR")
    
    if [ "$USER_COUNT" = "ERROR" ] || [ "$DEVICE_COUNT" = "ERROR" ]; then
        log_message "❌ Query test failed: $(basename "$backup")"
    else
        log_message "✅ Query test passed: $(basename "$backup") - Users: $USER_COUNT, Devices: $DEVICE_COUNT"
    fi
    
    # Clean up test database
    rm -f "$TEST_DB"
done

log_message "Backup verification completed"
```

## Backup Maintenance

### Backup Cleanup and Rotation

```bash
#!/bin/bash
echo "=== CVD BACKUP MAINTENANCE ==="

BACKUP_DIR="/opt/cvd/backups"
LOG_FILE="/opt/cvd/logs/backup_maintenance.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting backup maintenance..."

# Count backups by type
DB_COUNT=$(ls -1 "$BACKUP_DIR"/*.db* 2>/dev/null | wc -l)
APP_COUNT=$(ls -1 "$BACKUP_DIR/app"/*.tar.gz 2>/dev/null | wc -l)
SYSTEM_COUNT=$(ls -1 "$BACKUP_DIR/system"/*.tar.gz 2>/dev/null | wc -l)

log_message "Current backup counts - Database: $DB_COUNT, Application: $APP_COUNT, System: $SYSTEM_COUNT"

# Database backup cleanup (keep 30 days, max 200 files)
log_message "Cleaning up database backups..."
find "$BACKUP_DIR" -name "*.db*" -mtime +30 -type f -delete
ls -t "$BACKUP_DIR"/*.db* 2>/dev/null | tail -n +201 | xargs rm -f 2>/dev/null

# Application backup cleanup (keep 14 days)
log_message "Cleaning up application backups..."
find "$BACKUP_DIR/app" -name "*.tar.gz" -mtime +14 -type f -delete

# System backup cleanup (keep 28 days)
log_message "Cleaning up system backups..."
find "$BACKUP_DIR/system" -name "*.tar.gz" -mtime +28 -type f -delete

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
log_message "Total backup storage usage: $TOTAL_SIZE"

# Verify backup directory permissions
chown -R cvdapp:www-data "$BACKUP_DIR"
find "$BACKUP_DIR" -type d -exec chmod 755 {} \;
find "$BACKUP_DIR" -type f -exec chmod 644 {} \;

log_message "Backup maintenance completed"
```

## Monitoring and Alerting

### Backup Monitoring Script

```bash
#!/bin/bash
# Monitor backup health and send alerts if issues detected

BACKUP_DIR="/opt/cvd/backups"
ALERT_EMAIL="ops@company.com"
BACKUP_LOG="/opt/cvd/logs/backup.log"

# Check if recent backup exists (within 4 hours)
RECENT_BACKUP=$(find "$BACKUP_DIR" -name "cvd_auto_*.db.gz" -mmin -240 | head -n1)

if [ -z "$RECENT_BACKUP" ]; then
    echo "ALERT: No recent CVD database backup found" | \
        mail -s "CVD Backup Alert - No Recent Backup" "$ALERT_EMAIL" 2>/dev/null
    
    echo "$(date): ALERT - No recent backup found" >> "$BACKUP_LOG"
    exit 1
fi

# Check backup log for errors
if grep -q "ERROR" "$BACKUP_LOG"; then
    RECENT_ERRORS=$(grep "ERROR" "$BACKUP_LOG" | tail -n 5)
    echo "Recent backup errors detected:
    
$RECENT_ERRORS" | \
        mail -s "CVD Backup Alert - Backup Errors" "$ALERT_EMAIL" 2>/dev/null
fi

# Check backup size (alert if too small)
BACKUP_SIZE=$(stat -c%s "$RECENT_BACKUP" 2>/dev/null || echo "0")
MIN_SIZE=$((1024 * 1024))  # 1MB minimum

if [ "$BACKUP_SIZE" -lt "$MIN_SIZE" ]; then
    echo "ALERT: CVD backup file unusually small: $(($BACKUP_SIZE / 1024))KB
Backup file: $RECENT_BACKUP" | \
        mail -s "CVD Backup Alert - Small Backup File" "$ALERT_EMAIL" 2>/dev/null
fi

echo "Backup monitoring completed - Status: OK"
```

---

**Runbook Version**: 1.0  
**Last Updated**: 2024-01-01  
**Next Review Date**: 2024-04-01  
**Owner**: Operations Team  
**Approver**: Operations Manager

**Backup Schedules:**
- Database: Every 2 hours (automated)
- Application: Daily at 2:00 AM (automated)  
- System: Weekly on Sunday at 1:00 AM (automated)
- Verification: Daily at 6:00 AM (automated)