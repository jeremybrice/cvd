-- Security Enhancement Migration
-- Adds tables and columns for advanced threat detection

-- Step 1: IP Block table for brute force protection
CREATE TABLE IF NOT EXISTS ip_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    blocked_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    reason TEXT,
    blocked_by TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Index for quick lookups
    UNIQUE(ip_address, expires_at)
);

CREATE INDEX IF NOT EXISTS idx_ip_blocks_active ON ip_blocks(ip_address, expires_at);

-- Step 2: Enhanced activity alerts metadata
-- Update existing activity_alerts table to support new alert types
ALTER TABLE activity_alerts ADD COLUMN ip_address TEXT;
ALTER TABLE activity_alerts ADD COLUMN endpoint TEXT;
ALTER TABLE activity_alerts ADD COLUMN method TEXT;
ALTER TABLE activity_alerts ADD COLUMN data_rows INTEGER;

-- Step 3: Data export tracking table
CREATE TABLE IF NOT EXISTS data_export_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    endpoint TEXT NOT NULL,
    export_type TEXT, -- csv|json|pdf|excel
    row_count INTEGER,
    data_size_bytes INTEGER,
    query_params TEXT, -- JSON of query parameters
    export_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    session_id TEXT,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_export_log_user ON data_export_log(user_id, export_timestamp);
CREATE INDEX IF NOT EXISTS idx_export_log_endpoint ON data_export_log(endpoint, export_timestamp);

-- Step 4: Geographic location tracking
CREATE TABLE IF NOT EXISTS user_location_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ip_address TEXT NOT NULL,
    country TEXT,
    region TEXT,
    city TEXT,
    latitude REAL,
    longitude REAL,
    isp TEXT,
    is_vpn BOOLEAN DEFAULT 0,
    is_proxy BOOLEAN DEFAULT 0,
    login_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_location_user ON user_location_history(user_id, login_timestamp);
CREATE INDEX IF NOT EXISTS idx_location_ip ON user_location_history(ip_address);

-- Step 5: Sensitive data access log
CREATE TABLE IF NOT EXISTS sensitive_data_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resource_type TEXT NOT NULL, -- sales_report|financial_metrics|user_data|audit_log
    resource_id TEXT,
    access_type TEXT NOT NULL, -- view|export|modify|delete
    endpoint TEXT NOT NULL,
    access_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_after_hours BOOLEAN DEFAULT 0,
    is_weekend BOOLEAN DEFAULT 0,
    ip_address TEXT,
    session_id TEXT,
    metadata TEXT, -- JSON for additional context
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_sensitive_user ON sensitive_data_access_log(user_id, access_timestamp);
CREATE INDEX IF NOT EXISTS idx_sensitive_resource ON sensitive_data_access_log(resource_type, access_timestamp);

-- Step 6: Security incident tracking
CREATE TABLE IF NOT EXISTS security_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_type TEXT NOT NULL, -- brute_force|data_breach|privilege_escalation|suspicious_activity
    severity TEXT NOT NULL, -- low|medium|high|critical
    status TEXT DEFAULT 'open', -- open|investigating|mitigated|closed
    affected_users TEXT, -- JSON array of user IDs
    affected_systems TEXT, -- JSON array of affected systems/endpoints
    description TEXT NOT NULL,
    detection_method TEXT, -- automated|reported|audit
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_by INTEGER,
    resolved_by INTEGER,
    
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (resolved_by) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_incidents_status ON security_incidents(status, severity);
CREATE INDEX IF NOT EXISTS idx_incidents_type ON security_incidents(incident_type, detected_at);

-- Step 7: Add security configuration settings
INSERT OR IGNORE INTO system_config (key, value, description) VALUES
    ('security_brute_force_enabled', 'true', 'Enable brute force attack detection'),
    ('security_brute_force_max_attempts', '5', 'Maximum failed login attempts before blocking'),
    ('security_brute_force_window_minutes', '10', 'Time window for counting failed attempts'),
    ('security_brute_force_lockout_minutes', '30', 'Duration of IP block after brute force detection'),
    
    ('security_export_monitoring_enabled', 'true', 'Enable data export monitoring'),
    ('security_export_max_per_hour', '10', 'Maximum exports per user per hour'),
    ('security_export_max_rows_per_hour', '10000', 'Maximum total rows exported per hour'),
    ('security_export_bulk_threshold', '1000', 'Rows threshold for bulk export alert'),
    
    ('security_geo_anomaly_enabled', 'true', 'Enable geographic anomaly detection'),
    ('security_geo_max_distance_km', '500', 'Maximum travel distance between logins'),
    ('security_geo_time_threshold_hours', '2', 'Time threshold for impossible travel detection'),
    
    ('security_sensitive_monitoring_enabled', 'true', 'Enable sensitive data access monitoring'),
    ('security_business_hours_start', '6', 'Business hours start (24-hour format)'),
    ('security_business_hours_end', '20', 'Business hours end (24-hour format)'),
    
    ('security_privilege_monitoring_enabled', 'true', 'Enable privilege escalation detection'),
    ('security_incident_auto_create', 'true', 'Automatically create incidents for critical alerts');

-- Step 8: Create views for security dashboards
CREATE VIEW IF NOT EXISTS security_overview AS
SELECT 
    (SELECT COUNT(*) FROM ip_blocks WHERE expires_at > datetime('now')) as active_ip_blocks,
    (SELECT COUNT(*) FROM activity_alerts WHERE status = 'pending') as pending_alerts,
    (SELECT COUNT(*) FROM security_incidents WHERE status != 'closed') as open_incidents,
    (SELECT COUNT(*) FROM user_activity_log WHERE timestamp > datetime('now', '-1 hour')) as hourly_activity,
    (SELECT COUNT(DISTINCT user_id) FROM sessions WHERE expires_at > datetime('now')) as active_users,
    (SELECT COUNT(*) FROM audit_log WHERE action LIKE 'failed_%' AND created_at > datetime('now', '-24 hours')) as daily_failed_actions;

CREATE VIEW IF NOT EXISTS high_risk_users AS
SELECT 
    u.id,
    u.username,
    u.role,
    u.failed_login_attempts,
    COUNT(DISTINCT al.id) as recent_alerts,
    COUNT(DISTINCT sd.id) as sensitive_accesses,
    MAX(al.created_at) as last_alert
FROM users u
LEFT JOIN activity_alerts al ON u.id = al.user_id AND al.created_at > datetime('now', '-7 days')
LEFT JOIN sensitive_data_access_log sd ON u.id = sd.user_id AND sd.access_timestamp > datetime('now', '-7 days')
WHERE u.failed_login_attempts > 0 
   OR al.id IS NOT NULL 
   OR sd.id IS NOT NULL
GROUP BY u.id
ORDER BY recent_alerts DESC, sensitive_accesses DESC;

-- Step 9: Add triggers for automatic incident creation
CREATE TRIGGER IF NOT EXISTS create_incident_on_critical_alert
AFTER INSERT ON activity_alerts
WHEN NEW.severity = 'critical' AND (SELECT value FROM system_config WHERE key = 'security_incident_auto_create') = 'true'
BEGIN
    INSERT INTO security_incidents (
        incident_type,
        severity,
        status,
        affected_users,
        description,
        detection_method
    ) VALUES (
        NEW.alert_type,
        NEW.severity,
        'open',
        json_array(NEW.user_id),
        'Auto-generated from critical alert: ' || NEW.description,
        'automated'
    );
END;

-- Step 10: Migration metadata
INSERT INTO migrations (name, applied_at) VALUES ('003_security_enhancements', datetime('now'));