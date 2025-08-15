---
title: "CVD Security Features Guide"
author: "CVD Security Team"
category: "System Administration"
tags: ["security", "monitoring", "authentication", "threat-detection", "system-administration"]
difficulty: "Advanced"
last_updated: "2025-08-07T10:00:00Z"
description: "Comprehensive guide to all security features implemented in the CVD system including activity monitoring, brute force protection, data export monitoring, and threat detection systems."
---

# CVD Security Features Guide

The CVD (Vision Device Configuration) application implements a comprehensive security framework designed to protect against various types of threats and unauthorized access. This guide provides detailed information about all security features, their configuration, and management procedures.

## Table of Contents

1. [Security Framework Overview](#security-framework-overview)
2. [Activity Monitoring System](#activity-monitoring-system)
3. [Brute Force Protection](#brute-force-protection)
4. [Data Export Monitoring](#data-export-monitoring)
5. [Privilege Escalation Detection](#privilege-escalation-detection)
6. [Geographic Anomaly Detection](#geographic-anomaly-detection)
7. [Sensitive Data Access Monitoring](#sensitive-data-access-monitoring)
8. [Authentication & Authorization](#authentication--authorization)
9. [Security Dashboard](#security-dashboard)
10. [Configuration Management](#configuration-management)
11. [Alert Management](#alert-management)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

## Security Framework Overview

The CVD security system consists of several interconnected components that provide comprehensive protection:

### Core Security Components

- **ActivityTracker**: Real-time user activity monitoring with performance optimization
- **SecurityMonitor**: Advanced threat detection and alerting system
- **AuthManager**: Session-based authentication with role-based access control
- **SecurityDashboard**: Centralized security monitoring interface
- **Alert System**: Automated security alert generation and notification

### Security Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Request   │───▶│  Auth Manager   │───▶│ Activity Tracker│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                  │                      │
                                  ▼                      ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │Security Monitor │───▶│   Alert System  │
                       └─────────────────┘    └─────────────────┘
                                  │                      │
                                  ▼                      ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Database      │    │  Notifications  │
                       │   Logging       │    │  (Email/Slack)  │
                       └─────────────────┘    └─────────────────┘
```

### Database Security Tables

The security system uses several specialized database tables:

- `user_activity_log` - Detailed activity tracking
- `activity_alerts` - Security alerts and incidents
- `sessions` - Active user sessions with security metadata
- `ip_blocks` - Blocked IP addresses from brute force attempts
- `audit_log` - System-wide audit trail
- `security_overview` - Aggregated security metrics

## Activity Monitoring System

The activity monitoring system provides real-time tracking of user behavior to detect suspicious patterns and maintain audit trails.

### Real-Time Session Tracking

**Features:**
- Tracks all user interactions with page-level granularity
- Monitors API calls, file downloads, and navigation patterns
- Maintains device type detection (mobile, desktop, tablet)
- Records response times and performance metrics

**Implementation:**
- Asynchronous processing to minimize performance impact
- In-memory caching for real-time dashboard updates
- Background queue processing for database writes
- Automatic cleanup of old tracking data

### User Activity Logging

**Tracked Information:**
- Page visits and navigation patterns
- API endpoint access with duration metrics
- File downloads and data exports
- Session duration and idle time
- Device information and user agent details
- IP addresses and geographic indicators

**Configuration Options:**
```python
# Activity tracking settings (configurable via system_config table)
activity_monitoring_enabled = True
activity_retention_days = 90
activity_tracking_excluded_pages = ['/health', '/static/*']
```

### Alert Generation

The system automatically generates alerts for:

1. **Concurrent Sessions**: Multiple active sessions for one user
   - Default threshold: 2 concurrent sessions
   - Alert severity: Warning

2. **Rapid Navigation**: Potential bot activity detection
   - Default threshold: 20 pages in 1 minute
   - Uses sliding window calculation
   - Alert severity: Warning

3. **After-Hours Access**: Access outside business hours
   - Default business hours: 6 AM - 8 PM
   - One alert per session per day limit
   - Alert severity: Info

### Performance Optimization

**Caching Strategy:**
- 30-second TTL for active session cache
- Batch processing of activity records (up to 100 per batch)
- Background thread processing to avoid blocking requests
- Periodic cache cleanup every 5 minutes

**Resource Management:**
- Queue size limit: 1,000 pending activities
- Worker thread processes activities every 0.5 seconds
- Database connection pooling for batch operations

## Brute Force Protection

Comprehensive protection against password-based attacks with intelligent detection algorithms.

### Attack Detection

**Multi-Layer Detection:**
- Per-IP tracking of failed login attempts
- User-specific failed attempt monitoring
- Distributed attack pattern recognition
- Account lockout mechanisms

**Configuration Thresholds:**
```python
brute_force_config = {
    'max_failed_attempts': 5,           # Per IP in time window
    'time_window_minutes': 10,          # Rolling window
    'lockout_duration_minutes': 30,     # IP ban duration
    'alert_threshold': 3,               # Failed logins before alert
    'distributed_threshold': 10         # Failed logins across multiple IPs
}
```

### IP Blocking System

**Automatic Blocking:**
- IPs blocked after 5 failed attempts in 10 minutes
- 30-minute automatic ban duration
- Persistent storage in `ip_blocks` table
- Automatic cleanup of expired blocks

**Block Management:**
- Real-time IP block checking on login attempts
- Manual IP unblock capability for administrators
- Block history and audit trail
- Support for whitelisting trusted IPs

### Attack Pattern Recognition

**Distributed Attack Detection:**
- Monitors failed attempts across multiple IP addresses
- Escalates alert severity when distributed patterns detected
- Tracks user targeting patterns
- Generates critical alerts for coordinated attacks

**Smart Reset Logic:**
- Clears failed attempt counters on successful login
- Progressive lockout periods for repeat offenders
- User account lockout after multiple IP-based attempts

## Data Export Monitoring

Protects against data exfiltration by monitoring and alerting on excessive data exports.

### Export Tracking

**Monitored Endpoints:**
- `/api/sales` - Sales data exports
- `/api/planograms/export` - Planogram configurations
- `/api/metrics` - Performance metrics
- `/api/devices/metrics` - Device telemetry

**Tracking Metrics:**
- Number of exports per hour (per user)
- Total data volume exported (row counts)
- Individual export sizes
- Export frequency patterns

### Alert Triggers

**Volume-Based Alerts:**
- More than 10 exports per hour per user
- More than 10,000 total rows exported per hour
- Single export exceeding 1,000 rows (bulk download)

**Sensitivity Levels:**
- Regular endpoints: Basic monitoring
- Sensitive endpoints: Enhanced monitoring with immediate alerts
- Financial data: Critical alert classification

### Configuration Options

```python
export_config = {
    'max_exports_per_hour': 10,         # Per user limit
    'max_data_rows_per_hour': 10000,    # Total rows limit
    'alert_on_bulk': True,              # Enable bulk download alerts
    'bulk_threshold': 1000              # Rows for bulk classification
}
```

## Privilege Escalation Detection

Monitors and prevents unauthorized access to administrative functions.

### Real-Time Authorization Validation

**Protected Endpoints:**
- `/api/users` - User management functions
- `/api/admin` - Administrative controls
- `/api/system-config` - System configuration
- `/api/audit-log` - Audit log access

**Validation Logic:**
- Real-time role verification on each request
- Method-specific permissions (GET vs POST/PUT/DELETE)
- Immediate blocking of unauthorized attempts
- 403 Forbidden responses for violations

### Administrative Access Monitoring

**Access Patterns:**
- Tracks all admin endpoint access attempts
- Monitors role changes and permission modifications
- Logs administrative action details
- Maintains complete audit trail

**Alert Generation:**
- Immediate alerts for unauthorized admin access attempts
- Critical severity for privilege escalation attempts
- User context and session information included
- Automatic security team notifications

## Geographic Anomaly Detection

Detects impossible travel patterns and geographic inconsistencies in user logins.

### Location Tracking

**IP Geolocation Integration:**
- Ready for MaxMind GeoIP2 integration
- Fallback mock implementation for development
- Latitude/longitude coordinate tracking
- City and country-level location data

**Travel Analysis:**
- Calculates distance between login locations
- Compares against physically possible travel times
- Maximum travel speed threshold: 900 km/hour
- Time window analysis: 2 hours minimum

### Anomaly Detection Algorithm

**Impossible Travel Logic:**
```python
# Calculate if travel is physically possible
max_possible_distance = time_diff_hours * 900  # Max flight speed
is_anomaly = distance_km > max_possible_distance and time_diff < 2_hours
```

**Alert Conditions:**
- Distance > 500km between locations
- Time between logins < 2 hours
- Generates warning-level alerts
- Includes travel metrics in alert details

### Future Enhancements

**VPN Detection:**
- Framework for VPN IP range detection
- Known VPN provider identification
- Enhanced risk scoring for VPN usage
- Configurable VPN policy enforcement

## Sensitive Data Access Monitoring

Monitors access to confidential information, especially during non-business hours.

### Data Classification

**Sensitive Data Patterns:**
```regex
/api/sales.*report          # Sales reports
/api/metrics/financial      # Financial metrics
/api/users/.*/export        # User data exports
/api/audit-log             # System audit logs
```

### Business Hours Enforcement

**Default Business Hours:** 6 AM - 8 PM (configurable)

**Monitoring Logic:**
- Tracks access time and date
- Identifies after-hours access (before 6 AM or after 8 PM)
- Monitors weekend access patterns
- Generates alerts for unusual access times

### Alert Severity Levels

- **Info**: After-hours access during weekdays
- **Warning**: Weekend access to sensitive data
- **Critical**: Multiple after-hours accesses (future enhancement)

## Authentication & Authorization

Comprehensive authentication system with role-based access control.

### Session Management

**Security Features:**
- Cryptographically secure session tokens
- Automatic session expiration
- Session invalidation on logout
- Concurrent session monitoring

**Session Security:**
- HTTP-only cookies (prevents XSS attacks)
- Secure flag for HTTPS connections
- Session fixation protection
- CSRF token integration

### Role-Based Access Control (RBAC)

**User Roles:**
1. **Admin**: Full system access
2. **Manager**: Management functions and reporting
3. **Driver**: Field operations and service orders
4. **Viewer**: Read-only access to data

**Permission Matrix:**
```
Endpoint               | Admin | Manager | Driver | Viewer
/api/users            |   ✓   |    ✗    |   ✗    |   ✗
/api/devices          |   ✓   |    ✓    |   ✓    |   ✓
/api/service-orders   |   ✓   |    ✓    |   ✓    |   ✗
/api/reports          |   ✓   |    ✓    |   ✗    |   ✓
```

### Password Security

**Security Policies:**
- Werkzeug secure password hashing
- Minimum complexity requirements
- Account lockout after failed attempts
- Password change audit logging

## Security Dashboard

Centralized security monitoring interface for administrators.

### Dashboard Components

**Real-Time Overview:**
- Active security alerts count
- Blocked IP addresses
- High-risk users identification
- Suspicious activity summary

**Metrics Display:**
- Failed login attempts (last 24 hours)
- Data export volumes
- Geographic anomalies detected
- Privilege escalation attempts

### API Endpoint

**GET** `/api/security/dashboard`

**Response Structure:**
```json
{
  "overview": {
    "active_alerts": 5,
    "blocked_ips": 2,
    "high_risk_users": 1,
    "total_activities": 1250
  },
  "recent_alerts": [
    {
      "id": 1,
      "alert_type": "brute_force",
      "severity": "critical",
      "description": "5 failed login attempts from 192.168.1.100",
      "created_at": "2025-08-07T09:30:00Z"
    }
  ],
  "metrics": {
    "failed_logins_24h": 12,
    "data_exports_today": 45,
    "geographic_anomalies": 1
  }
}
```

### Access Control

**Authorization Requirements:**
- Admin role required for full dashboard access
- Manager role has limited read-only access
- All security actions logged in audit trail

## Configuration Management

Security features can be configured through the system configuration interface.

### Configurable Parameters

**Activity Monitoring:**
```
activity_monitoring_enabled = true
activity_retention_days = 90
activity_alert_concurrent_sessions_threshold = 2
activity_alert_rapid_navigation_threshold = 20
```

**Brute Force Protection:**
```
brute_force_max_attempts = 5
brute_force_time_window_minutes = 10
brute_force_lockout_duration_minutes = 30
```

**Data Export Monitoring:**
```
data_export_max_per_hour = 10
data_export_max_rows_per_hour = 10000
data_export_bulk_threshold = 1000
```

### Configuration API

**GET** `/api/system-config/security`
**PUT** `/api/system-config/security`

Configuration changes are:
- Immediately applied without restart
- Logged in the audit trail
- Cached for performance (5-minute TTL)

## Alert Management

Comprehensive alert management system for security incidents.

### Alert Types and Severities

**Alert Types:**
- `brute_force` - Failed login attempts
- `concurrent_sessions` - Multiple active sessions
- `rapid_navigation` - Potential bot activity
- `after_hours` - Outside business hours access
- `data_export` - Excessive data exports
- `privilege_escalation` - Unauthorized admin access
- `geographic_anomaly` - Impossible travel detected
- `sensitive_data_access` - Confidential data access

**Severity Levels:**
- `info` - Informational alerts
- `warning` - Potential security issues
- `critical` - Immediate attention required

### Alert Actions

**Available Actions:**
1. **Acknowledge**: Mark alert as reviewed
2. **Resolve**: Mark issue as resolved
3. **Dismiss**: Remove false positive alerts
4. **Escalate**: Promote to higher severity (future)

**API Endpoints:**
- `POST /api/security/alerts/{id}/acknowledge`
- `POST /api/security/alerts/{id}/resolve`
- `POST /api/security/alerts/{id}/dismiss`

### Notification Integration

**Planned Integrations:**
- Email notifications for critical alerts
- Slack/Teams integration
- PagerDuty incident creation
- SMS alerts for high-priority events

**Current Implementation:**
- Database logging with structured metadata
- Application log entries
- Dashboard real-time updates

## Best Practices

### For System Administrators

1. **Regular Monitoring**
   - Review security dashboard daily
   - Investigate all critical alerts within 1 hour
   - Weekly review of blocked IPs and user activity patterns

2. **Configuration Management**
   - Adjust thresholds based on organizational usage patterns
   - Regularly update geographic IP databases
   - Monitor performance impact of security features

3. **Incident Response**
   - Document incident response procedures
   - Maintain contact list for security notifications
   - Regular testing of alert mechanisms

### For Security Teams

1. **Threat Intelligence**
   - Monitor for emerging attack patterns
   - Update security rules based on threat landscape
   - Correlation with external security feeds

2. **User Education**
   - Train users on security best practices
   - Communicate legitimate reasons for alerts
   - Establish clear escalation procedures

### Performance Considerations

1. **Resource Monitoring**
   - Monitor database growth from activity logging
   - Adjust retention periods based on storage capacity
   - Regular cleanup of expired data

2. **Scalability Planning**
   - Consider read replicas for large deployments
   - Plan for horizontal scaling of monitoring components
   - Cache optimization for high-traffic environments

## Troubleshooting

### Common Issues and Solutions

**Issue: High Volume of False Positive Alerts**

*Symptoms:* Excessive brute force alerts, rapid navigation alerts from legitimate users

*Solutions:*
1. Adjust thresholds in configuration:
   ```sql
   UPDATE system_config 
   SET value = '30' 
   WHERE key = 'activity_alert_rapid_navigation_threshold';
   ```
2. Add trusted IP ranges to whitelist
3. Review user training on proper navigation patterns

**Issue: Performance Impact from Activity Tracking**

*Symptoms:* Slow response times, high database CPU usage

*Solutions:*
1. Reduce activity retention period:
   ```sql
   UPDATE system_config 
   SET value = '30' 
   WHERE key = 'activity_retention_days';
   ```
2. Increase batch processing size in configuration
3. Implement database indexing optimization

**Issue: Geographic Anomaly False Positives**

*Symptoms:* Alerts for legitimate business travel

*Solutions:*
1. Adjust distance and time thresholds
2. Implement VPN detection to filter known corporate VPNs
3. Add business travel notification system

### Debugging Security Features

**Enable Debug Logging:**
```python
import logging
logging.getLogger('security_monitor').setLevel(logging.DEBUG)
logging.getLogger('activity_tracker').setLevel(logging.DEBUG)
```

**Database Queries for Investigation:**

**Recent Security Alerts:**
```sql
SELECT * FROM activity_alerts 
WHERE created_at > datetime('now', '-24 hours') 
ORDER BY created_at DESC;
```

**User Activity Summary:**
```sql
SELECT user_id, COUNT(*) as activity_count, 
       COUNT(DISTINCT session_id) as session_count
FROM user_activity_log 
WHERE timestamp > datetime('now', '-1 day')
GROUP BY user_id;
```

**Blocked IPs Status:**
```sql
SELECT ip_address, blocked_at, expires_at, reason 
FROM ip_blocks 
WHERE expires_at > datetime('now');
```

### Log File Locations

**Security Logs:**
- Application logs: `/var/log/cvd/security.log`
- Activity tracking: `/var/log/cvd/activity.log`
- Authentication events: `/var/log/cvd/auth.log`

**Log Rotation:**
- Daily rotation with 30-day retention
- Compressed archives for long-term storage
- Centralized logging integration available

## Getting Support

### Internal Support Channels

1. **Security Team**: security@company.com
2. **System Admin**: sysadmin@company.com
3. **Development Team**: dev-team@company.com

### Documentation Resources

- [User Management Guide](user-management-guide.md)
- [CVD System Overview](../getting-started/getting-started-overview.md)
- [API Documentation](https://docs.cvd.company.com/api)

### Emergency Response

**Critical Security Incidents:**
1. Immediately contact security team
2. Document incident details and affected systems
3. Preserve evidence (log files, database snapshots)
4. Follow incident response playbook

---

This security features guide provides comprehensive coverage of all implemented security measures in the CVD system. Regular review and updates of this documentation ensure that security procedures remain current and effective against evolving threats.