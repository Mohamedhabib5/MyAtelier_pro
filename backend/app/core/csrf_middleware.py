from __future__ import annotations

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.core.config import get_settings
from app.core.csrf import get_csrf_token, set_csrf_cookie, verify_csrf_token


SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip CSRF entirely for non-API routes
        if not request.url.path.startswith("/api"):
            return await call_next(request)

        # Safe methods: ensure token exists in session and refresh cookie
        if request.method in SAFE_METHODS:
            response = await call_next(request)
            token = get_csrf_token(request)
            set_csrf_cookie(response, token)
            return response

        # Unsafe methods (POST/PUT/PATCH/DELETE): MUST verify CSRF token
        # Bypass in testing environment ONLY (controlled by settings, never env var)
        if get_settings().security_bypass_for_tests:
            return await call_next(request)

        token = request.headers.get(self.settings.csrf_header_name)
        if not verify_csrf_token(request, token):
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or missing CSRF token"},
            )

        response = await call_next(request)
        # Refresh the cookie on every unsafe request too, in case the
        # session was regenerated.
        current_token = get_csrf_token(request)
        set_csrf_cookie(response, current_token)
        return response
