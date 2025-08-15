# CVD Incident Response Runbook


## Metadata
- **ID**: 05_DEVELOPMENT_DEPLOYMENT_RUNBOOKS_INCIDENT_RESPONSE
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #api #authentication #coding #data-layer #database #debugging #development #device-management #integration #machine-learning #optimization #performance #planogram #product-placement #quality-assurance #security #testing #troubleshooting #vending-machine #workflows
- **Intent**: This runbook provides emergency response procedures for critical incidents affecting the CVD (Vision Device Configuration) system
- **Audience**: system administrators, managers, end users
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/05-development/deployment/runbooks/
- **Category**: Runbooks
- **Search Keywords**: ###, ####, (critical), (high), (medium), 1.0, 2024-01-01, 2024-04-01, action, actions, affected, analysis, applied, approver, areas

## Overview

This runbook provides emergency response procedures for critical incidents affecting the CVD (Vision Device Configuration) system. It includes immediate response actions, diagnostics, resolution steps, and escalation procedures.

### Scope
- System outages and service degradation
- Security incidents and breaches
- Database corruption or data loss
- Performance issues affecting users
- SSL/Certificate issues

### Response Time Targets
- **P0 (Critical)**: 15 minutes
- **P1 (High)**: 1 hour
- **P2 (Medium)**: 4 hours

## Incident Classification

### Priority Levels

#### P0 - Critical (System Down)
- Complete application outage
- Database corruption or complete failure
- Security breach with data exposure
- SSL certificate expired causing complete HTTPS failure

#### P1 - High (Degraded Service)
- Significant performance degradation (>5 second response times)
- Database connectivity issues affecting some operations
- Authentication system partially failing
- AI services completely unavailable

#### P2 - Medium (Limited Impact)
- Minor performance issues
- Non-critical feature failures
- Intermittent connectivity issues
- Non-critical security alerts

## Emergency Response Procedures

### Immediate Response (First 5 Minutes)

#### 1. Initial Assessment

```bash
#!/bin/bash
echo "=== INCIDENT RESPONSE INITIATED ==="
echo "Time: $(date)"
echo "Operator: $USER"

# Quick system status check
echo "=== System Status ==="
systemctl is-active cvd || echo "❌ CVD service is down"
systemctl is-active nginx || echo "❌ Nginx is down"
curl -f -m 5 http://localhost:5000/health || echo "❌ Health check failed"

# Check critical resources
echo "=== Resource Status ==="
df -h | grep -E "(Filesystem|/opt/cvd|/$)" | grep -E "(9[0-9]%|100%)" && echo "❌ Disk space critical"
free | awk '/Mem:/ {if ($3/$2 > 0.95) print "❌ Memory usage critical: " int($3/$2*100) "%"}'

# Check for obvious errors
echo "=== Recent Errors ==="
tail -n 20 /opt/cvd/logs/error.log | grep -i error | tail -n 5
```

#### 2. Immediate Stabilization

```bash
# If service is down, attempt quick restart
if ! systemctl is-active cvd > /dev/null; then
    echo "=== Attempting Service Restart ==="
    sudo systemctl restart cvd
    sleep 10
    
    if systemctl is-active cvd > /dev/null; then
        echo "✅ Service restarted successfully"
        curl -f http://localhost:5000/health && echo "✅ Health check passed"
    else
        echo "❌ Service restart failed - escalating"
    fi
fi
```

#### 3. Communication Setup

```bash
# Create incident channel (customize for your system)
echo "=== Setting Up Communication ==="
INCIDENT_ID="CVD-$(date +%Y%m%d-%H%M%S)"
echo "Incident ID: $INCIDENT_ID"

# Log incident start
echo "$INCIDENT_ID - Incident started at $(date)" >> /opt/cvd/logs/incidents.log

# Send initial alert (customize webhook URL)
curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"🚨 CVD Incident $INCIDENT_ID - Investigation started\"}" \
    YOUR_SLACK_WEBHOOK_URL 2>/dev/null || echo "Alert notification failed"
```

### Diagnostic Procedures

#### System Health Diagnostics

