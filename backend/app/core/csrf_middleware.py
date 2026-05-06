from __future__ import annotations

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.config import get_settings
from app.core.csrf import verify_csrf_token, get_csrf_token, set_csrf_cookie

class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Skip CSRF for safe methods
        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            response = await call_next(request)
            # Ensure CSRF token exists in session and set cookie for safe methods
            # so the frontend has it for subsequent unsafe requests.
            if request.url.path.startswith("/api"):
                 token = get_csrf_token(request)
                 set_csrf_cookie(response, token)
            return response

        # 2. Check CSRF for unsafe methods (POST, PUT, DELETE, PATCH)
        # Only check /api routes
        if request.url.path.startswith("/api"):
            # Exempt specific routes if needed (e.g. login is often exempted or handles it differently)
            # But here we use double-submit, so even login can use it if the cookie was set by a prior GET.
            
            csrf_token = request.headers.get(self.settings.csrf_header_name)
            if not verify_csrf_token(request, csrf_token):
                from fastapi import status
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF validation failed"}
                )

        response = await call_next(request)
        return response
