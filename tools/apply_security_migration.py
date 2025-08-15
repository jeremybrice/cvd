#!/usr/bin/env python3
"""
Apply Security Enhancement Migration
Runs the security enhancement migration to add new tables and features
"""

import sqlite3
import sys
import os

DATABASE = '../cvd.db'
MIGRATION_FILE = '../migrations/003_security_enhancements.sql'

def apply_migration():
    """Apply the security enhancement migration"""
    try:
        # Connect to database
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        
        # Check if migration already applied
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='migrations'
        """)
        
        if cursor.fetchone()[0] > 0:
            cursor.execute("""
                SELECT COUNT(*) FROM migrations 
                WHERE name = '003_security_enhancements'
            """)
            
            if cursor.fetchone()[0] > 0:
                print("Migration already applied.")
                return
        else:
            # Create migrations table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Read and execute migration
        with open(MIGRATION_FILE, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration statements
        cursor.executescript(migration_sql)
        
        db.commit()
        print("✅ Security enhancement migration applied successfully!")
        
        # Verify new tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (
                'ip_blocks', 'data_export_log', 'user_location_history',
                'sensitive_data_access_log', 'security_incidents'
            )
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        print(f"\nCreated {len(tables)} new security tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check security configuration
        cursor.execute("""
            SELECT COUNT(*) FROM system_config 
            WHERE key LIKE 'security_%'
        """)
        
        config_count = cursor.fetchone()[0]
        print(f"\nAdded {config_count} security configuration settings")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("Applying Security Enhancement Migration...")
    apply_migration()