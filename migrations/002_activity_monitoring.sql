-- Migration: 002_activity_monitoring.sql
-- Purpose: Add user activity monitoring tables and enhance existing sessions table
-- Date: 2025-08-06
-- Author: Activity Monitoring Feature

PRAGMA foreign_keys = ON;

-- Step 1: Enhance sessions table with activity tracking columns
ALTER TABLE sessions ADD COLUMN last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE sessions ADD COLUMN last_page TEXT;
ALTER TABLE sessions ADD COLUMN last_api_endpoint TEXT;
ALTER TABLE sessions ADD COLUMN activity_count INTEGER DEFAULT 0;
ALTER TABLE sessions ADD COLUMN device_type TEXT DEFAULT 'unknown';

-- Step 2: Create indexes for efficient activity queries on sessions
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user_expires ON sessions(user_id, expires_at);

-- Step 3: Create user_activity_log table for detailed tracking
CREATE TABLE IF NOT EXISTS user_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    page_url TEXT NOT NULL,
    page_title TEXT,
    action_type TEXT DEFAULT 'page_view', -- page_view|api_call|file_download
    duration_ms INTEGER,
    referrer TEXT,
    ip_address TEXT,
    user_agent TEXT,
    metadata TEXT, -- JSON string for additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Step 4: Create indexes for performance on activity log
CREATE INDEX IF NOT EXISTS idx_activity_user_time ON user_activity_log(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_activity_session ON user_activity_log(session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON user_activity_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_activity_page ON user_activity_log(page_url);
CREATE INDEX IF NOT EXISTS idx_activity_action_type ON user_activity_log(action_type);

-- Step 5: Create view for current activity (last 7 days)
CREATE VIEW IF NOT EXISTS user_activity_current AS
SELECT * FROM user_activity_log 
WHERE timestamp > datetime('now', '-7 days');

-- Step 6: Create activity_alerts table for security monitoring
CREATE TABLE IF NOT EXISTS activity_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL, -- concurrent_sessions|unusual_location|after_hours|rapid_navigation
    severity TEXT NOT NULL, -- info|warning|critical
    user_id INTEGER,
    session_id TEXT,
    description TEXT NOT NULL,
    metadata TEXT, -- JSON with alert details
    status TEXT DEFAULT 'pending', -- pending|acknowledged|resolved|dismissed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP,
    acknowledged_by INTEGER,
    resolved_at TIMESTAMP,
    resolved_by INTEGER,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (acknowledged_by) REFERENCES users(id),
    FOREIGN KEY (resolved_by) REFERENCES users(id)
);

-- Step 7: Create indexes for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_status ON activity_alerts(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_user ON activity_alerts(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON activity_alerts(severity, status);

-- Step 8: Create activity_summary_daily table for aggregated metrics
CREATE TABLE IF NOT EXISTS activity_summary_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    unique_users INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    total_page_views INTEGER DEFAULT 0,
    total_api_calls INTEGER DEFAULT 0,
    avg_session_duration_seconds INTEGER DEFAULT 0,
    peak_concurrent_users INTEGER DEFAULT 0,
    peak_hour INTEGER,
    top_pages TEXT, -- JSON array of top pages
    user_distribution TEXT, -- JSON object by role
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(date)
);

-- Step 9: Create index for summary queries
CREATE INDEX IF NOT EXISTS idx_summary_date ON activity_summary_daily(date DESC);

-- Step 10: Create system configuration table if not exists
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 11: Insert initial activity monitoring configuration
INSERT OR REPLACE INTO system_config (key, value, description) VALUES
('activity_monitoring_enabled', 'true', 'Enable user activity monitoring'),
('activity_retention_days', '90', 'Days to retain detailed activity logs'),
('activity_summary_retention_days', '730', 'Days to retain summary data'),
('activity_alert_email', '', 'Email for critical activity alerts'),
('activity_tracking_excluded_pages', '[]', 'JSON array of pages to exclude from tracking'),
('activity_session_idle_minutes', '15', 'Minutes before session considered idle'),
('activity_session_warning_minutes', '25', 'Minutes before session warning'),
('activity_alert_concurrent_sessions_threshold', '2', 'Max concurrent sessions before alert'),
('activity_alert_rapid_navigation_threshold', '20', 'Page views per minute before alert');

-- Step 12: Create view for active sessions with user info
CREATE VIEW IF NOT EXISTS active_sessions_view AS
SELECT 
    s.id as session_id,
    s.user_id,
    u.username,
    u.email as user_email,
    u.role,
    s.created_at as login_time,
    s.last_activity,
    s.last_page,
    s.last_api_endpoint,
    s.activity_count,
    s.ip_address,
    s.user_agent,
    s.device_type,
    CASE
        WHEN (julianday('now') - julianday(s.last_activity)) * 24 * 60 < 5 THEN 'active'
        WHEN (julianday('now') - julianday(s.last_activity)) * 24 * 60 < 15 THEN 'idle'
        WHEN (julianday('now') - julianday(s.last_activity)) * 24 * 60 < 25 THEN 'warning'
        ELSE 'expired'
    END as status,
    CAST((julianday('now') - julianday(s.created_at)) * 24 * 60 AS INTEGER) as session_duration_minutes
FROM sessions s
JOIN users u ON s.user_id = u.id
WHERE s.expires_at > datetime('now')
ORDER BY s.last_activity DESC;

-- Step 13: Add migration record
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO migrations (name) VALUES ('002_activity_monitoring');