```bash
echo "=== COMPREHENSIVE SYSTEM DIAGNOSTICS ==="

# 1. Service Status
echo "--- Service Status ---"
systemctl status cvd --no-pager
systemctl status nginx --no-pager

# 2. Process Information
echo "--- Process Information ---"
ps aux | grep -E "(python.*app|gunicorn|nginx)" | grep -v grep

# 3. Network Connectivity
echo "--- Network Status ---"
netstat -tlnp | grep -E "(:80|:443|:5000)"
ss -tlnp | grep -E "(:80|:443|:5000)"

# 4. System Resources
echo "--- System Resources ---"
uptime
free -h
df -h
iotop -b -n 1 2>/dev/null | head -n 20

# 5. Recent System Events
echo "--- System Events ---"
journalctl -u cvd --since "10 minutes ago" --no-pager | tail -n 20
dmesg | tail -n 20
```

#### Application-Specific Diagnostics

```bash
echo "=== APPLICATION DIAGNOSTICS ==="

# 1. Application Logs Analysis
echo "--- Application Logs (Last 50 lines) ---"
tail -n 50 /opt/cvd/logs/error.log

echo "--- Critical Errors (Last 24 hours) ---"
grep -i "error\|exception\|fatal\|critical" /opt/cvd/logs/error.log | \
    grep "$(date +%Y-%m-%d)" | tail -n 10

# 2. Database Health
echo "--- Database Health ---"
if [ -f "/opt/cvd/data/cvd.db" ]; then
    # Check database integrity
    sudo -u cvdapp sqlite3 /opt/cvd/data/cvd.db "PRAGMA integrity_check;" 2>&1
    
    # Check database size and locks
    ls -lh /opt/cvd/data/cvd.db
    lsof /opt/cvd/data/cvd.db 2>/dev/null || echo "No locks found"
    
    # Test basic query
    sudo -u cvdapp sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM users;" 2>&1 || echo "Database query failed"
else
    echo "❌ Database file not found!"
fi

# 3. Configuration Check
echo "--- Configuration Status ---"
if [ -f "/opt/cvd/config/.env" ]; then
    echo "Environment file exists"
    # Check critical variables without exposing secrets
    grep -E "^(FLASK_ENV|DATABASE_PATH|LOG_PATH)" /opt/cvd/config/.env 2>/dev/null || echo "Config variables not found"
else
    echo "❌ Environment configuration missing!"
fi

# 4. Dependency Check
echo "--- Python Dependencies ---"
cd /opt/cvd/app
sudo -u cvdapp bash -c 'source venv/bin/activate && pip check' 2>&1 | head -n 10
```

#### Network and SSL Diagnostics

```bash
echo "=== NETWORK AND SSL DIAGNOSTICS ==="

# 1. Local connectivity
echo "--- Local Connectivity ---"
curl -v -m 10 http://localhost:5000/health 2>&1 | head -n 20

# 2. External connectivity
echo "--- External Connectivity ---"
curl -I -m 10 https://your-domain.com/health 2>&1 | head -n 10

# 3. SSL Certificate Status
echo "--- SSL Certificate ---"
openssl s_client -connect your-domain.com:443 -servername your-domain.com </dev/null 2>/dev/null | \
    openssl x509 -noout -dates 2>/dev/null || echo "SSL certificate check failed"

# 4. DNS Resolution
echo "--- DNS Resolution ---"
nslookup your-domain.com || echo "DNS resolution failed"

# 5. Port Accessibility
echo "--- Port Status ---"
nc -zv localhost 5000 2>&1
nc -zv localhost 80 2>&1
nc -zv localhost 443 2>&1
```

## Incident-Specific Response Procedures

### P0 - System Completely Down

#### Procedure: Complete Outage Response

