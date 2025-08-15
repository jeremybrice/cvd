"""
Trends Cache Implementation
Thread-safe in-memory cache with TTL and LRU eviction
Phase 3: Caching Layer Implementation
"""

import time
import hashlib
import json
from collections import OrderedDict
from threading import RLock
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TrendsCache:
    """
    Thread-safe in-memory cache with TTL and LRU eviction
    Designed for desktop clients that can handle larger payloads
    """
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """
        Initialize the cache
        
        Args:
            max_size: Maximum number of entries in cache
            default_ttl: Default time-to-live in seconds (1 hour)
        """
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
    
    def generate_key(self, start_date: date, end_date: date, metrics: List[str]) -> str:
        """
        Generate consistent cache key from parameters
        
        Args:
            start_date: Start date
            end_date: End date
            metrics: List of metrics
        
        Returns:
            MD5 hash key
        """
        key_data = {
            'start': start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
            'end': end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date),
            'metrics': sorted(metrics)  # Sort for consistency
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache if not expired
        
        Args:
            key: Cache key
        
        Returns:
            Cached data or None if not found/expired
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
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None):
        """
        Store item in cache with TTL
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        with self.lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
                logger.debug(f"Evicted cache entry: {oldest_key}")
            
            self.cache[key] = {
                'data': data,
                'expires_at': time.time() + ttl,
                'created_at': time.time(),
                'ttl': ttl
            }
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.stats['sets'] += 1
    
    def get_ttl(self, key: str) -> int:
        """
        Get remaining TTL for cache entry
        
        Args:
            key: Cache key
        
        Returns:
            Remaining seconds or 0 if not found
        """
        with self.lock:
            if key not in self.cache:
                return 0
            
            entry = self.cache[key]
            remaining = max(0, entry['expires_at'] - time.time())
            return int(remaining)
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics
        
        Returns:
            Dictionary with cache statistics
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
    
    def cleanup_expired(self):
        """Remove expired entries from cache"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self.cache.items()
                if current_time > entry['expires_at']
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")


class CacheWarmer:
    """
    Preload cache with commonly requested data
    """
    
    def __init__(self, cache: TrendsCache, service):
        """
        Initialize cache warmer
        
        Args:
            cache: TrendsCache instance
            service: ActivityTrendsService instance
        """
        self.cache = cache
        self.service = service
    
    def warm_cache(self):
        """
        Preload cache with common date ranges
        Run this after server startup or cache clear
        """
        logger.info("Starting cache warming...")
        
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
        
        warmed_count = 0
        for start_date, end_date in common_ranges:
            try:
                # Fetch data
                data = self.service.get_trends(start_date, end_date, default_metrics)
                summary = self.service.calculate_summary(data)
                
                # Format response
                response_data = {
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'metrics': data,
                    'summary': summary
                }
                
                # Cache it
                cache_key = self.cache.generate_key(start_date, end_date, default_metrics)
                self.cache.set(cache_key, response_data)
                
                warmed_count += 1
                logger.info(f"Warmed cache for range {start_date} to {end_date}")
                
            except Exception as e:
                logger.error(f"Failed to warm cache for {start_date} to {end_date}: {e}")
        
        logger.info(f"Cache warming complete. Warmed {warmed_count} entries.")
    
    def _get_last_month_range(self) -> tuple:
        """
        Get date range for last month
        
        Returns:
            Tuple of (start_date, end_date) for last month
        """
        today = datetime.now().date()
        first_of_month = today.replace(day=1)
        last_month_end = first_of_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        return (last_month_start, last_month_end)


class RedisCache:
    """
    Redis cache implementation for future scaling
    Drop-in replacement for TrendsCache
    Note: This is a template for future Redis migration
    """
    
    def __init__(self, redis_client=None, prefix: str = 'trends:', default_ttl: int = 3600):
        """
        Initialize Redis cache
        
        Args:
            redis_client: Redis client instance
            prefix: Key prefix for namespacing
            default_ttl: Default time-to-live in seconds
        """
        self.redis = redis_client
        self.prefix = prefix
        self.default_ttl = default_ttl
        
        if self.redis is None:
            logger.warning("Redis client not provided. Cache operations will be no-ops.")
    
    def generate_key(self, start_date: date, end_date: date, metrics: List[str]) -> str:
        """
        Same key generation as in-memory cache
        
        Args:
            start_date: Start date
            end_date: End date  
            metrics: List of metrics
        
        Returns:
            Prefixed cache key
        """
        # Use the same key generation logic
        key_data = {
            'start': start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
            'end': end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date),
            'metrics': sorted(metrics)
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        base_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.prefix}{base_key}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve from Redis with automatic deserialization
        
        Args:
            key: Cache key
        
        Returns:
            Cached data or None
        """
        if self.redis is None:
            return None
        
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None):
        """
        Store in Redis with TTL
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds
        """
        if self.redis is None:
            return
        
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            self.redis.setex(
                key,
                ttl,
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def get_ttl(self, key: str) -> int:
        """
        Get remaining TTL from Redis
        
        Args:
            key: Cache key
        
        Returns:
            Remaining seconds or 0
        """
        if self.redis is None:
            return 0
        
        try:
            ttl = self.redis.ttl(key)
            return max(0, ttl)
        except Exception as e:
            logger.error(f"Redis TTL error: {e}")
            return 0
    
    def clear(self):
        """Clear all cache entries with prefix"""
        if self.redis is None:
            return
        
        try:
            # Get all keys with prefix
            keys = self.redis.keys(f"{self.prefix}*")
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} Redis cache entries")
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics (limited for Redis)
        
        Returns:
            Dictionary with available stats
        """
        if self.redis is None:
            return {'error': 'Redis not connected'}
        
        try:
            info = self.redis.info('stats')
            keys_count = len(self.redis.keys(f"{self.prefix}*"))
            
            return {
                'size': keys_count,
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': round(
                    info.get('keyspace_hits', 0) / 
                    (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)) * 100,
                    2
                )
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {'error': str(e)}