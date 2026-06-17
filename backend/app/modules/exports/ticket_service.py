from __future__ import annotations

import json
import time
import uuid
from typing import Dict, Optional, Any

from app.core.redis_client import redis_client
from app.core.config import get_settings


class DownloadTicketStore:
    """
    Redis-backed store for short-lived download tickets.
    
    Tickets are atomic, single-use, and expire automatically (no cleanup needed).
    Works correctly with multiple uvicorn workers because Redis is shared state.
    
    Fallback to in-memory is allowed only in non-production environments
    (for tests that don't have Redis available).
    """

    def __init__(self, expires_in_seconds: int = 60):
        self._expires_in = expires_in_seconds
        self._fallback_store: dict[str, dict[str, Any]] = {}
        self._settings = get_settings()

    def _use_redis(self) -> bool:
        # In production: Redis is mandatory. In dev/test: fallback is allowed.
        return self._settings.is_production() or self._can_connect_redis()

    def _can_connect_redis(self) -> bool:
        try:
            redis_client.ping()
            return True
        except Exception:
            return False

    def create_ticket(self, user_id: str, path: str, params: dict[str, Any]) -> str:
        ticket_id = str(uuid.uuid4())
        ticket_data = {
            "user_id": str(user_id),
            "path": path,
            "params": params,
            "created_at": time.time(),
        }
        if self._use_redis():
            redis_client.setex(
                f"download_ticket:{ticket_id}",
                self._expires_in,
                json.dumps(ticket_data),
            )
        else:
            self._fallback_store[ticket_id] = {
                **ticket_data,
                "expires_at": time.time() + self._expires_in,
            }
        return ticket_id

    def consume_ticket(self, ticket_id: str) -> Optional[dict[str, Any]]:
        """Atomic consume: returns ticket data and deletes it in one operation."""
        if self._use_redis():
            # Lua script for atomic get-and-delete
            lua_script = """
            local key = KEYS[1]
            local value = redis.call('GET', key)
            if value then
                redis.call('DEL', key)
                return value
            end
            return nil
            """
            result = redis_client.eval(lua_script, 1, f"download_ticket:{ticket_id}")
            if result is None:
                return None
            if isinstance(result, bytes):
                result = result.decode("utf-8")
            return json.loads(result)
        else:
            # Fallback in-memory
            ticket = self._fallback_store.pop(ticket_id, None)
            if not ticket:
                return None
            if time.time() > ticket.get("expires_at", 0):
                return None
            return {k: v for k, v in ticket.items() if k != "expires_at"}

    def cleanup(self) -> None:
        """No-op for Redis (TTL handles expiry). For in-memory, remove expired."""
        if not self._use_redis():
            now = time.time()
            expired = [tid for tid, t in self._fallback_store.items()
                       if t.get("expires_at", 0) < now]
            for tid in expired:
                self._fallback_store.pop(tid, None)


# Singleton instance
ticket_store = DownloadTicketStore()
