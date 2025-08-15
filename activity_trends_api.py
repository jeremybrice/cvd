"""
Activity Trends API Implementation
Flask Blueprint for activity trends endpoints with caching and rate limiting
Phase 4: API Endpoints Implementation
"""

from flask import Blueprint, jsonify, request, g, Response, current_app
from datetime import datetime, timedelta, date
from functools import wraps
import json
import time
import csv
from io import StringIO
from collections import defaultdict
from threading import RLock
import logging

# Import services
from activity_trends_service import (
    ActivityTrendsService, 
    TrendAnalyzer, 
    DailySummaryProcessor,
    DataCompletionService
)
from trends_cache import TrendsCache, CacheWarmer

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for API endpoints
    """
    
    def __init__(self, requests_per_minute: int = 100):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Maximum requests per minute per user
        """
        self.requests_per_minute = requests_per_minute
        self.buckets = defaultdict(lambda: {
            'tokens': requests_per_minute,
            'last_refill': time.time()
        })
        self.lock = RLock()
    
    def check_limit(self, user_id: int, endpoint: str) -> bool:
        """
        Check if request is allowed
        
        Args:
            user_id: User ID
            endpoint: API endpoint name
        
        Returns:
            True if request is allowed, False if rate limited
        """
        with self.lock:
            key = f"{user_id}:{endpoint}"
            bucket = self.buckets[key]
            
            # Refill tokens based on time elapsed
            now = time.time()
            elapsed = now - bucket['last_refill']
            tokens_to_add = elapsed * (self.requests_per_minute / 60)
            
            bucket['tokens'] = min(
                self.requests_per_minute,
                bucket['tokens'] + tokens_to_add
            )
            bucket['last_refill'] = now
            
            # Check if request is allowed
            if bucket['tokens'] >= 1:
                bucket['tokens'] -= 1
                return True
            
            return False
    
    def get_wait_time(self, user_id: int, endpoint: str) -> float:
        """
        Get seconds until next request is allowed
        
        Args:
            user_id: User ID
            endpoint: API endpoint name
        
        Returns:
            Seconds to wait
        """
        with self.lock:
            key = f"{user_id}:{endpoint}"
            bucket = self.buckets[key]
            
            if bucket['tokens'] >= 1:
                return 0
            
            # Calculate time until 1 token is available
            tokens_needed = 1 - bucket['tokens']
            seconds_per_token = 60 / self.requests_per_minute
            
            return tokens_needed * seconds_per_token


class PerformanceMonitor:
    """
    Monitor and enforce performance requirements
    """
    
    def __init__(self):
        self.thresholds = {
            'trends_api': 2000,  # 2 seconds max
            'export_api': 5000,  # 5 seconds max
            'cache_hit': 100,    # 100ms for cache hit
            'db_query': 500      # 500ms for database query
        }
        
        self.metrics = defaultdict(list)
    
    def measure(self, operation: str):
        """
        Decorator to measure operation performance
        
        Args:
            operation: Operation name
        """
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = f(*args, **kwargs)
                    
                    elapsed_ms = (time.time() - start_time) * 1000
                    self.record_metric(operation, elapsed_ms)
                    
                    # Log slow operations
                    if elapsed_ms > self.thresholds.get(operation, float('inf')):
                        logger.warning(
                            f"Slow operation: {operation} took {elapsed_ms:.2f}ms"
                        )
                    
                    # Add performance header to response
                    if isinstance(result, tuple) and len(result) >= 2:
                        response, status = result[:2]
                        headers = result[2] if len(result) > 2 else {}
                        headers['X-Response-Time'] = f"{elapsed_ms:.2f}ms"
                        return response, status, headers
                    
                    return result
                    
                except Exception as e:
                    elapsed_ms = (time.time() - start_time) * 1000
                    self.record_metric(operation, elapsed_ms, error=True)
                    raise
            
            return wrapper
        return decorator
    
    def record_metric(self, operation: str, duration_ms: float, error: bool = False):
        """
        Record performance metric
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            error: Whether an error occurred
        """
        self.metrics[operation].append({
            'timestamp': time.time(),
            'duration_ms': duration_ms,
            'error': error
        })
        
        # Keep only last 1000 metrics per operation
        if len(self.metrics[operation]) > 1000:
            self.metrics[operation] = self.metrics[operation][-1000:]
    
    def get_stats(self, operation: str) -> dict:
        """
        Get performance statistics for an operation
        
        Args:
            operation: Operation name
        
        Returns:
            Statistics dictionary
        """
        metrics = self.metrics.get(operation, [])
        
        if not metrics:
            return None
        
        durations = [m['duration_ms'] for m in metrics if not m['error']]
        
        if not durations:
            return None
        
        import numpy as np
        
        return {
            'count': len(durations),
            'avg_ms': np.mean(durations),
            'median_ms': np.median(durations),
            'p95_ms': np.percentile(durations, 95),
            'p99_ms': np.percentile(durations, 99),
            'max_ms': max(durations),
            'min_ms': min(durations),
            'error_rate': sum(1 for m in metrics if m['error']) / len(metrics)
        }


