# CVD Deployment Runbook


## Metadata
- **ID**: 05_DEVELOPMENT_DEPLOYMENT_RUNBOOKS_DEPLOYMENT_RUNBOOK
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #authentication #coding #data-layer #database #debugging #deployment #development #device-management #devops #driver-app #integration #machine-learning #metrics #mobile #optimization #performance #planogram #product-placement #pwa #quality-assurance #reporting #security #testing #troubleshooting #vending-machine #workflows
- **Intent**: This runbook provides step-by-step procedures for deploying the CVD (Vision Device Configuration) application to production environments
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/deployment/runbooks/
- **Category**: Runbooks
- **Search Keywords**: 1.0, 2024-01-01, 2024-04-01, approver, cvd, date, deployment, device, devops, execution, last, log:, manager, next, operations

## Overview

This runbook provides step-by-step procedures for deploying the CVD (Vision Device Configuration) application to production environments. It covers both initial deployments and updates to existing installations.

### Scope
- Application code deployment
- Database migrations
- Service configuration updates
- SSL certificate management
- Post-deployment verification

### Prerequisites
- SSH access to production servers
- Sudo privileges on target systems
- Git repository access
- Database backup verification
- Deployment approval (for production)

## Pre-Deployment Checklist

### Authorization
- [ ] Deployment approved by Operations Manager
- [ ] Change window scheduled and communicated
- [ ] Stakeholders notified of deployment timeline
- [ ] Emergency contacts available during deployment

### Technical Prerequisites
- [ ] Recent database backup verified (within 2 hours)
- [ ] Staging environment tested successfully
- [ ] Git tag created for release version
- [ ] SSL certificates valid (>30 days remaining)
- [ ] Disk space >20% available on target servers

### Team Readiness
- [ ] Primary operator available for full deployment window
- [ ] Secondary operator on standby for rollback if needed
- [ ] Development team available for 2 hours post-deployment

## Deployment Procedures

### Phase 1: Pre-Deployment Preparation

#### 1.1 Environment Verification

```bash
# Connect to production server
ssh cvdops@production-server.company.com

# Verify system status
echo "=== System Status Check ==="
df -h
free -h
uptime
systemctl status cvd
systemctl status nginx

# Expected output: Services running, <80% disk/memory usage
```

#### 1.2 Create Deployment Directory

```bash
# Create deployment workspace
DEPLOYMENT_DATE=$(date +%Y%m%d_%H%M%S)
DEPLOYMENT_DIR="/tmp/cvd_deployment_${DEPLOYMENT_DATE}"
mkdir -p "$DEPLOYMENT_DIR"
cd "$DEPLOYMENT_DIR"

echo "Deployment directory: $DEPLOYMENT_DIR"
```

#### 1.3 Backup Current System

```bash
# Backup database
echo "=== Creating Database Backup ==="
sudo -u cvdapp sqlite3 /opt/cvd/data/cvd.db ".backup /opt/cvd/backups/pre_deploy_${DEPLOYMENT_DATE}.db"

# Verify backup
sudo -u cvdapp sqlite3 "/opt/cvd/backups/pre_deploy_${DEPLOYMENT_DATE}.db" "PRAGMA integrity_check;"
# Expected output: ok

# Backup current application code
echo "=== Creating Application Backup ==="
sudo tar -czf "/opt/cvd/backups/app_backup_${DEPLOYMENT_DATE}.tar.gz" -C /opt/cvd/app .

# Record current version
cd /opt/cvd/app
CURRENT_VERSION=$(sudo -u cvdapp git rev-parse HEAD)
echo "Current version: $CURRENT_VERSION" > "$DEPLOYMENT_DIR/current_version.txt"

echo "Backups completed successfully"
```

### Phase 2: Application Deployment

#### 2.1 Stop Application Services

```bash
echo "=== Stopping Services ==="
sudo systemctl stop cvd

# Verify service is stopped
sudo systemctl is-active cvd
# Expected output: inactive

echo "Application stopped successfully"
```

