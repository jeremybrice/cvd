"""
Data Retention Service for Activity Monitoring
Handles automatic cleanup of old activity data and session management
"""

import sqlite3
import threading
import time
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class DataRetentionService:
    """Service for managing data retention and cleanup"""
    
    def __init__(self, app, db_path):
        """Initialize data retention service"""
        self.app = app
        self.db_path = db_path
        self.is_running = True
        self.cleanup_thread = None
        self.daily_summary_thread = None
        
        # Schedule cleanup tasks
        self.schedule_cleanup()
        self.schedule_daily_summary()
        
        logger.info("Data Retention Service initialized")
    
    def get_config(self, key, default=None):
        """Get configuration value from database"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            result = cursor.execute(
                "SELECT value FROM system_config WHERE key = ?", 
                (key,)
            ).fetchone()
            
            db.close()
            return result[0] if result else default
            
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")
            return default
    
    def schedule_cleanup(self):
        """Schedule daily cleanup job at 2 AM"""
        def run_cleanup():
            """Run cleanup tasks periodically"""
            while self.is_running:
                try:
                    # Calculate time until 2 AM
                    now = datetime.now()
                    target = now.replace(hour=2, minute=0, second=0, microsecond=0)
                    
                    # If it's already past 2 AM today, schedule for tomorrow
                    if target <= now:
                        target += timedelta(days=1)
                    
                    # Calculate seconds until target time
                    delay = (target - now).total_seconds()
                    
                    logger.info(f"Next cleanup scheduled for {target} ({delay/3600:.1f} hours from now)")
                    
                    # Wait until target time or shutdown
                    start_time = time.time()
                    while self.is_running and (time.time() - start_time) < delay:
                        time.sleep(60)  # Check every minute for shutdown
                    
                    if self.is_running:
                        logger.info("Starting scheduled cleanup tasks...")
                        self.cleanup_old_activity_data()
                        self.cleanup_expired_sessions()
                        self.cleanup_old_alerts()
                        self.optimize_database()
                        logger.info("Scheduled cleanup tasks completed")
                        
                except Exception as e:
                    logger.error(f"Cleanup scheduler error: {e}")
                    # Wait before retrying
                    time.sleep(3600)  # Wait 1 hour before retry
        
        self.cleanup_thread = threading.Thread(
            target=run_cleanup, 
            daemon=True, 
            name='DataRetentionCleanup'
        )
        self.cleanup_thread.start()
        logger.info("Data retention cleanup scheduler started")
    
    def cleanup_old_activity_data(self):
        """Remove activity data older than retention period"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            # Get retention settings
            retention_days = int(self.get_config('activity_retention_days', '90'))
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            logger.info(f"Cleaning up activity data older than {retention_days} days (before {cutoff_date})")
            
            # Delete old activity logs
            deleted = cursor.execute('''
                DELETE FROM user_activity_log
                WHERE timestamp < ?
            ''', (cutoff_date,)).rowcount
            
            if deleted > 0:
                logger.info(f"Deleted {deleted} old activity log records")
            
            # Clean up old daily summaries (keep longer than detailed logs)
            summary_retention_days = int(self.get_config('activity_summary_retention_days', '730'))
            summary_cutoff = datetime.now() - timedelta(days=summary_retention_days)
            
            deleted_summaries = cursor.execute('''
                DELETE FROM activity_summary_daily
                WHERE date < ?
            ''', (summary_cutoff.date(),)).rowcount
            
            if deleted_summaries > 0:
                logger.info(f"Deleted {deleted_summaries} old summary records")
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to cleanup old activity data: {e}")
            if db:
                db.close()
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            # Delete sessions that have expired
            deleted = cursor.execute('''
                DELETE FROM sessions
                WHERE expires_at < datetime('now')
            ''').rowcount
            
            if deleted > 0:
                logger.info(f"Deleted {deleted} expired sessions")
            
            # Also clean up sessions that have been inactive for too long
            # (even if not technically expired)
            inactive_hours = 24  # Sessions inactive for 24 hours
            inactive_cutoff = datetime.now() - timedelta(hours=inactive_hours)
            
            deleted_inactive = cursor.execute('''
                DELETE FROM sessions
                WHERE last_activity < ? AND last_activity IS NOT NULL
            ''', (inactive_cutoff,)).rowcount
            
            if deleted_inactive > 0:
                logger.info(f"Deleted {deleted_inactive} inactive sessions")
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            if db:
                db.close()
    
    def cleanup_old_alerts(self):
        """Clean up old resolved/dismissed alerts"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            # Keep resolved/dismissed alerts for 30 days
            alert_retention_days = 30
            cutoff_date = datetime.now() - timedelta(days=alert_retention_days)
            
            # Delete old resolved/dismissed alerts
            deleted = cursor.execute('''
                DELETE FROM activity_alerts
                WHERE created_at < ? 
                AND status IN ('resolved', 'dismissed')
            ''', (cutoff_date,)).rowcount
            
            if deleted > 0:
                logger.info(f"Deleted {deleted} old alerts")
            
            # Auto-dismiss old pending alerts (older than 7 days)
            auto_dismiss_days = 7
            auto_dismiss_cutoff = datetime.now() - timedelta(days=auto_dismiss_days)
            
            auto_dismissed = cursor.execute('''
                UPDATE activity_alerts
                SET status = 'dismissed',
                    resolved_at = ?
                WHERE created_at < ? 
                AND status = 'pending'
            ''', (datetime.now(), auto_dismiss_cutoff)).rowcount
            
            if auto_dismissed > 0:
                logger.info(f"Auto-dismissed {auto_dismissed} old pending alerts")
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to cleanup old alerts: {e}")
            if db:
                db.close()
    
    def optimize_database(self):
        """Optimize database by running VACUUM and ANALYZE"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            # Get database size before optimization
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            size_before = cursor.fetchone()[0]
            
            # Run VACUUM to reclaim space
            logger.info("Running VACUUM to optimize database...")
            cursor.execute("VACUUM")
            
            # Run ANALYZE to update statistics
            cursor.execute("ANALYZE")
            
            # Get database size after optimization
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            size_after = cursor.fetchone()[0]
            
            if size_before > size_after:
                saved_mb = (size_before - size_after) / (1024 * 1024)
                logger.info(f"Database optimized, freed {saved_mb:.2f} MB")
            else:
                logger.info("Database optimized")
            
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")
            if db:
                db.close()
    
    def schedule_daily_summary(self):
        """Schedule daily summary generation at 1 AM"""
        def run_summary():
            """Generate daily summaries periodically"""
            while self.is_running:
                try:
                    # Calculate time until 1 AM
                    now = datetime.now()
                    target = now.replace(hour=1, minute=0, second=0, microsecond=0)
                    
                    # If it's already past 1 AM today, schedule for tomorrow
                    if target <= now:
                        target += timedelta(days=1)
                    
                    # Calculate seconds until target time
                    delay = (target - now).total_seconds()
                    
                    logger.info(f"Next summary generation scheduled for {target}")
                    
                    # Wait until target time or shutdown
                    start_time = time.time()
                    while self.is_running and (time.time() - start_time) < delay:
                        time.sleep(60)  # Check every minute for shutdown
                    
                    if self.is_running:
                        logger.info("Generating daily activity summary...")
                        self.generate_daily_summary()
                        
                except Exception as e:
                    logger.error(f"Summary scheduler error: {e}")
                    time.sleep(3600)  # Wait 1 hour before retry
        
        self.daily_summary_thread = threading.Thread(
            target=run_summary, 
            daemon=True, 
            name='DailySummaryGenerator'
        )
        self.daily_summary_thread.start()
        logger.info("Daily summary generator started")
    
    def generate_daily_summary(self, date=None):
        """Generate activity summary for a specific date"""
        try:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            # Default to yesterday if no date specified
            if date is None:
                date = (datetime.now() - timedelta(days=1)).date()
            
            logger.info(f"Generating summary for {date}")
            
            # Check if summary already exists
            existing = cursor.execute('''
                SELECT id FROM activity_summary_daily 
                WHERE date = ?
            ''', (date,)).fetchone()
            
            if existing:
                logger.info(f"Summary already exists for {date}")
                db.close()
                return
            
            # Calculate date range
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = start_datetime + timedelta(days=1)
            
            # Get metrics
            metrics = cursor.execute('''
                SELECT 
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT session_id) as total_sessions,
                    SUM(CASE WHEN action_type = 'page_view' THEN 1 ELSE 0 END) as page_views,
                    SUM(CASE WHEN action_type = 'api_call' THEN 1 ELSE 0 END) as api_calls,
                    AVG(duration_ms) / 1000 as avg_duration_seconds
                FROM user_activity_log
                WHERE timestamp >= ? AND timestamp < ?
            ''', (start_datetime, end_datetime)).fetchone()
            
            if not metrics or metrics['unique_users'] == 0:
                logger.info(f"No activity data for {date}")
                db.close()
                return
            
            # Get peak concurrent users by hour
            hourly_users = cursor.execute('''
                SELECT 
                    strftime('%H', timestamp) as hour,
                    COUNT(DISTINCT user_id) as user_count
                FROM user_activity_log
                WHERE timestamp >= ? AND timestamp < ?
                GROUP BY hour
                ORDER BY user_count DESC
                LIMIT 1
            ''', (start_datetime, end_datetime)).fetchone()
            
            peak_hour = int(hourly_users['hour']) if hourly_users else None
            peak_users = hourly_users['user_count'] if hourly_users else 0
            
            # Get top pages
            top_pages = cursor.execute('''
                SELECT page_url, COUNT(*) as count
                FROM user_activity_log
                WHERE timestamp >= ? AND timestamp < ? 
                AND action_type = 'page_view'
                GROUP BY page_url
                ORDER BY count DESC
                LIMIT 10
            ''', (start_datetime, end_datetime)).fetchall()
            
            top_pages_json = json.dumps([
                {'url': row[0], 'count': row[1]} for row in top_pages
            ])
            
            # Get user distribution by role
            user_dist = cursor.execute('''
                SELECT u.role, COUNT(DISTINCT l.user_id) as count
                FROM user_activity_log l
                JOIN users u ON l.user_id = u.id
                WHERE l.timestamp >= ? AND l.timestamp < ?
                GROUP BY u.role
            ''', (start_datetime, end_datetime)).fetchall()
            
            user_dist_json = json.dumps({
                row[0]: row[1] for row in user_dist
            })
            
            # Calculate average session duration
            session_durations = cursor.execute('''
                SELECT 
                    session_id,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time
                FROM user_activity_log
                WHERE timestamp >= ? AND timestamp < ?
                GROUP BY session_id
            ''', (start_datetime, end_datetime)).fetchall()
            
            if session_durations:
                total_duration = sum(
                    (datetime.fromisoformat(row[2]) - datetime.fromisoformat(row[1])).total_seconds()
                    for row in session_durations
                )
                avg_session_duration = int(total_duration / len(session_durations))
            else:
                avg_session_duration = 0
            
            # Insert summary
            cursor.execute('''
                INSERT INTO activity_summary_daily 
                (date, unique_users, total_sessions, total_page_views, 
                 total_api_calls, avg_session_duration_seconds,
                 peak_concurrent_users, peak_hour, top_pages, user_distribution)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date,
                metrics['unique_users'],
                metrics['total_sessions'],
                metrics['page_views'] or 0,
                metrics['api_calls'] or 0,
                avg_session_duration,
                peak_users,
                peak_hour,
                top_pages_json,
                user_dist_json
            ))
            
            db.commit()
            logger.info(f"Generated summary for {date}: {metrics['unique_users']} users, {metrics['total_sessions']} sessions")
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to generate daily summary: {e}")
            if db:
                db.close()
    
    def shutdown(self):
        """Gracefully shutdown the retention service"""
        logger.info("Shutting down Data Retention Service...")
        self.is_running = False
        
        # Wait for threads to finish
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        if self.daily_summary_thread:
            self.daily_summary_thread.join(timeout=5)
        
        logger.info("Data Retention Service shutdown complete")