# Activity Monitor Enhancement - Backend Implementation Plan

## Executive Summary

This document provides a detailed technical implementation guide for backend engineers to implement the Activity Monitor Enhancement feature. The implementation leverages existing SQLite infrastructure with optimized queries, implements multi-layer caching, and provides comprehensive API endpoints for desktop-optimized trend visualization.

**Key Implementation Goals:**
- Sub-2 second response time for 365 days of trend data
- Zero-downtime deployment with backward compatibility
- Memory-efficient caching with automatic TTL management
- Robust error handling and graceful degradation

---

## 1. API Endpoint Specifications

### 1.1 Primary Trends Endpoint

#### **GET /api/admin/activity/trends**

```python
from flask import Blueprint, jsonify, request, g
from functools import wraps
import time
from datetime import datetime, timedelta
import json

activity_trends_bp = Blueprint('activity_trends', __name__)

@activity_trends_bp.route('/api/admin/activity/trends', methods=['GET'])
@auth_manager.require_role(['admin'])
@measure_performance
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
    """
    
    try:
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
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded. Please try again later.'
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
        
        # Step 7: Format response
        response_data = {
            'period': {
                'start': params['start_date'].isoformat(),
                'end': params['end_date'].isoformat()
            },
            'metrics': trends_data,
            'summary': summary
        }
        
        # Step 8: Update cache
        trends_cache.set(cache_key, response_data)
        
        # Step 9: Log activity
        audit_logger.log('VIEW_TRENDS', g.user['id'], {
            'date_range': f"{params['start_date']} to {params['end_date']}",
            'metrics': params['metrics']
        })
        
        return jsonify({
            'success': True,
            'data': response_data,
            'cached': False,
            'cache_ttl': 3600  # 1 hour TTL
        }), 200
        
    except Exception as e:
        app.logger.error(f"Trends API error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred while fetching trends'
        }), 500
```

#### **Validation Implementation**

```python
def validate_trends_request(args):
    """
    Comprehensive request validation with sanitization
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
```

### 1.2 Export Endpoint

```python
@activity_trends_bp.route('/api/admin/activity/export', methods=['GET'])
@auth_manager.require_role(['admin'])
@measure_performance
def export_activity_data():
    """
    Export activity data in CSV or JSON format
    Streams response for large datasets
    """
    from io import StringIO
    import csv
    
    # Validate parameters (similar to trends endpoint)
    validation_result = validate_trends_request(request.args)
    if not validation_result['valid']:
        return jsonify({'error': validation_result['error']}), 400
    
    params = validation_result['params']
    export_format = request.args.get('format', 'csv').lower()
    
    if export_format not in ['csv', 'json']:
        return jsonify({'error': 'Invalid format. Use csv or json'}), 400
    
    # Get data
    trends_data = trends_service.get_trends_raw(
        params['start_date'],
        params['end_date'],
        params['metrics']
    )
    
    # Log export event
    audit_logger.log('EXPORT_DATA', g.user['id'], {
        'format': export_format,
        'date_range': f"{params['start_date']} to {params['end_date']}",
        'record_count': len(trends_data)
    })
    
    if export_format == 'json':
        return jsonify({
            'export_date': datetime.now().isoformat(),
            'user': g.user['username'],
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
            
            # Write data rows
            for date_str, metrics in trends_data.items():
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
                'Content-Disposition': f'attachment; filename=activity_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
```

---

## 2. Database Optimization

### 2.1 Required Indexes

```sql
-- Primary performance index for date range queries
CREATE INDEX IF NOT EXISTS idx_activity_summary_date_range 
ON activity_summary_daily(date DESC)
WHERE date >= date('now', '-365 days');  -- Partial index for recent data

-- Composite index for metric queries
CREATE INDEX IF NOT EXISTS idx_activity_summary_metrics 
ON activity_summary_daily(
    date DESC,
    unique_users,
    total_sessions,
    total_page_views
);

-- Index for efficient aggregation queries
CREATE INDEX IF NOT EXISTS idx_activity_summary_aggregates
ON activity_summary_daily(
    date,
    total_sessions,
    unique_users
) WHERE unique_users > 0;  -- Partial index excluding empty days
```

### 2.2 Query Optimization Strategies