#### 2.2 Update Application Code

```bash
echo "=== Updating Application Code ==="
cd /opt/cvd/app

# Switch to application user
sudo -u cvdapp bash << 'EOF'
# Fetch latest changes
git fetch origin

# Get target version (replace with actual tag/commit)
TARGET_VERSION="v1.0.1"  # Update this with actual version
echo "Deploying version: $TARGET_VERSION"

# Checkout target version
git checkout "$TARGET_VERSION"

# Verify checkout
DEPLOYED_VERSION=$(git rev-parse HEAD)
echo "Deployed version: $DEPLOYED_VERSION"

# Update virtual environment if requirements changed
source venv/bin/activate
pip install -r requirements.txt

echo "Code update completed"
EOF
```

#### 2.3 Database Migration (if needed)

```bash
echo "=== Running Database Migrations ==="
cd /opt/cvd/app
sudo -u cvdapp bash << 'EOF'
source venv/bin/activate

# Check if migration is needed
if [ -f "migrations/migration_${TARGET_VERSION}.sql" ]; then
    echo "Running migration for version $TARGET_VERSION"
    sqlite3 /opt/cvd/data/cvd.db < "migrations/migration_${TARGET_VERSION}.sql"
    
    # Verify migration
    sqlite3 /opt/cvd/data/cvd.db "PRAGMA integrity_check;"
    echo "Migration completed successfully"
else
    echo "No migration required for this version"
fi
EOF
```

#### 2.4 Update Configuration Files

```bash
echo "=== Updating Configuration ==="

# Check if new environment variables are needed
if [ -f "/opt/cvd/config/.env.new" ]; then
    echo "New environment configuration found"
    sudo -u cvdapp cp /opt/cvd/config/.env /opt/cvd/config/.env.backup_${DEPLOYMENT_DATE}
    sudo -u cvdapp cp /opt/cvd/config/.env.new /opt/cvd/config/.env
    echo "Configuration updated"
else
    echo "No configuration changes required"
fi

# Update systemd service if changed
if [ -f "/opt/cvd/config/cvd.service.new" ]; then
    sudo cp /etc/systemd/system/cvd.service /opt/cvd/backups/cvd.service.backup_${DEPLOYMENT_DATE}
    sudo cp /opt/cvd/config/cvd.service.new /etc/systemd/system/cvd.service
    sudo systemctl daemon-reload
    echo "Systemd service updated"
fi
```

### Phase 3: Service Restart and Verification

#### 3.1 Start Application Services

```bash
echo "=== Starting Services ==="
sudo systemctl start cvd

# Wait for service to initialize
sleep 10

# Check service status
sudo systemctl is-active cvd
# Expected output: active

sudo systemctl status cvd
echo "Service started successfully"
```

#### 3.2 Health Check Verification

```bash
echo "=== Running Health Checks ==="

# Wait for application to fully initialize
echo "Waiting for application initialization..."
sleep 30

# Test basic health endpoint
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [ "$HEALTH_CHECK" = "200" ]; then
    echo "✓ Basic health check passed"
else
    echo "✗ Basic health check failed (HTTP $HEALTH_CHECK)"
    exit 1
fi

# Test detailed health endpoint
DETAILED_HEALTH=$(curl -s http://localhost:5000/health/detailed)
echo "Detailed health check response:"
echo "$DETAILED_HEALTH" | python3 -m json.tool

# Verify database connectivity
DB_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health/database)
if [ "$DB_HEALTH" = "200" ]; then
    echo "✓ Database health check passed"
else
    echo "✗ Database health check failed (HTTP $DB_HEALTH)"
    exit 1
fi

echo "All health checks passed"
```

#### 3.3 Functional Testing

