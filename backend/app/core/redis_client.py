from __future__ import annotations

import redis
from app.core.config import get_settings

settings = get_settings()

# H5: use effective_redis_url which resolves password correctly
redis_client = redis.from_url(settings.effective_redis_url(), decode_responses=True)

def get_redis_client() -> redis.Redis:
    return redis_client

def ping_redis() -> bool:
    """H5: Health check for Redis - used on startup and factory initialization."""
    try:
        redis_client.ping()
        return True
    except Exception:
        return False
