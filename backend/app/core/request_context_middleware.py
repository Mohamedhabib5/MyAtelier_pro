from __future__ import annotations

from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.request_context import AuditRequestContext, reset_audit_request_context, set_audit_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-Id", "").strip() or str(uuid4())
        session_id = None
        branch_id = None

        try:
            session_id = request.session.get("session_id")
            branch_id = request.session.get("active_branch_id")
        except Exception:
            session_id = None
            branch_id = None

        if not session_id:
            cookie_name = request.app.state.settings.session_cookie_name
            session_id = request.cookies.get(cookie_name)

        context = AuditRequestContext(
            request_id=request_id,
            session_id=session_id,
            branch_id=branch_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            method=request.method,
            path=request.url.path,
        )
        token = set_audit_request_context(context)
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception:
            reset_audit_request_context(token)
            raise

        reset_audit_request_context(token)
        response.headers.setdefault("X-Request-Id", request_id)
        return response