```python
class ActivityTrendsService:
    """
    Service class for efficient trend data retrieval
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection_pool = []  # Simple connection pooling
        self.max_pool_size = 5
    
    def get_trends(self, start_date, end_date, metrics):
        """
        Optimized query for trend data retrieval
        """
        query = """
        WITH date_range AS (
            SELECT 
                date,
                unique_users,
                total_sessions,
                total_page_views,
                total_api_calls,
                avg_session_duration_seconds,
                peak_concurrent_users
            FROM activity_summary_daily
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC
        ),
        moving_averages AS (
            SELECT 
                date,
                unique_users,
                total_sessions,
                total_page_views,
                total_api_calls,
                avg_session_duration_seconds,
                peak_concurrent_users,
                -- 7-day moving averages for trend calculation
                AVG(unique_users) OVER (
                    ORDER BY date 
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as users_7day_avg,
                AVG(total_sessions) OVER (
                    ORDER BY date 
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as sessions_7day_avg,
                -- 30-day moving averages for long-term trends
                AVG(unique_users) OVER (
                    ORDER BY date 
                    ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
                ) as users_30day_avg
            FROM date_range
        )
        SELECT * FROM moving_averages
        """
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (start_date, end_date))
            
            rows = cursor.fetchall()
            return self._format_trend_data(rows, metrics)
            
        finally:
            self._return_connection(conn)
    
    def _format_trend_data(self, rows, metrics):
        """
        Format raw database rows into API response format
        """
        result = {metric: [] for metric in metrics}
        
        for row in rows:
            date_str = row['date']
            for metric in metrics:
                if metric in row:
                    result[metric].append({
                        'date': date_str,
                        'value': row[metric],
                        '7day_avg': row.get(f'{metric}_7day_avg'),
                        '30day_avg': row.get(f'{metric}_30day_avg')
                    })
        
        return result
    
    def calculate_summary(self, trends_data):
        """
        Calculate summary statistics and trend indicators
        """
        import numpy as np
        from scipy import stats
        
        summary = {}
        
        for metric, data_points in trends_data.items():
            if not data_points:
                continue
            
            values = [p['value'] for p in data_points]
            dates = [p['date'] for p in data_points]
            
            # Basic statistics
            summary[metric] = {
                'average': np.mean(values),
                'median': np.median(values),
                'std_dev': np.std(values),
                'min': min(values),
                'max': max(values),
                'peak_date': dates[values.index(max(values))],
                'total': sum(values)
            }
            
            # Trend calculation using linear regression
            if len(values) >= 7:
                x = np.arange(len(values))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                
                # Determine trend direction
                if abs(slope) < 0.01 * np.mean(values):  # Less than 1% change
                    trend = 'stable'
                elif slope > 0:
                    trend = 'increasing'
                else:
                    trend = 'decreasing'
                
                # Calculate percentage change
                if values[0] != 0:
                    pct_change = ((values[-1] - values[0]) / values[0]) * 100
                else:
                    pct_change = 0
                
                summary[metric].update({
                    'trend': trend,
                    'trend_slope': slope,
                    'trend_confidence': abs(r_value),  # R-squared value
                    'percentage_change': round(pct_change, 2)
                })
        
        return summary
```

### 2.3 Data Aggregation Pipeline

```python
class ActivityAggregator:
    """
    Background task for aggregating daily activity summaries
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def aggregate_daily_summary(self, date=None):
        """
        Aggregate activity data for a specific date
        Run this as a scheduled task at midnight
        """
        if date is None:
            date = datetime.now().date() - timedelta(days=1)  # Yesterday
        
        aggregation_query = """
        INSERT OR REPLACE INTO activity_summary_daily (
            date,
            unique_users,
            total_sessions,
            total_page_views,
            total_api_calls,
            avg_session_duration_seconds,
            peak_concurrent_users,
            peak_hour,
            top_pages,
            user_distribution
        )
        SELECT 
            DATE(created_at) as date,
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(DISTINCT session_id) as total_sessions,
            SUM(CASE WHEN page_url IS NOT NULL THEN 1 ELSE 0 END) as total_page_views,
            SUM(CASE WHEN api_endpoint IS NOT NULL THEN 1 ELSE 0 END) as total_api_calls,
            AVG(
                CASE 
                    WHEN session_end IS NOT NULL 
                    THEN (julianday(session_end) - julianday(created_at)) * 86400
                    ELSE NULL
                END
            ) as avg_session_duration_seconds,
            MAX(concurrent_count) as peak_concurrent_users,
            MODE() WITHIN GROUP (ORDER BY strftime('%H', created_at)) as peak_hour,
            (
                SELECT json_group_array(json_object(
                    'page', page_url,
                    'count', page_count
                ))
                FROM (
                    SELECT page_url, COUNT(*) as page_count
                    FROM activity_log
                    WHERE DATE(created_at) = ?
                    GROUP BY page_url
                    ORDER BY page_count DESC
                    LIMIT 10
                )
            ) as top_pages,
            (
                SELECT json_object(
                    'admin', COUNT(DISTINCT CASE WHEN u.role = 'admin' THEN al.user_id END),
                    'manager', COUNT(DISTINCT CASE WHEN u.role = 'manager' THEN al.user_id END),
                    'driver', COUNT(DISTINCT CASE WHEN u.role = 'driver' THEN al.user_id END),
                    'viewer', COUNT(DISTINCT CASE WHEN u.role = 'viewer' THEN al.user_id END)
                )
                FROM activity_log al
                JOIN users u ON al.user_id = u.id
                WHERE DATE(al.created_at) = ?
            ) as user_distribution
        FROM activity_log
        WHERE DATE(created_at) = ?
        """
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(aggregation_query, (date, date, date))
            conn.commit()
            
            # Clean up old detailed logs (keep 30 days)
            cleanup_date = date - timedelta(days=30)
            cursor.execute(
                "DELETE FROM activity_log WHERE DATE(created_at) < ?",
                (cleanup_date,)
            )
            conn.commit()
            
        finally:
            conn.close()
```

