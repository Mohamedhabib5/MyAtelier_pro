from __future__ import annotations

import secrets
import hmac
from fastapi import Request, Response
from app.core.config import get_settings

def get_csrf_token(request: Request) -> str:
    """Retrieves or generates a CSRF token for the current session."""
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token

def verify_csrf_token(request: Request, token: str | None) -> bool:
    """Verifies the provided token against the session token."""
    session_token = request.session.get("csrf_token")
    if not session_token or not token:
        return False
    return hmac.compare_digest(session_token, token)

def set_csrf_cookie(response: Response, token: str):
    """Sets the CSRF token in a cookie for the frontend to read."""
    settings = get_settings()
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=token,
        httponly=False,  # Frontend needs to read this to send it back in a header
        samesite=settings.normalized_session_same_site(),
        secure=settings.effective_session_https_only(),
    )
