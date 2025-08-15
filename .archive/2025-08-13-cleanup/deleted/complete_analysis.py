import sqlite3
import json
from datetime import datetime
import os

# Run complete analysis
conn = sqlite3.connect('cvd.db')
cursor = conn.cursor()

# Get all data we need
print("Gathering database statistics...")

# Database file size
db_size = os.path.getsize('cvd.db')

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

# Detailed table analysis
table_stats = {}
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
    row_count = cursor.fetchone()[0]
    
    cursor.execute(f"PRAGMA table_info([{table}])")
    columns = cursor.fetchall()
    
    cursor.execute(f"PRAGMA foreign_key_list([{table}])")
    fks = cursor.fetchall()
    
    cursor.execute(f"PRAGMA index_list([{table}])")
    indexes = cursor.fetchall()
    
    # Check for created_at column
    has_created_at = any(col[1] == 'created_at' for col in columns)
    
    # Growth analysis
    growth_data = {}
    if has_created_at and row_count > 0:
        try:
            cursor.execute(f"""
                SELECT 
                    (SELECT COUNT(*) FROM [{table}] WHERE created_at >= datetime('now', '-1 days')) as last_24h,
                    (SELECT COUNT(*) FROM [{table}] WHERE created_at >= datetime('now', '-7 days')) as last_7d,
                    (SELECT COUNT(*) FROM [{table}] WHERE created_at >= datetime('now', '-30 days')) as last_30d,
                    (SELECT MIN(created_at) FROM [{table}]) as first_record,
                    (SELECT MAX(created_at) FROM [{table}]) as last_record
            """)
            result = cursor.fetchone()
            growth_data = {
                'last_24_hours': result[0],
                'last_7_days': result[1],
                'last_30_days': result[2],
                'first_record': result[3],
                'last_record': result[4]
            }
        except:
            pass
    
    table_stats[table] = {
        'row_count': row_count,
        'columns': len(columns),
        'foreign_keys': len(fks),
        'indexes': len(indexes),
        'has_timestamps': has_created_at,
        'growth': growth_data
    }

# Quality checks
print("Running quality checks...")
quality_issues = []

# Check orphaned device records
cursor.execute("""
    SELECT COUNT(*) FROM devices d 
    LEFT JOIN locations l ON d.location_id = l.id 
    WHERE d.location_id IS NOT NULL AND l.id IS NULL
""")
orphaned = cursor.fetchone()[0]
if orphaned > 0:
    quality_issues.append(f"CRITICAL: {orphaned} devices reference non-existent locations")

# Check orphaned sales
cursor.execute("""
    SELECT COUNT(*) FROM sales s 
    LEFT JOIN devices d ON s.device_id = d.id 
    WHERE s.device_id IS NOT NULL AND d.id IS NULL
""")
orphaned = cursor.fetchone()[0]
if orphaned > 0:
    quality_issues.append(f"CRITICAL: {orphaned} sales records reference non-existent devices")

# Check duplicate device assets
cursor.execute("""
    SELECT COUNT(*) FROM (
        SELECT asset, COUNT(*) as cnt 
        FROM devices 
        WHERE asset IS NOT NULL AND deleted_at IS NULL
        GROUP BY asset 
        HAVING COUNT(*) > 1
    )
""")
duplicates = cursor.fetchone()[0]
if duplicates > 0:
    quality_issues.append(f"HIGH: {duplicates} duplicate device assets found")

# Check null critical fields
cursor.execute("SELECT COUNT(*) FROM devices WHERE location_id IS NULL")
null_locations = cursor.fetchone()[0]
if null_locations > 0:
    quality_issues.append(f"HIGH: {null_locations} devices without location")

cursor.execute("SELECT COUNT(*) FROM products WHERE price IS NULL OR price <= 0")
bad_prices = cursor.fetchone()[0]
if bad_prices > 0:
    quality_issues.append(f"HIGH: {bad_prices} products with invalid prices")

# Check email formats
cursor.execute("SELECT COUNT(*) FROM users WHERE email NOT LIKE '%@%.%'")
bad_emails = cursor.fetchone()[0]
if bad_emails > 0:
    quality_issues.append(f"MEDIUM: {bad_emails} users with invalid email format")

# Check future dates
cursor.execute("SELECT COUNT(*) FROM sales WHERE created_at > datetime('now')")
future_sales = cursor.fetchone()[0]
if future_sales > 0:
    quality_issues.append(f"MEDIUM: {future_sales} sales with future dates")

conn.close()

# Prepare final results
results = {
    'analysis_date': datetime.now().isoformat(),
    'database': {
        'file_size_mb': round(db_size / 1024 / 1024, 2),
        'table_count': len(tables),
        'total_rows': sum(t['row_count'] for t in table_stats.values())
    },
    'tables': table_stats,
    'quality_issues': quality_issues,
    'high_volume_tables': [
        {'name': k, 'rows': v['row_count']} 
        for k, v in sorted(table_stats.items(), key=lambda x: x[1]['row_count'], reverse=True)[:10]
    ],
    'high_growth_tables': [
        {'name': k, 'last_30_days': v['growth'].get('last_30_days', 0)}
        for k, v in table_stats.items() 
        if v['growth'] and v['growth'].get('last_30_days', 0) > 100
    ]
}

# Save JSON results
with open('database_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nAnalysis Complete\!")
print(f"Database Size: {results['database']['file_size_mb']} MB")
print(f"Total Tables: {results['database']['table_count']}")
print(f"Total Rows: {results['database']['total_rows']:,}")
print(f"Quality Issues Found: {len(quality_issues)}")
