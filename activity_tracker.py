"""
Activity Tracking Middleware for CVD Application
Provides real-time user activity monitoring with minimal performance impact
"""

import json
import time
import sqlite3
import threading
import queue
from datetime import datetime, timedelta
from flask import g, request, session
from functools import wraps
import logging

# Set up logging
logger = logging.getLogger(__name__)


class ActivityTracker:
    """Main activity tracking middleware class"""
    
    def __init__(self, app, db_path):
        """Initialize activity tracker with Flask app and database path"""
        self.app = app
        self.db_path = db_path
        self.cache = {}  # In-memory cache for active sessions
        self.cache_ttl = 30  # Cache TTL in seconds
        self.max_cache_size = 500  # Maximum cache entries
        self.cache_lock = threading.Lock()
        self.activity_queue = queue.Queue(maxsize=1000)
        self.cleanup_lock = threading.Lock()
        self.is_running = True
        
        # Configuration cache
        self.config_cache = {}
        self.config_cache_time = 0
        self.config_cache_ttl = 300  # Refresh config every 5 minutes
        
        # Start background worker thread
        self.worker_thread = None
        self.start_background_worker()
        
        # Start cleanup scheduler
        self.cleanup_thread = None
        self.schedule_cleanup()
        
        self.app.logger.info("Activity Tracker initialized")
    
    def get_config(self, key, default=None):
        """Get configuration value from cache or database"""
        now = time.time()
        
        # Refresh cache if expired
        if now - self.config_cache_time > self.config_cache_ttl:
            self.refresh_config_cache()
        
        return self.config_cache.get(key, default)
    
    def refresh_config_cache(self):
        """Refresh configuration cache from database"""
        db = None
        try:
            db = sqlite3.connect(self.db_path, timeout=10.0)  # Add timeout
            cursor = db.cursor()
            
            cursor.execute("SELECT key, value FROM system_config WHERE key LIKE 'activity_%'")
            configs = cursor.fetchall()
            
            self.config_cache = {row[0]: row[1] for row in configs}
            self.config_cache_time = time.time()
            
        except Exception as e:
            logger.error(f"Failed to refresh config cache: {e}")
        finally:
            if db:
                db.close()
    
    def should_skip_tracking(self, path):
        """Determine if path should be excluded from tracking"""
        # Default excluded paths
        excluded_paths = [
            '/api/activity/track',  # Prevent recursion
            '/api/auth/logout',
            '/static/',
            '/css/',
            '/js/',
            '/images/',
            '/icons/',
            '/favicon.ico',
            '/health',
            '/api/admin/activity/current',  # Don't track monitoring itself
            '/service-worker.js',
            '/manifest.json'
        ]
        
        # Check if monitoring is enabled
        if self.get_config('activity_monitoring_enabled', 'true') != 'true':
            return True
        
        # Get additional excluded pages from config
        try:
            custom_excluded = json.loads(self.get_config('activity_tracking_excluded_pages', '[]'))
            excluded_paths.extend(custom_excluded)
        except:
            pass
        
        # Check if path matches any excluded pattern
        return any(path.startswith(p) for p in excluded_paths)
    
    def get_device_type(self, user_agent):
        """Determine device type from user agent string"""
        if not user_agent:
            return 'unknown'
        
        user_agent = user_agent.lower()
        
        if 'mobile' in user_agent or 'android' in user_agent:
            return 'mobile'
        elif 'ipad' in user_agent or 'tablet' in user_agent:
            return 'tablet'
        elif 'bot' in user_agent or 'crawler' in user_agent:
            return 'bot'
        else:
            return 'desktop'
    
    def track_activity(self):
        """Flask before_request handler to track user activity"""
        # Skip if tracking should be skipped
        if self.should_skip_tracking(request.path):
            return
        
        # Get current session
        session_id = session.get('session_id')
        if not session_id:
            return
        
        # Get user from g.user (set by auth middleware)
        user = getattr(g, 'user', None)
        if not user:
            return
        
        # Determine action type
        if '/api/' in request.path:
            action_type = 'api_call'
        elif request.path.endswith(('.png', '.jpg', '.pdf', '.csv')):
            action_type = 'file_download'
        else:
            action_type = 'page_view'
        
        # Get page title from request headers (can be set by frontend)
        page_title = request.headers.get('X-Page-Title', '')
        
        # Build activity data
        activity_data = {
            'session_id': session_id,
            'user_id': user['id'],
            'timestamp': datetime.utcnow().isoformat(),
            'page_url': request.path,
            'page_title': page_title,
            'action_type': action_type,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'referrer': request.referrer,
            'device_type': self.get_device_type(request.headers.get('User-Agent', ''))
        }
        
        # Store start time for duration calculation
        g.activity_start_time = time.time()
        
        # Queue for async processing
        try:
            self.activity_queue.put_nowait(activity_data)
        except queue.Full:
            # Log error but don't block request
            logger.warning('Activity queue full, dropping activity record')
        
        # Update cache for real-time dashboard
        self.update_session_cache(session_id, activity_data)
    
    def track_response_time(self, response):
        """Flask after_request handler to track response time"""
        # Calculate duration if we have a start time
        if hasattr(g, 'activity_start_time'):
            duration_ms = int((time.time() - g.activity_start_time) * 1000)
            
            # Add duration to last queued activity if possible
            # This is a best-effort approach
            if hasattr(g, 'user') and g.user:
                session_id = session.get('session_id')
                if session_id and session_id in self.cache:
                    with self.cache_lock:
                        if session_id in self.cache:
                            self.cache[session_id]['duration_ms'] = duration_ms
        
        return response
    
    def update_session_cache(self, session_id, activity_data):
        """Update in-memory cache for real-time dashboard"""
        with self.cache_lock:
            self.cache[session_id] = {
                'user_id': activity_data['user_id'],
                'last_activity': activity_data['timestamp'],
                'last_page': activity_data['page_url'],
                'device_type': activity_data['device_type'],
                'updated_at': time.time()
            }
            
            # Clean up old cache entries
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Remove expired entries from cache and enforce size limits"""
        now = time.time()
        expired = [k for k, v in self.cache.items() 
                  if now - v.get('updated_at', 0) > self.cache_ttl * 2]
        
        for key in expired:
            del self.cache[key]
        
        # Enforce max cache size by removing oldest entries
        if len(self.cache) > self.max_cache_size:
            # Sort by updated_at and remove oldest
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1].get('updated_at', 0))
            excess_count = len(self.cache) - self.max_cache_size
            for key, _ in sorted_items[:excess_count]:
                del self.cache[key]
            logger.warning(f"Cache size limit exceeded, removed {excess_count} old entries")
    
    def get_active_sessions(self):
        """Get current active sessions from cache and database"""
        # Combine cache data with database for complete picture
        with self.cache_lock:
            cached_sessions = dict(self.cache)
        
        return cached_sessions
    
    def start_background_worker(self):
        """Start background thread to process activity queue"""
        def worker():
            """Background worker thread function"""
            while self.is_running:
                try:
                    # Get batch of activities
                    batch = []
                    deadline = time.time() + 1  # Process for up to 1 second
                    
                    while time.time() < deadline and len(batch) < 100:
                        try:
                            activity = self.activity_queue.get(timeout=0.1)
                            batch.append(activity)
                        except queue.Empty:
                            break
                    
                    if batch:
                        self.process_activity_batch(batch)
                    
                except Exception as e:
                    logger.error(f'Activity worker error: {e}')
                
                time.sleep(0.5)  # Brief pause between batches
        
        self.worker_thread = threading.Thread(target=worker, daemon=True, name='ActivityWorker')
        self.worker_thread.start()
        logger.info("Activity background worker started")
    
    def process_activity_batch(self, batch):
        """Process a batch of activity records"""
        db = None
        try:
            db = sqlite3.connect(self.db_path, timeout=10.0)  # Add timeout
            db.execute('PRAGMA journal_mode=WAL')  # Enable WAL mode for better concurrency
            cursor = db.cursor()
            
            # Prepare batch data for insertion
            activity_records = []
            session_updates = {}
            
            for activity in batch:
                # Prepare activity log record
                activity_records.append((
                    activity['session_id'],
                    activity['user_id'],
                    activity['timestamp'],
                    activity['page_url'],
                    activity.get('page_title', ''),
                    activity['action_type'],
                    activity.get('duration_ms'),
                    activity.get('referrer'),
                    activity['ip_address'],
                    activity['user_agent'],
                    json.dumps(activity.get('metadata', {})) if activity.get('metadata') else None
                ))
                
                # Track session updates (keep latest for each session)
                session_updates[activity['session_id']] = {
                    'timestamp': activity['timestamp'],
                    'page_url': activity['page_url'],
                    'api_endpoint': activity['page_url'] if activity['action_type'] == 'api_call' else None,
                    'device_type': activity['device_type']
                }
            
            # Insert activity records
            if activity_records:
                cursor.executemany('''
                    INSERT INTO user_activity_log 
                    (session_id, user_id, timestamp, page_url, page_title, action_type, 
                     duration_ms, referrer, ip_address, user_agent, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', activity_records)
            
            # Update sessions
            for session_id, updates in session_updates.items():
                if updates['api_endpoint']:
                    cursor.execute('''
                        UPDATE sessions 
                        SET last_activity = ?, 
                            last_api_endpoint = ?,
                            activity_count = activity_count + 1,
                            device_type = ?
                        WHERE id = ?
                    ''', (updates['timestamp'], updates['api_endpoint'], 
                         updates['device_type'], session_id))
                else:
                    cursor.execute('''
                        UPDATE sessions 
                        SET last_activity = ?, 
                            last_page = ?,
                            activity_count = activity_count + 1,
                            device_type = ?
                        WHERE id = ?
                    ''', (updates['timestamp'], updates['page_url'], 
                         updates['device_type'], session_id))
            
            db.commit()
            
            # Check for alerts after processing
            self.check_activity_alerts(batch, db)
            
        except Exception as e:
            if db:
                db.rollback()
            logger.error(f'Failed to process activity batch: {e}')
        finally:
            if db:
                db.close()
    
    def check_activity_alerts(self, activities, db):
        """Check activities for alert conditions"""
        try:
            cursor = db.cursor()
            
            for activity in activities:
                user_id = activity['user_id']
                
                # Check for concurrent sessions
                cursor.execute('''
                    SELECT COUNT(DISTINCT id) as session_count
                    FROM sessions
                    WHERE user_id = ? 
                    AND expires_at > datetime('now')
                    AND last_activity > datetime('now', '-30 minutes')
                ''', (user_id,))
                
                result = cursor.fetchone()
                if result and result[0] > int(self.get_config('activity_alert_concurrent_sessions_threshold', '2')):
                    self.create_alert(db, 'concurrent_sessions', 'warning', user_id, 
                                    activity['session_id'], 
                                    f'User has {result[0]} concurrent active sessions')
                
                # Check for rapid navigation (potential bot activity)
                # Calculate the timestamp for 1 minute ago
                one_minute_ago = (datetime.utcnow() - timedelta(minutes=1)).isoformat()
                cursor.execute('''
                    SELECT COUNT(*) as page_count
                    FROM user_activity_log
                    WHERE user_id = ? 
                    AND timestamp > ?
                ''', (user_id, one_minute_ago))
                
                result = cursor.fetchone()
                threshold = int(self.get_config('activity_alert_rapid_navigation_threshold', '20'))
                if result and result[0] > threshold:
                    self.create_alert(db, 'rapid_navigation', 'warning', user_id,
                                    activity['session_id'],
                                    f'User navigated {result[0]} pages in 1 minute')
                
                # Check for after-hours access (if configured)
                hour = datetime.fromisoformat(activity['timestamp']).hour
                if hour < 6 or hour > 20:  # Outside 6 AM - 8 PM
                    # Only create one after-hours alert per session per day
                    cursor.execute('''
                        SELECT id FROM activity_alerts
                        WHERE user_id = ? 
                        AND alert_type = 'after_hours'
                        AND session_id = ?
                        AND date(created_at) = date('now')
                    ''', (user_id, activity['session_id']))
                    
                    if not cursor.fetchone():
                        self.create_alert(db, 'after_hours', 'info', user_id,
                                        activity['session_id'],
                                        f'Access outside business hours at {hour}:00')
                
        except Exception as e:
            logger.error(f'Failed to check activity alerts: {e}')
    
    def create_alert(self, db, alert_type, severity, user_id, session_id, description):
        """Create an activity alert"""
        try:
            cursor = db.cursor()
            
            # Check if similar alert already exists recently
            cursor.execute('''
                SELECT id FROM activity_alerts
                WHERE user_id = ? 
                AND alert_type = ?
                AND status = 'pending'
                AND created_at > datetime('now', '-5 minutes')
            ''', (user_id, alert_type))
            
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO activity_alerts 
                    (alert_type, severity, user_id, session_id, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (alert_type, severity, user_id, session_id, description))
                
                db.commit()
                logger.info(f'Created {severity} alert: {alert_type} for user {user_id}')
                
        except Exception as e:
            logger.error(f'Failed to create alert: {e}')
    
    def schedule_cleanup(self):
        """Schedule periodic cleanup of old data"""
        def cleanup_runner():
            """Run cleanup tasks periodically"""
            while self.is_running:
                try:
                    # Wait for next cleanup time (every hour)
                    time.sleep(3600)
                    
                    with self.cleanup_lock:
                        self.cleanup_old_data()
                        self.cleanup_expired_sessions()
                        self.generate_daily_summary()
                        
                except Exception as e:
                    logger.error(f'Cleanup task error: {e}')
        
        self.cleanup_thread = threading.Thread(target=cleanup_runner, daemon=True, name='ActivityCleanup')
        self.cleanup_thread.start()
        logger.info("Activity cleanup scheduler started")
    
    def cleanup_old_data(self):
        """Remove activity data older than retention period"""
        db = None
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)  # Longer timeout for cleanup
            db.execute('PRAGMA journal_mode=WAL')
            cursor = db.cursor()
            
            # Get retention settings
            retention_days = int(self.get_config('activity_retention_days', '90'))
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Delete old activity logs in batches to avoid long locks
            total_deleted = 0
            batch_size = 1000
            
            while True:
                deleted = cursor.execute('''
                    DELETE FROM user_activity_log
                    WHERE rowid IN (
                        SELECT rowid FROM user_activity_log
                        WHERE timestamp < ?
                        LIMIT ?
                    )
                ''', (cutoff_date, batch_size)).rowcount
                
                total_deleted += deleted
                db.commit()
                
                if deleted < batch_size:
                    break
                
                # Brief pause between batches
                time.sleep(0.1)
            
            if total_deleted > 0:
                logger.info(f'Cleaned up {total_deleted} old activity records')
            
            # Delete old alerts
            cursor.execute('''
                DELETE FROM activity_alerts
                WHERE created_at < ? AND status IN ('resolved', 'dismissed')
            ''', (cutoff_date,))
            
            db.commit()
            
        except Exception as e:
            logger.error(f'Failed to cleanup old data: {e}')
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        db = None
        try:
            db = sqlite3.connect(self.db_path, timeout=10.0)
            db.execute('PRAGMA journal_mode=WAL')
            cursor = db.cursor()
            
            # Delete expired sessions
            deleted = cursor.execute('''
                DELETE FROM sessions
                WHERE expires_at < datetime('now')
            ''').rowcount
            
            if deleted > 0:
                logger.info(f'Cleaned up {deleted} expired sessions')
            
            db.commit()
            
        except Exception as e:
            logger.error(f'Failed to cleanup expired sessions: {e}')
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
    
    def generate_daily_summary(self):
        """Generate daily activity summary if needed"""
        db = None
        try:
            db = sqlite3.connect(self.db_path, timeout=10.0)
            db.execute('PRAGMA journal_mode=WAL')
            cursor = db.cursor()
            
            # Generate summary for yesterday
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # Check if yesterday's summary already exists
            cursor.execute('''
                SELECT id FROM activity_summary_daily 
                WHERE date = ?
            ''', (yesterday,))
            
            if cursor.fetchone():
                return  # Summary already exists
            
            # Get metrics
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT session_id) as total_sessions,
                    SUM(CASE WHEN action_type = 'page_view' THEN 1 ELSE 0 END) as page_views,
                    SUM(CASE WHEN action_type = 'api_call' THEN 1 ELSE 0 END) as api_calls
                FROM user_activity_log
                WHERE date(timestamp) = ?
            ''', (yesterday,))
            
            metrics = cursor.fetchone()
            
            if metrics and metrics[0] > 0:  # Only create summary if there was activity
                # Get top pages
                cursor.execute('''
                    SELECT page_url, COUNT(*) as count
                    FROM user_activity_log
                    WHERE date(timestamp) = ? AND action_type = 'page_view'
                    GROUP BY page_url
                    ORDER BY count DESC
                    LIMIT 10
                ''', (yesterday,))
                
                top_pages = [{'url': row[0], 'count': row[1]} for row in cursor.fetchall()]
                
                # Get user distribution by role
                cursor.execute('''
                    SELECT u.role, COUNT(DISTINCT l.user_id) as count
                    FROM user_activity_log l
                    JOIN users u ON l.user_id = u.id
                    WHERE date(l.timestamp) = ?
                    GROUP BY u.role
                ''', (yesterday,))
                
                user_dist = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Insert summary
                cursor.execute('''
                    INSERT INTO activity_summary_daily 
                    (date, unique_users, total_sessions, total_page_views, 
                     total_api_calls, top_pages, user_distribution)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (yesterday, metrics[0], metrics[1], metrics[2] or 0, 
                     metrics[3] or 0, json.dumps(top_pages), json.dumps(user_dist)))
                
                db.commit()
                logger.info(f'Generated daily summary for {yesterday}')
            
        except Exception as e:
            logger.error(f'Failed to generate daily summary: {e}')
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
    
    def shutdown(self):
        """Gracefully shutdown the activity tracker"""
        logger.info("Shutting down activity tracker...")
        self.is_running = False
        
        # Wait for threads to finish
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        
        logger.info("Activity tracker shutdown complete")