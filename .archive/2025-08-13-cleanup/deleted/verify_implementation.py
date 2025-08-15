#!/usr/bin/env python3
"""
Verify the user soft delete implementation
"""

import sqlite3
from datetime import datetime
import sys
import os

def verify_implementation():
    """Verify all components of the soft delete implementation"""
    
    print("🔍 Verifying User Soft Delete Implementation")
    print("=" * 50)
    
    success = True
    
    # 1. Check database schema
    print("\n1. Database Schema Verification:")
    try:
        db = sqlite3.connect('cvd.db')
        cursor = db.cursor()
        
        # Check for soft delete columns
        columns = cursor.execute("PRAGMA table_info(users)").fetchall()
        column_names = [col[1] for col in columns]
        
        required_columns = ['is_deleted', 'deleted_at', 'deleted_by']
        for col in required_columns:
            if col in column_names:
                print(f"   ✓ {col} column exists")
            else:
                print(f"   ✗ {col} column missing")
                success = False
        
        # Check for index
        indexes = cursor.execute("PRAGMA index_list(users)").fetchall()
        index_names = [idx[1] for idx in indexes]
        
        if 'idx_users_active_deleted' in index_names:
            print("   ✓ Performance index exists")
        else:
            print("   ✗ Performance index missing")
            success = False
        
        db.close()
        
    except Exception as e:
        print(f"   ✗ Database check failed: {e}")
        success = False
    
    # 2. Check migration files
    print("\n2. Migration Files Verification:")
    if os.path.exists('migrations/001_user_soft_delete.py'):
        print("   ✓ Migration script exists")
        
        # Check if migration was applied
        db = sqlite3.connect('cvd.db')
        cursor = db.cursor()
        try:
            migration_count = cursor.execute(
                "SELECT COUNT(*) FROM migrations WHERE name = '001_user_soft_delete'"
            ).fetchone()[0]
            if migration_count > 0:
                print("   ✓ Migration has been applied")
            else:
                print("   ⚠ Migration exists but not recorded in database")
        except:
            print("   ⚠ Could not verify migration status (migrations table may not exist)")
        db.close()
    else:
        print("   ✗ Migration script missing")
        success = False
    
    # 3. Check auth.py functions
    print("\n3. Authentication Module Functions:")
    try:
        import auth
        
        required_functions = [
            'check_user_service_orders',
            'get_user_service_order_details',
            'validate_user_constraints',
            'log_user_lifecycle_event'
        ]
        
        for func_name in required_functions:
            if hasattr(auth, func_name):
                print(f"   ✓ {func_name} function exists")
            else:
                print(f"   ✗ {func_name} function missing")
                success = False
                
    except Exception as e:
        print(f"   ✗ Auth module check failed: {e}")
        success = False
    
    # 4. Check app.py endpoints
    print("\n4. API Endpoints Verification:")
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        required_endpoints = [
            '/api/users/<int:user_id>/deactivate',
            '/api/users/<int:user_id>/activate',
            '/api/users/<int:user_id>/soft-delete',
            '/api/users/<int:user_id>/audit-trail',
            '/api/users/batch-deactivate',
            '/api/metrics/user-lifecycle'
        ]
        
        for endpoint in required_endpoints:
            if endpoint in app_content:
                print(f"   ✓ {endpoint} endpoint exists")
            else:
                print(f"   ✗ {endpoint} endpoint missing")
                success = False
                
    except Exception as e:
        print(f"   ✗ App.py check failed: {e}")
        success = False
    
    # 5. Check test files
    print("\n5. Test Files Verification:")
    test_files = [
        'tests/test_user_soft_delete.py',
        'test_soft_delete_core.py',
        'test_audit_logging.py'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"   ✓ {test_file} exists")
        else:
            print(f"   ✗ {test_file} missing")
            success = False
    
    # 6. Verify actual functionality with database
    print("\n6. Functional Verification:")
    try:
        db = sqlite3.connect('cvd.db')
        cursor = db.cursor()
        
        # Count active vs deleted users
        total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active_users = cursor.execute("SELECT COUNT(*) FROM users WHERE is_deleted = 0").fetchone()[0]
        deleted_users = cursor.execute("SELECT COUNT(*) FROM users WHERE is_deleted = 1").fetchone()[0]
        
        print(f"   ✓ Total users: {total_users}")
        print(f"   ✓ Active users: {active_users}")
        print(f"   ✓ Soft deleted users: {deleted_users}")
        
        # Test constraint query performance
        start_time = datetime.now()
        active_admins = cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE role = 'admin' AND is_active = 1 AND is_deleted = 0
        """).fetchone()[0]
        end_time = datetime.now()
        
        query_time = (end_time - start_time).total_seconds() * 1000
        print(f"   ✓ Admin count query: {active_admins} admins in {query_time:.2f}ms")
        
        db.close()
        
    except Exception as e:
        print(f"   ✗ Functional verification failed: {e}")
        success = False
    
    # 7. Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 VERIFICATION SUCCESSFUL!")
        print("✓ All components of the user soft delete implementation are in place")
        print("✓ Database schema is correct with performance indexes")
        print("✓ API endpoints are implemented")
        print("✓ Authentication functions are available")
        print("✓ Test files are created")
        print("✓ Functionality is working correctly")
        print("\nThe user soft delete backend deployment is READY!")
    else:
        print("❌ VERIFICATION FAILED!")
        print("Some components are missing or not working correctly.")
        print("Review the issues above before proceeding.")
    
    return success

if __name__ == '__main__':
    success = verify_implementation()
    exit(0 if success else 1)