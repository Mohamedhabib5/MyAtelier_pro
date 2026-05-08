from __future__ import annotations

import time
import uuid
import threading
from typing import Dict, Optional, Any

class DownloadTicketStore:
    """
    Simple thread-safe in-memory store for short-lived download tickets.
    """
    def __init__(self, expires_in_seconds: int = 60):
        self._tickets: Dict[str, Dict[str, Any]] = {}
        self._expires_in = expires_in_seconds
        self._lock = threading.Lock()

    def create_ticket(self, user_id: str, path: str, params: Dict[str, Any]) -> str:
        ticket_id = str(uuid.uuid4())
        with self._lock:
            self._tickets[ticket_id] = {
                "user_id": user_id,
                "path": path,
                "params": params,
                "expires_at": time.time() + self._expires_in
            }
        return ticket_id

    def consume_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            ticket = self._tickets.pop(ticket_id, None)
            if not ticket:
                return None
            if time.time() > ticket["expires_at"]:
                return None
            return ticket

    def cleanup(self) -> None:
        """Manual cleanup to prevent memory leaks in case tickets are not consumed."""
        now = time.time()
        with self._lock:
            expired = [tid for tid, t in self._tickets.items() if t["expires_at"] < now]
            for tid in expired:
                self._tickets.pop(tid, None)

# Singleton instance
ticket_store = DownloadTicketStore()
