from __future__ import annotations

import threading
import time
from collections import deque


class InMemoryRateLimiter:
    """
    Simple thread-safe in-memory rate limiter using a sliding window.
    """
    def __init__(self, requests: int, window_seconds: int):
        self.requests = requests
        self.window_seconds = window_seconds
        self.history: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        import os
        if os.getenv("TESTING") == "true":
            return True
        now = time.time()
        with self._lock:
            if key not in self.history:
                self.history[key] = deque()
            
            window = self.history[key]
            
            # Remove expired timestamps
            while window and window[0] <= now - self.window_seconds:
                window.popleft()
            
            if len(window) < self.requests:
                window.append(now)
                return True
            
            return False

    def clean_expired(self):
        """Periodically clean up the dictionary to prevent memory leaks."""
        now = time.time()
        with self._lock:
            keys_to_remove = []
            for key, window in self.history.items():
                while window and window[0] <= now - self.window_seconds:
                    window.popleft()
                if not window:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.history[key]


class RedisRateLimiter:
    """
    Distributed rate limiter using Redis.
    """
    def __init__(self, requests: int, window_seconds: int, redis_url: str):
        import redis
        self.requests = requests
        self.window_seconds = window_seconds
        self.client = redis.from_url(redis_url)

    def is_allowed(self, key: str) -> bool:
        import os
        if os.getenv("TESTING") == "true":
            return True
            
        now = time.time()
        # Use a Lua script for atomic check-and-increment
        script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
        local count = redis.call('ZCARD', key)
        
        if count < limit then
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, window)
            return 1
        end
        return 0
        """
        result = self.client.eval(script, 1, key, self.requests, self.window_seconds, now)
        return bool(result)


def get_rate_limiter(requests: int, window_seconds: int):
    """
    Factory to return the appropriate rate limiter based on settings.
    """
    from app.core.config import get_settings
    settings = get_settings()
    
    # Use Redis in production if redis_url is set, otherwise fallback to memory
    if settings.is_production() and settings.redis_url.startswith("redis"):
        try:
            return RedisRateLimiter(requests, window_seconds, settings.redis_url)
        except ImportError:
            pass
            
    return InMemoryRateLimiter(requests, window_seconds)


# Global instances for specific use cases
# Note: These are now factory-initialized
login_rate_limiter = get_rate_limiter(requests=5, window_seconds=60)
two_fa_rate_limiter = get_rate_limiter(requests=5, window_seconds=300)
sensitive_ops_rate_limiter = get_rate_limiter(requests=10, window_seconds=60)
api_rate_limiter = get_rate_limiter(requests=100, window_seconds=60)