```bash
echo "=== Running Functional Tests ==="

# Test login functionality
LOGIN_TEST=$(curl -s -X POST http://localhost:5000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "test_user", "password": "test_password"}')

echo "Login test response: $LOGIN_TEST"

# Test device listing (adjust based on your API)
DEVICES_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/devices)
if [ "$DEVICES_TEST" = "200" ]; then
    echo "✓ Device API endpoint working"
else
    echo "✗ Device API endpoint failed (HTTP $DEVICES_TEST)"
fi

# Test planogram endpoint
PLANOGRAM_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/planograms)
if [ "$PLANOGRAM_TEST" = "200" ]; then
    echo "✓ Planogram API endpoint working"
else
    echo "✗ Planogram API endpoint failed (HTTP $PLANOGRAM_TEST)"
fi

echo "Functional tests completed"
```

#### 3.4 SSL/HTTPS Verification

```bash
echo "=== Verifying SSL Configuration ==="

# Check SSL certificate
SSL_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://your-domain.com/health)
if [ "$SSL_CHECK" = "200" ]; then
    echo "✓ SSL/HTTPS working correctly"
else
    echo "✗ SSL/HTTPS check failed (HTTP $SSL_CHECK)"
    echo "Checking HTTP to HTTPS redirect..."
    HTTP_REDIRECT=$(curl -s -o /dev/null -w "%{http_code}" http://your-domain.com/health)
    echo "HTTP redirect status: $HTTP_REDIRECT"
fi

# Check SSL certificate expiration
SSL_EXPIRY=$(openssl s_client -connect your-domain.com:443 2>/dev/null | \
    openssl x509 -noout -dates | grep "notAfter")
echo "SSL certificate expires: $SSL_EXPIRY"

echo "SSL verification completed"
```

### Phase 4: Monitoring and Validation

#### 4.1 Monitor Application Logs

```bash
echo "=== Monitoring Application Logs ==="

# Check for errors in application logs
echo "Checking for errors in last 100 log entries..."
sudo tail -n 100 /opt/cvd/logs/error.log | grep -i error || echo "No errors found"

# Monitor real-time logs for 2 minutes
echo "Monitoring real-time logs for 2 minutes..."
timeout 120 sudo tail -f /opt/cvd/logs/error.log &
TAIL_PID=$!

# Let logs run in background while we do other checks
sleep 10

echo "Log monitoring started in background"
```

#### 4.2 Performance Baseline Check

```bash
echo "=== Performance Baseline Check ==="

# Measure response times
echo "Measuring API response times..."
for i in {1..5}; do
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:5000/health)
    echo "Response time $i: ${RESPONSE_TIME}s"
done

# Check system resources
echo "Current system resources:"
df -h | grep -E "(Filesystem|/opt/cvd|/$)"
free -h
uptime

# Check database performance
echo "Database performance check:"
sudo -u cvdapp sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM users;" 2>&1 | \
    (read result; echo "User count query: $result")

echo "Performance baseline check completed"
```

#### 4.3 User Acceptance Testing

```bash
echo "=== User Acceptance Testing ==="

# Test main application page
MAIN_PAGE=$(curl -s -o /dev/null -w "%{http_code}" https://your-domain.com/)
if [ "$MAIN_PAGE" = "200" ]; then
    echo "✓ Main application page accessible"
else
    echo "✗ Main application page failed (HTTP $MAIN_PAGE)"
fi

# Test PWA manifest
PWA_MANIFEST=$(curl -s -o /dev/null -w "%{http_code}" https://your-domain.com/manifest.json)
if [ "$PWA_MANIFEST" = "200" ]; then
    echo "✓ PWA manifest accessible"
else
    echo "✗ PWA manifest failed (HTTP $PWA_MANIFEST)"
fi

# Test service worker
SERVICE_WORKER=$(curl -s -o /dev/null -w "%{http_code}" https://your-domain.com/service-worker.js)
if [ "$SERVICE_WORKER" = "200" ]; then
    echo "✓ Service worker accessible"
else
    echo "✗ Service worker failed (HTTP $SERVICE_WORKER)"
fi

echo "User acceptance testing completed"
```

## Post-Deployment Activities

### 5.1 Update Monitoring

