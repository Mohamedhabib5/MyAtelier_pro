from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass


@dataclass(slots=True)
class AuditRequestContext:
    request_id: str
    session_id: str | None
    branch_id: str | None
    ip_address: str | None
    user_agent: str | None
    method: str
    path: str


_audit_request_context: ContextVar[AuditRequestContext | None] = ContextVar("audit_request_context", default=None)


def set_audit_request_context(context: AuditRequestContext) -> Token:
    return _audit_request_context.set(context)


def reset_audit_request_context(token: Token) -> None:
    _audit_request_context.reset(token)


def get_audit_request_context() -> AuditRequestContext | None:
    return _audit_request_context.get()

