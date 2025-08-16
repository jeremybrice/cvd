#!/usr/bin/env python3
"""
Railway startup script - Initialize database and ensure data persistence
"""
import os
import shutil
import sqlite3

def main():
    """Initialize Railway deployment environment"""
    print("🚂 Railway startup script starting...")
    
    # Ensure data directory exists for persistent volume
    data_dir = os.environ.get('DATA_DIR', '/app/data')
    os.makedirs(data_dir, exist_ok=True)
    print(f"✓ Data directory ensured: {data_dir}")

    db_path = os.path.join(data_dir, 'cvd.db')
    
    # Copy database to persistent volume if not exists
    if not os.path.exists(db_path):
        if os.path.exists('cvd.db'):
            print(f"📦 Copying database to persistent volume: {db_path}")
            shutil.copy('cvd.db', db_path)
            print("✓ Database copied successfully")
        else:
            print("⚠️  Warning: No initial database found - app will create new one")
    else:
        print("✓ Database already exists in persistent volume")

    # Verify database is accessible
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        if result:
            print("✓ Database connection verified")
        else:
            print("⚠️  Database appears to be empty")
    except Exception as e:
        print(f"❌ Database verification failed: {e}")

    # Create symlink in app directory as fallback for Flask
    app_db_path = './cvd.db'
    if os.path.exists(db_path) and not os.path.exists(app_db_path):
        try:
            os.symlink(db_path, app_db_path)
            print(f"✓ Created symlink from {app_db_path} to {db_path}")
        except Exception as e:
            print(f"⚠️  Could not create symlink: {e}")
    
    print(f"🎯 Final database location: {db_path}")
    print("🚂 Railway startup complete!")

if __name__ == "__main__":
    main()