```bash
#!/bin/bash
echo "=== P0 INCIDENT: COMPLETE OUTAGE ==="

# Step 1: Immediate service recovery attempt
echo "Step 1: Service Recovery"
sudo systemctl stop cvd nginx
sleep 5
sudo systemctl start nginx cvd

# Wait for services to initialize
sleep 30

# Step 2: Quick health verification
echo "Step 2: Health Verification"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [ "$HEALTH_STATUS" = "200" ]; then
    echo "✅ Quick recovery successful"
    echo "=== INCIDENT RESOLVED - Quick Recovery ==="
    exit 0
fi

# Step 3: Detailed diagnosis if quick recovery failed
echo "Step 3: Detailed Diagnosis Required"
echo "❌ Quick recovery failed - proceeding with detailed investigation"

# Check for disk space issues
DISK_USAGE=$(df /opt/cvd | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 95 ]; then
    echo "❌ Critical disk space issue detected: ${DISK_USAGE}% used"
    
    # Emergency cleanup
    echo "Performing emergency cleanup..."
    find /opt/cvd/logs -name "*.log" -mtime +7 -exec rm {} \;
    find /tmp -name "core.*" -mtime +1 -exec rm {} \; 2>/dev/null
    
    # Restart services after cleanup
    sudo systemctl restart cvd
    sleep 30
fi

# Check for memory issues
MEMORY_USAGE=$(free | awk '/Mem:/ {print int($3/$2*100)}')
if [ "$MEMORY_USAGE" -gt 95 ]; then
    echo "❌ Critical memory usage: ${MEMORY_USAGE}%"
    
    # Kill any runaway processes
    pkill -f "python.*zombie" 2>/dev/null || true
    
    # Restart service to clear memory
    sudo systemctl restart cvd
    sleep 30
fi

# Step 4: Database recovery check
echo "Step 4: Database Recovery"
if ! sudo -u cvdapp sqlite3 /opt/cvd/data/cvd.db "PRAGMA integrity_check;" | grep -q "ok"; then
    echo "❌ Database corruption detected - initiating emergency restore"
    
    # Find most recent backup
    LATEST_BACKUP=$(ls -t /opt/cvd/backups/*.db 2>/dev/null | head -n1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        echo "Restoring from backup: $LATEST_BACKUP"
        sudo systemctl stop cvd
        sudo -u cvdapp cp "$LATEST_BACKUP" /opt/cvd/data/cvd.db
        sudo systemctl start cvd
        sleep 30
    else
        echo "❌ No database backups available - CRITICAL"
        echo "=== ESCALATION REQUIRED ==="
        exit 1
    fi
fi

# Step 5: Final verification
FINAL_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [ "$FINAL_HEALTH" = "200" ]; then
    echo "✅ System recovery successful"
    echo "=== INCIDENT RESOLVED - Full Recovery ==="
else
    echo "❌ System recovery failed - manual intervention required"
    echo "=== ESCALATION REQUIRED ==="
    exit 1
fi
```

### P1 - Performance Degradation

#### Procedure: Performance Issues

```bash
#!/bin/bash
echo "=== P1 INCIDENT: PERFORMANCE DEGRADATION ==="

# Step 1: Measure current performance
echo "Step 1: Performance Baseline"
for i in {1..5}; do
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:5000/health)
    echo "Response time $i: ${RESPONSE_TIME}s"
done

# Step 2: Identify bottlenecks
echo "Step 2: Bottleneck Analysis"

# CPU analysis
echo "--- CPU Analysis ---"
top -bn1 | head -n 20

# Memory analysis
echo "--- Memory Analysis ---"
ps aux --sort=-%mem | head -n 10

# I/O analysis
echo "--- I/O Analysis ---"
iotop -b -n 1 2>/dev/null | head -n 15 || iostat -x 1 1

# Database analysis
echo "--- Database Analysis ---"
# Check for long-running queries or locks
lsof /opt/cvd/data/cvd.db 2>/dev/null | wc -l | xargs echo "Database connections:"

# Network analysis
echo "--- Network Analysis ---"
netstat -i
ss -s

# Step 3: Quick performance optimizations
echo "Step 3: Performance Optimization"

# Clear application cache if applicable
if [ -f "/opt/cvd/data/ai_cache.db" ]; then
    echo "Clearing AI cache..."
    sudo -u cvdapp rm -f /opt/cvd/data/ai_cache.db
fi

# Restart application to clear memory leaks
echo "Restarting application for memory cleanup..."
sudo systemctl restart cvd
sleep 30

# Optimize database
echo "Running database optimization..."
sudo -u cvdapp sqlite3 /opt/cvd/data/cvd.db "PRAGMA optimize;"

# Step 4: Verify improvement
echo "Step 4: Performance Verification"
sleep 30  # Allow system to stabilize

for i in {1..3}; do
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:5000/health)
    echo "Post-optimization response time $i: ${RESPONSE_TIME}s"
done

echo "Performance optimization completed"
```

### Security Incident Response

#### Procedure: Security Breach Detection

