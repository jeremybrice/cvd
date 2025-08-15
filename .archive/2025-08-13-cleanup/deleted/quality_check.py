import sqlite3
import json
from datetime import datetime

def check_data_quality():
    conn = sqlite3.connect('cvd.db')
    cursor = conn.cursor()
    
    issues = {
        'orphaned_records': [],
        'duplicate_records': [],
        'null_violations': [],
        'format_issues': [],
        'business_rule_violations': [],
        'data_anomalies': [],
        'integrity_issues': []
    }
    
    print("=" * 80)
    print("DATA QUALITY ASSESSMENT")
    print("=" * 80)
    
    # 1. Check for orphaned foreign keys
    print("\n1. CHECKING FOREIGN KEY INTEGRITY...")
    
    # Check devices -> locations
    cursor.execute("""
        SELECT COUNT(*) FROM devices d 
        LEFT JOIN locations l ON d.location_id = l.id 
        WHERE d.location_id IS NOT NULL AND l.id IS NULL
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues['orphaned_records'].append({
            'table': 'devices',
            'issue': f'{orphaned} devices reference non-existent locations'
        })
    
    # Check cabinet_configurations -> devices
    cursor.execute("""
        SELECT COUNT(*) FROM cabinet_configurations c 
        LEFT JOIN devices d ON c.device_id = d.id 
        WHERE c.device_id IS NOT NULL AND d.id IS NULL
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues['orphaned_records'].append({
            'table': 'cabinet_configurations',
            'issue': f'{orphaned} cabinet configurations reference non-existent devices'
        })
    
    # Check planogram_slots -> planograms
    cursor.execute("""
        SELECT COUNT(*) FROM planogram_slots ps 
        LEFT JOIN planograms p ON ps.planogram_id = p.id 
        WHERE ps.planogram_id IS NOT NULL AND p.id IS NULL
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues['orphaned_records'].append({
            'table': 'planogram_slots',
            'issue': f'{orphaned} planogram slots reference non-existent planograms'
        })
    
    # Check planogram_slots -> products
    cursor.execute("""
        SELECT COUNT(*) FROM planogram_slots ps 
        LEFT JOIN products pr ON ps.product_id = pr.id 
        WHERE ps.product_id IS NOT NULL AND pr.id IS NULL
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues['orphaned_records'].append({
            'table': 'planogram_slots',
            'issue': f'{orphaned} planogram slots reference non-existent products'
        })
    
    # Check service_orders -> users
    cursor.execute("""
        SELECT COUNT(*) FROM service_orders so 
        LEFT JOIN users u ON so.assigned_driver_id = u.id 
        WHERE so.assigned_driver_id IS NOT NULL AND u.id IS NULL
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues['orphaned_records'].append({
            'table': 'service_orders',
            'issue': f'{orphaned} service orders assigned to non-existent users'
        })
    
    print(f"  Found {len(issues['orphaned_records'])} orphaned record issues")
    
    # 2. Check for duplicates
    print("\n2. CHECKING FOR DUPLICATE RECORDS...")
    
    # Check duplicate devices by serial number
    cursor.execute("""
        SELECT serial_number, COUNT(*) as cnt 
        FROM devices 
        WHERE serial_number IS NOT NULL 
        GROUP BY serial_number 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        for serial, count in duplicates:
            issues['duplicate_records'].append({
                'table': 'devices',
                'issue': f'Serial number {serial} appears {count} times'
            })
    
    # Check duplicate users by email
    cursor.execute("""
        SELECT email, COUNT(*) as cnt 
        FROM users 
        GROUP BY email 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        for email, count in duplicates:
            issues['duplicate_records'].append({
                'table': 'users',
                'issue': f'Email {email} appears {count} times'
            })
    
    print(f"  Found {len(issues['duplicate_records'])} duplicate record issues")
    
    # 3. Check for null values in critical fields
    print("\n3. CHECKING FOR NULL VALUES IN CRITICAL FIELDS...")
    
    # Check devices
    cursor.execute("SELECT COUNT(*) FROM devices WHERE location_id IS NULL")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        issues['null_violations'].append({
            'table': 'devices',
            'issue': f'{null_count} devices have no location assigned'
        })
    
    # Check products
    cursor.execute("SELECT COUNT(*) FROM products WHERE price IS NULL OR par_level IS NULL")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        issues['null_violations'].append({
            'table': 'products',
            'issue': f'{null_count} products missing price or par level'
        })
    
    # Check users
    cursor.execute("SELECT COUNT(*) FROM users WHERE role IS NULL")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        issues['null_violations'].append({
            'table': 'users',
            'issue': f'{null_count} users have no role assigned'
        })
    
    print(f"  Found {len(issues['null_violations'])} null value issues")
    
    # 4. Check data formats
    print("\n4. CHECKING DATA FORMATS...")
    
    # Check email formats
    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE email NOT LIKE '%@%.%' 
        OR email LIKE '% %'
    """)
    bad_emails = cursor.fetchone()[0]
    if bad_emails > 0:
        issues['format_issues'].append({
            'table': 'users',
            'issue': f'{bad_emails} users have invalid email format'
        })
    
    # Check phone number formats (if applicable)
    cursor.execute("""
        SELECT COUNT(*) FROM locations 
        WHERE phone IS NOT NULL 
        AND LENGTH(REPLACE(REPLACE(REPLACE(REPLACE(phone, '-', ''), '(', ''), ')', ''), ' ', '')) NOT IN (10, 11)
    """)
    bad_phones = cursor.fetchone()[0]
    if bad_phones > 0:
        issues['format_issues'].append({
            'table': 'locations',
            'issue': f'{bad_phones} locations have invalid phone number format'
        })
    
    print(f"  Found {len(issues['format_issues'])} format issues")
    
    # 5. Check business rules
    print("\n5. CHECKING BUSINESS RULES...")
    
    # Check for negative prices
    cursor.execute("SELECT COUNT(*) FROM products WHERE price < 0")
    negative_prices = cursor.fetchone()[0]
    if negative_prices > 0:
        issues['business_rule_violations'].append({
            'table': 'products',
            'issue': f'{negative_prices} products have negative prices'
        })
    
    # Check for negative par levels
    cursor.execute("SELECT COUNT(*) FROM products WHERE par_level < 0")
    negative_par = cursor.fetchone()[0]
    if negative_par > 0:
        issues['business_rule_violations'].append({
            'table': 'products',
            'issue': f'{negative_par} products have negative par levels'
        })
    
    # Check for invalid capacity
    cursor.execute("SELECT COUNT(*) FROM planogram_slots WHERE capacity < 0")
    negative_capacity = cursor.fetchone()[0]
    if negative_capacity > 0:
        issues['business_rule_violations'].append({
            'table': 'planogram_slots',
            'issue': f'{negative_capacity} planogram slots have negative capacity'
        })
    
    # Check for overlapping planogram slots (same position in same planogram)
    cursor.execute("""
        SELECT planogram_id, row, column, COUNT(*) as cnt
        FROM planogram_slots
        GROUP BY planogram_id, row, column
        HAVING COUNT(*) > 1
    """)
    overlapping = cursor.fetchall()
    if overlapping:
        issues['business_rule_violations'].append({
            'table': 'planogram_slots',
            'issue': f'{len(overlapping)} cases of overlapping slot positions'
        })
    
    # Check service orders without cabinets
    cursor.execute("""
        SELECT COUNT(DISTINCT so.id)
        FROM service_orders so
        LEFT JOIN service_order_cabinets soc ON so.id = soc.service_order_id
        WHERE soc.id IS NULL
    """)
    empty_orders = cursor.fetchone()[0]
    if empty_orders > 0:
        issues['business_rule_violations'].append({
            'table': 'service_orders',
            'issue': f'{empty_orders} service orders have no cabinet assignments'
        })
    
    print(f"  Found {len(issues['business_rule_violations'])} business rule violations")
    
    # 6. Check for data anomalies
    print("\n6. CHECKING FOR DATA ANOMALIES...")
    
    # Check for extreme prices
    cursor.execute("""
        SELECT MIN(price), MAX(price), AVG(price), 
               COUNT(CASE WHEN price > 100 THEN 1 END) as extreme_high,
               COUNT(CASE WHEN price < 0.5 AND price > 0 THEN 1 END) as extreme_low
        FROM products WHERE price IS NOT NULL
    """)
    min_price, max_price, avg_price, extreme_high, extreme_low = cursor.fetchone()
    if extreme_high > 0 or extreme_low > 0:
        issues['data_anomalies'].append({
            'table': 'products',
            'issue': f'Price anomalies: {extreme_high} products > $100, {extreme_low} products < $0.50. Range: ${min_price:.2f}-${max_price:.2f}, Avg: ${avg_price:.2f}'
        })
    
    # Check for future dates
    cursor.execute("""
        SELECT COUNT(*) FROM sales 
        WHERE transaction_date > datetime('now')
    """)
    future_sales = cursor.fetchone()[0]
    if future_sales > 0:
        issues['data_anomalies'].append({
            'table': 'sales',
            'issue': f'{future_sales} sales records have future dates'
        })
    
    # Check for very old dates
    cursor.execute("""
        SELECT COUNT(*) FROM sales 
        WHERE transaction_date < '2020-01-01'
    """)
    old_sales = cursor.fetchone()[0]
    if old_sales > 0:
        issues['data_anomalies'].append({
            'table': 'sales',
            'issue': f'{old_sales} sales records dated before 2020'
        })
    
    print(f"  Found {len(issues['data_anomalies'])} data anomalies")
    
    # 7. SQLite to PostgreSQL migration considerations
    print("\n7. MIGRATION COMPATIBILITY CHECKS...")
    migration_notes = []
    
    # Check for AUTOINCREMENT usage
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND sql LIKE '%AUTOINCREMENT%'
    """)
    autoincrement_tables = cursor.fetchall()
    if autoincrement_tables:
        migration_notes.append({
            'issue': 'AUTOINCREMENT to SERIAL conversion',
            'tables': [t[0] for t in autoincrement_tables],
            'action': 'Convert INTEGER PRIMARY KEY AUTOINCREMENT to SERIAL/BIGSERIAL'
        })
    
    # Check for DATETIME fields
    cursor.execute("""
        SELECT DISTINCT m.name as table_name
        FROM sqlite_master m
        WHERE type='table' AND sql LIKE '%DATETIME%'
    """)
    datetime_tables = cursor.fetchall()
    if datetime_tables:
        migration_notes.append({
            'issue': 'DATETIME to TIMESTAMP conversion',
            'tables': [t[0] for t in datetime_tables],
            'action': 'Convert DATETIME to TIMESTAMP WITH TIME ZONE'
        })
    
    # Check for TEXT fields that might need VARCHAR
    migration_notes.append({
        'issue': 'TEXT to VARCHAR conversion',
        'action': 'Review TEXT fields and set appropriate VARCHAR lengths'
    })
    
    # Check for BLOB fields
    cursor.execute("""
        SELECT DISTINCT m.name as table_name
        FROM sqlite_master m
        WHERE type='table' AND sql LIKE '%BLOB%'
    """)
    blob_tables = cursor.fetchall()
    if blob_tables:
        migration_notes.append({
            'issue': 'BLOB to BYTEA conversion',
            'tables': [t[0] for t in blob_tables],
            'action': 'Convert BLOB to BYTEA'
        })
    
    conn.close()
    
    # Print summary
    print("\n" + "=" * 80)
    print("QUALITY ASSESSMENT SUMMARY")
    print("=" * 80)
    
    total_issues = sum(len(v) for v in issues.values() if isinstance(v, list))
    print(f"Total issues found: {total_issues}")
    
    for category, category_issues in issues.items():
        if category_issues:
            print(f"\n{category.upper().replace('_', ' ')}:")
            for issue in category_issues[:5]:  # Show first 5 of each category
                print(f"  - {issue['table']}: {issue['issue']}")
    
    print("\nMIGRATION CONSIDERATIONS:")
    for note in migration_notes:
        print(f"  - {note['issue']}: {note['action']}")
        if 'tables' in note:
            print(f"    Affected tables: {', '.join(note['tables'][:5])}")
    
    return issues, migration_notes

# Run quality assessment
issues, migration_notes = check_data_quality()

# Save results
with open('quality_assessment.json', 'w') as f:
    json.dump({'issues': issues, 'migration_notes': migration_notes}, f, indent=2, default=str)

print("\nDetailed results saved to quality_assessment.json")
