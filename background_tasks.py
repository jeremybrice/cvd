"""
Background Tasks for Activity Monitoring
Phase 6: Monitoring and Health Checks
"""

import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from activity_trends_service import DailySummaryProcessor
from trends_cache import CacheWarmer

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """
    Manages background tasks for the activity monitoring system
    """
    
    def __init__(self, database_path: str, cache=None, service=None):
        """
        Initialize background task manager
        
        Args:
            database_path: Path to SQLite database
            cache: TrendsCache instance (optional)
            service: ActivityTrendsService instance (optional)
        """
        self.database_path = database_path
        self.cache = cache
        self.service = service
        self.running = False
        self.thread = None
    
    def process_daily_summaries(self):
        """
        Process missing daily summaries
        Runs at 2 AM daily
        """
        try:
            logger.info("Starting daily summary processing...")
            processor = DailySummaryProcessor(self.database_path)
            
            # Process yesterday's data
            yesterday = datetime.now().date() - timedelta(days=1)
            if processor.generate_summary_for_date(yesterday.isoformat()):
                logger.info(f"Generated summary for {yesterday}")
            
            # Process any other missing days
            processed = processor.process_missing_days()
            if processed > 0:
                logger.info(f"Processed {processed} additional missing days")
            
            logger.info("Daily summary processing complete")
            
        except Exception as e:
            logger.error(f"Error in daily summary processing: {e}", exc_info=True)
    
    def warm_cache(self):
        """
        Warm the cache with common date ranges
        Runs every hour
        """
        if not self.cache or not self.service:
            logger.warning("Cache or service not available for warming")
            return
        
        try:
            logger.info("Starting cache warming...")
            warmer = CacheWarmer(self.cache, self.service)
            warmer.warm_cache()
            logger.info("Cache warming complete")
            
        except Exception as e:
            logger.error(f"Error in cache warming: {e}", exc_info=True)
    
    def cleanup_cache(self):
        """
        Clean up expired cache entries
        Runs every 15 minutes
        """
        if not self.cache:
            return
        
        try:
            self.cache.cleanup_expired()
            stats = self.cache.get_stats()
            logger.debug(f"Cache cleanup complete. Current size: {stats['size']}")
            
        except Exception as e:
            logger.error(f"Error in cache cleanup: {e}", exc_info=True)
    
    def cleanup_old_logs(self):
        """
        Clean up old activity logs (keep 30 days of detailed logs)
        Runs weekly on Sunday at 3 AM
        """
        try:
            import sqlite3
            
            logger.info("Starting old log cleanup...")
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Keep 30 days of detailed logs
            cleanup_date = datetime.now().date() - timedelta(days=30)
            
            # Count records to be deleted
            count = cursor.execute(
                "SELECT COUNT(*) FROM user_activity_log WHERE DATE(timestamp) < ?",
                (cleanup_date.isoformat(),)
            ).fetchone()[0]
            
            if count > 0:
                # Delete old logs
                cursor.execute(
                    "DELETE FROM user_activity_log WHERE DATE(timestamp) < ?",
                    (cleanup_date.isoformat(),)
                )
                conn.commit()
                logger.info(f"Deleted {count} old activity log records")
            else:
                logger.info("No old activity logs to clean up")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error in log cleanup: {e}", exc_info=True)
    
    def schedule_tasks(self):
        """
        Schedule all background tasks
        """
        # Daily tasks
        schedule.every().day.at("02:00").do(self.process_daily_summaries)
        
        # Hourly tasks
        schedule.every().hour.do(self.warm_cache)
        
        # Every 15 minutes
        schedule.every(15).minutes.do(self.cleanup_cache)
        
        # Weekly tasks
        schedule.every().sunday.at("03:00").do(self.cleanup_old_logs)
        
        logger.info("Background tasks scheduled:")
        logger.info("  - Daily summary processing: 2:00 AM")
        logger.info("  - Cache warming: Every hour")
        logger.info("  - Cache cleanup: Every 15 minutes")
        logger.info("  - Log cleanup: Sunday 3:00 AM")
    
    def run_scheduler(self):
        """
        Run the scheduler in a loop
        """
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start(self):
        """
        Start the background task manager
        """
        if self.running:
            logger.warning("Background task manager already running")
            return
        
        self.running = True
        self.schedule_tasks()
        
        # Run initial tasks
        self.process_daily_summaries()
        self.warm_cache()
        
        # Start scheduler thread
        self.thread = threading.Thread(target=self.run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Background task manager started")
    
    def stop(self):
        """
        Stop the background task manager
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        schedule.clear()
        logger.info("Background task manager stopped")


def init_background_tasks(app, database_path: str, cache=None, service=None):
    """
    Initialize background tasks for Flask app
    
    Args:
        app: Flask application instance
        database_path: Path to SQLite database
        cache: TrendsCache instance (optional)
        service: ActivityTrendsService instance (optional)
    
    Returns:
        BackgroundTaskManager instance
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start task manager
    manager = BackgroundTaskManager(database_path, cache, service)
    manager.start()
    
    # Register shutdown handler
    import atexit
    atexit.register(manager.stop)
    
    return manager