---

## 3. Caching Implementation

### 3.1 In-Memory Cache Structure

```python
import time
import hashlib
import json
from collections import OrderedDict
from threading import RLock

class TrendsCache:
    """
    Thread-safe in-memory cache with TTL and LRU eviction
    Designed for desktop clients that can handle larger payloads
    """
    
    def __init__(self, max_size=100, default_ttl=3600):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0
        }
    
    def generate_key(self, start_date, end_date, metrics):
        """
        Generate consistent cache key from parameters
        """
        key_data = {
            'start': start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
            'end': end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date),
            'metrics': sorted(metrics)  # Sort for consistency
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key):
        """
        Retrieve item from cache if not expired
        """
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if time.time() > entry['expires_at']:
                del self.cache[key]
                self.stats['misses'] += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.stats['hits'] += 1
            
            return entry['data']
    
    def set(self, key, data, ttl=None):
        """
        Store item in cache with TTL
        """
        if ttl is None:
            ttl = self.default_ttl
        
        with self.lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
            
            self.cache[key] = {
                'data': data,
                'expires_at': time.time() + ttl,
                'created_at': time.time(),
                'ttl': ttl
            }
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.stats['sets'] += 1
    
    def get_ttl(self, key):
        """
        Get remaining TTL for cache entry
        """
        with self.lock:
            if key not in self.cache:
                return 0
            
            entry = self.cache[key]
            remaining = max(0, entry['expires_at'] - time.time())
            return int(remaining)
    
    def clear(self):
        """
        Clear all cache entries
        """
        with self.lock:
            self.cache.clear()
    
    def get_stats(self):
        """
        Get cache performance statistics
        """
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': round(hit_rate, 2),
                'evictions': self.stats['evictions'],
                'sets': self.stats['sets']
            }
```

### 3.2 Cache Warming Strategy

```python
class CacheWarmer:
    """
    Preload cache with commonly requested data
    """
    
    def __init__(self, cache: TrendsCache, service: ActivityTrendsService):
        self.cache = cache
        self.service = service
    
    def warm_cache(self):
        """
        Preload cache with common date ranges
        Run this after server startup or cache clear
        """
        common_ranges = [
            # Last 7 days
            (datetime.now().date() - timedelta(days=7), datetime.now().date()),
            # Last 30 days
            (datetime.now().date() - timedelta(days=30), datetime.now().date()),
            # Last 90 days
            (datetime.now().date() - timedelta(days=90), datetime.now().date()),
            # Current month
            (datetime.now().date().replace(day=1), datetime.now().date()),
            # Last month
            self._get_last_month_range()
        ]
        
        default_metrics = ['unique_users', 'total_sessions', 'total_page_views']
        
        for start_date, end_date in common_ranges:
            try:
                # Fetch data
                data = self.service.get_trends(start_date, end_date, default_metrics)
                
                # Cache it
                cache_key = self.cache.generate_key(start_date, end_date, default_metrics)
                self.cache.set(cache_key, data)
                
                app.logger.info(f"Warmed cache for range {start_date} to {end_date}")
                
            except Exception as e:
                app.logger.error(f"Failed to warm cache: {e}")
    
    def _get_last_month_range(self):
        """
        Get date range for last month
        """
        today = datetime.now().date()
        first_of_month = today.replace(day=1)
        last_month_end = first_of_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        return (last_month_start, last_month_end)
```

### 3.3 Future Redis Migration Path

```python
class RedisCache:
    """
    Redis cache implementation for future scaling
    Drop-in replacement for TrendsCache
    """
    
    def __init__(self, redis_client, prefix='trends:', default_ttl=3600):
        self.redis = redis_client
        self.prefix = prefix
        self.default_ttl = default_ttl
    
    def generate_key(self, start_date, end_date, metrics):
        """
        Same key generation as in-memory cache
        """
        base_key = TrendsCache.generate_key(None, start_date, end_date, metrics)
        return f"{self.prefix}{base_key}"
    
    def get(self, key):
        """
        Retrieve from Redis with automatic deserialization
        """
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def set(self, key, data, ttl=None):
        """
        Store in Redis with TTL
        """
        if ttl is None:
            ttl = self.default_ttl
        
        self.redis.setex(
            key,
            ttl,
            json.dumps(data)
        )
    
    def get_ttl(self, key):
        """
        Get remaining TTL from Redis
        """
        ttl = self.redis.ttl(key)
        return max(0, ttl)
```

---

## 4. Data Processing Pipeline

### 4.1 Efficient Daily Summary Generation

