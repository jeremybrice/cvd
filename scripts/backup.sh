#!/bin/bash
# Database backup script for CVD system

set -e

# Configuration
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-cvd}"
DB_USER="${DB_USER:-cvd}"
BACKUP_DIR="/backups"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/cvd_backup_${TIMESTAMP}.sql"
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to clean old backups
cleanup_old_backups() {
    log "Cleaning backups older than $RETENTION_DAYS days..."
    find "$BACKUP_DIR" -name "cvd_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
}

# Function to verify backup
verify_backup() {
    if [ -f "$BACKUP_FILE_GZ" ]; then
        SIZE=$(stat -c%s "$BACKUP_FILE_GZ")
        if [ "$SIZE" -gt 0 ]; then
            log "Backup verified: $BACKUP_FILE_GZ ($(numfmt --to=iec-i --suffix=B $SIZE))"
            return 0
        fi
    fi
    log "ERROR: Backup verification failed!"
    return 1
}

# Main backup process
log "Starting database backup..."

# Perform database dump
log "Dumping database: $DB_NAME"
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --verbose \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    --create \
    --encoding=UTF8 \
    > "$BACKUP_FILE"

# Compress the backup
log "Compressing backup..."
gzip -9 "$BACKUP_FILE"

# Verify the backup
if verify_backup; then
    log "Backup completed successfully"
    
    # Clean old backups
    cleanup_old_backups
    
    # If AWS S3 is configured, upload to S3
    if [ ! -z "$AWS_S3_BUCKET" ]; then
        log "Uploading backup to S3..."
        aws s3 cp "$BACKUP_FILE_GZ" "s3://$AWS_S3_BUCKET/database-backups/" \
            --storage-class STANDARD_IA
        log "S3 upload completed"
    fi
    
    exit 0
else
    log "ERROR: Backup failed!"
    exit 1
fi