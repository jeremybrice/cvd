import sqlite3
import json
from datetime import datetime, timedelta
import os

def run_complete_analysis():
    conn = sqlite3.connect('cvd.db')
    cursor = conn.cursor()
    
    # ============= VOLUME ANALYSIS =============
    print("Running Volume Analysis...")
    
    # Get database file size
    db_size = os.path.getsize('cvd.db')
    
    # Get all tables with detailed statistics
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    volume_data = {
        'database_size_mb': round(db_size / 1024 / 1024, 2),
        'tables': {}
    }
    
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
        
        # Get indexes
        cursor.execute(f"PRAGMA index_list([{table}])")
        indexes = cursor.fetchall()
        
        # Estimate average row size (sample approach)
        avg_row_size = 0
        if row_count > 0:
            # Estimate based on column types
            for col in columns:
                col_type = col[2].upper()
                if 'INT' in col_type:
                    avg_row_size += 8
                elif 'TEXT' in col_type or 'VARCHAR' in col_type:
                    avg_row_size += 50  # Estimated average
                elif 'DECIMAL' in col_type or 'REAL' in col_type:
                    avg_row_size += 8
                elif 'TIMESTAMP' in col_type or 'DATETIME' in col_type:
                    avg_row_size += 20
                elif 'BLOB' in col_type:
                    avg_row_size += 100  # Estimated average
                else:
                    avg_row_size += 10
        
        # Check for created_at to analyze growth
        has_created_at = any(col[1] == 'created_at' for col in columns)
        
        growth_analysis = {
            'daily_average': 0,
            'weekly_average': 0,
            'monthly_average': 0,
            'last_30_days': 0,
            'last_7_days': 0,
            'last_24_hours': 0,
            'projected_annual': 0
        }
        
        if has_created_at and row_count > 0:
            try:
                # Get date range
                cursor.execute(f"SELECT MIN(created_at), MAX(created_at) FROM [{table}] WHERE created_at IS NOT NULL")
                min_date, max_date = cursor.fetchone()
                
                if min_date and max_date:
                    # Recent growth
                    cursor.execute(f"SELECT COUNT(*) FROM [{table}] WHERE created_at >= datetime('now', '-30 days')")
                    growth_analysis['last_30_days'] = cursor.fetchone()[0]
                    
                    cursor.execute(f"SELECT COUNT(*) FROM [{table}] WHERE created_at >= datetime('now', '-7 days')")
                    growth_analysis['last_7_days'] = cursor.fetchone()[0]
                    
                    cursor.execute(f"SELECT COUNT(*) FROM [{table}] WHERE created_at >= datetime('now', '-1 days')")
                    growth_analysis['last_24_hours'] = cursor.fetchone()[0]
                    
                    # Calculate averages
                    if growth_analysis['last_30_days'] > 0:
                        growth_analysis['daily_average'] = round(growth_analysis['last_30_days'] / 30, 1)
                        growth_analysis['weekly_average'] = round(growth_analysis['last_30_days'] / 4.3, 1)
                        growth_analysis['monthly_average'] = growth_analysis['last_30_days']
                        growth_analysis['projected_annual'] = round(growth_analysis['monthly_average'] * 12)
            except:
                pass
        
        volume_data['tables'][table] = {
            'row_count': row_count,
            'column_count': len(columns),
            'foreign_key_count': len(foreign_keys),
            'index_count': len(indexes),
            'estimated_row_size_bytes': avg_row_size,
            'estimated_table_size_mb': round((row_count * avg_row_size) / 1024 / 1024, 3),
            'has_timestamps': has_created_at,
            'growth_analysis': growth_analysis
        }
    
    # ============= QUALITY ANALYSIS =============
    print("Running Quality Analysis...")
    
    quality_data = {
        'orphaned_records': [],
        'duplicate_records': [],
        'null_violations': [],
        'format_issues': [],
        'business_rule_violations': [],
        'data_anomalies': [],
        'migration_considerations': []
    }
    
    # Check orphaned records
    checks = [
        ("devices", "location_id", "locations", "id"),
        ("cabinet_configurations", "device_id", "devices", "id"),
        ("planogram_slots", "planogram_id", "planograms", "id"),
        ("planogram_slots", "product_id", "products", "id"),
        ("sales", "device_id", "devices", "id"),
        ("sales", "product_id", "products", "id"),
        ("service_orders", "driver_id", "users", "id"),
        ("service_order_cabinets", "service_order_id", "service_orders", "id"),
        ("audit_log", "user_id", "users", "id"),
    ]
    
    for child_table, child_col, parent_table, parent_col in checks:
        try:
            cursor.execute(f"""
                SELECT COUNT(*) FROM [{child_table}] c 
                LEFT JOIN [{parent_table}] p ON c.{child_col} = p.{parent_col} 
                WHERE c.{child_col} IS NOT NULL AND p.{parent_col} IS NULL
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                quality_data['orphaned_records'].append({
                    'table': child_table,
                    'column': child_col,
                    'references': f"{parent_table}.{parent_col}",
                    'count': count
                })
        except:
            pass
    
    # Check for duplicates
    duplicate_checks = [
        ("devices", "asset"),
        ("users", "email"),
        ("locations", "name"),
        ("products", "name")
    ]
    
    for table, column in duplicate_checks:
        try:
            cursor.execute(f"""
                SELECT {column}, COUNT(*) as cnt 
                FROM [{table}]
                WHERE {column} IS NOT NULL
                GROUP BY {column}
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            if duplicates:
                for value, count in duplicates[:5]:  # Limit to first 5
                    quality_data['duplicate_records'].append({
                        'table': table,
                        'column': column,
                        'value': str(value)[:50],  # Truncate long values
                        'count': count
                    })
        except:
            pass
    
    # Check null violations
    null_checks = [
        ("devices", "location_id"),
        ("devices", "asset"),
        ("products", "price"),
        ("products", "par_level"),
        ("users", "email"),
        ("users", "role"),
        ("locations", "address")
    ]
    
    for table, column in null_checks:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{table}] WHERE {column} IS NULL OR {column} = ''")
            count = cursor.fetchone()[0]
            if count > 0:
                quality_data['null_violations'].append({
                    'table': table,
                    'column': column,
                    'count': count
                })
        except:
            pass
    
    # Check business rules
    # Negative values
    cursor.execute("SELECT COUNT(*) FROM products WHERE price < 0")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_data['business_rule_violations'].append({
            'rule': 'No negative prices',
            'violation': f'{count} products with negative prices'
        })
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE par_level < 0")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_data['business_rule_violations'].append({
            'rule': 'No negative par levels',
            'violation': f'{count} products with negative par levels'
        })
    
    cursor.execute("SELECT COUNT(*) FROM planogram_slots WHERE capacity <= 0")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_data['business_rule_violations'].append({
            'rule': 'Positive slot capacity',
            'violation': f'{count} slots with invalid capacity'
        })
    
    # Check for overlapping planogram slots
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT planogram_id, row, column, COUNT(*) as cnt
            FROM planogram_slots
            GROUP BY planogram_id, row, column
            HAVING COUNT(*) > 1
        )
    """)
    count = cursor.fetchone()[0]
    if count > 0:
        quality_data['business_rule_violations'].append({
            'rule': 'Unique slot positions',
            'violation': f'{count} overlapping slot positions'
        })
    
    # Data anomalies
    cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM products WHERE price > 0")
    min_price, max_price, avg_price = cursor.fetchone()
    if min_price is not None:
        quality_data['data_anomalies'].append({
            'type': 'Price range',
            'details': f'Min: ${min_price:.2f}, Max: ${max_price:.2f}, Avg: ${avg_price:.2f}'
        })
    
    # Future dates in sales
    cursor.execute("SELECT COUNT(*) FROM sales WHERE created_at > datetime('now')")
    count = cursor.fetchone()[0]
    if count > 0:
        quality_data['data_anomalies'].append({
            'type': 'Future dates',
            'details': f'{count} sales records with future dates'
        })
    
    # Migration considerations
    quality_data['migration_considerations'] = [
        {
            'area': 'Data Types',
            'items': [
                'Convert INTEGER PRIMARY KEY to SERIAL/BIGSERIAL',
                'Convert DATETIME/TIMESTAMP to TIMESTAMP WITH TIME ZONE',
                'Review TEXT fields for VARCHAR conversion with appropriate lengths',
                'Convert DECIMAL to NUMERIC with proper precision'
            ]
        },
        {
            'area': 'Constraints',
            'items': [
                'Add explicit foreign key constraints with ON DELETE/UPDATE actions',
                'Add CHECK constraints for business rules (e.g., price > 0)',
                'Add UNIQUE constraints where appropriate',
                'Review and add NOT NULL constraints'
            ]
        },
        {
            'area': 'Indexes',
            'items': [
                'Create indexes on all foreign key columns',
                'Add composite indexes for common query patterns',
                'Consider partial indexes for soft-deleted records',
                'Add GIN/GiST indexes for text search if needed'
            ]
        },
        {
            'area': 'Performance',
            'items': [
                'Consider partitioning for high-volume tables (sales, user_activity_log)',
                'Implement table inheritance for similar structures',
                'Use EXPLAIN ANALYZE to optimize query plans',
                'Consider materialized views for complex aggregations'
            ]
        }
    ]
    
    conn.close()
    
    return volume_data, quality_data

# Run analysis
print("Starting comprehensive data migration analysis...")
volume_results, quality_results = run_complete_analysis()

# Save results
with open('migration_analysis_results.json', 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'volume_analysis': volume_results,
        'quality_assessment': quality_results
    }, f, indent=2)

print("Analysis complete. Results saved to migration_analysis_results.json")

# Print summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Database Size: {volume_results['database_size_mb']} MB")
print(f"Total Tables: {len(volume_results['tables'])}")
print(f"Total Rows: {sum(t['row_count'] for t in volume_results['tables'].values()):,}")

# Top tables by size
top_tables = sorted(volume_results['tables'].items(), key=lambda x: x[1]['row_count'], reverse=True)[:5]
print("\nTop 5 Tables by Row Count:")
for table, data in top_tables:
    print(f"  {table:30} {data['row_count']:10,} rows")

# Quality issues
total_issues = (
    len(quality_results['orphaned_records']) +
    len(quality_results['duplicate_records']) +
    len(quality_results['null_violations']) +
    len(quality_results['business_rule_violations'])
)
print(f"\nTotal Quality Issues Found: {total_issues}")
print(f"  Orphaned Records: {len(quality_results['orphaned_records'])}")
print(f"  Duplicate Records: {len(quality_results['duplicate_records'])}")
print(f"  Null Violations: {len(quality_results['null_violations'])}")
print(f"  Business Rule Violations: {len(quality_results['business_rule_violations'])}")
