#!/bin/bash

# CVD Documentation Backup Creator
# Automated backup and versioning system for the CVD documentation
#
# Features:
# - Automated documentation backups
# - Version control integration
# - Incremental and full backup support
# - Backup verification and validation
# - Retention policy management
# - Error reporting and alerting
# - Integration with health monitoring

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOC_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BACKUP_ROOT="$DOC_ROOT/maintenance/backups"
LOG_FILE="$DOC_ROOT/maintenance/reports/backup.log"
CONFIG_FILE="$DOC_ROOT/maintenance/config/backup.conf"

# Default configuration
RETENTION_DAYS=90
MAX_BACKUPS=50
COMPRESS_BACKUPS=true
VERIFY_BACKUPS=true
INCLUDE_METRICS=true
INCLUDE_REPORTS=false
BACKUP_TYPE="incremental"
NOTIFICATION_EMAIL=""
ENABLE_ENCRYPTION=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$@"
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_warn() {
    log "WARN" "$@"
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    log "ERROR" "$@"
    echo -e "${RED}[ERROR]${NC} $*"
}

log_success() {
    log "SUCCESS" "$@"
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

# Load configuration if exists
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        log_info "Loading configuration from $CONFIG_FILE"
        source "$CONFIG_FILE"
    else
        log_info "No configuration file found, using defaults"
        create_default_config
    fi
}

# Create default configuration file
create_default_config() {
    mkdir -p "$(dirname "$CONFIG_FILE")"
    cat > "$CONFIG_FILE" << EOF
# CVD Documentation Backup Configuration

# Backup retention (days)
RETENTION_DAYS=90

# Maximum number of backups to keep
MAX_BACKUPS=50

# Compress backups (true/false)
COMPRESS_BACKUPS=true

# Verify backups after creation (true/false)
VERIFY_BACKUPS=true

# Include metrics data in backups (true/false)
INCLUDE_METRICS=true

# Include report files in backups (true/false)
INCLUDE_REPORTS=false

# Default backup type (full/incremental)
BACKUP_TYPE="incremental"

# Email for notifications (empty to disable)
NOTIFICATION_EMAIL=""

# Enable backup encryption (true/false)
ENABLE_ENCRYPTION=false

# Encryption key file (if encryption enabled)
ENCRYPTION_KEY_FILE=""
EOF
    log_info "Created default configuration file: $CONFIG_FILE"
}

# Initialize backup environment
init_backup_env() {
    log_info "Initializing backup environment"
    
    # Create backup directories
    mkdir -p "$BACKUP_ROOT"
    mkdir -p "$BACKUP_ROOT/full"
    mkdir -p "$BACKUP_ROOT/incremental"
    mkdir -p "$BACKUP_ROOT/metadata"
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Create backup state file
    local state_file="$BACKUP_ROOT/backup_state.json"
    if [[ ! -f "$state_file" ]]; then
        cat > "$state_file" << EOF
{
    "last_full_backup": null,
    "last_incremental_backup": null,
    "backup_count": 0,
    "total_size_mb": 0,
    "initialized": "$(date -Iseconds)"
}
EOF
        log_info "Created backup state file: $state_file"
    fi
    
    log_success "Backup environment initialized"
}

# Get current backup state
get_backup_state() {
    local state_file="$BACKUP_ROOT/backup_state.json"
    if [[ -f "$state_file" ]]; then
        cat "$state_file"
    else
        echo '{"last_full_backup": null, "last_incremental_backup": null, "backup_count": 0, "total_size_mb": 0}'
    fi
}

# Update backup state
update_backup_state() {
    local backup_type=$1
    local backup_path=$2
    local backup_size_mb=$3
    
    local state_file="$BACKUP_ROOT/backup_state.json"
    local current_state=$(get_backup_state)
    local timestamp=$(date -Iseconds)
    
    # Update state using jq if available, otherwise use simple replacement
    if command -v jq >/dev/null 2>&1; then
        echo "$current_state" | jq \
            --arg type "$backup_type" \
            --arg path "$backup_path" \
            --arg timestamp "$timestamp" \
            --argjson size "$backup_size_mb" \
            "
            if \$type == \"full\" then
                .last_full_backup = \$timestamp
            else
                .last_incremental_backup = \$timestamp
            end |
            .backup_count += 1 |
            .total_size_mb += \$size |
            .last_backup_path = \$path
            " > "$state_file.tmp" && mv "$state_file.tmp" "$state_file"
    else
        # Fallback without jq
        local backup_count=$(echo "$current_state" | grep -o '"backup_count": [0-9]*' | cut -d' ' -f2)
        backup_count=$((backup_count + 1))
        
        cat > "$state_file" << EOF
{
    "last_${backup_type}_backup": "$timestamp",
    "backup_count": $backup_count,
    "total_size_mb": $backup_size_mb,
    "last_backup_path": "$backup_path",
    "updated": "$timestamp"
}
EOF
    fi
}

# Calculate directory size in MB
calculate_size_mb() {
    local path=$1
    local size_kb=$(du -sk "$path" 2>/dev/null | cut -f1)
    echo $((size_kb / 1024))
}

# Create file list for backup
create_file_list() {
    local backup_type=$1
    local list_file=$2
    local exclude_file="$BACKUP_ROOT/exclude.txt"
    
    # Create exclude patterns
    cat > "$exclude_file" << EOF
*.log
*.tmp
*.swp
*~
.DS_Store
Thumbs.db
node_modules/
.git/
__pycache__/
*.pyc
.pytest_cache/
*.sqlite-shm
*.sqlite-wal
EOF

    if [[ "$INCLUDE_REPORTS" != "true" ]]; then
        echo "maintenance/reports/" >> "$exclude_file"
    fi
    
    if [[ "$INCLUDE_METRICS" != "true" ]]; then
        echo "maintenance/data/" >> "$exclude_file"
    fi
    
    log_info "Creating file list for $backup_type backup"
    
    if [[ "$backup_type" == "full" ]]; then
        # Full backup - include all documentation
        find "$DOC_ROOT/documentation" -type f -name "*.md" > "$list_file"
        find "$DOC_ROOT/documentation" -type f -name "*.json" >> "$list_file"
        find "$DOC_ROOT/documentation" -type f -name "*.yaml" >> "$list_file"
        find "$DOC_ROOT/documentation" -type f -name "*.yml" >> "$list_file"
        
        if [[ "$INCLUDE_METRICS" == "true" ]]; then
            find "$DOC_ROOT/documentation/maintenance" -type f >> "$list_file"
        fi
    else
        # Incremental backup - only changed files in last 24 hours
        find "$DOC_ROOT/documentation" -type f -name "*.md" -mtime -1 > "$list_file"
        find "$DOC_ROOT/documentation" -type f -name "*.json" -mtime -1 >> "$list_file"
        find "$DOC_ROOT/documentation" -type f -name "*.yaml" -mtime -1 >> "$list_file"
        find "$DOC_ROOT/documentation" -type f -name "*.yml" -mtime -1 >> "$list_file"
    fi
    
    # Filter out excluded files
    local temp_file="$list_file.tmp"
    while IFS= read -r pattern; do
        grep -v "$pattern" "$list_file" > "$temp_file" 2>/dev/null || true
        mv "$temp_file" "$list_file"
    done < "$exclude_file"
    
    local file_count=$(wc -l < "$list_file")
    log_info "Found $file_count files for backup"
}

# Create backup archive
create_backup_archive() {
    local backup_type=$1
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_name="cvd_docs_${backup_type}_${timestamp}"
    local list_file="$BACKUP_ROOT/${backup_name}_files.txt"
    local backup_path="$BACKUP_ROOT/${backup_type}/${backup_name}"
    
    log_info "Creating $backup_type backup: $backup_name"
    
    # Create file list
    create_file_list "$backup_type" "$list_file"
    
    # Check if there are files to backup
    if [[ ! -s "$list_file" ]]; then
        log_warn "No files found for $backup_type backup"
        return 1
    fi
    
    # Create backup directory
    mkdir -p "$backup_path"
    
    # Copy files preserving structure
    local file_count=0
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            local rel_path=$(realpath --relative-to="$DOC_ROOT" "$file")
            local dest_dir="$backup_path/$(dirname "$rel_path")"
            mkdir -p "$dest_dir"
            cp "$file" "$dest_dir/"
            ((file_count++))
        fi
    done < "$list_file"
    
    log_info "Copied $file_count files to backup"
    
    # Create backup metadata
    create_backup_metadata "$backup_path" "$backup_type" "$timestamp" "$file_count"
    
    # Compress if enabled
    if [[ "$COMPRESS_BACKUPS" == "true" ]]; then
        log_info "Compressing backup archive"
        local archive_path="${backup_path}.tar.gz"
        tar -czf "$archive_path" -C "$(dirname "$backup_path")" "$(basename "$backup_path")"
        rm -rf "$backup_path"
        backup_path="$archive_path"
        log_info "Backup compressed to: $backup_path"
    fi
    
    # Encrypt if enabled
    if [[ "$ENABLE_ENCRYPTION" == "true" && -n "$ENCRYPTION_KEY_FILE" && -f "$ENCRYPTION_KEY_FILE" ]]; then
        log_info "Encrypting backup"
        local encrypted_path="${backup_path}.enc"
        openssl enc -aes-256-cbc -salt -in "$backup_path" -out "$encrypted_path" -kfile "$ENCRYPTION_KEY_FILE"
        rm "$backup_path"
        backup_path="$encrypted_path"
        log_info "Backup encrypted to: $backup_path"
    fi
    
    # Calculate backup size
    local backup_size_mb=$(calculate_size_mb "$backup_path")
    
    # Update state
    update_backup_state "$backup_type" "$backup_path" "$backup_size_mb"
    
    # Verify backup if enabled
    if [[ "$VERIFY_BACKUPS" == "true" ]]; then
        verify_backup "$backup_path" "$backup_type"
    fi
    
    log_success "Backup created successfully: $backup_path (${backup_size_mb}MB)"
    echo "$backup_path"
}

