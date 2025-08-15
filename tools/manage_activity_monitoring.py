#!/usr/bin/env python3
"""
Activity Monitoring Management Tool
Provides administrative functions for the activity monitoring system
"""

import sqlite3
import sys
import argparse
from datetime import datetime, timedelta
import json

DATABASE = '../cvd.db'

def get_stats():
    """Get current activity monitoring statistics"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    print("\n📊 Activity Monitoring Statistics")
    print("=" * 50)
    
    # Active sessions
    active = cursor.execute("""
        SELECT COUNT(*) FROM sessions 
        WHERE expires_at > datetime('now')
    """).fetchone()[0]
    
    print(f"Active Sessions: {active}")
    
    # Activity records
    total_activities = cursor.execute("""
        SELECT COUNT(*) FROM user_activity_log
    """).fetchone()[0]
    
    recent_activities = cursor.execute("""
        SELECT COUNT(*) FROM user_activity_log
        WHERE timestamp > datetime('now', '-24 hours')
    """).fetchone()[0]
    
    print(f"Total Activity Records: {total_activities}")
    print(f"Activities (last 24h): {recent_activities}")
    
    # Alerts
    pending_alerts = cursor.execute("""
        SELECT COUNT(*) FROM activity_alerts
        WHERE status = 'pending'
    """).fetchone()[0]
    
    print(f"Pending Alerts: {pending_alerts}")
    
    # Database size
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    size_bytes = cursor.fetchone()[0]
    size_mb = size_bytes / (1024 * 1024)
    print(f"Database Size: {size_mb:.2f} MB")
    
    # Top active users today
    print("\n👥 Top Active Users (Today)")
    print("-" * 30)
    
    top_users = cursor.execute("""
        SELECT u.username, u.role, COUNT(*) as activity_count
        FROM user_activity_log l
        JOIN users u ON l.user_id = u.id
        WHERE l.timestamp > datetime('now', 'start of day')
        GROUP BY l.user_id
        ORDER BY activity_count DESC
        LIMIT 5
    """).fetchall()
    
    for user in top_users:
        print(f"  {user[0]} ({user[1]}): {user[2]} activities")
    
    # Most visited pages today
    print("\n📄 Most Visited Pages (Today)")
    print("-" * 30)
    
    top_pages = cursor.execute("""
        SELECT page_url, COUNT(*) as visits
        FROM user_activity_log
        WHERE timestamp > datetime('now', 'start of day')
        AND action_type = 'page_view'
        GROUP BY page_url
        ORDER BY visits DESC
        LIMIT 5
    """).fetchall()
    
    for page in top_pages:
        print(f"  {page[0]}: {page[1]} visits")
    
    db.close()

def cleanup_data(days=None):
    """Manually trigger data cleanup"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    if days is None:
        # Get from config
        days = cursor.execute("""
            SELECT value FROM system_config 
            WHERE key = 'activity_retention_days'
        """).fetchone()
        days = int(days[0]) if days else 90
    
    cutoff = datetime.now() - timedelta(days=days)
    
    print(f"\n🧹 Cleaning up data older than {days} days (before {cutoff.date()})")
    
    # Delete old activity logs
    deleted = cursor.execute("""
        DELETE FROM user_activity_log
        WHERE timestamp < ?
    """, (cutoff,)).rowcount
    
    print(f"  Deleted {deleted} activity records")
    
    # Delete old sessions
    deleted_sessions = cursor.execute("""
        DELETE FROM sessions
        WHERE expires_at < datetime('now')
    """).rowcount
    
    print(f"  Deleted {deleted_sessions} expired sessions")
    
    # Vacuum database
    print("  Optimizing database...")
    cursor.execute("VACUUM")
    
    db.commit()
    db.close()
    print("✅ Cleanup completed")