```python
class DailySummaryProcessor:
    """
    Process activity logs into daily summaries efficiently
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def process_missing_days(self):
        """
        Find and process any missing daily summaries
        """
        query = """
        WITH all_dates AS (
            SELECT DISTINCT DATE(created_at) as activity_date
            FROM activity_log
            WHERE created_at >= date('now', '-365 days')
        ),
        existing_summaries AS (
            SELECT date
            FROM activity_summary_daily
            WHERE date >= date('now', '-365 days')
        )
        SELECT activity_date
        FROM all_dates
        WHERE activity_date NOT IN (SELECT date FROM existing_summaries)
        ORDER BY activity_date
        """
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            missing_dates = cursor.fetchall()
            
            for (date,) in missing_dates:
                self.generate_summary_for_date(date)
                app.logger.info(f"Generated missing summary for {date}")
                
        finally:
            conn.close()
    
    def generate_summary_for_date(self, date):
        """
        Generate summary for a specific date
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Main metrics
            metrics_query = """
            SELECT 
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT session_id) as total_sessions,
                SUM(CASE WHEN page_url IS NOT NULL THEN 1 ELSE 0 END) as total_page_views,
                SUM(CASE WHEN api_endpoint IS NOT NULL THEN 1 ELSE 0 END) as total_api_calls
            FROM activity_log
            WHERE DATE(created_at) = ?
            """
            
            cursor.execute(metrics_query, (date,))
            metrics = cursor.fetchone()
            
            if not metrics or metrics['unique_users'] == 0:
                # No activity for this date
                return
            
            # Session duration
            duration_query = """
            SELECT AVG(duration_seconds) as avg_duration
            FROM (
                SELECT 
                    session_id,
                    (julianday(MAX(created_at)) - julianday(MIN(created_at))) * 86400 as duration_seconds
                FROM activity_log
                WHERE DATE(created_at) = ?
                GROUP BY session_id
            )
            """
            
            cursor.execute(duration_query, (date,))
            duration_result = cursor.fetchone()
            avg_duration = duration_result['avg_duration'] if duration_result else 0
            
            # Peak concurrent users
            concurrent_query = """
            WITH time_slots AS (
                SELECT 
                    strftime('%Y-%m-%d %H:00', created_at) as hour_slot,
                    COUNT(DISTINCT user_id) as concurrent_users
                FROM activity_log
                WHERE DATE(created_at) = ?
                GROUP BY hour_slot
            )
            SELECT 
                MAX(concurrent_users) as peak_concurrent,
                hour_slot as peak_hour
            FROM time_slots
            """
            
            cursor.execute(concurrent_query, (date,))
            concurrent_result = cursor.fetchone()
            
            # Top pages
            top_pages_query = """
            SELECT json_group_array(
                json_object('page', page_url, 'count', page_count)
            ) as top_pages
            FROM (
                SELECT page_url, COUNT(*) as page_count
                FROM activity_log
                WHERE DATE(created_at) = ? AND page_url IS NOT NULL
                GROUP BY page_url
                ORDER BY page_count DESC
                LIMIT 10
            )
            """
            
            cursor.execute(top_pages_query, (date,))
            top_pages_result = cursor.fetchone()
            
            # User distribution
            distribution_query = """
            SELECT json_object(
                'admin', SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END),
                'manager', SUM(CASE WHEN role = 'manager' THEN 1 ELSE 0 END),
                'driver', SUM(CASE WHEN role = 'driver' THEN 1 ELSE 0 END),
                'viewer', SUM(CASE WHEN role = 'viewer' THEN 1 ELSE 0 END)
            ) as user_distribution
            FROM (
                SELECT DISTINCT al.user_id, u.role
                FROM activity_log al
                JOIN users u ON al.user_id = u.id
                WHERE DATE(al.created_at) = ?
            )
            """
            
            cursor.execute(distribution_query, (date,))
            distribution_result = cursor.fetchone()
            
            # Insert summary
            insert_query = """
            INSERT OR REPLACE INTO activity_summary_daily (
                date, unique_users, total_sessions, total_page_views,
                total_api_calls, avg_session_duration_seconds,
                peak_concurrent_users, peak_hour, top_pages, user_distribution
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(insert_query, (
                date,
                metrics['unique_users'],
                metrics['total_sessions'],
                metrics['total_page_views'],
                metrics['total_api_calls'],
                int(avg_duration) if avg_duration else 0,
                concurrent_result['peak_concurrent'] if concurrent_result else 0,
                concurrent_result['peak_hour'] if concurrent_result else None,
                top_pages_result['top_pages'] if top_pages_result else '[]',
                distribution_result['user_distribution'] if distribution_result else '{}'
            ))
            
            conn.commit()
            
        finally:
            conn.close()
```

### 4.2 Handling Missing Data Points

```python
class DataCompletionService:
    """
    Handle missing data points in trend visualization
    """
    
    def fill_missing_dates(self, data, start_date, end_date):
        """
        Fill missing dates with zero values for continuous chart display
        """
        current_date = start_date
        filled_data = {}
        
        # Create a lookup for existing data
        existing_data = {item['date']: item['value'] for item in data}
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            
            if date_str in existing_data:
                filled_data[date_str] = existing_data[date_str]
            else:
                # Fill with zero or interpolated value
                filled_data[date_str] = self._interpolate_value(
                    date_str, existing_data
                )
            
            current_date += timedelta(days=1)
        
        return [
            {'date': date, 'value': value}
            for date, value in filled_data.items()
        ]
    
    def _interpolate_value(self, date_str, existing_data):
        """
        Simple interpolation for missing values
        For activity data, we use 0 for missing days (no activity)
        """
        return 0  # No activity on missing days
        
        # Alternative: Linear interpolation between known points
        # This could be used for metrics that should have continuous values
        """
        dates = sorted(existing_data.keys())
        
        # Find surrounding dates
        before = [d for d in dates if d < date_str]
        after = [d for d in dates if d > date_str]
        
        if not before:
            return existing_data[after[0]] if after else 0
        if not after:
            return existing_data[before[-1]]
        
        # Linear interpolation
        date_before = before[-1]
        date_after = after[0]
        value_before = existing_data[date_before]
        value_after = existing_data[date_after]
        
        # Calculate position between dates
        total_days = (
            datetime.fromisoformat(date_after) - 
            datetime.fromisoformat(date_before)
        ).days
        
        days_from_before = (
            datetime.fromisoformat(date_str) - 
            datetime.fromisoformat(date_before)
        ).days
        
        # Interpolate
        ratio = days_from_before / total_days
        return value_before + (value_after - value_before) * ratio
        """
```

### 4.3 Trend Calculation

```python
class TrendAnalyzer:
    """
    Advanced trend analysis for activity data
    """
    
    def calculate_trend(self, data_points, confidence_threshold=0.7):
        """
        Calculate trend direction and strength
        
        Returns:
        {
            'direction': 'increasing' | 'decreasing' | 'stable',
            'strength': float (0-1),
            'confidence': float (0-1),
            'forecast': list of predicted values
        }
        """
        import numpy as np
        from scipy import stats
        from sklearn.linear_model import LinearRegression
        
        if len(data_points) < 3:
            return {
                'direction': 'stable',
                'strength': 0,
                'confidence': 0,
                'forecast': []
            }
        
        # Extract values and prepare for regression
        values = np.array([p['value'] for p in data_points])
        x = np.arange(len(values)).reshape(-1, 1)
        
        # Linear regression for trend
        model = LinearRegression()
        model.fit(x, values)
        
        # Calculate statistics
        predictions = model.predict(x)
        r_squared = model.score(x, values)
        slope = model.coef_[0]
        
        # Normalize slope relative to mean
        mean_value = np.mean(values)
        if mean_value > 0:
            normalized_slope = slope / mean_value
        else:
            normalized_slope = 0
        
        # Determine trend direction
        if abs(normalized_slope) < 0.01:  # Less than 1% change per period
            direction = 'stable'
        elif normalized_slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        # Calculate strength (0-1 scale)
        strength = min(1.0, abs(normalized_slope) * 10)
        
        # Generate forecast for next 7 days
        future_x = np.arange(len(values), len(values) + 7).reshape(-1, 1)
        forecast = model.predict(future_x).tolist()
        
        # Ensure forecast values are non-negative
        forecast = [max(0, val) for val in forecast]
        
        return {
            'direction': direction,
            'strength': round(strength, 3),
            'confidence': round(r_squared, 3),
            'slope': round(slope, 3),
            'forecast': forecast,
            'percentage_change': round(normalized_slope * 100, 2)
        }
```

---

## 5. Integration Points

### 5.1 Authentication Middleware Integration

```python
from functools import wraps
from flask import g, jsonify

def require_admin_role(f):
    """
    Decorator to enforce admin role for trends endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not hasattr(g, 'user') or not g.user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check role
        if g.user.get('role') != 'admin':
            # Log unauthorized access attempt
            audit_logger.log('UNAUTHORIZED_ACCESS', g.user['id'], {
                'endpoint': request.path,
                'required_role': 'admin',
                'user_role': g.user.get('role')
            })
            
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
```

### 5.2 Audit Logging Integration

```python
class AuditLogger:
    """
    Audit logging for activity trends access
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def log(self, action, user_id, details):
        """
        Log audit event to database
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (
                    user_id, action, details, ip_address, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                action,
                json.dumps(details),
                request.remote_addr,
                datetime.now()
            ))
            conn.commit()
        finally:
            conn.close()
```

### 5.3 Session State Management

```python
class SessionPreferenceManager:
    """
    Manage user preferences in session
    """
    
    def get_preferences(self):
        """
        Get user preferences from session
        """
        if 'activity_preferences' not in session:
            session['activity_preferences'] = {
                'date_range': 30,  # Default 30 days
                'metrics': ['unique_users', 'total_sessions'],
                'chart_type': 'line',
                'auto_refresh': False
            }
        
        return session['activity_preferences']
    
    def update_preferences(self, preferences):
        """
        Update user preferences in session
        """
        current = self.get_preferences()
        current.update(preferences)
        session['activity_preferences'] = current
        session.permanent = True
        
        return current
```

### 5.4 Export Streaming

```python
from flask import Response
import csv
from io import StringIO

class StreamingExporter:
    """
    Stream large datasets for export
    """
    
    def stream_csv(self, data_generator, headers):
        """
        Stream CSV data to client
        """
        def generate():
            # Use StringIO for line buffering
            output = StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(headers)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
            
            # Stream data rows
            for row in data_generator:
                writer.writerow(row)
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
        
        return Response(
            generate(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=export.csv',
                'X-Accel-Buffering': 'no'  # Disable proxy buffering
            }
        )
```

---

## 6. Performance Requirements

### 6.1 Query Performance Targets

```python
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
    
    def measure(self, operation):
        """
        Decorator to measure operation performance
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
                        app.logger.warning(
                            f"Slow operation: {operation} took {elapsed_ms:.2f}ms"
                        )
                    
                    return result
                    
                except Exception as e:
                    elapsed_ms = (time.time() - start_time) * 1000
                    self.record_metric(operation, elapsed_ms, error=True)
                    raise
            
            return wrapper
        return decorator
    
    def record_metric(self, operation, duration_ms, error=False):
        """
        Record performance metric
        """
        self.metrics[operation].append({
            'timestamp': time.time(),
            'duration_ms': duration_ms,
            'error': error
        })
        
        # Keep only last 1000 metrics per operation
        if len(self.metrics[operation]) > 1000:
            self.metrics[operation] = self.metrics[operation][-1000:]
    
    def get_stats(self, operation):
        """
        Get performance statistics for an operation
        """
        metrics = self.metrics.get(operation, [])
        
        if not metrics:
            return None
        
        durations = [m['duration_ms'] for m in metrics if not m['error']]
        
        if not durations:
            return None
        
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
```

### 6.2 Memory Usage Constraints

```python
import psutil
import gc

class MemoryManager:
    """
    Monitor and manage memory usage
    """
    
    def __init__(self, max_memory_mb=100):
        self.max_memory_mb = max_memory_mb
        self.process = psutil.Process()
    
    def check_memory(self):
        """
        Check current memory usage
        """
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        if memory_mb > self.max_memory_mb:
            app.logger.warning(f"High memory usage: {memory_mb:.2f}MB")
            
            # Trigger garbage collection
            gc.collect()
            
            # Clear caches if needed
            if memory_mb > self.max_memory_mb * 1.2:
                trends_cache.clear()
                app.logger.info("Cleared trends cache due to memory pressure")
        
        return {
            'current_mb': memory_mb,
            'max_mb': self.max_memory_mb,
            'percentage': (memory_mb / self.max_memory_mb) * 100
        }
```

### 6.3 Concurrent Request Handling

```python
from threading import Semaphore

class ConcurrencyManager:
    """
    Manage concurrent request limits
    """
    
    def __init__(self, max_concurrent=50):
        self.semaphore = Semaphore(max_concurrent)
        self.active_requests = 0
        self.max_concurrent = max_concurrent
    
    def acquire(self, timeout=5):
        """
        Acquire a slot for processing
        """
        if not self.semaphore.acquire(timeout=timeout):
            raise Exception("Too many concurrent requests")
        
        self.active_requests += 1
    
    def release(self):
        """
        Release a processing slot
        """
        self.semaphore.release()
        self.active_requests -= 1
    
    def get_stats(self):
        """
        Get concurrency statistics
        """
        return {
            'active': self.active_requests,
            'max': self.max_concurrent,
            'available': self.max_concurrent - self.active_requests
        }
```

---

## 7. Step-by-Step Implementation

### 7.1 Implementation Order

```python
"""
Implementation Phases and Dependencies
"""

# Phase 1: Database Setup (Day 1)
def phase1_database_setup():
    """
    1. Create new indexes on activity_summary_daily
    2. Run migration to ensure table structure
    3. Backfill any missing daily summaries
    4. Verify query performance
    """
    steps = [
        "Run index creation SQL",
        "Execute DailySummaryProcessor.process_missing_days()",
        "Test query performance with EXPLAIN QUERY PLAN",
        "Document baseline performance metrics"
    ]
    
# Phase 2: Core Service Layer (Day 2-3)
def phase2_service_layer():
    """
    1. Implement ActivityTrendsService class
    2. Implement TrendAnalyzer class
    3. Create unit tests for service layer
    4. Validate calculations against manual queries
    """
    steps = [
        "Create activity_trends_service.py",
        "Implement data retrieval methods",
        "Add trend calculation logic",
        "Write comprehensive unit tests"
    ]

# Phase 3: Caching Layer (Day 4)
def phase3_caching():
    """
    1. Implement TrendsCache class
    2. Add cache warming logic
    3. Test cache hit/miss scenarios
    4. Monitor memory usage
    """
    steps = [
        "Create trends_cache.py",
        "Implement LRU eviction",
        "Add TTL management",
        "Test concurrent access"
    ]

# Phase 4: API Endpoints (Day 5-6)
def phase4_api_endpoints():
    """
    1. Create trends blueprint
    2. Implement validation logic
    3. Add rate limiting
    4. Create export endpoint
    """
    steps = [
        "Create activity_trends_api.py",
        "Implement GET /api/admin/activity/trends",
        "Implement GET /api/admin/activity/export",
        "Add comprehensive error handling"
    ]

# Phase 5: Integration (Day 7)
def phase5_integration():
    """
    1. Wire up all components
    2. Add middleware integration
    3. Test end-to-end flow
    4. Performance testing
    """
    steps = [
        "Register blueprint in app.py",
        "Configure cache initialization",
        "Add background tasks",
        "Run load tests"
    ]

# Phase 6: Monitoring & Optimization (Day 8)
def phase6_monitoring():
    """
    1. Add performance monitoring
    2. Implement health checks
    3. Optimize slow queries
    4. Documentation
    """
    steps = [
        "Add performance metrics collection",
        "Create monitoring dashboard endpoint",
        "Optimize based on profiling",
        "Write deployment documentation"
    ]
```

### 7.2 Testing Approach

```python
import unittest
from unittest.mock import Mock, patch
import sqlite3

class TestActivityTrendsAPI(unittest.TestCase):
    """
    Comprehensive test suite for trends API
    """
    
    def setUp(self):
        """
        Set up test database and fixtures
        """
        self.app = create_test_app()
        self.client = self.app.test_client()
        self.setup_test_data()
    
    def setup_test_data(self):
        """
        Create test data in database
        """
        # Create 30 days of test data
        for i in range(30):
            date = datetime.now().date() - timedelta(days=i)
            self.create_daily_summary(date, 
                unique_users=10 + i,
                total_sessions=20 + i * 2,
                total_page_views=100 + i * 10
            )
    
    def test_valid_date_range(self):
        """
        Test API with valid date range
        """
        response = self.client.get('/api/admin/activity/trends', 
            query_string={
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            },
            headers={'Authorization': 'Bearer admin_token'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('metrics', data['data'])
    
    def test_cache_behavior(self):
        """
        Test caching behavior
        """
        # First request - cache miss
        response1 = self.client.get('/api/admin/activity/trends',
            query_string={
                'start_date': '2024-01-01',
                'end_date': '2024-01-07'
            }
        )
        self.assertFalse(response1.get_json()['cached'])
        
        # Second request - cache hit
        response2 = self.client.get('/api/admin/activity/trends',
            query_string={
                'start_date': '2024-01-01',
                'end_date': '2024-01-07'
            }
        )
        self.assertTrue(response2.get_json()['cached'])
    
    def test_rate_limiting(self):
        """
        Test rate limiting enforcement
        """
        # Make 100 requests rapidly
        for i in range(100):
            response = self.client.get('/api/admin/activity/trends',
                query_string={
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-07'
                }
            )
            
            if response.status_code == 429:
                # Rate limit hit
                break
        
        self.assertEqual(response.status_code, 429)
    
    def test_performance_requirements(self):
        """
        Test that API meets performance requirements
        """
        import time
        
        start = time.time()
        response = self.client.get('/api/admin/activity/trends',
            query_string={
                'start_date': '2023-01-01',
                'end_date': '2023-12-31'  # Full year
            }
        )
        elapsed = time.time() - start
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 2.0)  # Must respond within 2 seconds
```

### 7.3 Rollback Strategies

```python
class RollbackManager:
    """
    Handle rollback scenarios gracefully
    """
    
    def __init__(self):
        self.feature_flags = {
            'trends_api_enabled': True,
            'use_cache': True,
            'rate_limiting_enabled': True
        }
    
    def disable_feature(self, feature):
        """
        Disable a feature without restart
        """
        self.feature_flags[feature] = False
        app.logger.warning(f"Feature {feature} disabled")
    
    def create_backup(self):
        """
        Create backup before deployment
        """
        import shutil
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup database
        shutil.copy2('cvd.db', f'backups/cvd_{timestamp}.db')
        
        # Backup configuration
        with open(f'backups/config_{timestamp}.json', 'w') as f:
            json.dump(self.feature_flags, f)
        
        app.logger.info(f"Backup created: {timestamp}")
    
    def restore_backup(self, timestamp):
        """
        Restore from backup
        """
        import shutil
        
        # Restore database
        shutil.copy2(f'backups/cvd_{timestamp}.db', 'cvd.db')
        
        # Restore configuration
        with open(f'backups/config_{timestamp}.json', 'r') as f:
            self.feature_flags = json.load(f)
        
        app.logger.info(f"Restored from backup: {timestamp}")
```

### 7.4 Monitoring and Logging Setup

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_monitoring():
    """
    Configure comprehensive monitoring
    """
    
    # Performance logger
    perf_logger = logging.getLogger('performance')
    perf_handler = RotatingFileHandler(
        'logs/performance.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    perf_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    perf_logger.addHandler(perf_handler)
    
    # Audit logger
    audit_logger = logging.getLogger('audit')
    audit_handler = RotatingFileHandler(
        'logs/audit.log',
        maxBytes=10485760,
        backupCount=30
    )
    audit_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(user)s %(action)s: %(details)s'
    ))
    audit_logger.addHandler(audit_handler)
    
    # Error logger
    error_logger = logging.getLogger('errors')
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10485760,
        backupCount=10
    )
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s\n%(exc_info)s'
    ))
    error_logger.addHandler(error_handler)
    
    return {
        'performance': perf_logger,
        'audit': audit_logger,
        'errors': error_logger
    }