# Create backup metadata
create_backup_metadata() {
    local backup_path=$1
    local backup_type=$2
    local timestamp=$3
    local file_count=$4
    
    local metadata_file="$backup_path/backup_metadata.json"
    
    cat > "$metadata_file" << EOF
{
    "backup_type": "$backup_type",
    "timestamp": "$timestamp",
    "created_at": "$(date -Iseconds)",
    "file_count": $file_count,
    "backup_path": "$backup_path",
    "documentation_root": "$DOC_ROOT",
    "script_version": "1.0.0",
    "configuration": {
        "retention_days": $RETENTION_DAYS,
        "compress_backups": $COMPRESS_BACKUPS,
        "verify_backups": $VERIFY_BACKUPS,
        "include_metrics": $INCLUDE_METRICS,
        "include_reports": $INCLUDE_REPORTS
    },
    "system_info": {
        "hostname": "$(hostname)",
        "user": "$(whoami)",
        "os": "$(uname -s)",
        "kernel": "$(uname -r)"
    }
}
EOF
    
    # Create file manifest
    local manifest_file="$backup_path/file_manifest.txt"
    find "$backup_path" -type f -not -name "backup_metadata.json" -not -name "file_manifest.txt" | \
        sed "s|$backup_path/||" | sort > "$manifest_file"
    
    log_info "Created backup metadata and manifest"
}

# Verify backup integrity
verify_backup() {
    local backup_path=$1
    local backup_type=$2
    
    log_info "Verifying backup: $backup_path"
    
    if [[ "$backup_path" == *.tar.gz ]]; then
        # Verify compressed archive
        if tar -tzf "$backup_path" >/dev/null 2>&1; then
            log_success "Backup archive verification passed"
        else
            log_error "Backup archive verification failed"
            return 1
        fi
    elif [[ "$backup_path" == *.enc ]]; then
        # For encrypted files, we can only check if the file exists and has size
        if [[ -f "$backup_path" && -s "$backup_path" ]]; then
            log_success "Encrypted backup file verification passed"
        else
            log_error "Encrypted backup file verification failed"
            return 1
        fi
    else
        # Verify directory structure
        local metadata_file="$backup_path/backup_metadata.json"
        local manifest_file="$backup_path/file_manifest.txt"
        
        if [[ -f "$metadata_file" && -f "$manifest_file" ]]; then
            # Check if all files in manifest exist
            local missing_files=0
            while IFS= read -r file; do
                if [[ ! -f "$backup_path/$file" ]]; then
                    log_warn "Missing file in backup: $file"
                    ((missing_files++))
                fi
            done < "$manifest_file"
            
            if [[ $missing_files -eq 0 ]]; then
                log_success "Backup verification passed"
            else
                log_error "Backup verification failed: $missing_files missing files"
                return 1
            fi
        else
            log_error "Backup verification failed: missing metadata or manifest"
            return 1
        fi
    fi
}

