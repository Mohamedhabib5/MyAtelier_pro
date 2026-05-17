from __future__ import annotations

import redis
from app.core.config import get_settings

settings = get_settings()

# Initialize a shared redis client
# Note: decode_responses=True makes it easier to work with strings
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

def get_redis_client() -> redis.Redis:
    return redis_client