# Initialize components (will be configured in init function)
trends_cache = None
trends_service = None
performance_monitor = None
rate_limiter = None
audit_logger = None

# Create blueprint
activity_trends_bp = Blueprint('activity_trends', __name__)


def validate_trends_request(args: dict) -> dict:
    """
    Comprehensive request validation with sanitization
    
    Args:
        args: Request arguments
    
    Returns:
        Validation result with params or error
    """
    errors = []
    params = {}
    
    # Validate start_date
    try:
        start_date_str = args.get('start_date')
        if not start_date_str:
            errors.append('start_date is required')
        else:
            params['start_date'] = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            
            # Enforce maximum historical range (365 days from today)
            min_allowed_date = datetime.now().date() - timedelta(days=365)
            if params['start_date'] < min_allowed_date:
                errors.append(f'start_date cannot be before {min_allowed_date}')
    except ValueError:
        errors.append('Invalid start_date format. Use YYYY-MM-DD')
    
    # Validate end_date
    try:
        end_date_str = args.get('end_date')
        if not end_date_str:
            errors.append('end_date is required')
        else:
            params['end_date'] = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # Cannot be future date
            if params['end_date'] > datetime.now().date():
                params['end_date'] = datetime.now().date()
    except ValueError:
        errors.append('Invalid end_date format. Use YYYY-MM-DD')
    
    # Validate date range
    if 'start_date' in params and 'end_date' in params:
        if params['end_date'] < params['start_date']:
            errors.append('end_date must be after start_date')
        
        date_diff = (params['end_date'] - params['start_date']).days
        if date_diff > 365:
            errors.append('Date range cannot exceed 365 days')
    
    # Validate metrics
    metrics_str = args.get('metrics', '')
    if metrics_str:
        requested_metrics = [m.strip() for m in metrics_str.split(',')]
        valid_metrics = {
            'unique_users', 'total_sessions', 'total_page_views',
            'total_api_calls', 'avg_session_duration_seconds',
            'peak_concurrent_users'
        }
        
        invalid_metrics = set(requested_metrics) - valid_metrics
        if invalid_metrics:
            errors.append(f'Invalid metrics: {", ".join(invalid_metrics)}')
        else:
            params['metrics'] = requested_metrics
    else:
        # Default to all metrics
        params['metrics'] = [
            'unique_users', 'total_sessions', 'total_page_views'
        ]
    
    # Validate cache_bypass
    params['cache_bypass'] = args.get('cache_bypass', '').lower() == 'true'
    
    if errors:
        return {'valid': False, 'error': '; '.join(errors)}
    
    return {'valid': True, 'params': params}


def ensure_initialized():
    """Verify all components are initialized"""
    if not all([trends_cache, trends_service, performance_monitor, rate_limiter]):
        missing = []
        if not trends_cache: missing.append('cache')
        if not trends_service: missing.append('service')
        if not performance_monitor: missing.append('monitor')
        if not rate_limiter: missing.append('rate_limiter')
        
        logger.error(f"Trends module not initialized. Missing: {', '.join(missing)}")
        return False
    return True


