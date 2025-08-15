# CVD Deployment Guide


## Metadata
- **ID**: 05_DEVELOPMENT_DEPLOYMENT_GUIDE
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #coding #data-layer #database #debugging #deployment #development #device-management #devops #driver-app #integration #machine-learning #metrics #mobile #optimization #performance #pwa #quality-assurance #reporting #security #testing #troubleshooting #vending-machine #workflows
- **Intent**: This guide provides comprehensive deployment procedures for the CVD (Vision Device Configuration) enterprise vending machine fleet management system
- **Audience**: system administrators, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/deployment/
- **Category**: Deployment
- **Search Keywords**: ###, ####, 123, 22.04, 443, analysis, balancer, contact, cpu, cvd, dashboard, database, deployment, device, documentation

## Overview

This guide provides comprehensive deployment procedures for the CVD (Vision Device Configuration) enterprise vending machine fleet management system. The system uses Flask/SQLite architecture with Progressive Web App capabilities and AI-powered features.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [Production Deployment](#production-deployment)
4. [SSL/TLS Configuration](#ssltls-configuration)
5. [Database Management](#database-management)
6. [Log Management](#log-management)
7. [Rollback Procedures](#rollback-procedures)
8. [Security Hardening](#security-hardening)
9. [Troubleshooting](#troubleshooting)

## System Requirements

### Server Infrastructure

#### Minimum Requirements
- **OS**: Ubuntu 20.04 LTS or CentOS 8+
- **CPU**: 2 vCPUs
- **Memory**: 4 GB RAM
- **Storage**: 50 GB SSD
- **Network**: 1 Gbps connection

#### Recommended (Production)
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4 vCPUs
- **Memory**: 8 GB RAM
- **Storage**: 100 GB SSD with automated backup
- **Network**: 10 Gbps connection with redundancy
- **Load Balancer**: NGINX with SSL termination

#### Software Dependencies

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Application runtime |
| pip | 23.0+ | Package management |
| SQLite | 3.39+ | Database engine |
| NGINX | 1.20+ | Web server/proxy |
| Gunicorn | 21.2+ | WSGI server |
| Certbot | 2.0+ | SSL certificate management |
| systemd | 246+ | Service management |
| Redis | 7.0+ | Session store (optional) |

### Network Requirements

#### Inbound Ports
- `443` - HTTPS (production)
- `80` - HTTP (redirect to HTTPS)
- `22` - SSH (restricted IPs only)

#### Outbound Access
- `443` - HTTPS for AI services (anthropic.com)
- `53` - DNS resolution
- `123` - NTP time synchronization

## Environment Setup

### 1. System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    nginx \
    sqlite3 \
    git \
    curl \
    unzip \
    certbot \
    python3-certbot-nginx \
    htop \
    tmux \
    fail2ban \
    ufw

# Create application user
sudo useradd -m -s /bin/bash cvdapp
sudo usermod -aG www-data cvdapp
```

### 2. Application Directory Structure

```bash
# Create directory structure
sudo mkdir -p /opt/cvd/{app,data,logs,backups,config}
sudo chown -R cvdapp:www-data /opt/cvd
sudo chmod -R 755 /opt/cvd

# Directory layout
/opt/cvd/
├── app/           # Application code
├── data/          # SQLite database and uploads
├── logs/          # Application logs
├── backups/       # Database backups
└── config/        # Configuration files
```

### 3. Environment Configuration

Create environment configuration file:

```bash
sudo -u cvdapp tee /opt/cvd/config/.env << 'EOF'
# Flask Configuration
FLASK_ENV=production
FLASK_APP=app.py
SESSION_SECRET=<GENERATE-SECURE-SECRET>

# Database Configuration
DATABASE_PATH=/opt/cvd/data/cvd.db
BACKUP_PATH=/opt/cvd/backups

# AI Services (Optional)
ANTHROPIC_API_KEY=<YOUR-API-KEY>
AI_RATE_LIMIT=1000
AI_CACHE_ENABLED=true

# Security Settings
SESSION_TIMEOUT=28800  # 8 hours
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900   # 15 minutes

# Logging Configuration
LOG_LEVEL=INFO
LOG_PATH=/opt/cvd/logs
LOG_MAX_SIZE=10MB
LOG_RETENTION_DAYS=30

# Performance Settings
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
GUNICORN_MAX_REQUESTS=1000

# SSL/Security Headers
FORCE_HTTPS=true
HSTS_MAX_AGE=31536000
CONTENT_SECURITY_POLICY=true
EOF

# Secure the environment file
sudo chmod 600 /opt/cvd/config/.env
```

Generate secure session secret:

```bash
python3 -c "import secrets; print('SESSION_SECRET=' + secrets.token_hex(32))" | \
sudo -u cvdapp tee -a /opt/cvd/config/.env
```

## Production Deployment

### 1. Application Deployment

```bash
# Switch to application user
sudo su - cvdapp

# Clone repository
cd /opt/cvd/app
git clone https://github.com/your-org/cvd.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Set up database
python3 -c "from app import init_db; init_db()"

# Create default admin user
python3 tools/python/reset_admin_password.py --password "ChangeMeNow123!"
```

### 2. Systemd Service Configuration

Create systemd service file:

```bash
sudo tee /etc/systemd/system/cvd.service << 'EOF'
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
ExecStart=/opt/cvd/app/venv/bin/gunicorn \
    --bind unix:/opt/cvd/app/cvd.sock \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --max-requests 1000 \
    --preload \
    --access-logfile /opt/cvd/logs/access.log \
    --error-logfile /opt/cvd/logs/error.log \
    --log-level info \
    app:app
ExecReload=/bin/kill -s HUP $MAINPID
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

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable cvd
sudo systemctl start cvd
sudo systemctl status cvd
```

### 3. NGINX Configuration

Create NGINX configuration:

```bash
sudo tee /etc/nginx/sites-available/cvd << 'EOF'
upstream cvd_app {
    server unix:/opt/cvd/app/cvd.sock fail_timeout=0;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name your-domain.com;
    
    # Allow Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL configuration (will be filled by certbot)
    ssl_certificate /path/to/certificate;
    ssl_certificate_key /path/to/private/key;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.anthropic.com; frame-src 'self'" always;
    
    # Hide nginx version
    server_tokens off;
    
    # Client settings
    client_max_body_size 10M;
    client_body_timeout 30s;
    client_header_timeout 30s;
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # Static files
    location /static {
        alias /opt/cvd/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Frame-Options "SAMEORIGIN" always;
    }
    
    # Static assets (CSS, JS, images)
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /opt/cvd/app;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Frame-Options "SAMEORIGIN" always;
    }
    
    # PWA files
    location ~* \.(json|webmanifest)$ {
        root /opt/cvd/app;
        add_header Cache-Control "public, max-age=86400";
    }
    
    # Service Worker
    location /service-worker.js {
        root /opt/cvd/app;
        add_header Cache-Control "public, max-age=0";
    }
    
    # Main application
    location / {
        include proxy_params;
        proxy_pass http://cvd_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable site and test configuration
sudo ln -s /etc/nginx/sites-available/cvd /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/TLS Configuration

### 1. Let's Encrypt Certificate

```bash
# Install certificate
sudo certbot --nginx -d your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Create renewal cron job
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. SSL Security Verification

```bash
# Test SSL configuration
curl -I https://your-domain.com

# Check SSL rating (external)
# Visit: https://www.ssllabs.com/ssltest/
```

## Database Management

### 1. Database Initialization

```bash
# Initialize database with schema
sudo -u cvdapp bash << 'EOF'
cd /opt/cvd/app
source venv/bin/activate
python3 -c "
from app import init_db
init_db()
print('Database initialized successfully')
"
EOF
```

### 2. Backup Procedures

Create automated backup script:

```bash
sudo tee /opt/cvd/scripts/backup.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Configuration
SOURCE_DB="/opt/cvd/data/cvd.db"
BACKUP_DIR="/opt/cvd/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/cvd_backup_${TIMESTAMP}.db"
RETENTION_DAYS=30
LOG_FILE="/opt/cvd/logs/backup.log"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Create backup
log_message "Starting database backup..."

if [ -f "$SOURCE_DB" ]; then
    # Create SQLite backup
    sqlite3 "$SOURCE_DB" ".backup $BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        # Verify backup
        sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" > /dev/null
        if [ $? -eq 0 ]; then
            # Compress backup
            gzip "$BACKUP_FILE"
            log_message "Backup completed successfully: ${BACKUP_FILE}.gz"
        else
            log_message "ERROR: Backup verification failed"
            rm -f "$BACKUP_FILE"
            exit 1
        fi
    else
        log_message "ERROR: Backup creation failed"
        exit 1
    fi
else
    log_message "ERROR: Source database not found: $SOURCE_DB"
    exit 1
fi

# Clean up old backups
find "$BACKUP_DIR" -name "cvd_backup_*.db.gz" -mtime +$RETENTION_DAYS -delete
log_message "Cleaned up backups older than $RETENTION_DAYS days"

# Log backup size and count
BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "cvd_backup_*.db.gz" | wc -l)
log_message "Backup size: $BACKUP_SIZE, Total backups: $BACKUP_COUNT"

log_message "Backup process completed"
EOF

# Make script executable
sudo chmod +x /opt/cvd/scripts/backup.sh
sudo chown cvdapp:www-data /opt/cvd/scripts/backup.sh

# Create backup cron job
sudo -u cvdapp crontab -e
# Add: 0 2 * * * /opt/cvd/scripts/backup.sh
```

### 3. Recovery Procedures

Create recovery script:

```bash
sudo tee /opt/cvd/scripts/restore.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Usage: ./restore.sh <backup_file>

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /opt/cvd/backups/cvd_backup_20240101_120000.db.gz"
    exit 1
fi

BACKUP_FILE="$1"
SOURCE_DB="/opt/cvd/data/cvd.db"
BACKUP_DB="/opt/cvd/data/cvd.db.backup.$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/opt/cvd/logs/restore.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting database restore from: $BACKUP_FILE"

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log_message "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Stop application service
log_message "Stopping CVD service..."
sudo systemctl stop cvd

# Backup current database
if [ -f "$SOURCE_DB" ]; then
    log_message "Backing up current database to: $BACKUP_DB"
    cp "$SOURCE_DB" "$BACKUP_DB"
fi

# Extract and restore backup
log_message "Restoring database..."
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" > "$SOURCE_DB"
else
    cp "$BACKUP_FILE" "$SOURCE_DB"
fi

# Verify restored database
sqlite3 "$SOURCE_DB" "PRAGMA integrity_check;" > /dev/null
if [ $? -eq 0 ]; then
    log_message "Database integrity check passed"
    
    # Set correct permissions
    chown cvdapp:www-data "$SOURCE_DB"
    chmod 644 "$SOURCE_DB"
    
    # Start application service
    log_message "Starting CVD service..."
    sudo systemctl start cvd
    
    # Verify service is running
    sleep 5
    if systemctl is-active --quiet cvd; then
        log_message "Restore completed successfully"
    else
        log_message "ERROR: Service failed to start after restore"
        exit 1
    fi
else
    log_message "ERROR: Restored database failed integrity check"
    # Restore original database
    if [ -f "$BACKUP_DB" ]; then
        cp "$BACKUP_DB" "$SOURCE_DB"
        sudo systemctl start cvd
    fi
    exit 1
fi
EOF

# Make script executable
sudo chmod +x /opt/cvd/scripts/restore.sh
sudo chown cvdapp:www-data /opt/cvd/scripts/restore.sh
```

## Log Management

### 1. Log Rotation Configuration

```bash
sudo tee /etc/logrotate.d/cvd << 'EOF'
/opt/cvd/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    create 644 cvdapp www-data
    postrotate
        systemctl reload cvd > /dev/null 2>&1 || true
    endscript
}
EOF
```

### 2. Centralized Logging (Optional)

For enterprise deployments, configure log forwarding:

```bash
# Install rsyslog forwarding (optional)
sudo tee /etc/rsyslog.d/50-cvd.conf << 'EOF'
# CVD application logs
$ModLoad imfile
$InputFileName /opt/cvd/logs/error.log
$InputFileTag cvd-error:
$InputFileStateFile stat-cvd-error
$InputFileSeverity error
$InputFilePersistStateInterval 1000
$InputRunFileMonitor

$InputFileName /opt/cvd/logs/access.log
$InputFileTag cvd-access:
$InputFileStateFile stat-cvd-access
$InputFileSeverity info
$InputFilePersistStateInterval 1000
$InputRunFileMonitor

# Forward to remote syslog server (uncomment if needed)
# *.* @@log.example.com:514
EOF

sudo systemctl restart rsyslog
```

## Rollback Procedures

### 1. Application Rollback

Create rollback script:

```bash
sudo tee /opt/cvd/scripts/rollback.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Usage: ./rollback.sh <git_commit_or_tag>

if [ $# -ne 1 ]; then
    echo "Usage: $0 <git_commit_or_tag>"
    echo "Example: $0 v1.0.0"
    exit 1
fi

TARGET_VERSION="$1"
APP_DIR="/opt/cvd/app"
LOG_FILE="/opt/cvd/logs/rollback.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting rollback to: $TARGET_VERSION"

# Switch to app user and directory
sudo -u cvdapp bash << EOL
cd "$APP_DIR"
source venv/bin/activate

# Backup current state
CURRENT_COMMIT=\$(git rev-parse HEAD)
log_message "Current version: \$CURRENT_COMMIT"

# Stop service
sudo systemctl stop cvd

# Rollback code
git fetch origin
git checkout "$TARGET_VERSION"

if [ \$? -eq 0 ]; then
    log_message "Code rollback successful"
    
    # Install dependencies (in case requirements changed)
    pip install -r requirements.txt
    
    # Start service
    sudo systemctl start cvd
    
    # Verify service
    sleep 5
    if systemctl is-active --quiet cvd; then
        log_message "Rollback completed successfully"
    else
        log_message "ERROR: Service failed to start after rollback"
        # Rollback to previous version
        git checkout "\$CURRENT_COMMIT"
        sudo systemctl start cvd
        exit 1
    fi
else
    log_message "ERROR: Git checkout failed"
    sudo systemctl start cvd
    exit 1
fi
EOL
EOF

# Make script executable
sudo chmod +x /opt/cvd/scripts/rollback.sh
sudo chown cvdapp:www-data /opt/cvd/scripts/rollback.sh
```

### 2. Emergency Rollback

```bash
# Quick emergency rollback commands
sudo systemctl stop cvd
sudo -u cvdapp git -C /opt/cvd/app checkout HEAD~1
sudo systemctl start cvd
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Restrict SSH access (replace with your IP)
sudo ufw delete allow ssh
sudo ufw allow from YOUR_IP_ADDRESS to any port ssh
```

### 2. Fail2Ban Configuration

```bash
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-botsearch]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 3
EOF

sudo systemctl restart fail2ban
```

### 3. System Security Updates

```bash
# Configure automatic security updates
sudo tee /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

sudo dpkg-reconfigure -plow unattended-upgrades
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Service Won't Start

```bash
# Check service status
sudo systemctl status cvd

# Check logs
sudo journalctl -u cvd -f

# Check application logs
sudo tail -f /opt/cvd/logs/error.log

# Common fixes
sudo systemctl daemon-reload
sudo systemctl restart cvd
```

#### 2. Database Issues

```bash
# Check database integrity
sqlite3 /opt/cvd/data/cvd.db "PRAGMA integrity_check;"

# Check database permissions
ls -la /opt/cvd/data/

# Fix permissions
sudo chown cvdapp:www-data /opt/cvd/data/cvd.db
sudo chmod 644 /opt/cvd/data/cvd.db
```

#### 3. SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Test SSL configuration
sudo nginx -t
```

#### 4. High Resource Usage

```bash
# Check system resources
htop
df -h
free -h

# Check application processes
ps aux | grep gunicorn

# Restart services
sudo systemctl restart cvd nginx
```

### Performance Monitoring

```bash
# Install monitoring tools
sudo apt install -y iotop nethogs

# Monitor in real-time
iotop -o  # Disk I/O
nethogs   # Network usage
htop      # CPU/Memory
```

### Log Analysis

```bash
# Application logs
tail -f /opt/cvd/logs/error.log
tail -f /opt/cvd/logs/access.log

# System logs
sudo journalctl -u cvd -f
sudo journalctl -u nginx -f

# Analyze log patterns
grep "ERROR" /opt/cvd/logs/error.log | tail -20
grep "500" /var/log/nginx/access.log | tail -10
```

## Deployment Checklist

### Pre-Deployment

- [ ] Server meets minimum requirements
- [ ] Domain name configured and DNS propagated
- [ ] SSL certificate ready or Let's Encrypt available
- [ ] Firewall rules configured
- [ ] Backup system tested
- [ ] Monitoring system configured

### During Deployment

- [ ] Application code deployed
- [ ] Database initialized
- [ ] Services started and enabled
- [ ] SSL certificate installed
- [ ] Security headers configured
- [ ] Backup scripts scheduled

### Post-Deployment

- [ ] Application accessible via HTTPS
- [ ] Login functionality tested
- [ ] Core features verified
- [ ] SSL rating A+ (SSLLabs test)
- [ ] Logs being generated correctly
- [ ] Monitoring alerts configured
- [ ] Documentation updated

## Maintenance Schedule

| Task | Frequency | Owner | Notes |
|------|-----------|-------|-------|
| Security updates | Weekly | DevOps | Automated via unattended-upgrades |
| Certificate renewal | Automated | System | Let's Encrypt auto-renewal |
| Database backup verification | Weekly | DevOps | Test restore process |
| Log rotation | Daily | System | Automated via logrotate |
| Performance review | Monthly | DevOps | Check metrics and optimize |
| Security audit | Quarterly | Security | Full security assessment |

## Support Information

- **Emergency Contact**: ops-emergency@company.com
- **Documentation**: https://docs.cvd.company.com
- **Issue Tracker**: https://github.com/company/cvd/issues
- **Monitoring Dashboard**: https://monitoring.cvd.company.com