from __future__ import annotations

import hashlib
import base64
from typing import Any
from cryptography.fernet import Fernet
from app.core.config import get_settings

def _get_fernet() -> Fernet:
    settings = get_settings()
    # Ensure key is 32 bytes and base64 encoded
    key = hashlib.sha256(settings.app_secret_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))

def encrypt_secret(plain_text: str) -> str:
    if not plain_text:
        return ""
    f = _get_fernet()
    return f.encrypt(plain_text.encode()).decode()

def decrypt_secret(encrypted_text: str) -> str:
    if not encrypted_text:
        return ""
    f = _get_fernet()
    return f.decrypt(encrypted_text.encode()).decode()

def calculate_log_hash(prev_hash: str | None, action: str, target_id: str | None, summary: str, diff_json: str | None) -> str:
    """Calculates a SHA-256 hash for an audit log entry, chaining it to the previous one."""
    content = f"{prev_hash or 'ROOT'}|{action}|{target_id or ''}|{summary}|{diff_json or ''}"
    return hashlib.sha256(content.encode()).hexdigest()

class SecurityNotificationService:
    @staticmethod
    def notify_security_event(event_type: str, details: dict[str, Any]):
        # TODO: Integration with real notification channels (Email, Webhook, etc.)
        # For Phase 1, we log it to stderr for immediate visibility in Docker logs
        import sys
        print(f" SECURITY_ALERT [{event_type}]: {details}", file=sys.stderr)
