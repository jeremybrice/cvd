# Emergency Procedures Quick Reference

## Emergency Response Overview

### Severity Levels
- **🔴 CRITICAL**: System down, data loss risk, security breach
- **🟠 HIGH**: Major functionality impaired, user impact
- **🟡 MEDIUM**: Minor issues, workarounds available  
- **🔵 LOW**: Cosmetic issues, minimal impact

### Immediate Response Protocol
1. **Assess severity** (30 seconds)
2. **Implement immediate fix** if available (2 minutes)
3. **Activate emergency contacts** if needed (5 minutes)
4. **Document incident** (ongoing)
5. **Communicate status** to stakeholders

---

## Critical System Failures

### 🔴 Complete System Down

#### Symptoms
- Application completely inaccessible
- HTTP 500/502/503 errors
- Database connection failures

#### Immediate Actions
```bash
# 1. Check service status
sudo systemctl status nginx
sudo supervisorctl status cvd

# 2. Check system resources
free -h && df -h && uptime

# 3. Check logs
tail -20 /var/log/cvd/application.log
tail -20 /var/log/nginx/error.log

# 4. Restart services (if needed)
sudo supervisorctl restart cvd
sudo systemctl restart nginx
```

#### If Above Fails
```bash
# Emergency system restart
sudo reboot

# Or hard reset if SSH unresponsive
# (Physical access or cloud console required)
```

### 🔴 Database Corruption

#### Symptoms
- SQLite database errors
- Data inconsistencies
- Application crashes on database operations

#### Immediate Actions
```bash
# 1. Stop application immediately
sudo supervisorctl stop cvd

# 2. Check database integrity
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "PRAGMA integrity_check;"

# 3. If corrupted, restore from backup
sudo -u cvd cp /opt/cvd/backups/cvd_latest.db.gz /tmp/
gunzip /tmp/cvd_latest.db.gz
sudo -u cvd cp /tmp/cvd_latest.db /opt/cvd/data/cvd.db

# 4. Verify restoration
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM users;"

# 5. Restart application
sudo supervisorctl start cvd
```

### 🔴 Security Breach

#### Symptoms
- Unauthorized admin access detected
- Suspicious audit log entries
- Multiple failed login attempts from same IP
- Unusual system behavior

#### Immediate Actions
```bash
# 1. Change default admin password
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "
UPDATE users 
SET password_hash = 'new_secure_hash' 
WHERE username = 'admin';"

# 2. Terminate all sessions
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "DELETE FROM sessions;"

# 3. Check for unauthorized users
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "
SELECT username, role, created_at FROM users 
ORDER BY created_at DESC LIMIT 10;"

# 4. Block suspicious IPs (if using firewall)
sudo ufw deny from SUSPICIOUS_IP_ADDRESS

# 5. Review recent activity
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "
SELECT * FROM audit_log 
WHERE created_at > datetime('now', '-24 hours')
ORDER BY created_at DESC;"
```

---

## High Priority Issues

### 🟠 Application Performance Degradation

#### Symptoms
- Slow response times (>5 seconds)
- Timeouts
- High CPU/memory usage

#### Quick Diagnosis
```bash
# System resources
top -n 1
free -h
df -h

# Database performance
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db ".timer ON" "SELECT COUNT(*) FROM devices;"

# Network connectivity
ping -c 3 8.8.8.8
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/devices
```

#### Quick Fixes
```bash
# 1. Restart application
sudo supervisorctl restart cvd

# 2. Clear old sessions and logs
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "
DELETE FROM sessions WHERE expires_at < datetime('now');
DELETE FROM audit_log WHERE created_at < date('now', '-30 days');"

# 3. Database optimization
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "VACUUM; ANALYZE;"

# 4. If disk space low, clean logs
sudo find /var/log -name "*.log" -mtime +7 -delete
```

### 🟠 Authentication System Failure

#### Symptoms
- Users cannot log in
- Session validation failing
- Authentication endpoints returning errors

#### Quick Fixes
```bash
# 1. Check session table
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM sessions;"

# 2. Clear all sessions (forces re-login)
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "DELETE FROM sessions;"

# 3. Reset admin user if locked
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "
UPDATE users 
SET status = 'Active' 
WHERE username = 'admin';"

# 4. Restart application
sudo supervisorctl restart cvd
```

### 🟠 File System Full

#### Symptoms
- Disk usage at 100%
- Application cannot write files
- Log rotation failures

#### Immediate Actions
```bash
# 1. Check disk usage
df -h
du -sh /var/log/*
du -sh /opt/cvd/*

# 2. Clear log files
sudo truncate -s 0 /var/log/nginx/access.log
sudo truncate -s 0 /var/log/nginx/error.log
sudo truncate -s 0 /var/log/cvd/application.log

# 3. Clean old backups
sudo find /opt/cvd/backups -name "*.db.gz" -mtime +7 -delete

# 4. Emergency space cleanup
sudo apt autoclean
sudo apt autoremove

# 5. Clean temporary files
sudo rm -rf /tmp/*
```

---

## Medium Priority Issues

### 🟡 API Endpoints Failing

#### Symptoms
- Specific API calls returning errors
- Frontend functionality partially broken
- Database queries timing out

#### Diagnosis & Fixes
```bash
# 1. Test specific endpoints
curl -v http://localhost:5000/api/devices
curl -v http://localhost:5000/api/auth/current-user

# 2. Check application logs
tail -50 /var/log/cvd/application.log | grep -i error

# 3. Test database connectivity
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM devices;"

# 4. Restart application if needed
sudo supervisorctl restart cvd
```