@activity_trends_bp.route('/api/admin/activity/trends', methods=['GET'])
def get_activity_trends():
    """
    Retrieve aggregated daily activity trends with caching
    
    Query Parameters:
    - start_date (required): ISO format date string "YYYY-MM-DD"
    - end_date (required): ISO format date string "YYYY-MM-DD"
    - metrics (optional): Comma-separated list of metrics to return
    - cache_bypass (optional): Force cache refresh (boolean)
    
    Returns:
    - 200: Success with trend data
    - 400: Invalid parameters
    - 403: Unauthorized (non-admin)
    - 429: Rate limit exceeded
    - 500: Server error
    - 503: Service temporarily unavailable
    """
    from auth import log_audit_event
    
    # Check if module is initialized
    if not ensure_initialized():
        return jsonify({
            'error': 'Service temporarily unavailable',
            'details': 'Trends module is initializing. Please try again in a few seconds.'
        }), 503
    
    # Start performance tracking
    start_time = time.time()
    
    try:
        # Check authentication and role
        if not hasattr(g, 'user') or not g.user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        if g.user.get('role') != 'admin':
            log_audit_event(
                g.user['id'],
                'UNAUTHORIZED_ACCESS_ATTEMPT',
                {
                    'endpoint': request.path,
                    'required_role': 'admin',
                    'user_role': g.user.get('role')
                }
            )
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        # Step 1: Validate request parameters
        validation_result = validate_trends_request(request.args)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': validation_result['error']
            }), 400
        
        params = validation_result['params']
        
        # Step 2: Check rate limiting
        if not rate_limiter.check_limit(g.user['id'], 'trends_api'):
            wait_time = rate_limiter.get_wait_time(g.user['id'], 'trends_api')
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded. Please try again later.',
                'retry_after': int(wait_time)
            }), 429
        
        # Step 3: Generate cache key
        cache_key = trends_cache.generate_key(
            params['start_date'],
            params['end_date'],
            params['metrics']
        )
        
        # Step 4: Check cache unless bypass requested
        if not params.get('cache_bypass', False):
            cached_data = trends_cache.get(cache_key)
            if cached_data:
                # Record cache hit performance
                if performance_monitor:
                    elapsed_ms = (time.time() - start_time) * 1000
                    performance_monitor.record_metric('trends_api', elapsed_ms)
                    performance_monitor.record_metric('cache_hit', elapsed_ms)
                
                return jsonify({
                    'success': True,
                    'data': cached_data,
                    'cached': True,
                    'cache_ttl': trends_cache.get_ttl(cache_key)
                }), 200
        
        # Step 5: Query database for trend data
        trends_data = trends_service.get_trends(
            params['start_date'],
            params['end_date'],
            params['metrics']
        )
        
        # Step 6: Calculate summary statistics
        summary = trends_service.calculate_summary(trends_data)
        
        # Step 7: Add trend analysis
        trend_analyzer = TrendAnalyzer()
        for metric in params['metrics']:
            if metric in trends_data and trends_data[metric]:
                trend_analysis = trend_analyzer.calculate_trend(trends_data[metric])
                if metric in summary:
                    summary[metric]['trend_analysis'] = trend_analysis
        
        # Step 8: Format response
        response_data = {
            'period': {
                'start': params['start_date'].isoformat(),
                'end': params['end_date'].isoformat(),
                'days': (params['end_date'] - params['start_date']).days + 1
            },
            'metrics': trends_data,
            'summary': summary,
            'generated_at': datetime.now().isoformat()
        }
        
        # Step 9: Update cache
        trends_cache.set(cache_key, response_data)
        
        # Step 10: Log activity
        log_audit_event(
            g.user['id'],
            'VIEW_ACTIVITY_TRENDS',
            {
                'date_range': f"{params['start_date']} to {params['end_date']}",
                'metrics': params['metrics'],
                'cached': False
            }
        )
        
        # Record performance metrics
        if performance_monitor:
            elapsed_ms = (time.time() - start_time) * 1000
            performance_monitor.record_metric('trends_api', elapsed_ms)
        
        return jsonify({
            'success': True,
            'data': response_data,
            'cached': False,
            'cache_ttl': 3600  # 1 hour TTL
        }), 200
        
    except Exception as e:
        # Record error metric
        if performance_monitor:
            elapsed_ms = (time.time() - start_time) * 1000
            performance_monitor.record_metric('trends_api', elapsed_ms, error=True)
        logger.error(f"Trends API error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred while fetching trends'
        }), 500