# Clean old backups based on retention policy
cleanup_old_backups() {
    log_info "Cleaning up old backups (retention: ${RETENTION_DAYS} days, max: ${MAX_BACKUPS})"
    
    local cleaned_count=0
    local total_size_freed=0
    
    # Clean by age
    for backup_dir in "$BACKUP_ROOT/full" "$BACKUP_ROOT/incremental"; do
        if [[ -d "$backup_dir" ]]; then
            while IFS= read -r -d '' backup; do
                local backup_size=$(calculate_size_mb "$backup")
                rm -rf "$backup"
                ((cleaned_count++))
                total_size_freed=$((total_size_freed + backup_size))
                log_info "Removed old backup: $(basename "$backup")"
            done < <(find "$backup_dir" -maxdepth 1 -type d -mtime +$RETENTION_DAYS -print0 2>/dev/null)
        fi
    done
    
    # Clean by count (keep only MAX_BACKUPS most recent)
    for backup_dir in "$BACKUP_ROOT/full" "$BACKUP_ROOT/incremental"; do
        if [[ -d "$backup_dir" ]]; then
            local backup_count=$(find "$backup_dir" -maxdepth 1 -type d -o -name "*.tar.gz" -o -name "*.enc" | wc -l)
            if [[ $backup_count -gt $MAX_BACKUPS ]]; then
                local excess=$((backup_count - MAX_BACKUPS))
                find "$backup_dir" -maxdepth 1 \( -type d -o -name "*.tar.gz" -o -name "*.enc" \) -printf '%T@ %p\n' | \
                    sort -n | head -n $excess | cut -d' ' -f2- | \
                    while IFS= read -r backup; do
                        local backup_size=$(calculate_size_mb "$backup")
                        rm -rf "$backup"
                        ((cleaned_count++))
                        total_size_freed=$((total_size_freed + backup_size))
                        log_info "Removed excess backup: $(basename "$backup")"
                    done
            fi
        fi
    done
    
    if [[ $cleaned_count -gt 0 ]]; then
        log_success "Cleaned up $cleaned_count old backups, freed ${total_size_freed}MB"
    else
        log_info "No old backups to clean up"
    fi
}