def toggle_monitoring():
    """Enable or disable activity monitoring"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    current = cursor.execute("""
        SELECT value FROM system_config 
        WHERE key = 'activity_monitoring_enabled'
    """).fetchone()
    
    current_value = current[0] if current else 'true'
    new_value = 'false' if current_value == 'true' else 'true'
    
    cursor.execute("""
        UPDATE system_config 
        SET value = ?, updated_at = ?
        WHERE key = 'activity_monitoring_enabled'
    """, (new_value, datetime.now()))
    
    db.commit()
    db.close()
    
    status = "ENABLED" if new_value == 'true' else "DISABLED"
    print(f"\n✅ Activity monitoring is now {status}")

def generate_summary(date_str=None):
    """Generate daily summary for a specific date"""
    from data_retention_service import DataRetentionService
    
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            print("❌ Invalid date format. Use YYYY-MM-DD")
            return
    else:
        # Default to yesterday
        target_date = (datetime.now() - timedelta(days=1)).date()
    
    print(f"\n📊 Generating summary for {target_date}...")
    
    service = DataRetentionService(None, DATABASE)
    service.generate_daily_summary(target_date)
    
    print("✅ Summary generation completed")

def clear_alerts():
    """Clear all pending alerts"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    count = cursor.execute("""
        SELECT COUNT(*) FROM activity_alerts
        WHERE status = 'pending'
    """).fetchone()[0]
    
    if count == 0:
        print("\nℹ️  No pending alerts to clear")
        return
    
    response = input(f"\n⚠️  Clear {count} pending alerts? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled")
        return
    
    cursor.execute("""
        UPDATE activity_alerts
        SET status = 'dismissed', resolved_at = ?
        WHERE status = 'pending'
    """, (datetime.now(),))
    
    db.commit()
    db.close()
    
    print(f"✅ Cleared {count} alerts")

def export_activity(user=None, days=7):
    """Export activity data to JSON"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    
    if user:
        # Get user ID
        user_data = cursor.execute("""
            SELECT id, username FROM users WHERE username = ?
        """, (user,)).fetchone()
        
        if not user_data:
            print(f"❌ User '{user}' not found")
            return
        
        activities = cursor.execute("""
            SELECT * FROM user_activity_log
            WHERE user_id = ? AND timestamp > ?
            ORDER BY timestamp DESC
        """, (user_data['id'], cutoff)).fetchall()
        
        filename = f"activity_export_{user}_{datetime.now().strftime('%Y%m%d')}.json"
    else:
        activities = cursor.execute("""
            SELECT l.*, u.username
            FROM user_activity_log l
            JOIN users u ON l.user_id = u.id
            WHERE l.timestamp > ?
            ORDER BY l.timestamp DESC
        """, (cutoff,)).fetchall()
        
        filename = f"activity_export_all_{datetime.now().strftime('%Y%m%d')}.json"
    
    # Convert to list of dicts
    data = []
    for row in activities:
        data.append(dict(row))
    
    # Write to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    db.close()
    print(f"✅ Exported {len(data)} records to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Activity Monitoring Management Tool')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    subparsers.add_parser('stats', help='Show activity monitoring statistics')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old data')
    cleanup_parser.add_argument('--days', type=int, help='Days of data to keep')
    
    # Toggle command
    subparsers.add_parser('toggle', help='Enable/disable activity monitoring')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Generate daily summary')
    summary_parser.add_argument('--date', help='Date to generate summary for (YYYY-MM-DD)')
    
    # Clear alerts command
    subparsers.add_parser('clear-alerts', help='Clear all pending alerts')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export activity data')
    export_parser.add_argument('--user', help='Export data for specific user')
    export_parser.add_argument('--days', type=int, default=7, help='Days of data to export')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'stats':
        get_stats()
    elif args.command == 'cleanup':
        cleanup_data(args.days)
    elif args.command == 'toggle':
        toggle_monitoring()
    elif args.command == 'summary':
        generate_summary(args.date)
    elif args.command == 'clear-alerts':
        clear_alerts()
    elif args.command == 'export':
        export_activity(args.user, args.days)

if __name__ == '__main__':
    main()