@activity_trends_bp.route('/api/admin/activity/export', methods=['GET'])
def export_activity_data():
    """
    Export activity data in CSV or JSON format
    Streams response for large datasets
    
    Query Parameters:
    - start_date (required): ISO format date string
    - end_date (required): ISO format date string
    - metrics (optional): Comma-separated list of metrics
    - format (optional): 'csv' or 'json' (default: csv)
    
    Returns:
    - 200: Success with data file
    - 400: Invalid parameters
    - 403: Unauthorized
    - 500: Server error
    """
    from auth import log_audit_event
    
    try:
        # Check authentication and role
        if not hasattr(g, 'user') or not g.user:
            return jsonify({'error': 'Authentication required'}), 401
        
        if g.user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Validate parameters
        validation_result = validate_trends_request(request.args)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['error']}), 400
        
        params = validation_result['params']
        export_format = request.args.get('format', 'csv').lower()
        
        if export_format not in ['csv', 'json']:
            return jsonify({'error': 'Invalid format. Use csv or json'}), 400
        
        # Get raw data for export
        trends_data = trends_service.get_trends_raw(
            params['start_date'],
            params['end_date'],
            params['metrics']
        )
        
        # Log export event
        log_audit_event(
            g.user['id'],
            'EXPORT_ACTIVITY_DATA',
            {
                'format': export_format,
                'date_range': f"{params['start_date']} to {params['end_date']}",
                'record_count': len(trends_data),
                'metrics': params['metrics']
            }
        )
        
        if export_format == 'json':
            return jsonify({
                'export_date': datetime.now().isoformat(),
                'user': g.user['username'],
                'period': {
                    'start': params['start_date'].isoformat(),
                    'end': params['end_date'].isoformat()
                },
                'metrics': params['metrics'],
                'data': trends_data
            }), 200, {
                'Content-Disposition': f'attachment; filename=activity_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        
        else:  # CSV format
            def generate_csv():
                output = StringIO()
                writer = csv.writer(output)
                
                # Write headers
                headers = ['date'] + params['metrics']
                writer.writerow(headers)
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
                
                # Write data rows
                for date_str, metrics in sorted(trends_data.items()):
                    row = [date_str]
                    for metric in params['metrics']:
                        row.append(metrics.get(metric, 0))
                    writer.writerow(row)
                    yield output.getvalue()
                    output.seek(0)
                    output.truncate(0)
            
            return Response(
                generate_csv(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=activity_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    'X-Accel-Buffering': 'no'  # Disable proxy buffering
                }
            )
    
    except Exception as e:
        logger.error(f"Export API error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred while exporting data'
        }), 500


