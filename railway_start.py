#!/usr/bin/env python3
"""
Railway startup script - Initialize database and ensure data persistence
"""
import os
import sys
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
    
    # Set DATABASE environment variable for app.py to use
    os.environ['DATABASE_PATH'] = db_path
    
    # Copy database to persistent volume if not exists
    if not os.path.exists(db_path):
        if os.path.exists('cvd.db'):
            print(f"📦 Copying database to persistent volume: {db_path}")
            shutil.copy('cvd.db', db_path)
            print("✓ Database copied successfully")
        else:
            print("⚠️  No initial database found - will initialize from scratch")
    else:
        print("✓ Database already exists in persistent volume")

    # Check if database needs initialization
    needs_init = False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        if result:
            print("✓ Database connection verified - checking if tables exist")
            # Check if key tables exist
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            users_table = cursor.fetchone()
            conn.close()
            if not users_table:
                print("📋 Database exists but tables missing - needs initialization")
                needs_init = True
        else:
            print("📋 Database is empty - needs initialization")
            needs_init = True
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        needs_init = True

    # Initialize database if needed
    if needs_init:
        print("🏗️  Initializing database schema and seed data...")
        try:
            # Import Flask app and initialization functions
            from app import init_db, migrate_database_schema, migrate_products
            from app import migrate_device_types, migrate_cabinet_types, init_sentinel_product
            from app import create_initial_admin, app
            
            # Set up Flask app context for database operations
            with app.app_context():
                print("📄 Creating database tables...")
                init_db()
                
                print("🔄 Running database migrations...")
                migrate_database_schema()
                
                print("📦 Populating products...")
                migrate_products()
                
                print("🏭 Populating device types...")
                migrate_device_types()
                
                print("🗄️  Populating cabinet types...")
                migrate_cabinet_types()
                
                print("🎯 Initializing sentinel product...")
                init_sentinel_product()
                
                print("👤 Creating initial admin user...")
                create_initial_admin()
                
            print("✅ Database initialization completed successfully!")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            sys.exit(1)
    else:
        print("✅ Database already initialized")

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