# List existing backups
list_backups() {
    log_info "Listing existing backups"
    
    echo "=== CVD Documentation Backups ==="
    echo
    
    for backup_type in "full" "incremental"; do
        echo "[$backup_type backups]"
        local backup_dir="$BACKUP_ROOT/$backup_type"
        
        if [[ -d "$backup_dir" ]]; then
            local count=0
            for backup in "$backup_dir"/*; do
                if [[ -e "$backup" ]]; then
                    local size=$(calculate_size_mb "$backup")
                    local date=$(date -r "$backup" '+%Y-%m-%d %H:%M:%S')
                    echo "  $(basename "$backup") - ${size}MB - $date"
                    ((count++))
                fi
            done
            
            if [[ $count -eq 0 ]]; then
                echo "  No $backup_type backups found"
            fi
        else
            echo "  No $backup_type backups directory"
        fi
        echo
    done
    
    # Show backup state
    local state=$(get_backup_state)
    echo "=== Backup State ==="
    if command -v jq >/dev/null 2>&1; then
        echo "$state" | jq .
    else
        echo "$state"
    fi
}

# Restore from backup
restore_backup() {
    local backup_path=$1
    local restore_target=${2:-"$DOC_ROOT/documentation_restored"}
    
    log_info "Restoring backup: $backup_path to $restore_target"
    
    if [[ ! -e "$backup_path" ]]; then
        log_error "Backup not found: $backup_path"
        return 1
    fi
    
    # Create restore target
    mkdir -p "$restore_target"
    
    if [[ "$backup_path" == *.tar.gz ]]; then
        # Extract compressed archive
        log_info "Extracting compressed backup"
        tar -xzf "$backup_path" -C "$restore_target" --strip-components=1
    elif [[ "$backup_path" == *.enc ]]; then
        log_error "Cannot restore encrypted backup without decryption key"
        return 1
    else
        # Copy directory
        log_info "Copying backup directory"
        cp -r "$backup_path"/* "$restore_target/"
    fi
    
    log_success "Backup restored to: $restore_target"
}

# Send notification
send_notification() {
    local subject=$1
    local message=$2
    
    if [[ -n "$NOTIFICATION_EMAIL" ]]; then
        log_info "Sending notification to $NOTIFICATION_EMAIL"
        echo "$message" | mail -s "$subject" "$NOTIFICATION_EMAIL" 2>/dev/null || \
            log_warn "Failed to send email notification"
    fi
}

# Generate backup report
generate_backup_report() {
    local report_file="$BACKUP_ROOT/backup_report.md"
    local state=$(get_backup_state)
    
    cat > "$report_file" << EOF
# CVD Documentation Backup Report

**Generated**: $(date -Iseconds)

## Backup Status

\`\`\`json
$state
\`\`\`

## Recent Backups

### Full Backups
$(find "$BACKUP_ROOT/full" -maxdepth 1 -type d -o -name "*.tar.gz" -o -name "*.enc" 2>/dev/null | \
  sort -r | head -5 | while read -r backup; do
    if [[ -e "$backup" ]]; then
        local size=$(calculate_size_mb "$backup")
        local date=$(date -r "$backup" '+%Y-%m-%d %H:%M:%S')
        echo "- $(basename "$backup") - ${size}MB - $date"
    fi
  done)

### Incremental Backups
$(find "$BACKUP_ROOT/incremental" -maxdepth 1 -type d -o -name "*.tar.gz" -o -name "*.enc" 2>/dev/null | \
  sort -r | head -5 | while read -r backup; do
    if [[ -e "$backup" ]]; then
        local size=$(calculate_size_mb "$backup")
        local date=$(date -r "$backup" '+%Y-%m-%d %H:%M:%S')
        echo "- $(basename "$backup") - ${size}MB - $date"
    fi
  done)

## Configuration

- **Retention Days**: $RETENTION_DAYS
- **Max Backups**: $MAX_BACKUPS
- **Compression**: $COMPRESS_BACKUPS
- **Verification**: $VERIFY_BACKUPS
- **Include Metrics**: $INCLUDE_METRICS
- **Include Reports**: $INCLUDE_REPORTS

## Recommendations

$(if [[ $(echo "$state" | grep -o '"backup_count": [0-9]*' | cut -d' ' -f2) -lt 3 ]]; then
    echo "- Consider running more frequent backups"
fi)

$(if [[ "$VERIFY_BACKUPS" != "true" ]]; then
    echo "- Enable backup verification for better reliability"
fi)

$(if [[ -z "$NOTIFICATION_EMAIL" ]]; then
    echo "- Configure email notifications for backup status"
fi)
EOF

    log_info "Backup report generated: $report_file"
}

# Main function
main() {
    local command=${1:-"help"}
    
    # Initialize environment
    init_backup_env
    load_config
    
    case "$command" in
        "full")
            BACKUP_TYPE="full"
            create_backup_archive "full"
            cleanup_old_backups
            generate_backup_report
            send_notification "CVD Documentation Full Backup Completed" "Full backup completed successfully"
            ;;
        "incremental")
            BACKUP_TYPE="incremental"
            create_backup_archive "incremental"
            cleanup_old_backups
            generate_backup_report
            ;;
        "auto")
            # Automatic backup - decide based on last full backup
            local state=$(get_backup_state)
            local last_full=$(echo "$state" | grep -o '"last_full_backup": "[^"]*"' | cut -d'"' -f4)
            
            if [[ -z "$last_full" || "$last_full" == "null" ]]; then
                log_info "No previous full backup found, creating full backup"
                main "full"
            else
                # Check if last full backup is older than 7 days
                local last_full_epoch=$(date -d "$last_full" +%s 2>/dev/null || echo 0)
                local current_epoch=$(date +%s)
                local days_diff=$(( (current_epoch - last_full_epoch) / 86400 ))
                
                if [[ $days_diff -ge 7 ]]; then
                    log_info "Last full backup is $days_diff days old, creating full backup"
                    main "full"
                else
                    log_info "Creating incremental backup"
                    main "incremental"
                fi
            fi
            ;;
        "list")
            list_backups
            ;;
        "cleanup")
            cleanup_old_backups
            ;;
        "restore")
            if [[ -n "${2:-}" ]]; then
                restore_backup "$2" "${3:-}"
            else
                log_error "Usage: $0 restore <backup_path> [restore_target]"
                exit 1
            fi
            ;;
        "report")
            generate_backup_report
            ;;
        "verify")
            if [[ -n "${2:-}" ]]; then
                verify_backup "$2" "manual"
            else
                log_error "Usage: $0 verify <backup_path>"
                exit 1
            fi
            ;;
        "help"|"-h"|"--help")
            cat << EOF
CVD Documentation Backup Creator

Usage: $0 <command> [options]

Commands:
    full                 Create full backup
    incremental         Create incremental backup
    auto                Automatically choose full or incremental
    list                List existing backups
    cleanup             Clean up old backups
    restore <path>      Restore from backup
    report              Generate backup report
    verify <path>       Verify backup integrity
    help                Show this help

Configuration:
    Edit $CONFIG_FILE to customize backup settings

Examples:
    $0 full                                    # Create full backup
    $0 incremental                            # Create incremental backup
    $0 auto                                   # Smart backup selection
    $0 restore /path/to/backup                # Restore backup
    $0 cleanup                                # Clean old backups

EOF
            ;;
        *)
            log_error "Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi