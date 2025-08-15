#!/usr/bin/env python3
"""
Validate the planogram optimizer installation and functionality.
"""

import os
import sys
import sqlite3

def validate_optimizer_installation():
    """Validate the optimizer is correctly installed and functional."""
    checks = {
        'module_import': False,
        'api_key_set': False,
        'database_accessible': False,
        'claude_api_functional': False,
        'test_database_creation': False
    }
    
    print("=== Planogram Optimizer Installation Validation ===\n")
    
    # Check 1: Module import
    try:
        from planogram_optimizer import PlanogramOptimizer
        checks['module_import'] = True
        print("✅ Module Import: planogram_optimizer imported successfully")
    except ImportError as e:
        print(f"❌ Module Import: Failed to import planogram_optimizer - {e}")
        
    # Check 2: API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        checks['api_key_set'] = True
        print(f"✅ API Key Set: ANTHROPIC_API_KEY is configured (length: {len(api_key)})")
    else:
        print("❌ API Key Set: ANTHROPIC_API_KEY not set in environment")
        
    # Check 3: Database access
    try:
        conn = sqlite3.connect('cvd.db')
        cursor = conn.cursor()
        
        # Check products table
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        # Check sales table
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        
        # Check devices table
        cursor.execute("SELECT COUNT(*) FROM devices WHERE deleted_at IS NULL")
        device_count = cursor.fetchone()[0]
        
        conn.close()
        
        if product_count > 0:
            checks['database_accessible'] = True
            print(f"✅ Database Access: Connected successfully")
            print(f"   - Products: {product_count}")
            print(f"   - Sales records: {sales_count}")
            print(f"   - Active devices: {device_count}")
        else:
            print("⚠️  Database Access: Connected but no products found")
            
    except Exception as e:
        print(f"❌ Database Access: Failed - {e}")
        
    # Check 4: Test database creation (verify test can create its own DB)
    try:
        test_db = 'test_validation.db'
        if os.path.exists(test_db):
            os.remove(test_db)
            
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        cursor.execute("INSERT INTO test VALUES (1)")
        conn.commit()
        conn.close()
        
        os.remove(test_db)
        checks['test_database_creation'] = True
        print("✅ Test Database Creation: Can create test databases")
    except Exception as e:
        print(f"❌ Test Database Creation: Failed - {e}")
        
    # Check 5: Claude API (optional test)
    if checks['module_import'] and checks['api_key_set']:
        try:
            from planogram_optimizer import PlanogramOptimizer
            optimizer = PlanogramOptimizer(api_key)
            
            # Try to access the client (won't make actual API call)
            if hasattr(optimizer, 'client'):
                checks['claude_api_functional'] = True
                print("✅ Claude API: Client initialized successfully")
            else:
                print("⚠️  Claude API: Client initialization unclear")
                
        except Exception as e:
            print(f"⚠️  Claude API: Initialization test failed - {e}")
    else:
        print("⏭️  Claude API: Skipped (missing prerequisites)")
    
    # Additional checks
    print("\n=== Additional Checks ===")
    
    # Check if required files exist
    files_to_check = [
        ('app.py', 'Flask backend'),
        ('api.js', 'Frontend API client'),
        ('pages/NSPT.html', 'Planogram editor'),
        ('planogram_optimizer.py', 'AI optimizer module'),
        ('tests/test_planogram_optimizer.py', 'Unit tests')
    ]
    
    all_files_exist = True
    for filepath, description in files_to_check:
        if os.path.exists(filepath):
            print(f"✅ {description}: {filepath}")
        else:
            print(f"❌ {description}: {filepath} not found")
            all_files_exist = False
    
    # Check if AI endpoints were added to app.py
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            app_content = f.read()
            if '/api/planograms/ai-suggestions' in app_content:
                print("✅ API Endpoints: AI endpoints found in app.py")
            else:
                print("❌ API Endpoints: AI endpoints not found in app.py")
                
    # Summary
    print("\n=== Validation Summary ===")
    passed_checks = sum(checks.values())
    total_checks = len(checks)
    
    print(f"\nCore checks passed: {passed_checks}/{total_checks}")
    
    if all(checks.values()) and all_files_exist:
        print("\n🎉 All validation checks passed! The AI planogram optimizer is ready to use.")
        return True
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        return False

def test_optimizer_functionality():
    """Run a simple functionality test if all checks pass."""
    print("\n=== Functionality Test ===")
    
    try:
        from planogram_optimizer import PlanogramOptimizer
        
        # Create optimizer with test API key
        optimizer = PlanogramOptimizer('test_key', 'cvd.db')
        
        # Test data fetching
        print("\nTesting data fetch methods...")
        
        # Try to get sales data for device 1
        try:
            sales_data = optimizer.get_sales_data(1, days=7)
            if sales_data:
                print(f"✅ Sales data fetch: Retrieved {len(sales_data)} product sales records")
            else:
                print("⚠️  Sales data fetch: No sales data found for device 1")
        except Exception as e:
            print(f"❌ Sales data fetch: Failed - {e}")
            
        # Try to get planogram for device 1
        try:
            planogram = optimizer.get_current_planogram(1, 0)
            if planogram:
                slots = planogram.get('slots', [])
                print(f"✅ Planogram fetch: Retrieved planogram with {len(slots)} slots")
            else:
                print("⚠️  Planogram fetch: No planogram found for device 1")
        except Exception as e:
            print(f"❌ Planogram fetch: Failed - {e}")
            
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")

if __name__ == "__main__":
    # Run validation
    validation_passed = validate_optimizer_installation()
    
    # Run functionality test if validation passed
    if validation_passed and '--test' in sys.argv:
        test_optimizer_functionality()
    
    # Exit with appropriate code
    sys.exit(0 if validation_passed else 1)