```bash
echo "=== Updating Monitoring Configuration ==="

# Record deployment in monitoring system
DEPLOYMENT_VERSION=$(cd /opt/cvd/app && git rev-parse --short HEAD)
echo "Deployment completed: Version $DEPLOYMENT_VERSION at $(date)" >> /opt/cvd/logs/deployments.log

# Send deployment notification (customize for your notification system)
curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"CVD deployment completed: Version $DEPLOYMENT_VERSION\"}" \
    YOUR_SLACK_WEBHOOK_URL || echo "Notification failed (non-critical)"

echo "Monitoring updates completed"
```

### 5.2 Clean Up Deployment Artifacts

```bash
echo "=== Cleaning Up Deployment Artifacts ==="

# Stop log monitoring
kill $TAIL_PID 2>/dev/null || true

# Clean up temporary files
rm -rf "$DEPLOYMENT_DIR"

# Keep only last 10 backups
cd /opt/cvd/backups
ls -t pre_deploy_*.db | tail -n +11 | xargs rm -f || true
ls -t app_backup_*.tar.gz | tail -n +11 | xargs rm -f || true

echo "Cleanup completed"
```

### 5.3 Final Verification

```bash
echo "=== Final Verification ==="

# Comprehensive health check
FINAL_HEALTH=$(curl -s https://your-domain.com/health/detailed | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('Status:', data.get('status', 'unknown'))
    if data.get('status') == 'healthy':
        sys.exit(0)
    else:
        sys.exit(1)
except:
    sys.exit(1)
")

if [ $? -eq 0 ]; then
    echo "✓ Final health check passed"
else
    echo "✗ Final health check failed"
    echo "Deployment may have issues - recommend immediate investigation"
fi

# Document deployment completion
echo "=== Deployment Summary ==="
echo "Deployment Date: $(date)"
echo "Previous Version: $CURRENT_VERSION"
echo "Deployed Version: $DEPLOYMENT_VERSION"
echo "Database Migration: $([ -f "migrations/migration_${TARGET_VERSION}.sql" ] && echo "Yes" || echo "No")"
echo "Duration: Started at $DEPLOYMENT_DATE"
echo "Status: $([ $? -eq 0 ] && echo "SUCCESS" || echo "FAILED")"

echo "Deployment completed successfully"
```

## Rollback Procedures

### Emergency Rollback (if deployment fails)

```bash
#!/bin/bash
echo "=== EMERGENCY ROLLBACK INITIATED ==="

# Stop current application
sudo systemctl stop cvd

# Restore previous code version
cd /opt/cvd/app
sudo -u cvdapp git checkout "$CURRENT_VERSION"

# Restore database if migration was performed
if [ -f "/opt/cvd/backups/pre_deploy_${DEPLOYMENT_DATE}.db" ]; then
    echo "Restoring database..."
    sudo -u cvdapp cp "/opt/cvd/backups/pre_deploy_${DEPLOYMENT_DATE}.db" /opt/cvd/data/cvd.db
fi

# Restore configuration if changed
if [ -f "/opt/cvd/config/.env.backup_${DEPLOYMENT_DATE}" ]; then
    sudo -u cvdapp cp "/opt/cvd/config/.env.backup_${DEPLOYMENT_DATE}" /opt/cvd/config/.env
fi

# Restore systemd service if changed
if [ -f "/opt/cvd/backups/cvd.service.backup_${DEPLOYMENT_DATE}" ]; then
    sudo cp "/opt/cvd/backups/cvd.service.backup_${DEPLOYMENT_DATE}" /etc/systemd/system/cvd.service
    sudo systemctl daemon-reload
fi

# Start application
sudo systemctl start cvd

# Verify rollback
sleep 10
if sudo systemctl is-active cvd >/dev/null; then
    echo "✓ Rollback completed successfully"
    curl -f http://localhost:5000/health && echo "✓ Application responding"
else
    echo "✗ Rollback failed - manual intervention required"
    exit 1
fi

echo "=== ROLLBACK COMPLETED ==="
```

