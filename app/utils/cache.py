"""
This file handles caching - storing responses so we don't have to process the same request twice.
If someone asks the same question, we return the cached answer instantly 
instead of re-processing it.
"""

"""
Caching Module
Simple caching for query results
"""

from typing import Optional, Any
from app.config import settings
from app.utils.logger import get_logger
import hashlib
import json

logger = get_logger(__name__)


class SimpleCache:
    """Simple in-memory cache for responses"""
    
    def __init__(self):
        """Initialize cache"""
        self.cache = {}
        logger.info("Simple cache initialized")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set item in cache"""
        self.cache[key] = value
        logger.debug(f"Cached key: {key}")
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def generate_key(self, query: str, context: str = "") -> str:
        """Generate cache key from query"""
        combined = f"{query}:{context}"
        return hashlib.md5(combined.encode()).hexdigest()


class RedisCache:
    """Redis-based cache for distributed scenarios"""
    
    def __init__(self, redis_url: str = settings.REDIS_URL):
        """
        Initialize Redis cache
        
        Args:
            redis_url: Redis connection URL
        """
        try:
            import redis
            self.redis_client = redis.from_url(redis_url)
            logger.info(f"Redis cache initialized: {redis_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {str(e)}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from Redis cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
        except Exception as e:
            logger.error(f"Failed to get from Redis: {str(e)}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set item in Redis cache"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(value))
                logger.debug(f"Cached in Redis: {key}")
        except Exception as e:
            logger.error(f"Failed to set in Redis: {str(e)}")
    
    def clear(self) -> None:
        """Clear Redis cache"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
                logger.info("Redis cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear Redis: {str(e)}")
    
    def generate_key(self, query: str, context: str = "") -> str:
        """Generate cache key"""
        combined = f"{query}:{context}"
        return hashlib.md5(combined.encode()).hexdigest()


# Initialize cache based on settings
if settings.USE_REDIS:
    cache = RedisCache()
else:
    cache = SimpleCache()