```bash
#!/bin/bash
echo "=== SECURITY INCIDENT RESPONSE ==="

# Step 1: Immediate containment
echo "Step 1: Immediate Containment"

# Check for active suspicious connections
echo "--- Active Connections ---"
netstat -an | grep :5000 | grep ESTABLISHED

# Check recent authentication attempts
echo "--- Recent Authentication ---"
tail -n 100 /opt/cvd/logs/error.log | grep -i "login\|auth\|security" | tail -n 10

# Step 2: Evidence collection
echo "Step 2: Evidence Collection"

# Collect security logs
SECURITY_LOG="/tmp/security_incident_$(date +%Y%m%d_%H%M%S).log"
echo "Creating security log: $SECURITY_LOG"

{
    echo "=== Security Incident Log - $(date) ==="
    echo "--- Failed Login Attempts (Last 24 hours) ---"
    grep -i "failed\|unauthorized\|denied" /opt/cvd/logs/error.log | grep "$(date +%Y-%m-%d)"
    
    echo "--- Suspicious Network Activity ---"
    netstat -an | grep :5000
    
    echo "--- System Processes ---"
    ps aux | grep -E "(python|gunicorn)"
    
    echo "--- Recent System Changes ---"
    find /opt/cvd -type f -mtime -1 -ls 2>/dev/null | head -n 20
    
} > "$SECURITY_LOG"

# Step 3: Threat assessment
echo "Step 3: Threat Assessment"

# Check for SQL injection attempts
if grep -qi "union\|select\|drop\|insert" /opt/cvd/logs/error.log; then
    echo "⚠️  Possible SQL injection attempts detected"
fi

# Check for XSS attempts
if grep -qi "script\|javascript\|onerror" /opt/cvd/logs/error.log; then
    echo "⚠️  Possible XSS attempts detected"
fi

# Check for brute force attacks
FAILED_LOGINS=$(grep -c -i "login.*failed" /opt/cvd/logs/error.log)
if [ "$FAILED_LOGINS" -gt 10 ]; then
    echo "⚠️  High number of failed login attempts: $FAILED_LOGINS"
fi

# Step 4: Immediate security actions
echo "Step 4: Security Hardening"

# Update fail2ban rules if installed
if command -v fail2ban-client > /dev/null; then
    sudo fail2ban-client reload
    echo "✅ Fail2ban rules reloaded"
fi

# Force SSL redirect check
if curl -I http://your-domain.com 2>/dev/null | grep -q "301\|302"; then
    echo "✅ HTTP to HTTPS redirect working"
else
    echo "⚠️  HTTP to HTTPS redirect may not be working"
fi

# Check SSL certificate
SSL_EXPIRY=$(openssl s_client -connect your-domain.com:443 2>/dev/null | \
    openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
echo "SSL certificate expires: $SSL_EXPIRY"

echo "Security incident response completed"
echo "Evidence collected in: $SECURITY_LOG"
echo "⚠️  MANUAL REVIEW REQUIRED - Contact security team"
```

## Escalation Procedures

### When to Escalate

#### Immediate Escalation (Within 15 minutes)
- System remains down after initial recovery attempts
- Database corruption with no viable backup
- Active security breach with data exposure
- Multiple systems affected simultaneously

#### Standard Escalation (Within 1 hour)
- Performance issues not resolved by standard procedures
- Intermittent issues that cannot be reproduced
- Resource exhaustion that requires infrastructure changes
- Complex database issues requiring specialized knowledge

### Escalation Contacts

```bash
# Emergency escalation script
#!/bin/bash
INCIDENT_SEVERITY="$1"  # P0, P1, P2
INCIDENT_DESCRIPTION="$2"

case "$INCIDENT_SEVERITY" in
    "P0")
        echo "Escalating P0 incident..."
        # Send to on-call engineer
        curl -X POST "YOUR_PAGERDUTY_WEBHOOK" \
            -d "{\"incident_key\": \"cvd-$(date +%s)\", \"service_key\": \"YOUR_SERVICE_KEY\", \"description\": \"$INCIDENT_DESCRIPTION\"}"
        
        # Email operations manager
        echo "Critical CVD incident: $INCIDENT_DESCRIPTION" | \
            mail -s "CRITICAL: CVD System Down" ops-manager@company.com
        ;;
    "P1")
        echo "Escalating P1 incident..."
        # Slack notification
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 P1 CVD Incident: $INCIDENT_DESCRIPTION\"}" \
            YOUR_SLACK_WEBHOOK_URL
        ;;
    "P2")
        echo "Logging P2 incident..."
        echo "$(date): P2 - $INCIDENT_DESCRIPTION" >> /opt/cvd/logs/incidents.log
        ;;
esac
```

## Recovery Procedures

### System Recovery Checklist

After resolving an incident:

- [ ] Verify all services are running normally
- [ ] Confirm database integrity
- [ ] Test critical user workflows
- [ ] Monitor system resources for stability
- [ ] Review and clear any temporary fixes
- [ ] Update monitoring thresholds if needed

### Post-Incident Activities

#### 1. System Validation

```bash
echo "=== POST-INCIDENT VALIDATION ==="

# Comprehensive health check
curl -f https://your-domain.com/health/detailed | python3 -m json.tool

# Performance validation
for endpoint in "/health" "/api/devices" "/api/planograms"; do
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:5000$endpoint")
    echo "$endpoint response time: ${RESPONSE_TIME}s"
done

# Resource validation
echo "System resources post-incident:"
df -h | grep -E "(Filesystem|/opt/cvd|/$)"
free -h
uptime
```

#### 2. Incident Documentation

```bash
# Create incident report template
INCIDENT_REPORT="/opt/cvd/logs/incident_report_$(date +%Y%m%d_%H%M%S).md"

cat > "$INCIDENT_REPORT" << 'EOF'
# Incident Report

## Incident Details
- **Incident ID**: 
- **Date/Time**: 
- **Duration**: 
- **Severity**: 
- **Primary Responder**: 

## Impact Assessment
- **Users Affected**: 
- **Services Affected**: 
- **Revenue Impact**: 

## Root Cause Analysis
- **Primary Cause**: 
- **Contributing Factors**: 
- **Timeline of Events**: 

## Resolution Actions
- **Immediate Actions Taken**: 
- **Permanent Fix Applied**: 
- **Verification Steps**: 

## Prevention Measures
- **Monitoring Improvements**: 
- **Process Changes**: 
- **Technical Changes**: 

## Lessons Learned
- **What Went Well**: 
- **Areas for Improvement**: 
- **Action Items**: 
EOF

echo "Incident report template created: $INCIDENT_REPORT"
```

#### 3. Follow-up Actions

```bash
echo "=== FOLLOW-UP ACTIONS ==="

# Schedule increased monitoring
echo "Implementing increased monitoring for next 24 hours..."
# This would integrate with your monitoring system

# Check for similar issues in other environments
echo "Checking staging environment for similar issues..."
# Commands to check staging would go here

# Update documentation if needed
echo "Consider updating runbooks based on incident learnings"

# Schedule post-incident review
echo "Schedule post-incident review meeting within 48 hours"
```

## Emergency Commands Reference

### Quick Recovery Commands

```bash
# Emergency restart
sudo systemctl restart cvd nginx

# Emergency stop
sudo systemctl stop cvd nginx

# Emergency database backup
sudo -u cvdapp sqlite3 /opt/cvd/data/cvd.db ".backup /opt/cvd/backups/emergency_$(date +%Y%m%d_%H%M%S).db"

# Emergency log clearing (if disk full)
sudo truncate -s 0 /opt/cvd/logs/error.log
sudo truncate -s 0 /var/log/nginx/error.log

# Emergency process killing
sudo pkill -f "python.*app.py"
sudo pkill gunicorn

# Emergency SSL certificate renewal
sudo certbot renew --force-renewal
```

### Status Check Commands

```bash
# Quick status check
systemctl is-active cvd nginx && curl -f http://localhost:5000/health

# Resource check
df -h | grep -E "(9[0-9]%|100%)" && free | awk '/Mem:/ {if ($3/$2 > 0.9) print "High memory usage"}'

# Error log check
tail -n 20 /opt/cvd/logs/error.log | grep -i error
```

## Incident Response Checklist

### During Incident Response

- [ ] Record incident start time
- [ ] Assess severity and classify priority
- [ ] Notify appropriate stakeholders
- [ ] Begin diagnostic procedures
- [ ] Apply appropriate resolution procedures
- [ ] Document all actions taken
- [ ] Escalate if unable to resolve within time limits
- [ ] Communicate status updates regularly

### Post-Incident

- [ ] Verify system stability
- [ ] Document resolution actions
- [ ] Update monitoring if needed
- [ ] Schedule post-incident review
- [ ] Update runbooks if procedures changed
- [ ] Communicate resolution to stakeholders

---

**Runbook Version**: 1.0  
**Last Updated**: 2024-01-01  
**Next Review Date**: 2024-04-01  
**Owner**: Operations Team  
**Approver**: Operations Manager

**Emergency Contacts:**
- Primary On-Call: +1-XXX-XXX-XXXX
- Operations Manager: +1-XXX-XXX-XXXX
- Security Team: security@company.com