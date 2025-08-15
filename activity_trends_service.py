"""
Activity Trends Service
Core service layer for efficient trend data retrieval and analysis
Phase 2: Core Service Layer Implementation
"""

import sqlite3
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional, Tuple
import json
import numpy as np
from scipy import stats
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ActivityTrendsService:
    """
    Service class for efficient trend data retrieval
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection - always create new for thread safety"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _return_connection(self, conn: sqlite3.Connection):
        """Close connection - no pooling for SQLite due to thread safety"""
        conn.close()
    
    def get_trends(self, start_date: date, end_date: date, metrics: List[str]) -> Dict[str, List[Dict]]:
        """
        Optimized query for trend data retrieval with moving averages
        
        Args:
            start_date: Start date for trend data
            end_date: End date for trend data
            metrics: List of metrics to retrieve
        
        Returns:
            Dictionary with metric names as keys and trend data as values
        """
        # Build dynamic column selection based on requested metrics
        metric_columns = []
        for metric in metrics:
            if metric in ['unique_users', 'total_sessions', 'total_page_views', 
                         'total_api_calls', 'avg_session_duration_seconds', 'peak_concurrent_users']:
                metric_columns.append(metric)
        
        if not metric_columns:
            metric_columns = ['unique_users', 'total_sessions', 'total_page_views']
        
        columns_str = ', '.join(metric_columns)
        
        query = f"""
        WITH date_range AS (
            SELECT 
                date,
                {columns_str}
            FROM activity_summary_daily
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC
        ),
        moving_averages AS (
            SELECT 
                date,
                {', '.join(metric_columns)},
                -- 7-day moving averages for trend calculation
                {', '.join([f'''AVG({metric}) OVER (
                    ORDER BY date 
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) as {metric}_7day_avg''' for metric in metric_columns])},
                -- 30-day moving averages for long-term trends
                {', '.join([f'''AVG({metric}) OVER (
                    ORDER BY date 
                    ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
                ) as {metric}_30day_avg''' for metric in metric_columns if metric in ['unique_users', 'total_sessions']])}
            FROM date_range
        )
        SELECT * FROM moving_averages
        """
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            return self._format_trend_data(rows, metrics)
            
        finally:
            self._return_connection(conn)
    
    def get_trends_raw(self, start_date: date, end_date: date, metrics: List[str]) -> Dict[str, Dict]:
        """
        Get raw trend data for export purposes
        
        Args:
            start_date: Start date for trend data
            end_date: End date for trend data
            metrics: List of metrics to retrieve
        
        Returns:
            Dictionary with dates as keys and metric values as nested dict
        """
        metric_columns = []
        for metric in metrics:
            if metric in ['unique_users', 'total_sessions', 'total_page_views', 
                         'total_api_calls', 'avg_session_duration_seconds', 'peak_concurrent_users']:
                metric_columns.append(metric)
        
        if not metric_columns:
            metric_columns = ['unique_users', 'total_sessions', 'total_page_views']
        
        columns_str = ', '.join(metric_columns)
        
        query = f"""
        SELECT date, {columns_str}
        FROM activity_summary_daily
        WHERE date BETWEEN ? AND ?
        ORDER BY date ASC
        """
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            result = {}
            
            for row in rows:
                date_str = row['date']
                result[date_str] = {metric: row[metric] for metric in metric_columns}
            
            return result
            
        finally:
            self._return_connection(conn)
    
    def _format_trend_data(self, rows: List[sqlite3.Row], metrics: List[str]) -> Dict[str, List[Dict]]:
        """
        Format raw database rows into API response format
        
        Args:
            rows: Database rows
            metrics: List of requested metrics
        
        Returns:
            Formatted trend data
        """
        result = {metric: [] for metric in metrics}
        
        for row in rows:
            date_str = row['date']
            for metric in metrics:
                if metric in dict(row):
                    data_point = {
                        'date': date_str,
                        'value': row[metric] or 0
                    }
                    
                    # Add moving averages if available
                    if f'{metric}_7day_avg' in dict(row):
                        data_point['7day_avg'] = round(row[f'{metric}_7day_avg'] or 0, 2)
                    if f'{metric}_30day_avg' in dict(row):
                        data_point['30day_avg'] = round(row[f'{metric}_30day_avg'] or 0, 2)
                    
                    result[metric].append(data_point)
        
        return result
    
    def calculate_summary(self, trends_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """
        Calculate summary statistics and trend indicators
        
        Args:
            trends_data: Trend data from get_trends
        
        Returns:
            Summary statistics for each metric
        """
        summary = {}
        
        for metric, data_points in trends_data.items():
            if not data_points:
                continue
            
            values = [p['value'] for p in data_points]
            dates = [p['date'] for p in data_points]
            
            # Basic statistics
            summary[metric] = {
                'average': round(np.mean(values), 2),
                'median': round(np.median(values), 2),
                'std_dev': round(np.std(values), 2),
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
                mean_val = np.mean(values)
                if mean_val > 0:
                    relative_slope = abs(slope) / mean_val
                else:
                    relative_slope = 0
                
                if relative_slope < 0.01:  # Less than 1% change
                    trend = 'stable'
                elif slope > 0:
                    trend = 'increasing'
                else:
                    trend = 'decreasing'
                
                # Calculate percentage change
                if values[0] != 0:
                    pct_change = ((values[-1] - values[0]) / values[0]) * 100
                else:
                    pct_change = 0 if values[-1] == 0 else 100
                
                summary[metric].update({
                    'trend': trend,
                    'trend_slope': round(slope, 3),
                    'trend_confidence': round(abs(r_value), 3),  # R-squared value
                    'percentage_change': round(pct_change, 2)
                })
        
        return summary


class TrendAnalyzer:
    """
    Advanced trend analysis for activity data
    """
    
    def calculate_trend(self, data_points: List[Dict], confidence_threshold: float = 0.7) -> Dict:
        """
        Calculate trend direction and strength with forecast
        
        Args:
            data_points: List of data points with 'value' key
            confidence_threshold: Minimum R-squared for confident trend
        
        Returns:
            Trend analysis with direction, strength, confidence, and forecast
        """
        if len(data_points) < 3:
            return {
                'direction': 'stable',
                'strength': 0,
                'confidence': 0,
                'forecast': [],
                'percentage_change': 0
            }
        
        # Extract values and prepare for regression
        values = np.array([p['value'] for p in data_points])
        x = np.arange(len(values)).reshape(-1, 1)
        
        # Simple linear regression (scikit-learn not available, using numpy)
        # Calculate slope and intercept manually
        x_flat = x.flatten()
        slope, intercept = np.polyfit(x_flat, values, 1)
        
        # Calculate predictions
        predictions = slope * x_flat + intercept
        
        # Calculate R-squared
        ss_res = np.sum((values - predictions) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
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
        future_x = np.arange(len(values), len(values) + 7)
        forecast = (slope * future_x + intercept).tolist()
        
        # Ensure forecast values are non-negative
        forecast = [max(0, val) for val in forecast]
        
        # Calculate percentage change
        if values[0] != 0:
            pct_change = ((values[-1] - values[0]) / values[0]) * 100
        else:
            pct_change = 0 if values[-1] == 0 else 100
        
        return {
            'direction': direction,
            'strength': round(strength, 3),
            'confidence': round(r_squared, 3),
            'slope': round(slope, 3),
            'forecast': [round(v, 2) for v in forecast],
            'percentage_change': round(pct_change, 2)
        }


class DailySummaryProcessor:
    """
    Process activity logs into daily summaries efficiently
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def process_missing_days(self) -> int:
        """
        Find and process any missing daily summaries
        
        Returns:
            Number of days processed
        """
        query = """
        WITH all_dates AS (
            SELECT DISTINCT DATE(timestamp) as activity_date
            FROM user_activity_log
            WHERE timestamp >= date('now', '-365 days')
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
        
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        processed_count = 0
        
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            missing_dates = cursor.fetchall()
            
            for (date_val,) in missing_dates:
                if self.generate_summary_for_date(date_val):
                    processed_count += 1
                    logger.info(f"Generated missing summary for {date_val}")
                
        finally:
            conn.close()
        
        return processed_count
    
    def generate_summary_for_date(self, target_date: str) -> bool:
        """
        Generate summary for a specific date
        
        Args:
            target_date: Date string in YYYY-MM-DD format
        
        Returns:
            True if summary was generated, False otherwise
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            cursor = conn.cursor()
            
            # Main metrics from user_activity_log
            metrics_query = """
            SELECT 
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT session_id) as total_sessions,
                SUM(CASE WHEN page_url IS NOT NULL THEN 1 ELSE 0 END) as total_page_views,
                SUM(CASE WHEN action_type = 'api_call' THEN 1 ELSE 0 END) as total_api_calls
            FROM user_activity_log
            WHERE DATE(timestamp) = ?
            """
            
            cursor.execute(metrics_query, (target_date,))
            metrics = cursor.fetchone()
            
            if not metrics or metrics[0] == 0:  # No activity for this date
                return False
            
            # Session duration (approximate from activity timestamps)
            duration_query = """
            SELECT AVG(duration_seconds) as avg_duration
            FROM (
                SELECT 
                    session_id,
                    (julianday(MAX(timestamp)) - julianday(MIN(timestamp))) * 86400 as duration_seconds
                FROM user_activity_log
                WHERE DATE(timestamp) = ?
                GROUP BY session_id
                HAVING duration_seconds > 0
            )
            """
            
            cursor.execute(duration_query, (target_date,))
            duration_result = cursor.fetchone()
            avg_duration = int(duration_result[0]) if duration_result and duration_result[0] else 0
            
            # Peak concurrent users (approximate by hour)
            concurrent_query = """
            WITH time_slots AS (
                SELECT 
                    strftime('%H', timestamp) as hour_slot,
                    COUNT(DISTINCT user_id) as concurrent_users
                FROM user_activity_log
                WHERE DATE(timestamp) = ?
                GROUP BY hour_slot
            )
            SELECT 
                MAX(concurrent_users) as peak_concurrent,
                hour_slot as peak_hour
            FROM time_slots
            """
            
            cursor.execute(concurrent_query, (target_date,))
            concurrent_result = cursor.fetchone()
            
            # Top pages
            top_pages_query = """
            SELECT json_group_array(
                json_object('page', page_url, 'count', page_count)
            ) as top_pages
            FROM (
                SELECT page_url, COUNT(*) as page_count
                FROM user_activity_log
                WHERE DATE(timestamp) = ? AND page_url IS NOT NULL
                GROUP BY page_url
                ORDER BY page_count DESC
                LIMIT 10
            )
            """
            
            cursor.execute(top_pages_query, (target_date,))
            top_pages_result = cursor.fetchone()
            
            # User distribution by role
            distribution_query = """
            SELECT json_object(
                'admin', SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END),
                'manager', SUM(CASE WHEN role = 'manager' THEN 1 ELSE 0 END),
                'driver', SUM(CASE WHEN role = 'driver' THEN 1 ELSE 0 END),
                'viewer', SUM(CASE WHEN role = 'viewer' THEN 1 ELSE 0 END)
            ) as user_distribution
            FROM (
                SELECT DISTINCT al.user_id, u.role
                FROM user_activity_log al
                JOIN users u ON al.user_id = u.id
                WHERE DATE(al.timestamp) = ?
            )
            """
            
            cursor.execute(distribution_query, (target_date,))
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
                target_date,
                metrics[0],  # unique_users
                metrics[1],  # total_sessions
                metrics[2],  # total_page_views
                metrics[3],  # total_api_calls
                avg_duration,
                concurrent_result[0] if concurrent_result else 0,
                int(concurrent_result[1]) if concurrent_result and concurrent_result[1] else None,
                top_pages_result[0] if top_pages_result else '[]',
                distribution_result[0] if distribution_result else '{}'
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error generating summary for {target_date}: {e}")
            return False
        finally:
            conn.close()


class DataCompletionService:
    """
    Handle missing data points in trend visualization
    """
    
    def fill_missing_dates(self, data: List[Dict], start_date: date, end_date: date) -> List[Dict]:
        """
        Fill missing dates with zero values for continuous chart display
        
        Args:
            data: List of data points with 'date' and 'value' keys
            start_date: Start date
            end_date: End date
        
        Returns:
            Complete list with missing dates filled
        """
        # Create a lookup for existing data
        existing_data = {item['date']: item['value'] for item in data}
        
        filled_data = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            
            if date_str in existing_data:
                value = existing_data[date_str]
            else:
                # Fill with zero for missing days (no activity)
                value = 0
            
            filled_data.append({
                'date': date_str,
                'value': value
            })
            
            current_date += timedelta(days=1)
        
        return filled_data