## Troubleshooting

### Common Issues

#### Issue: Service fails to start

**Symptoms:**
- `systemctl status cvd` shows failed state
- Error logs show port binding issues

**Resolution:**
```bash
# Check if port is in use
sudo netstat -tlnp | grep :5000

# Check for zombie processes
ps aux | grep python | grep app.py

# Kill any hanging processes
sudo pkill -f "python.*app.py"

# Restart service
sudo systemctl start cvd
```

#### Issue: Database migration fails

**Symptoms:**
- Migration script returns error
- Database integrity check fails

**Resolution:**
```bash
# Restore database from backup
sudo -u cvdapp cp "/opt/cvd/backups/pre_deploy_${DEPLOYMENT_DATE}.db" /opt/cvd/data/cvd.db

# Verify database integrity
sudo -u cvdapp sqlite3 /opt/cvd/data/cvd.db "PRAGMA integrity_check;"

# Check migration script syntax
sqlite3 /tmp/test.db < "migrations/migration_${TARGET_VERSION}.sql"
```

#### Issue: SSL certificate problems

**Symptoms:**
- HTTPS requests fail
- SSL certificate warnings

**Resolution:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate if needed
sudo certbot renew

# Restart nginx
sudo systemctl restart nginx

# Test SSL configuration
curl -I https://your-domain.com
```

### Recovery Procedures

#### Application Won't Start After Rollback

```bash
# Check application dependencies
cd /opt/cvd/app
sudo -u cvdapp source venv/bin/activate
sudo -u cvdapp pip check

# Reinstall requirements
sudo -u cvdapp pip install -r requirements.txt --force-reinstall

# Check file permissions
sudo chown -R cvdapp:www-data /opt/cvd/app
sudo chmod +x /opt/cvd/app/app.py
```

#### Database Corruption Detected

```bash
# Stop application immediately
sudo systemctl stop cvd

# Restore from most recent clean backup
LATEST_BACKUP=$(ls -t /opt/cvd/backups/*.db | head -n1)
sudo -u cvdapp cp "$LATEST_BACKUP" /opt/cvd/data/cvd.db

# Verify integrity
sudo -u cvdapp sqlite3 /opt/cvd/data/cvd.db "PRAGMA integrity_check;"

# Start application
sudo systemctl start cvd
```

## Verification Checklist

### Deployment Success Criteria

- [ ] Application service running (`systemctl status cvd`)
- [ ] Health endpoints responding (200 status)
- [ ] Database integrity verified
- [ ] SSL certificate valid and working
- [ ] All API endpoints responding
- [ ] No critical errors in logs
- [ ] Performance within acceptable limits
- [ ] PWA functionality working
- [ ] User login/authentication working

### Post-Deployment Monitoring

Monitor these metrics for 2 hours post-deployment:
- [ ] HTTP response times <2 seconds
- [ ] Error rate <1%
- [ ] CPU usage <70%
- [ ] Memory usage <80%
- [ ] No database lock timeouts
- [ ] SSL certificate chain valid

## Documentation Updates

### Required Documentation

After successful deployment:
- [ ] Update version in documentation
- [ ] Record deployment in change log
- [ ] Update configuration documentation if changed
- [ ] Document any manual steps performed
- [ ] Update runbook if procedures changed

### Communication

- [ ] Notify stakeholders of successful deployment
- [ ] Update status page if maintenance window was scheduled
- [ ] Send deployment summary to operations team
- [ ] Schedule post-deployment review meeting if issues occurred

---

**Runbook Version**: 1.0  
**Last Updated**: 2024-01-01  
**Next Review Date**: 2024-04-01  
**Owner**: DevOps Team  
**Approver**: Operations Manager

**Execution Log:**
- Date: ___________
- Operator: ___________
- Version Deployed: ___________
- Duration: ___________
- Issues Encountered: ___________
- Resolution: ___________
- Verification Status: ___________