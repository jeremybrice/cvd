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
    
    # Check service_orders -> users (driver_id)
    cursor.execute("""
        SELECT COUNT(*) FROM service_orders so 
        LEFT JOIN users u ON so.driver_id = u.id 
        WHERE so.driver_id IS NOT NULL AND u.id IS NULL
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues['orphaned_records'].append({
            'table': 'service_orders',
            'issue': f'{orphaned} service orders assigned to non-existent drivers'
        })
    
    # Check sales -> devices
    cursor.execute("""
        SELECT COUNT(*) FROM sales s 
        LEFT JOIN devices d ON s.device_id = d.id 
        WHERE s.device_id IS NOT NULL AND d.id IS NULL
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues['orphaned_records'].append({
            'table': 'sales',
            'issue': f'{orphaned} sales records reference non-existent devices'
        })
    
    # Check sales -> products
    cursor.execute("""
        SELECT COUNT(*) FROM sales s 
        LEFT JOIN products p ON s.product_id = p.id 
        WHERE s.product_id IS NOT NULL AND p.id IS NULL
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues['orphaned_records'].append({
            'table': 'sales',
            'issue': f'{orphaned} sales records reference non-existent products'
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
    
    # Check duplicate locations by name
    cursor.execute("""
        SELECT name, COUNT(*) as cnt 
        FROM locations 
        WHERE name IS NOT NULL
        GROUP BY name 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        for name, count in duplicates:
            issues['duplicate_records'].append({
                'table': 'locations',
                'issue': f'Location name "{name}" appears {count} times'
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
    
    cursor.execute("SELECT COUNT(*) FROM devices WHERE serial_number IS NULL OR serial_number = ''")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        issues['null_violations'].append({
            'table': 'devices',
            'issue': f'{null_count} devices missing serial number'
        })
    
    # Check products
    cursor.execute("SELECT COUNT(*) FROM products WHERE price IS NULL")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        issues['null_violations'].append({
            'table': 'products',
            'issue': f'{null_count} products missing price'
        })
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE par_level IS NULL")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        issues['null_violations'].append({
            'table': 'products',
            'issue': f'{null_count} products missing par level'
        })
    
    # Check users
    cursor.execute("SELECT COUNT(*) FROM users WHERE role IS NULL")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        issues['null_violations'].append({
            'table': 'users',
            'issue': f'{null_count} users have no role assigned'
        })
    
    # Check locations
    cursor.execute("SELECT COUNT(*) FROM locations WHERE address IS NULL OR address = ''")
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        issues['null_violations'].append({
            'table': 'locations',
            'issue': f'{null_count} locations missing address'
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
    
    # Check phone number formats
    cursor.execute("""
        SELECT COUNT(*) FROM locations 
        WHERE phone IS NOT NULL 
        AND phone \!= ''
        AND LENGTH(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, '-', ''), '(', ''), ')', ''), ' ', ''), '.', '')) NOT IN (10, 11)
    """)
    bad_phones = cursor.fetchone()[0]
    if bad_phones > 0:
        issues['format_issues'].append({
            'table': 'locations',
            'issue': f'{bad_phones} locations have invalid phone number format'
        })
    
    # Check date formats
    cursor.execute("""
        SELECT COUNT(*) FROM sales 
        WHERE transaction_date IS NOT NULL 
        AND datetime(transaction_date) IS NULL
    """)
    bad_dates = cursor.fetchone()[0]
    if bad_dates > 0:
        issues['format_issues'].append({
            'table': 'sales',
            'issue': f'{bad_dates} sales have invalid date format'
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
    
    # Check for zero prices
    cursor.execute("SELECT COUNT(*) FROM products WHERE price = 0")
    zero_prices = cursor.fetchone()[0]
    if zero_prices > 0:
        issues['business_rule_violations'].append({
            'table': 'products',
            'issue': f'{zero_prices} products have zero price'
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
    cursor.execute("SELECT COUNT(*) FROM planogram_slots WHERE capacity <= 0")
    invalid_capacity = cursor.fetchone()[0]
    if invalid_capacity > 0:
        issues['business_rule_violations'].append({
            'table': 'planogram_slots',
            'issue': f'{invalid_capacity} planogram slots have invalid capacity (<=0)'
        })
    
    # Check for overlapping planogram slots
    cursor.execute("""
        SELECT planogram_id, row, column, COUNT(*) as cnt
        FROM planogram_slots
        GROUP BY planogram_id, row, column
        HAVING COUNT(*) > 1
    """)
    overlapping = cursor.fetchall()
    if overlapping:
        total_overlaps = sum(cnt - 1 for _, _, _, cnt in overlapping)
        issues['business_rule_violations'].append({
            'table': 'planogram_slots',
            'issue': f'{total_overlaps} overlapping slot positions in {len(overlapping)} locations'
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
    
    # Check for invalid quantities in sales
    cursor.execute("SELECT COUNT(*) FROM sales WHERE quantity <= 0")
    invalid_qty = cursor.fetchone()[0]
    if invalid_qty > 0:
        issues['business_rule_violations'].append({
            'table': 'sales',
            'issue': f'{invalid_qty} sales records have invalid quantity (<=0)'
        })
    
    print(f"  Found {len(issues['business_rule_violations'])} business rule violations")
    
    # 6. Check for data anomalies
    print("\n6. CHECKING FOR DATA ANOMALIES...")
    
    # Check for extreme prices
    cursor.execute("""
        SELECT MIN(price), MAX(price), AVG(price), 
               COUNT(CASE WHEN price > 100 THEN 1 END) as extreme_high,
               COUNT(CASE WHEN price < 0.5 AND price > 0 THEN 1 END) as extreme_low
        FROM products WHERE price IS NOT NULL AND price > 0
    """)
    result = cursor.fetchone()
    if result[0] is not None:
        min_price, max_price, avg_price, extreme_high, extreme_low = result
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
    
    # Check for unusual par levels
    cursor.execute("""
        SELECT MIN(par_level), MAX(par_level), AVG(par_level),
               COUNT(CASE WHEN par_level > 100 THEN 1 END) as extreme_high
        FROM products WHERE par_level IS NOT NULL AND par_level > 0
    """)
    result = cursor.fetchone()
    if result[0] is not None:
        min_par, max_par, avg_par, extreme_high = result
        if extreme_high > 0:
            issues['data_anomalies'].append({
                'table': 'products',
                'issue': f'Par level anomalies: {extreme_high} products with par > 100. Range: {min_par}-{max_par}, Avg: {avg_par:.1f}'
            })
    
    # Check for suspicious user activity patterns
    cursor.execute("""
        SELECT user_id, COUNT(*) as action_count
        FROM user_activity_log
        WHERE timestamp >= datetime('now', '-1 day')
        GROUP BY user_id
        HAVING COUNT(*) > 1000
    """)
    suspicious_activity = cursor.fetchall()
    if suspicious_activity:
        for user_id, count in suspicious_activity:
            issues['data_anomalies'].append({
                'table': 'user_activity_log',
                'issue': f'User {user_id} has {count} activities in last 24 hours (potential bot/abuse)'
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
            'action': 'Convert INTEGER PRIMARY KEY AUTOINCREMENT to SERIAL/BIGSERIAL in PostgreSQL'
        })
    
    # Check for DATETIME/TIMESTAMP fields
    cursor.execute("""
        SELECT DISTINCT m.name as table_name
        FROM sqlite_master m
        WHERE type='table' AND (sql LIKE '%DATETIME%' OR sql LIKE '%TIMESTAMP%')
    """)
    datetime_tables = cursor.fetchall()
    if datetime_tables:
        migration_notes.append({
            'issue': 'Date/Time field conversion',
            'tables': [t[0] for t in datetime_tables],
            'action': 'Convert DATETIME/TIMESTAMP to TIMESTAMP WITH TIME ZONE for proper timezone handling'
        })
    
    # Check for TEXT fields
    cursor.execute("""
        SELECT DISTINCT m.name as table_name
        FROM sqlite_master m
        WHERE type='table' AND sql LIKE '%TEXT%'
    """)
    text_tables = cursor.fetchall()
    if text_tables:
        migration_notes.append({
            'issue': 'TEXT to VARCHAR/TEXT conversion',
            'tables': [t[0] for t in text_tables][:10],  # Limit to first 10
            'action': 'Review TEXT fields - use VARCHAR with length limits where appropriate, keep TEXT for unbounded fields'
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
            'action': 'Convert BLOB to BYTEA for binary data storage'
        })
    
    # Check for case-insensitive LIKE operations
    migration_notes.append({
        'issue': 'Case-insensitive search',
        'action': 'SQLite LIKE is case-insensitive by default, PostgreSQL is case-sensitive. Use ILIKE or LOWER() for case-insensitive searches'
    })
    
    # Check for string concatenation
    migration_notes.append({
        'issue': 'String concatenation operator',
        'action': 'Convert SQLite || operator usage to PostgreSQL CONCAT() function or ensure || operator is properly used'
    })
    
    # Foreign key constraints
    migration_notes.append({
        'issue': 'Foreign key constraints',
        'action': 'Ensure all foreign keys are properly defined with ON DELETE and ON UPDATE actions'
    })
    
    # Sequences for auto-increment
    migration_notes.append({
        'issue': 'Sequence management',
        'action': 'Create sequences for all auto-increment fields and set proper starting values based on existing data'
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
            if len(category_issues) > 5:
                print(f"  ... and {len(category_issues) - 5} more")
    
    print("\nMIGRATION CONSIDERATIONS:")
    for note in migration_notes:
        print(f"  - {note['issue']}")
        print(f"    Action: {note['action']}")
        if 'tables' in note and note['tables']:
            tables_str = ', '.join(note['tables'][:5])
            if len(note['tables']) > 5:
                tables_str += f" ... and {len(note['tables']) - 5} more"
            print(f"    Affected tables: {tables_str}")
    
    return issues, migration_notes

# Run quality assessment
issues, migration_notes = check_data_quality()

# Save results
with open('quality_assessment.json', 'w') as f:
    json.dump({'issues': issues, 'migration_notes': migration_notes}, f, indent=2, default=str)

print("\nDetailed results saved to quality_assessment.json")
