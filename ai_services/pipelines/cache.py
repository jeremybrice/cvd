"""
Multi-tier caching system for AI services

Implements three-tier caching:
- L1: In-memory cache (5 minute TTL)
- L2: Redis cache (1 hour TTL) 
- L3: SQLite cache (24 hour TTL)
"""

import json
import time
import hashlib
import logging
import sqlite3
from typing import Optional, Any, Dict, Callable
from datetime import datetime, timedelta
from functools import wraps
import pickle

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available. L2 cache disabled.")

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Three-tier caching system for AI responses
    """
    
    # TTL settings (in seconds)
    L1_TTL = 300  # 5 minutes
    L2_TTL = 3600  # 1 hour
    L3_TTL = 86400  # 24 hours
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        sqlite_path: str = "ai_cache.db",
        enable_l1: bool = True,
        enable_l2: bool = True,
        enable_l3: bool = True
    ):
        """
        Initialize cache manager
        
        Args:
            redis_url: Redis connection URL
            sqlite_path: Path to SQLite cache database
            enable_l1: Enable memory cache
            enable_l2: Enable Redis cache
            enable_l3: Enable SQLite cache
        """
        # L1: Memory cache
        self.enable_l1 = enable_l1
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # L2: Redis cache
        self.enable_l2 = enable_l2 and REDIS_AVAILABLE
        self.redis_client = None
        if self.enable_l2 and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self.enable_l2 = False
        
        # L3: SQLite cache
        self.enable_l3 = enable_l3
        self.sqlite_path = sqlite_path
        if self.enable_l3:
            self._init_sqlite()
        
        # Statistics
        self.hits = {"L1": 0, "L2": 0, "L3": 0}
        self.misses = 0
        self.writes = {"L1": 0, "L2": 0, "L3": 0}
    
    def _init_sqlite(self):
        """Initialize SQLite cache database"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_cache (
                    cache_key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    hit_count INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON ai_cache(expires_at)
            """)
            conn.commit()
            conn.close()
            logger.info("SQLite cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite cache: {e}")
            self.enable_l3 = False
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Generate cache key from function arguments
        
        Returns:
            MD5 hash of arguments
        """
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (checks all tiers)
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        # Check L1 (Memory)
        if self.enable_l1:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if time.time() < entry["expires_at"]:
                    self.hits["L1"] += 1
                    logger.debug(f"L1 cache hit for key: {key}")
                    return entry["value"]
                else:
                    del self.memory_cache[key]
        
        # Check L2 (Redis)
        if self.enable_l2 and self.redis_client:
            try:
                cached = self.redis_client.get(f"ai_cache:{key}")
                if cached:
                    value = pickle.loads(cached)
                    self.hits["L2"] += 1
                    logger.debug(f"L2 cache hit for key: {key}")
                    
                    # Promote to L1
                    if self.enable_l1:
                        self._set_l1(key, value)
                    
                    return value
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # Check L3 (SQLite)
        if self.enable_l3:
            try:
                conn = sqlite3.connect(self.sqlite_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value FROM ai_cache
                    WHERE cache_key = ? AND expires_at > ?
                """, (key, datetime.now()))
                
                result = cursor.fetchone()
                if result:
                    value = json.loads(result[0])
                    self.hits["L3"] += 1
                    logger.debug(f"L3 cache hit for key: {key}")
                    
                    # Update hit count
                    cursor.execute("""
                        UPDATE ai_cache SET hit_count = hit_count + 1
                        WHERE cache_key = ?
                    """, (key,))
                    conn.commit()
                    
                    # Promote to L1 and L2
                    if self.enable_l1:
                        self._set_l1(key, value)
                    if self.enable_l2:
                        self._set_l2(key, value)
                    
                    conn.close()
                    return value
                
                conn.close()
            except Exception as e:
                logger.warning(f"SQLite get error: {e}")
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in all cache tiers
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override
        """
        if self.enable_l1:
            self._set_l1(key, value, ttl)
        
        if self.enable_l2:
            self._set_l2(key, value, ttl)
        
        if self.enable_l3:
            self._set_l3(key, value, ttl)
    
    def _set_l1(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in L1 (memory) cache"""
        ttl = ttl or self.L1_TTL
        self.memory_cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }
        self.writes["L1"] += 1
    
    def _set_l2(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in L2 (Redis) cache"""
        if not self.redis_client:
            return
        
        ttl = ttl or self.L2_TTL
        try:
            self.redis_client.setex(
                f"ai_cache:{key}",
                ttl,
                pickle.dumps(value)
            )
            self.writes["L2"] += 1
        except Exception as e:
            logger.warning(f"Redis set error: {e}")
    
    def _set_l3(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in L3 (SQLite) cache"""
        ttl = ttl or self.L3_TTL
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(seconds=ttl)
            cursor.execute("""
                INSERT OR REPLACE INTO ai_cache (cache_key, value, created_at, expires_at, hit_count)
                VALUES (?, ?, ?, ?, 0)
            """, (key, json.dumps(value), datetime.now(), expires_at))
            
            conn.commit()
            conn.close()
            self.writes["L3"] += 1
        except Exception as e:
            logger.warning(f"SQLite set error: {e}")
    
    def invalidate(self, key: str):
        """
        Invalidate cache entry across all tiers
        
        Args:
            key: Cache key to invalidate
        """
        # L1
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # L2
        if self.redis_client:
            try:
                self.redis_client.delete(f"ai_cache:{key}")
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        
        # L3
        if self.enable_l3:
            try:
                conn = sqlite3.connect(self.sqlite_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ai_cache WHERE cache_key = ?", (key,))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.warning(f"SQLite delete error: {e}")
    
    def clear_expired(self):
        """Clear expired entries from all cache tiers"""
        # L1
        now = time.time()
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if v["expires_at"] < now
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # L3
        if self.enable_l3:
            try:
                conn = sqlite3.connect(self.sqlite_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ai_cache WHERE expires_at < ?", (datetime.now(),))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.warning(f"SQLite cleanup error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        total_hits = sum(self.hits.values())
        total_requests = total_hits + self.misses
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "writes": self.writes,
            "hit_rate": (total_hits / total_requests * 100) if total_requests > 0 else 0,
            "memory_cache_size": len(self.memory_cache),
            "enabled_tiers": {
                "L1": self.enable_l1,
                "L2": self.enable_l2,
                "L3": self.enable_l3
            }
        }


def cached(cache_manager: CacheManager, ttl: Optional[int] = None):
    """
    Decorator for caching function results
    
    Args:
        cache_manager: CacheManager instance
        ttl: Optional TTL override
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(func.__name__, *args, **kwargs)
            
            # Check cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator