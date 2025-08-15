# Deployment Checklist

## Pre-Deployment Preparation

### 1. Code Quality Verification
- [ ] All tests pass (`python -m pytest`)
- [ ] No critical bugs in issue tracker
- [ ] Code review completed and approved
- [ ] Documentation updated
- [ ] Version number incremented

### 2. Database Preparation
- [ ] Database backup created
- [ ] Migration scripts tested
- [ ] Data integrity verified
- [ ] Performance benchmarks meet requirements
- [ ] Index optimization completed

### 3. Security Checklist
- [ ] Security audit completed
- [ ] Secrets and API keys secured
- [ ] HTTPS configuration verified
- [ ] CORS settings appropriate for production
- [ ] Authentication mechanisms tested

### 4. Configuration Review
- [ ] Environment variables documented
- [ ] Configuration files updated for production
- [ ] Logging levels set appropriately
- [ ] Error handling configured
- [ ] Session settings secured

---

## Production Environment Setup

### 1. Server Requirements
```bash
# Minimum server specifications
CPU: 2 cores
RAM: 4GB
Disk: 20GB SSD
OS: Ubuntu 20.04+ or CentOS 8+
Python: 3.8+
```

### 2. System Dependencies
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install nginx sqlite3 supervisor -y

# Optional: Install SSL certificate tools
sudo apt install certbot python3-certbot-nginx -y
```

### 3. Application Setup
```bash
# Create application directory
sudo mkdir -p /opt/cvd
cd /opt/cvd

# Create application user
sudo useradd -r -s /bin/false cvd
sudo chown -R cvd:cvd /opt/cvd

# Switch to application user for setup
sudo -u cvd bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install application dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

### 4. Database Setup
```bash
# Set appropriate permissions
chmod 644 cvd.db
chown cvd:cvd cvd.db

# Create database directory
mkdir -p /opt/cvd/data
mv cvd.db /opt/cvd/data/
ln -s /opt/cvd/data/cvd.db /opt/cvd/cvd.db

# Backup directory
mkdir -p /opt/cvd/backups
chown cvd:cvd /opt/cvd/backups
```

### 5. Configuration Files

#### Environment Configuration
```bash
# /opt/cvd/.env
FLASK_ENV=production
FLASK_DEBUG=0
ANTHROPIC_API_KEY=your-production-api-key
SESSION_SECRET=your-secure-session-secret-key
DATABASE=/opt/cvd/data/cvd.db
```

#### Gunicorn Configuration
```python
# /opt/cvd/gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
```

