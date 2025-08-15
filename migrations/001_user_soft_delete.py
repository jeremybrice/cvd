"""
User Soft Delete Migration
Adds soft delete functionality to users table
"""

import sqlite3
from datetime import datetime
import sys
import os

def migrate_up(db_path):
    """Apply the migration"""
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    try:
        # Check if migrations table exists, create if not
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if migration already applied
        existing = cursor.execute(
            'SELECT COUNT(*) FROM migrations WHERE name = ?', 
            ('001_user_soft_delete',)
        ).fetchone()[0]
        
        if existing > 0:
            print("✓ Migration already applied")
            return
        
        # Add new columns
        cursor.execute('ALTER TABLE users ADD COLUMN is_deleted BOOLEAN DEFAULT 0')
        cursor.execute('ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL')
        cursor.execute('ALTER TABLE users ADD COLUMN deleted_by INTEGER NULL')
        
        # Set is_deleted = 0 for all existing users
        cursor.execute('UPDATE users SET is_deleted = 0 WHERE is_deleted IS NULL')
        
        # Create performance index
        cursor.execute('CREATE INDEX idx_users_active_deleted ON users(is_active, is_deleted)')
        
        # Record migration
        cursor.execute('''
            INSERT INTO migrations (name, applied_at) 
            VALUES (?, ?)
        ''', ('001_user_soft_delete', datetime.now()))
        
        db.commit()
        print("✓ User soft delete migration applied successfully")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        db.close()

def migrate_down(db_path):
    """Rollback the migration"""
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    try:
        # SQLite doesn't support DROP COLUMN, so we recreate the table
        cursor.execute('''
            CREATE TABLE users_backup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'driver', 'viewer')),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        # Copy data without soft delete columns
        cursor.execute('''
            INSERT INTO users_backup 
            SELECT id, username, email, password_hash, role, is_active, 
                   created_at, updated_at, last_login, failed_login_attempts, locked_until
            FROM users WHERE is_deleted = 0
        ''')
        
        # Drop original table and rename backup
        cursor.execute('DROP TABLE users')
        cursor.execute('ALTER TABLE users_backup RENAME TO users')
        
        # Drop the index
        cursor.execute('DROP INDEX IF EXISTS idx_users_active_deleted')
        
        # Remove migration record
        cursor.execute('DELETE FROM migrations WHERE name = ?', ('001_user_soft_delete',))
        
        db.commit()
        print("✓ User soft delete migration rolled back successfully")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Rollback failed: {e}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python migration.py <up|down> <db_path>")
        sys.exit(1)
    
    action = sys.argv[1]
    db_path = sys.argv[2]
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist")
        sys.exit(1)
    
    if action == 'up':
        migrate_up(db_path)
    elif action == 'down':
        migrate_down(db_path)
    else:
        print("Action must be 'up' or 'down'")
        sys.exit(1)