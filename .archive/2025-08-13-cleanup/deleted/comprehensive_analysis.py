import sqlite3
import json
from datetime import datetime, timedelta

def comprehensive_data_analysis():
    conn = sqlite3.connect('cvd.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("COMPREHENSIVE DATA MIGRATION ANALYSIS")
    print("=" * 80)
    
    # Get database size
    import os
    db_size = os.path.getsize('cvd.db')
    print(f"\nDatabase file size: {db_size / 1024 / 1024:.2f} MB")
    
    # Volume analysis with detailed statistics
    volume_analysis = {}
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
        row_count = cursor.fetchone()[0]
        
        # Get column info
        cursor.execute(f"PRAGMA table_info([{table}])")
        columns = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list([{table}])")
        foreign_keys = cursor.fetchall()
        
        # Check for timestamps
        has_created_at = any(col[1] == 'created_at' for col in columns)
        
        # Analyze growth if has timestamp
        growth_stats = {}
        if has_created_at and row_count > 0:
            try:
                # Monthly growth analysis
                cursor.execute(f"""
                    SELECT 
                        strftime('%Y-%m', created_at) as month,
                        COUNT(*) as count
                    FROM [{table}]
                    WHERE created_at IS NOT NULL
                    GROUP BY strftime('%Y-%m', created_at)
                    ORDER BY month DESC
                    LIMIT 12
                """)
                monthly_data = cursor.fetchall()
                
                if monthly_data:
                    growth_stats['monthly_growth'] = dict(monthly_data)
                    
                    # Calculate average monthly growth
                    if len(monthly_data) > 1:
                        recent_3_months = sum(count for _, count in monthly_data[:3]) / 3
                        growth_stats['avg_monthly_growth'] = round(recent_3_months, 1)
            except:
                pass
        
        volume_analysis[table] = {
            'row_count': row_count,
            'column_count': len(columns),
            'foreign_key_count': len(foreign_keys),
            'has_timestamps': has_created_at,
            'growth_stats': growth_stats
        }
    
    # Quality assessment
    quality_issues = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': []
    }
    
    # Check orphaned records
    print("\nCHECKING DATA QUALITY...")
    
    # Critical: Check devices without locations
    cursor.execute("SELECT COUNT(*) FROM devices WHERE location_id IS NULL OR location_id = 0")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_issues['critical'].append(f"{count} devices without valid location")
    
    # Critical: Check products without prices
    cursor.execute("SELECT COUNT(*) FROM products WHERE price IS NULL OR price <= 0")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_issues['critical'].append(f"{count} products without valid price")
    
    # High: Check for duplicate device assets
    cursor.execute("""
        SELECT asset, COUNT(*) as cnt 
        FROM devices 
        WHERE asset IS NOT NULL AND deleted_at IS NULL
        GROUP BY asset 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        quality_issues['high'].append(f"{len(duplicates)} duplicate device assets found")
    
    # High: Check planogram slots without products
    cursor.execute("SELECT COUNT(*) FROM planogram_slots WHERE product_id IS NULL OR product_id = 0")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_issues['high'].append(f"{count} planogram slots without products")
    
    # Medium: Check sales with future dates
    cursor.execute("SELECT COUNT(*) FROM sales WHERE transaction_date > datetime('now')")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_issues['medium'].append(f"{count} sales with future dates")
    
    # Medium: Check for invalid email formats
    cursor.execute("SELECT COUNT(*) FROM users WHERE email NOT LIKE '%@%.%'")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_issues['medium'].append(f"{count} users with invalid email format")
    
    # Low: Check for missing phone numbers in locations
    cursor.execute("SELECT COUNT(*) FROM locations WHERE phone IS NULL OR phone = ''")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_issues['low'].append(f"{count} locations without phone numbers")
    
    # Migration complexity analysis
    migration_complexity = {
        'high_volume_tables': [],
        'high_growth_tables': [],
        'complex_relationships': [],
        'large_text_fields': [],
        'binary_data_tables': []
    }
    
    # Identify high volume tables (>1000 rows)
    for table, stats in volume_analysis.items():
        if stats['row_count'] > 1000:
            migration_complexity['high_volume_tables'].append({
                'table': table,
                'rows': stats['row_count']
            })
        
        # High growth tables
        if stats['growth_stats'] and stats['growth_stats'].get('avg_monthly_growth', 0) > 100:
            migration_complexity['high_growth_tables'].append({
                'table': table,
                'avg_monthly_growth': stats['growth_stats']['avg_monthly_growth']
            })
        
        # Complex relationships (>2 foreign keys)
        if stats['foreign_key_count'] > 2:
            migration_complexity['complex_relationships'].append({
                'table': table,
                'foreign_keys': stats['foreign_key_count']
            })
    
    # Check for large text fields
    cursor.execute("""
        SELECT m.name, COUNT(*) as text_columns
        FROM sqlite_master m, pragma_table_info(m.name) p
        WHERE m.type = 'table' AND p.type = 'TEXT'
        GROUP BY m.name
        HAVING COUNT(*) > 3
    """)
    large_text = cursor.fetchall()
    for table, count in large_text:
        migration_complexity['large_text_fields'].append({
            'table': table,
            'text_columns': count
        })
    
    conn.close()
    
    return volume_analysis, quality_issues, migration_complexity

# Run comprehensive analysis
volume, quality, complexity = comprehensive_data_analysis()

# Display summary
print("\n" + "=" * 80)
print("ANALYSIS SUMMARY")
print("=" * 80)

# Volume Summary
total_rows = sum(t['row_count'] for t in volume.values())
print(f"\nTotal Tables: {len(volume)}")
print(f"Total Rows: {total_rows:,}")

print("\nTop 5 Largest Tables:")
largest = sorted(volume.items(), key=lambda x: x[1]['row_count'], reverse=True)[:5]
for table, stats in largest:
    print(f"  {table:30} {stats['row_count']:10,} rows")

# Quality Summary
print("\nData Quality Issues:")
for severity, issues in quality.items():
    if issues:
        print(f"  {severity.upper()}: {len(issues)} issues")
        for issue in issues[:2]:
            print(f"    - {issue}")

# Complexity Summary
print("\nMigration Complexity:")
print(f"  High-volume tables (>1000 rows): {len(complexity['high_volume_tables'])}")
print(f"  High-growth tables: {len(complexity['high_growth_tables'])}")
print(f"  Tables with complex relationships: {len(complexity['complex_relationships'])}")

# Save detailed results
results = {
    'timestamp': datetime.now().isoformat(),
    'volume_analysis': volume,
    'quality_issues': quality,
    'migration_complexity': complexity
}

with open('comprehensive_analysis.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("\nDetailed results saved to comprehensive_analysis.json")
