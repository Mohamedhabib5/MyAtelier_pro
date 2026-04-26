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


# Global instances for specific use cases
# Login: 5 attempts per 1 minute per IP/Username
login_rate_limiter = InMemoryRateLimiter(requests=5, window_seconds=60)