#### Supervisor Configuration
```ini
# /etc/supervisor/conf.d/cvd.conf
[program:cvd]
command=/opt/cvd/venv/bin/gunicorn -c gunicorn.conf.py app:app
directory=/opt/cvd
user=cvd
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/cvd/application.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
environment=PATH="/opt/cvd/venv/bin"
```

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/cvd
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend files
    location / {
        root /opt/cvd;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Static files
    location /pages/ {
        root /opt/cvd;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

---

## Deployment Process

### 1. File Transfer
```bash
# Using rsync (recommended)
rsync -avz --exclude 'venv/' --exclude '*.pyc' \
  /local/cvd/ user@server:/opt/cvd/

# Using scp
scp -r /local/cvd/* user@server:/opt/cvd/

# Set proper permissions
sudo chown -R cvd:cvd /opt/cvd
sudo chmod 755 /opt/cvd
sudo chmod 644 /opt/cvd/*.py
sudo chmod 644 /opt/cvd/cvd.db
```

### 2. Service Configuration
```bash
# Enable and start supervisor
sudo systemctl enable supervisor
sudo systemctl start supervisor

# Reload supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start CVD application
sudo supervisorctl start cvd

# Enable and configure nginx
sudo ln -s /etc/nginx/sites-available/cvd /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### 3. SSL Certificate (Optional but Recommended)
```bash
# Using Let's Encrypt
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### 4. Firewall Configuration
```bash
# UFW firewall rules
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

---

## Post-Deployment Verification

### 1. Service Status Checks
```bash
# Check application status
sudo supervisorctl status cvd

# Check nginx status
sudo systemctl status nginx

# Check system resources
free -h
df -h
top

# Check log files
tail -f /var/log/cvd/application.log
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 2. Functional Testing
```bash
# Backend API test
curl -f http://localhost:5000/api/auth/current-user
curl -f https://your-domain.com/api/auth/current-user

# Frontend test
curl -f http://localhost/
curl -f https://your-domain.com/

# Database connectivity
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM users;"
```

### 3. Performance Testing
```bash
# Load testing with ab (Apache Bench)
ab -n 1000 -c 10 https://your-domain.com/

# Database performance
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db ".timer ON" "SELECT COUNT(*) FROM devices;"

# Memory usage monitoring
ps aux | grep gunicorn
```

### 4. Security Verification
```bash
# SSL certificate check
curl -I https://your-domain.com/

# Security headers check
curl -I https://your-domain.com/ | grep -i security

# Port scan (should only show 80, 443, 22)
nmap -p 1-10000 localhost
```

---

## Monitoring & Maintenance

### 1. Log Rotation Setup
```bash
# /etc/logrotate.d/cvd
/var/log/cvd/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 cvd cvd
    postrotate
        supervisorctl restart cvd
    endscript
}
```

### 2. Database Backup Cron Job
```bash
# Add to crontab for cvd user
sudo crontab -u cvd -e

# Daily backup at 2 AM
0 2 * * * /opt/cvd/scripts/backup.sh

# Weekly cleanup at 3 AM Sunday
0 3 * * 0 /opt/cvd/scripts/cleanup.sh
```

### 3. Backup Script
```bash
#!/bin/bash
# /opt/cvd/scripts/backup.sh
BACKUP_DIR="/opt/cvd/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_FILE="/opt/cvd/data/cvd.db"

# Create backup
sqlite3 "$DB_FILE" ".backup $BACKUP_DIR/cvd_$TIMESTAMP.db"

# Compress backup
gzip "$BACKUP_DIR/cvd_$TIMESTAMP.db"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "cvd_*.db.gz" -mtime +30 -delete

echo "Backup completed: cvd_$TIMESTAMP.db.gz"
```

### 4. Health Check Script
```bash
#!/bin/bash
# /opt/cvd/scripts/healthcheck.sh
set -e

echo "=== CVD Health Check ==="
echo "Date: $(date)"

# Check services
if supervisorctl status cvd | grep -q RUNNING; then
    echo "✅ Application: Running"
else
    echo "❌ Application: Not running"
    exit 1
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: Running"
else
    echo "❌ Nginx: Not running"
    exit 1
fi

# Check database
if sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database: Accessible"
else
    echo "❌ Database: Not accessible"
    exit 1
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ Disk Space: ${DISK_USAGE}% used"
else
    echo "⚠️  Disk Space: ${DISK_USAGE}% used (Warning: >80%)"
fi

# Check HTTP response
if curl -f -s https://your-domain.com/ > /dev/null; then
    echo "✅ Web Service: Responding"
else
    echo "❌ Web Service: Not responding"
    exit 1
fi

echo "=== Health Check Complete ==="
```

---

## Rollback Procedures

### 1. Quick Rollback
```bash
# Stop current version
sudo supervisorctl stop cvd

# Restore previous version
sudo rsync -avz /opt/cvd/backup/previous_version/ /opt/cvd/

# Restore database if needed
sudo -u cvd cp /opt/cvd/backups/cvd_backup.db /opt/cvd/data/cvd.db

# Restart services
sudo supervisorctl start cvd
sudo systemctl restart nginx
```

### 2. Database Rollback
```bash
# Stop application
sudo supervisorctl stop cvd

# Restore database
sudo -u cvd cp /opt/cvd/backups/cvd_YYYYMMDD_HHMMSS.db.gz /tmp/
gunzip /tmp/cvd_YYYYMMDD_HHMMSS.db.gz
sudo -u cvd cp /tmp/cvd_YYYYMMDD_HHMMSS.db /opt/cvd/data/cvd.db

# Restart application
sudo supervisorctl start cvd
```

---

## Final Checklist

### Pre-Go-Live
- [ ] All services running and stable
- [ ] SSL certificates installed and valid
- [ ] Backup procedures tested
- [ ] Monitoring configured
- [ ] DNS records updated
- [ ] Load testing completed
- [ ] Security scan passed

### Go-Live
- [ ] Announce maintenance window
- [ ] Switch DNS to production server
- [ ] Verify all functionality
- [ ] Monitor logs for errors
- [ ] Confirm user access
- [ ] Update documentation

### Post-Go-Live
- [ ] Monitor system performance for 24 hours
- [ ] Verify backup procedures
- [ ] Update team on deployment status
- [ ] Document any issues encountered
- [ ] Schedule post-deployment review

---

*This checklist should be customized for your specific environment and requirements.*