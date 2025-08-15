import sqlite3
import json
from datetime import datetime

def analyze_database():
    conn = sqlite3.connect('cvd.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    results = {}
    
    for table in tables:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
        row_count = cursor.fetchone()[0]
        
        # Get column info
        cursor.execute(f"PRAGMA table_info([{table}])")
        columns = cursor.fetchall()
        column_count = len(columns)
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list([{table}])")
        foreign_keys = cursor.fetchall()
        fk_count = len(foreign_keys)
        
        # Get indexes
        cursor.execute(f"PRAGMA index_list([{table}])")
        indexes = cursor.fetchall()
        index_count = len(indexes)
        
        # Check for timestamps to analyze growth
        has_created_at = any(col[1] == 'created_at' for col in columns)
        has_updated_at = any(col[1] == 'updated_at' for col in columns)
        
        growth_info = {}
        if has_created_at and row_count > 0:
            try:
                # Get date range
                cursor.execute(f"SELECT MIN(created_at), MAX(created_at) FROM [{table}] WHERE created_at IS NOT NULL")
                min_date, max_date = cursor.fetchone()
                
                if min_date and max_date:
                    # Get recent growth (last 30 days)
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM [{table}] 
                        WHERE created_at >= datetime('now', '-30 days')
                    """)
                    recent_30d = cursor.fetchone()[0]
                    
                    # Get last 7 days
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM [{table}] 
                        WHERE created_at >= datetime('now', '-7 days')
                    """)
                    recent_7d = cursor.fetchone()[0]
                    
                    # Get last 24 hours
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM [{table}] 
                        WHERE created_at >= datetime('now', '-1 days')
                    """)
                    recent_1d = cursor.fetchone()[0]
                    
                    growth_info = {
                        'first_record': min_date,
                        'last_record': max_date,
                        'last_30_days': recent_30d,
                        'last_7_days': recent_7d,
                        'last_24_hours': recent_1d,
                        'avg_daily_growth': recent_30d / 30 if recent_30d > 0 else 0
                    }
            except Exception as e:
                print(f"Error analyzing growth for {table}: {e}")
        
        results[table] = {
            'row_count': row_count,
            'column_count': column_count,
            'foreign_key_count': fk_count,
            'index_count': index_count,
            'has_created_at': has_created_at,
            'has_updated_at': has_updated_at,
            'growth_info': growth_info,
            'columns': [{'name': col[1], 'type': col[2], 'nullable': not col[3], 'default': col[4], 'pk': col[5]} for col in columns],
            'foreign_keys': [{'id': fk[0], 'table': fk[2], 'from': fk[3], 'to': fk[4]} for fk in foreign_keys]
        }
    
    conn.close()
    return results

# Analyze the database
analysis = analyze_database()

# Print summary
print("=" * 80)
print("DATABASE VOLUME ANALYSIS SUMMARY")
print("=" * 80)
print(f"Total tables: {len(analysis)}")
print(f"Total rows: {sum(t['row_count'] for t in analysis.values()):,}")
print()

# Top 10 largest tables by row count
print("TOP 10 TABLES BY ROW COUNT:")
sorted_by_rows = sorted(analysis.items(), key=lambda x: x[1]['row_count'], reverse=True)[:10]
for table, info in sorted_by_rows:
    print(f"  {table:35} {info['row_count']:10,} rows | {info['column_count']:3} cols | {info['foreign_key_count']:2} FKs")
print()

# Tables with highest growth
print("TABLES WITH RECENT ACTIVITY (last 30 days):")
active_tables = [(t, i) for t, i in analysis.items() if i['growth_info'] and i['growth_info'].get('last_30_days', 0) > 0]
active_tables.sort(key=lambda x: x[1]['growth_info']['last_30_days'], reverse=True)
for table, info in active_tables[:10]:
    growth = info['growth_info']
    print(f"  {table:35} {growth['last_30_days']:6,} (30d) | {growth['last_7_days']:6,} (7d) | {growth['last_24_hours']:6,} (24h)")

# Calculate relationships complexity
print("\nRELATIONSHIP COMPLEXITY:")
tables_with_fks = [(t, i) for t, i in analysis.items() if i['foreign_key_count'] > 0]
tables_with_fks.sort(key=lambda x: x[1]['foreign_key_count'], reverse=True)
for table, info in tables_with_fks[:10]:
    print(f"  {table:35} {info['foreign_key_count']:3} foreign keys")

# Save detailed results
with open('volume_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2, default=str)

print("\nDetailed analysis saved to volume_analysis.json")
