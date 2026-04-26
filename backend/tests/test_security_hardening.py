import time
import pytest
from app.core.rate_limiter import InMemoryRateLimiter
from app.core.exceptions import RateLimitError


def test_rate_limiter_allows_requests():
    limiter = InMemoryRateLimiter(requests=3, window_seconds=1)
    key = "test_user"
    
    assert limiter.is_allowed(key) is True
    assert limiter.is_allowed(key) is True
    assert limiter.is_allowed(key) is True
    assert limiter.is_allowed(key) is False


def test_rate_limiter_resets_after_window():
    limiter = InMemoryRateLimiter(requests=1, window_seconds=1)
    key = "test_user"
    
    assert limiter.is_allowed(key) is True
    assert limiter.is_allowed(key) is False
    
    time.sleep(1.1)
    assert limiter.is_allowed(key) is True


def test_rate_limiter_is_thread_safe():
    import threading
    
    limiter = InMemoryRateLimiter(requests=100, window_seconds=60)
    key = "test_user"
    
    def worker():
        for _ in range(10):
            limiter.is_allowed(key)
            
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert len(limiter.history[key]) == 100