### 🟡 Frontend Loading Issues

#### Symptoms
- Pages not loading correctly
- JavaScript errors
- Static files not serving

#### Quick Fixes
```bash
# 1. Check nginx status and logs
sudo systemctl status nginx
tail -20 /var/log/nginx/error.log

# 2. Test static file serving
curl -I http://localhost/api.js
curl -I http://localhost/index.html

# 3. Check file permissions
ls -la /opt/cvd/index.html
ls -la /opt/cvd/pages/

# 4. Restart nginx if needed
sudo systemctl restart nginx
```

---

## Data Recovery Procedures

### Emergency Database Recovery

#### From Recent Backup
```bash
# 1. Stop application
sudo supervisorctl stop cvd

# 2. Backup current (potentially corrupted) database
sudo -u cvd cp /opt/cvd/data/cvd.db /opt/cvd/data/cvd.db.corrupted

# 3. List available backups
ls -la /opt/cvd/backups/cvd_*.db.gz

# 4. Restore from most recent backup
BACKUP_FILE="cvd_20250812_020000.db.gz"  # Replace with actual file
sudo -u cvd cp "/opt/cvd/backups/$BACKUP_FILE" /tmp/
gunzip "/tmp/${BACKUP_FILE}"
sudo -u cvd cp "/tmp/${BACKUP_FILE%.gz}" /opt/cvd/data/cvd.db

# 5. Verify restoration
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "PRAGMA integrity_check;"
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db "SELECT COUNT(*) FROM users;"

# 6. Restart application
sudo supervisorctl start cvd
```

#### Manual Data Salvage
```bash
# If no recent backup available
sudo -u cvd sqlite3 /opt/cvd/data/cvd.db.corrupted

# Try to extract what you can
.output /tmp/users_recovery.sql
.dump users

.output /tmp/devices_recovery.sql  
.dump devices

# Create new database and import salvaged data
sudo -u cvd sqlite3 /opt/cvd/data/cvd_new.db < /tmp/users_recovery.sql
# Repeat for other critical tables
```

### Configuration Recovery

#### Application Files
```bash
# Restore from version control or backup
sudo rsync -avz /opt/cvd/backup/app.py /opt/cvd/
sudo rsync -avz /opt/cvd/backup/auth.py /opt/cvd/
sudo chown cvd:cvd /opt/cvd/*.py

# Restore frontend files
sudo rsync -avz /opt/cvd/backup/pages/ /opt/cvd/pages/
sudo chown -R cvd:cvd /opt/cvd/pages/
```

#### System Configuration
```bash
# Restore nginx config
sudo cp /etc/nginx/sites-available/cvd.backup /etc/nginx/sites-available/cvd
sudo nginx -t && sudo systemctl restart nginx

# Restore supervisor config
sudo cp /etc/supervisor/conf.d/cvd.conf.backup /etc/supervisor/conf.d/cvd.conf
sudo supervisorctl reread && sudo supervisorctl update
```

---

## Communication Templates

### Critical Incident Notification
```
SUBJECT: [CRITICAL] CVD System Emergency - Action Required

CVD System Status: DOWN
Incident Start: [TIMESTAMP]
Severity: CRITICAL
Impact: Complete system unavailable

Actions Taken:
- [List immediate actions]

Estimated Resolution: [TIME]
Next Update: [TIME]

Contact: [EMERGENCY_CONTACT]
```

### Status Update Template
```
SUBJECT: [UPDATE] CVD System Incident - [STATUS]

Incident Update: [TIMESTAMP]
Current Status: [INVESTIGATING/RESOLVING/RESOLVED]

Progress:
- [What has been done]
- [What is currently being done]
- [What will be done next]

Estimated Resolution: [UPDATED_TIME]
Next Update: [TIME]
```

### All Clear Notification
```
SUBJECT: [RESOLVED] CVD System Restored

Incident Resolution: [TIMESTAMP]
Duration: [TOTAL_TIME]
Root Cause: [BRIEF_DESCRIPTION]

Resolution:
- [What was done to fix]
- [What was done to prevent recurrence]

Post-Incident Actions:
- [Monitoring plan]
- [Follow-up items]

System Status: FULLY OPERATIONAL
```

---

## Emergency Contacts & Resources

### Internal Escalation
1. **System Administrator** (Primary)
2. **Technical Lead** (Secondary)
3. **Department Manager** (Business Impact)

### External Resources
- **Cloud Provider Support** (if applicable)
- **ISP Technical Support**
- **Security Incident Response Team**

### Key Information Quick Access
```bash
# System info
hostname
whoami
uname -a
ip addr show

# Service status
sudo systemctl list-units --failed
sudo supervisorctl status

# Resource usage
free -h && df -h && uptime
```

### Emergency Scripts Location
```
/opt/cvd/scripts/emergency/
├── health_check.sh
├── backup_now.sh
├── restart_all.sh
├── database_repair.sh
└── emergency_contacts.txt
```

---

## Prevention Checklist

### Daily Monitoring
- [ ] Check system resource usage
- [ ] Review error logs
- [ ] Verify backup completion
- [ ] Test critical functionality

### Weekly Tasks
- [ ] Database integrity check
- [ ] Security audit log review
- [ ] Performance baseline comparison
- [ ] Update monitoring thresholds

### Monthly Tasks
- [ ] Full system backup test
- [ ] Disaster recovery drill
- [ ] Security patches review
- [ ] Capacity planning assessment

---

*Keep this guide accessible and update contact information regularly.*