from __future__ import annotations

import base64
import hashlib
import hmac
import os
from base64 import b64decode, b64encode
from typing import Any

from cryptography.fernet import Fernet

PBKDF2_ALGO = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260_000
DEFAULT_ADMIN_SEEDED_KEY = "auth.default_admin_seeded"


def norm_text(value: str | None) -> str:
    return (value or "").strip()


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{PBKDF2_ALGO}${PBKDF2_ITERATIONS}${b64encode(salt).decode()}${b64encode(digest).decode()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != PBKDF2_ALGO:
        return False
    salt = b64decode(salt_b64.encode())
    expected_digest = b64decode(digest_b64.encode())
    actual_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
    return hmac.compare_digest(actual_digest, expected_digest)


def role_list_contains(role_names: list[str], role_name: str) -> bool:
    normalized = {item.strip().lower() for item in role_names}
    return role_name.strip().lower() in normalized


def _get_fernet() -> Any:
    from app.core.config import get_settings
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
        import sys
        print(f" SECURITY_ALERT [{event_type}]: {details}", file=sys.stderr)