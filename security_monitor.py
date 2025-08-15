"""
Enhanced Security Monitoring Module for CVD Application
Provides advanced threat detection and alerting capabilities
"""

import sqlite3
import json
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import re

logger = logging.getLogger(__name__)

class SecurityMonitor:
    """Advanced security monitoring and threat detection"""
    
    def __init__(self, db_path, activity_tracker):
        self.db_path = db_path
        self.activity_tracker = activity_tracker
        
        # Brute force detection thresholds
        self.brute_force_config = {
            'max_failed_attempts': 5,           # Per IP in time window
            'time_window_minutes': 10,          # Rolling window
            'lockout_duration_minutes': 30,     # IP ban duration
            'alert_threshold': 3,               # Failed logins before alert
            'distributed_threshold': 10         # Failed logins across multiple IPs
        }
        
        # Data export monitoring thresholds
        self.export_config = {
            'max_exports_per_hour': 10,         # Per user
            'max_data_rows_per_hour': 10000,    # Total rows exported
            'sensitive_endpoints': [
                '/api/sales',
                '/api/planograms/export',
                '/api/metrics',
                '/api/devices/metrics'
            ],
            'alert_on_bulk': True,
            'bulk_threshold': 1000              # Rows in single request
        }
        
        # Privilege escalation detection
        self.privilege_config = {
            'monitor_role_changes': True,
            'monitor_admin_endpoints': True,
            'alert_on_unauthorized': True,
            'admin_endpoints': [
                '/api/users',
                '/api/admin',
                '/api/system-config',
                '/api/audit-log'
            ]
        }
        
        # Geographic anomaly detection
        self.geo_config = {
            'enabled': True,
            'max_distance_km': 500,             # Max distance between logins
            'time_threshold_hours': 2,          # Time between distant logins
            'track_vpn_patterns': True,
            'known_vpn_ranges': []              # Can be populated with known VPN IP ranges
        }
        
        # Sensitive data access monitoring
        self.sensitive_data_config = {
            'monitor_financial': True,
            'monitor_user_data': True,
            'alert_after_hours': True,
            'business_hours': (6, 20),          # 6 AM to 8 PM
            'sensitive_patterns': [
                r'/api/sales.*report',
                r'/api/metrics/financial',
                r'/api/users/.*/export',
                r'/api/audit-log'
            ]
        }
        
        # In-memory caches for performance
        self.failed_login_cache = defaultdict(list)  # IP -> [(timestamp, user_id)]
        self.export_cache = defaultdict(list)        # user_id -> [(timestamp, rows)]
        self.location_cache = {}                     # user_id -> last_location
        self.cache_cleanup_interval = 300            # 5 minutes
        self.last_cleanup = time.time()
    
    def check_brute_force(self, ip_address, user_id=None, success=False):
        """
        Monitor for brute force attacks
        Returns: (is_blocked, should_alert, alert_details)
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=self.brute_force_config['time_window_minutes'])
        
        # Clean up old entries from cache
        self._cleanup_cache()
        
        if success:
            # Clear failed attempts on successful login
            if ip_address in self.failed_login_cache:
                del self.failed_login_cache[ip_address]
            return False, False, None
        
        # Add failed attempt to cache
        self.failed_login_cache[ip_address].append((now, user_id))
        
        # Filter attempts within time window
        recent_attempts = [
            attempt for attempt in self.failed_login_cache[ip_address]
            if attempt[0] > window_start
        ]
        self.failed_login_cache[ip_address] = recent_attempts
        
        # Check thresholds
        attempt_count = len(recent_attempts)
        
        # Check if IP should be blocked
        is_blocked = attempt_count >= self.brute_force_config['max_failed_attempts']
        
        # Check if alert should be triggered
        should_alert = attempt_count >= self.brute_force_config['alert_threshold']
        
        alert_details = None
        if should_alert:
            # Check for distributed attack pattern
            total_failed = sum(
                len(attempts) for attempts in self.failed_login_cache.values()
            )
            
            severity = 'critical' if is_blocked else 'warning'
            if total_failed >= self.brute_force_config['distributed_threshold']:
                severity = 'critical'
                
            alert_details = {
                'type': 'brute_force',
                'severity': severity,
                'ip_address': ip_address,
                'attempt_count': attempt_count,
                'user_targets': list(set(a[1] for a in recent_attempts if a[1])),
                'is_distributed': total_failed >= self.brute_force_config['distributed_threshold'],
                'total_failed_attempts': total_failed,
                'description': f'Brute force attack detected from {ip_address}: {attempt_count} failed attempts'
            }
        
        # Store block in database if needed
        if is_blocked:
            self._store_ip_block(ip_address, now)
        
        return is_blocked, should_alert, alert_details
    
    def check_data_export(self, user_id, endpoint, row_count=None, data_size=None):
        """
        Monitor for excessive data exports and potential data exfiltration
        Returns: (is_excessive, should_alert, alert_details)
        """
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Add to cache
        self.export_cache[user_id].append((now, endpoint, row_count or 0))
        
        # Filter recent exports
        recent_exports = [
            exp for exp in self.export_cache[user_id]
            if exp[0] > hour_ago
        ]
        self.export_cache[user_id] = recent_exports
        
        # Calculate metrics
        export_count = len(recent_exports)
        total_rows = sum(exp[2] for exp in recent_exports)
        
        # Check if this is a sensitive endpoint
        is_sensitive = any(
            endpoint.startswith(sensitive_ep) 
            for sensitive_ep in self.export_config['sensitive_endpoints']
        )
        
        # Check thresholds
        is_excessive = (
            export_count > self.export_config['max_exports_per_hour'] or
            total_rows > self.export_config['max_data_rows_per_hour'] or
            (row_count and row_count > self.export_config['bulk_threshold'])
        )
        
        should_alert = is_excessive and is_sensitive
        
        alert_details = None
        if should_alert:
            alert_details = {
                'type': 'data_export',
                'severity': 'warning' if export_count < 20 else 'critical',
                'user_id': user_id,
                'endpoint': endpoint,
                'export_count': export_count,
                'total_rows_exported': total_rows,
                'current_export_rows': row_count,
                'description': f'Excessive data export detected: {export_count} exports, {total_rows} total rows'
            }
        
        return is_excessive, should_alert, alert_details
    
    def check_privilege_escalation(self, user_id, user_role, endpoint, method='GET'):
        """
        Monitor for unauthorized access to admin functions
        Returns: (is_unauthorized, should_alert, alert_details)
        """
        # Check if endpoint is admin-only
        is_admin_endpoint = any(
            endpoint.startswith(admin_ep)
            for admin_ep in self.privilege_config['admin_endpoints']
        )
        
        if not is_admin_endpoint:
            return False, False, None
        
        # Check if user has appropriate role
        is_unauthorized = user_role not in ['admin', 'manager'] and method != 'GET'
        
        should_alert = is_unauthorized and self.privilege_config['alert_on_unauthorized']
        
        alert_details = None
        if should_alert:
            alert_details = {
                'type': 'privilege_escalation',
                'severity': 'critical',
                'user_id': user_id,
                'user_role': user_role,
                'endpoint': endpoint,
                'method': method,
                'description': f'Unauthorized admin access attempt by {user_role} user to {endpoint}'
            }
        
        return is_unauthorized, should_alert, alert_details
    
    def check_geographic_anomaly(self, user_id, ip_address, user_agent=None):
        """
        Detect impossible travel / geographic anomalies
        Returns: (is_anomaly, should_alert, alert_details)
        """
        if not self.geo_config['enabled']:
            return False, False, None
        
        # Get IP geolocation (simplified - would integrate with GeoIP service)
        current_location = self._get_ip_location(ip_address)
        
        if not current_location:
            return False, False, None
        
        # Check last known location
        if user_id not in self.location_cache:
            self.location_cache[user_id] = {
                'location': current_location,
                'timestamp': datetime.now(),
                'ip': ip_address
            }
            return False, False, None
        
        last_info = self.location_cache[user_id]
        time_diff = (datetime.now() - last_info['timestamp']).total_seconds() / 3600  # hours
        
        # Calculate distance (simplified)
        distance = self._calculate_distance(
            last_info['location'],
            current_location
        )
        
        # Check for impossible travel
        max_possible_distance = time_diff * 900  # Assuming max 900 km/h (flight speed)
        is_anomaly = distance > max_possible_distance and time_diff < self.geo_config['time_threshold_hours']
        
        # Update cache
        self.location_cache[user_id] = {
            'location': current_location,
            'timestamp': datetime.now(),
            'ip': ip_address
        }
        
        should_alert = is_anomaly
        
        alert_details = None
        if should_alert:
            alert_details = {
                'type': 'geographic_anomaly',
                'severity': 'warning',
                'user_id': user_id,
                'current_ip': ip_address,
                'previous_ip': last_info['ip'],
                'distance_km': distance,
                'time_hours': time_diff,
                'description': f'Impossible travel detected: {distance:.0f}km in {time_diff:.1f} hours'
            }
        
        return is_anomaly, should_alert, alert_details
    
    def check_sensitive_data_access(self, user_id, endpoint, timestamp=None):
        """
        Monitor access to sensitive data, especially outside business hours
        Returns: (is_sensitive, should_alert, alert_details)
        """
        timestamp = timestamp or datetime.now()
        
        # Check if endpoint contains sensitive data
        is_sensitive = any(
            re.match(pattern, endpoint)
            for pattern in self.sensitive_data_config['sensitive_patterns']
        )
        
        if not is_sensitive:
            return False, False, None
        
        # Check if access is after hours
        hour = timestamp.hour
        is_after_hours = (
            hour < self.sensitive_data_config['business_hours'][0] or
            hour >= self.sensitive_data_config['business_hours'][1]
        )
        
        # Check if it's weekend
        is_weekend = timestamp.weekday() >= 5
        
        should_alert = (
            is_sensitive and 
            (is_after_hours or is_weekend) and 
            self.sensitive_data_config['alert_after_hours']
        )
        
        alert_details = None
        if should_alert:
            alert_details = {
                'type': 'sensitive_data_access',
                'severity': 'info' if not is_weekend else 'warning',
                'user_id': user_id,
                'endpoint': endpoint,
                'access_time': timestamp.isoformat(),
                'is_after_hours': is_after_hours,
                'is_weekend': is_weekend,
                'description': f'Sensitive data accessed {"after hours" if is_after_hours else "on weekend"}: {endpoint}'
            }
        
        return is_sensitive, should_alert, alert_details
    
    def _cleanup_cache(self):
        """Periodically clean up old cache entries"""
        if time.time() - self.last_cleanup < self.cache_cleanup_interval:
            return
        
        now = datetime.now()
        window = timedelta(minutes=self.brute_force_config['time_window_minutes'])
        
        # Clean failed login cache
        for ip in list(self.failed_login_cache.keys()):
            self.failed_login_cache[ip] = [
                attempt for attempt in self.failed_login_cache[ip]
                if attempt[0] > now - window
            ]
            if not self.failed_login_cache[ip]:
                del self.failed_login_cache[ip]
        
        # Clean export cache
        hour_ago = now - timedelta(hours=1)
        for user_id in list(self.export_cache.keys()):
            self.export_cache[user_id] = [
                exp for exp in self.export_cache[user_id]
                if exp[0] > hour_ago
            ]
            if not self.export_cache[user_id]:
                del self.export_cache[user_id]
        
        self.last_cleanup = time.time()
    
    def _store_ip_block(self, ip_address, timestamp):
        """Store IP block in database"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    blocked_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            expires_at = timestamp + timedelta(
                minutes=self.brute_force_config['lockout_duration_minutes']
            )
            
            cursor.execute('''
                INSERT INTO ip_blocks (ip_address, blocked_at, expires_at, reason)
                VALUES (?, ?, ?, ?)
            ''', (ip_address, timestamp, expires_at, 'Brute force attack'))
            
            db.commit()
            db.close()
            
            logger.info(f'Blocked IP {ip_address} until {expires_at}')
            
        except Exception as e:
            logger.error(f'Failed to store IP block: {e}')
    
    def _get_ip_location(self, ip_address):
        """
        Get geographic location from IP address
        This is a simplified implementation - in production, integrate with GeoIP2 or similar
        """
        # For now, return a mock location based on IP hash
        # In production, use MaxMind GeoIP2 or similar service
        
        if ip_address.startswith('127.') or ip_address.startswith('192.168.'):
            return {'lat': 0, 'lon': 0, 'city': 'Local'}
        
        # Mock implementation - hash IP to generate consistent fake coordinates
        ip_hash = hashlib.md5(ip_address.encode()).hexdigest()
        lat = (int(ip_hash[:8], 16) % 180) - 90
        lon = (int(ip_hash[8:16], 16) % 360) - 180
        
        return {'lat': lat, 'lon': lon, 'city': 'Unknown'}
    
    def _calculate_distance(self, loc1, loc2):
        """
        Calculate distance between two locations in kilometers
        Using simplified Haversine formula
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = radians(loc1['lat']), radians(loc1['lon'])
        lat2, lon2 = radians(loc2['lat']), radians(loc2['lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def is_ip_blocked(self, ip_address):
        """Check if an IP address is currently blocked"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            # Check for active blocks
            cursor.execute('''
                SELECT id FROM ip_blocks
                WHERE ip_address = ? 
                AND expires_at > datetime('now')
                ORDER BY expires_at DESC
                LIMIT 1
            ''', (ip_address,))
            
            result = cursor.fetchone()
            db.close()
            
            return result is not None
            
        except Exception as e:
            logger.error(f'Failed to check IP block: {e}')
            return False
    
    def create_security_alert(self, alert_details):
        """Create a security alert in the database"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            # Store in activity_alerts table with enhanced metadata
            cursor.execute('''
                INSERT INTO activity_alerts 
                (alert_type, severity, user_id, session_id, description, metadata, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
            ''', (
                alert_details['type'],
                alert_details['severity'],
                alert_details.get('user_id'),
                alert_details.get('session_id'),
                alert_details['description'],
                json.dumps(alert_details)
            ))
            
            db.commit()
            db.close()
            
            logger.warning(f'Security alert created: {alert_details["type"]} - {alert_details["description"]}')
            
            # Could also trigger notifications here (email, Slack, etc.)
            self._send_alert_notification(alert_details)
            
        except Exception as e:
            logger.error(f'Failed to create security alert: {e}')
    
    def _send_alert_notification(self, alert_details):
        """Send alert notifications (email, Slack, etc.)"""
        # Placeholder for notification integration
        # In production, integrate with notification services
        
        if alert_details['severity'] == 'critical':
            # Send immediate notification for critical alerts
            logger.critical(f'CRITICAL SECURITY ALERT: {alert_details["description"]}')
            # TODO: Send email to security team
            # TODO: Post to Slack security channel
            # TODO: Create PagerDuty incident if configured