@activity_trends_bp.route('/api/admin/activity/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring
    
    Returns:
    - 200: Healthy
    - 503: Degraded or unhealthy
    """
    try:
        # Check authentication
        if not hasattr(g, 'user') or not g.user:
            return jsonify({'error': 'Authentication required'}), 401
        
        if g.user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Check database
        try:
            import sqlite3
            conn = sqlite3.connect(current_app.config['DATABASE'])
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM activity_summary_daily")
            count = cursor.fetchone()[0]
            conn.close()
            
            health['checks']['database'] = {
                'status': 'ok',
                'records': count
            }
        except Exception as e:
            health['checks']['database'] = {
                'status': 'error',
                'error': str(e)
            }
            health['status'] = 'degraded'
        
        # Check cache
        if trends_cache:
            cache_stats = trends_cache.get_stats()
            health['checks']['cache'] = {
                'status': 'ok',
                'stats': cache_stats
            }
        else:
            health['checks']['cache'] = {
                'status': 'error',
                'error': 'Cache not initialized'
            }
            health['status'] = 'degraded'
        
        # Performance metrics
        if performance_monitor:
            perf_stats = {}
            for operation in ['trends_api', 'export_api']:
                stats = performance_monitor.get_stats(operation)
                if stats:
                    perf_stats[operation] = {
                        'avg_ms': round(stats['avg_ms'], 2),
                        'p95_ms': round(stats['p95_ms'], 2),
                        'error_rate': round(stats['error_rate'], 3)
                    }
            
            health['checks']['performance'] = perf_stats
        
        status_code = 200 if health['status'] == 'healthy' else 503
        return jsonify(health), status_code
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 503


@activity_trends_bp.route('/api/admin/activity/cache/stats', methods=['GET'])
def get_cache_stats():
    """
    Get cache statistics
    
    Returns:
    - 200: Cache statistics
    - 403: Unauthorized
    """
    # Check authentication
    if not hasattr(g, 'user') or not g.user:
        return jsonify({'error': 'Authentication required'}), 401
    
    if g.user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    if trends_cache:
        return jsonify({
            'success': True,
            'stats': trends_cache.get_stats()
        }), 200
    
    return jsonify({
        'success': False,
        'error': 'Cache not initialized'
    }), 500


@activity_trends_bp.route('/api/admin/activity/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear the activity trends cache
    
    Returns:
    - 200: Cache cleared
    - 403: Unauthorized
    """
    from auth import log_audit_event
    
    # Check authentication
    if not hasattr(g, 'user') or not g.user:
        return jsonify({'error': 'Authentication required'}), 401
    
    if g.user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    if trends_cache:
        trends_cache.clear()
        
        log_audit_event(
            g.user['id'],
            'CLEAR_ACTIVITY_CACHE',
            {'cleared_at': datetime.now().isoformat()}
        )
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        }), 200
    
    return jsonify({
        'success': False,
        'error': 'Cache not initialized'
    }), 500


# Error handlers
@activity_trends_bp.errorhandler(429)
def handle_rate_limit(e):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.',
        'retry_after': 60
    }), 429


@activity_trends_bp.errorhandler(500)
def handle_server_error(e):
    logger.error(f"Server error: {str(e)}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'An internal error occurred'
    }), 500


def init_trends_module(app, database_path: str):
    """
    Initialize trends module with Flask app
    
    Args:
        app: Flask application instance
        database_path: Path to SQLite database
    """
    global trends_cache, trends_service, performance_monitor, rate_limiter
    
    # Skip re-initialization if already done (handles Flask debug reloader)
    if all([trends_cache, trends_service, performance_monitor, rate_limiter]):
        logger.info("Trends module already initialized, skipping re-initialization")
        return
    
    # Initialize components
    trends_cache = TrendsCache(max_size=100, default_ttl=3600)
    trends_service = ActivityTrendsService(database_path)
    performance_monitor = PerformanceMonitor()
    rate_limiter = RateLimiter(requests_per_minute=100)
    
    # Register blueprint
    app.register_blueprint(activity_trends_bp)
    
    # Process any missing daily summaries
    processor = DailySummaryProcessor(database_path)
    processed = processor.process_missing_days()
    if processed > 0:
        logger.info(f"Processed {processed} missing daily summaries")
    
    # Warm cache on startup
    cache_warmer = CacheWarmer(trends_cache, trends_service)
    
    # Run cache warming in background to not block startup
    import threading
    warm_thread = threading.Thread(target=cache_warmer.warm_cache)
    warm_thread.daemon = True
    warm_thread.start()
    
    # Initialize background tasks
    try:
        from background_tasks import init_background_tasks
        background_manager = init_background_tasks(
            app, 
            database_path, 
            cache=trends_cache, 
            service=trends_service
        )
        logger.info("Background tasks initialized")
    except ImportError:
        logger.warning("Background tasks module not available. Install 'schedule' package for background tasks.")
    except Exception as e:
        logger.error(f"Failed to initialize background tasks: {e}")
    
    logger.info("Activity Trends module initialized")