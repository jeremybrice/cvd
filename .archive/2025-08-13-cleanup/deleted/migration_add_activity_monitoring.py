#!/usr/bin/env python3
"""
Database migration script for User Activity Monitoring feature
Run this script to add activity monitoring tables and enhance the sessions table.

Usage: python migration_add_activity_monitoring.py
"""

import sqlite3
import os
import sys
from datetime import datetime

DATABASE = 'cvd.db'
MIGRATION_FILE = 'migrations/002_activity_monitoring.sql'

def backup_database():
    """Create a backup of the database before migration"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = 'backups'
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_file = os.path.join(backup_dir, f'cvd_backup_{timestamp}.db')
    
    try:
        shutil.copy2(DATABASE, backup_file)
        print(f"✓ Database backed up to: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"✗ Failed to backup database: {e}")
        return None

def check_migration_status(db):
    """Check if migration has already been applied"""
    cursor = db.cursor()
    
    # Check if migrations table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='migrations'
    """)
    
    if not cursor.fetchone():
        # Create migrations table if it doesn't exist
        cursor.execute("""
            CREATE TABLE migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()
        return False
    
    # Check if this migration has been applied
    cursor.execute("""
        SELECT id FROM migrations 
        WHERE name = '002_activity_monitoring'
    """)
    
    return cursor.fetchone() is not None

def validate_database_structure(db):
    """Validate that required base tables exist"""
    cursor = db.cursor()
    required_tables = ['users', 'sessions', 'audit_log']
    missing_tables = []
    
    for table in required_tables:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table,))
        
        if not cursor.fetchone():
            missing_tables.append(table)
    
    if missing_tables:
        print(f"✗ Missing required tables: {', '.join(missing_tables)}")
        print("  Please ensure the base CVD database is properly initialized.")
        return False
    
    return True

def check_column_exists(db, table, column):
    """Check if a column already exists in a table"""
    cursor = db.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def apply_migration(db):
    """Apply the activity monitoring migration"""
    cursor = db.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("\n📋 Starting migration: User Activity Monitoring")
        print("-" * 50)
        
        # Step 1: Enhance sessions table
        print("→ Enhancing sessions table...")
        
        # Check which columns already exist
        columns_to_add = [
            ('last_activity', 'TIMESTAMP'),
            ('last_page', 'TEXT'),
            ('last_api_endpoint', 'TEXT'),
            ('activity_count', 'INTEGER'),
            ('device_type', 'TEXT')
        ]
        
        for column_name, column_def in columns_to_add:
            if not check_column_exists(db, 'sessions', column_name):
                cursor.execute(f"ALTER TABLE sessions ADD COLUMN {column_name} {column_def}")
                print(f"  ✓ Added column: {column_name}")
                
                # Set default values for new columns
                if column_name == 'last_activity':
                    cursor.execute("UPDATE sessions SET last_activity = created_at WHERE last_activity IS NULL")
                elif column_name == 'activity_count':
                    cursor.execute("UPDATE sessions SET activity_count = 0 WHERE activity_count IS NULL")
                elif column_name == 'device_type':
                    cursor.execute("UPDATE sessions SET device_type = 'unknown' WHERE device_type IS NULL")
            else:
                print(f"  ℹ Column already exists: {column_name}")
        
        # Step 2: Create indexes
        print("\n→ Creating indexes...")
        
        indexes = [
            ('idx_sessions_last_activity', 'sessions', 'last_activity DESC'),
            ('idx_sessions_user_expires', 'sessions', 'user_id, expires_at')
        ]
        
        for idx_name, table, columns in indexes:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {idx_name} 
                ON {table}({columns})
            """)
            print(f"  ✓ Created index: {idx_name}")
        
        # Step 3: Create user_activity_log table
        print("\n→ Creating user_activity_log table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                page_url TEXT NOT NULL,
                page_title TEXT,
                action_type TEXT DEFAULT 'page_view',
                duration_ms INTEGER,
                referrer TEXT,
                ip_address TEXT,
                user_agent TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        print("  ✓ Created user_activity_log table")
        
        # Create activity log indexes
        activity_indexes = [
            ('idx_activity_user_time', 'user_id, timestamp DESC'),
            ('idx_activity_session', 'session_id, timestamp DESC'),
            ('idx_activity_timestamp', 'timestamp DESC'),
            ('idx_activity_page', 'page_url'),
            ('idx_activity_action_type', 'action_type')
        ]
        
        for idx_name, columns in activity_indexes:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {idx_name}
                ON user_activity_log({columns})
            """)
            print(f"  ✓ Created index: {idx_name}")
        
        # Step 4: Create activity view
        print("\n→ Creating activity views...")
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS user_activity_current AS
            SELECT * FROM user_activity_log 
            WHERE timestamp > datetime('now', '-7 days')
        """)
        print("  ✓ Created user_activity_current view")
        
        # Step 5: Create activity_alerts table
        print("\n→ Creating activity_alerts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id INTEGER,
                session_id TEXT,
                description TEXT NOT NULL,
                metadata TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged_at TIMESTAMP,
                acknowledged_by INTEGER,
                resolved_at TIMESTAMP,
                resolved_by INTEGER,
                
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (acknowledged_by) REFERENCES users(id),
                FOREIGN KEY (resolved_by) REFERENCES users(id)
            )
        """)
        print("  ✓ Created activity_alerts table")
        
        # Create alert indexes
        alert_indexes = [
            ('idx_alerts_status', 'status, created_at DESC'),
            ('idx_alerts_user', 'user_id, created_at DESC'),
            ('idx_alerts_severity', 'severity, status')
        ]
        
        for idx_name, columns in alert_indexes:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {idx_name}
                ON activity_alerts({columns})
            """)
            print(f"  ✓ Created index: {idx_name}")
        
        # Step 6: Create activity_summary_daily table
        print("\n→ Creating activity_summary_daily table...")
        cursor.execute("""
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
                top_pages TEXT,
                user_distribution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(date)
            )
        """)
        print("  ✓ Created activity_summary_daily table")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_summary_date 
            ON activity_summary_daily(date DESC)
        """)
        print("  ✓ Created index: idx_summary_date")
        
        # Step 7: Create system_config table
        print("\n→ Setting up configuration...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert configuration values
        config_values = [
            ('activity_monitoring_enabled', 'true', 'Enable user activity monitoring'),
            ('activity_retention_days', '90', 'Days to retain detailed activity logs'),
            ('activity_summary_retention_days', '730', 'Days to retain summary data'),
            ('activity_alert_email', '', 'Email for critical activity alerts'),
            ('activity_tracking_excluded_pages', '[]', 'JSON array of pages to exclude from tracking'),
            ('activity_session_idle_minutes', '15', 'Minutes before session considered idle'),
            ('activity_session_warning_minutes', '25', 'Minutes before session warning'),
            ('activity_alert_concurrent_sessions_threshold', '2', 'Max concurrent sessions before alert'),
            ('activity_alert_rapid_navigation_threshold', '20', 'Page views per minute before alert')
        ]
        
        for key, value, description in config_values:
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (key, value, description)
                VALUES (?, ?, ?)
            """, (key, value, description))
        
        print("  ✓ Configuration values set")
        
        # Step 8: Create active sessions view
        print("\n→ Creating active_sessions_view...")
        cursor.execute("""
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
            ORDER BY s.last_activity DESC
        """)
        print("  ✓ Created active_sessions_view")
        
        # Step 9: Record migration
        cursor.execute("""
            INSERT INTO migrations (name) 
            VALUES ('002_activity_monitoring')
        """)
        
        db.commit()
        
        print("\n" + "=" * 50)
        print("✅ Migration completed successfully!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration(db):
    """Verify that migration was applied successfully"""
    cursor = db.cursor()
    
    print("\n🔍 Verifying migration...")
    print("-" * 50)
    
    # Check tables
    tables_to_check = [
        'user_activity_log',
        'activity_alerts', 
        'activity_summary_daily',
        'system_config'
    ]
    
    for table in tables_to_check:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table,))
        
        if cursor.fetchone():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✓ Table {table}: exists ({count} records)")
        else:
            print(f"  ✗ Table {table}: missing")
            return False
    
    # Check views
    views_to_check = ['user_activity_current', 'active_sessions_view']
    
    for view in views_to_check:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name=?
        """, (view,))
        
        if cursor.fetchone():
            print(f"  ✓ View {view}: exists")
        else:
            print(f"  ✗ View {view}: missing")
            return False
    
    # Check session table columns
    cursor.execute("PRAGMA table_info(sessions)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = ['last_activity', 'last_page', 'activity_count', 'device_type']
    missing_columns = [col for col in required_columns if col not in columns]
    
    if missing_columns:
        print(f"  ✗ Missing columns in sessions table: {', '.join(missing_columns)}")
        return False
    else:
        print(f"  ✓ Sessions table has all required columns")
    
    print("\n✅ Migration verification passed!")
    return True

def main():
    """Main migration function"""
    print("\n" + "=" * 50)
    print("User Activity Monitoring - Database Migration")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists(DATABASE):
        print(f"✗ Database not found: {DATABASE}")
        print("  Please ensure you're running this from the CVD project root.")
        sys.exit(1)
    
    # Create backup
    backup_file = backup_database()
    if not backup_file:
        response = input("\n⚠️  Continue without backup? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            sys.exit(0)
    
    # Connect to database
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    
    try:
        # Check if migration already applied
        if check_migration_status(db):
            print("\nℹ️  Migration '002_activity_monitoring' has already been applied.")
            
            # Verify the migration
            if verify_migration(db):
                print("\n✅ Database is ready for activity monitoring!")
            else:
                print("\n⚠️  Migration was previously applied but verification failed.")
                print("   You may need to restore from backup and re-run migration.")
            
            return
        
        # Validate database structure
        if not validate_database_structure(db):
            print("\n✗ Database validation failed. Migration cancelled.")
            sys.exit(1)
        
        # Apply migration
        if apply_migration(db):
            # Verify the migration
            if verify_migration(db):
                print("\n🎉 Migration completed and verified successfully!")
                print(f"\n💡 Next steps:")
                print(f"   1. Restart the Flask application")
                print(f"   2. Activity monitoring will begin automatically")
                print(f"   3. Access the dashboard at /pages/admin/activity-monitor.html")
            else:
                print("\n⚠️  Migration applied but verification failed.")
                print(f"   Backup is available at: {backup_file}")
        else:
            print("\n✗ Migration failed!")
            print(f"   Backup is available at: {backup_file}")
            print(f"   To restore: cp {backup_file} {DATABASE}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    main()