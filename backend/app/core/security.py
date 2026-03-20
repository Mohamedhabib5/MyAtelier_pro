from __future__ import annotations

import hashlib
import hmac
import os
from base64 import b64decode, b64encode

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