# Health check endpoint
@app.route('/api/admin/activity/health', methods=['GET'])
@require_admin_role
def health_check():
    """
    Health check endpoint for monitoring
    """
    health = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # Check database
    try:
        conn = sqlite3.connect(DATABASE)
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
    cache_stats = trends_cache.get_stats()
    health['checks']['cache'] = {
        'status': 'ok',
        'stats': cache_stats
    }
    
    # Check memory
    memory_stats = memory_manager.check_memory()
    health['checks']['memory'] = {
        'status': 'ok' if memory_stats['percentage'] < 80 else 'warning',
        'usage': memory_stats
    }
    
    # Performance metrics
    perf_stats = {}
    for operation in ['trends_api', 'export_api', 'db_query']:
        stats = performance_monitor.get_stats(operation)
        if stats:
            perf_stats[operation] = {
                'avg_ms': round(stats['avg_ms'], 2),
                'p95_ms': round(stats['p95_ms'], 2)
            }
    
    health['checks']['performance'] = perf_stats
    
    status_code = 200 if health['status'] == 'healthy' else 503
    return jsonify(health), status_code
```

---

## 8. Critical Code Examples

### 8.1 Complete API Implementation

```python
# activity_trends_api.py
from flask import Blueprint, jsonify, request, g, Response
from datetime import datetime, timedelta
import json
import time

# Initialize components
trends_cache = TrendsCache(max_size=100, default_ttl=3600)
trends_service = ActivityTrendsService(DATABASE)
performance_monitor = PerformanceMonitor()
rate_limiter = RateLimiter(requests_per_minute=100)
audit_logger = AuditLogger(DATABASE)

# Create blueprint
activity_trends_bp = Blueprint('activity_trends', __name__)

# Main implementation file content...
# [Previous endpoint implementations go here]

# Register error handlers
@activity_trends_bp.errorhandler(429)
def handle_rate_limit(e):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.',
        'retry_after': 60
    }), 429

@activity_trends_bp.errorhandler(500)
def handle_server_error(e):
    app.logger.error(f"Server error: {str(e)}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'An internal error occurred'
    }), 500

# Initialize on app startup
def init_trends_module(app):
    """
    Initialize trends module with Flask app
    """
    app.register_blueprint(activity_trends_bp)
    
    # Warm cache on startup
    cache_warmer = CacheWarmer(trends_cache, trends_service)
    cache_warmer.warm_cache()
    
    # Start background tasks
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    # Daily summary aggregation at 2 AM
    scheduler.add_job(
        func=lambda: DailySummaryProcessor(DATABASE).process_missing_days(),
        trigger="cron",
        hour=2,
        minute=0
    )
    
    # Cache warming every hour
    scheduler.add_job(
        func=cache_warmer.warm_cache,
        trigger="interval",
        hours=1
    )
    
    scheduler.start()
    
    app.logger.info("Activity Trends module initialized")
```

### 8.2 Rate Limiting Implementation

```python
# rate_limiter.py
from collections import defaultdict
from threading import RLock
import time

class RateLimiter:
    """
    Token bucket rate limiter
    """
    
    def __init__(self, requests_per_minute=100):
        self.requests_per_minute = requests_per_minute
        self.buckets = defaultdict(lambda: {
            'tokens': requests_per_minute,
            'last_refill': time.time()
        })
        self.lock = RLock()
    
    def check_limit(self, user_id, endpoint):
        """
        Check if request is allowed
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
    
    def get_wait_time(self, user_id, endpoint):
        """
        Get seconds until next request is allowed
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
```

---

## Summary

This comprehensive backend implementation plan provides:

1. **Complete API specifications** with validation, error handling, and response formats
2. **Optimized database queries** with proper indexing and aggregation strategies
3. **Multi-layer caching** with in-memory implementation and Redis migration path
4. **Efficient data processing** with missing data handling and trend analysis
5. **Robust integration points** for authentication, audit logging, and session management
6. **Performance monitoring** with specific targets and measurement tools
7. **Step-by-step implementation guide** with testing and rollback strategies

The implementation is optimized for desktop clients, taking advantage of their ability to handle larger payloads and richer data responses. The architecture ensures sub-2 second response times for 365 days of data while maintaining system stability and providing graceful degradation under load.

Key technical decisions:
- SQLite with optimized indexes for efficient queries
- In-memory caching with LRU eviction for fast response times
- Token bucket rate limiting for fair resource usage
- Streaming exports for large datasets
- Comprehensive monitoring and health checks for operational visibility

This plan provides backend engineers with everything needed to implement the Activity Monitor Enhancement feature successfully.