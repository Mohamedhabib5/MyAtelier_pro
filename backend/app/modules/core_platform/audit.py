from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.core.request_context import get_audit_request_context
from app.modules.core_platform.models import AuditLog
from app.modules.core_platform.repository import CorePlatformRepository


def record_audit(
    db: Session,
    *,
    actor_user_id: str | None,
    action: str,
    target_type: str,
    target_id: str | None,
    summary: str,
    diff: dict | None = None,
    reason_code: str | None = None,
    reason_text: str | None = None,
    success: bool | None = None,
    error_code: str | None = None,
) -> AuditLog:
    context = get_audit_request_context()
    repo = CorePlatformRepository(db)
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        summary=summary,
        diff_json=json.dumps(diff, ensure_ascii=False) if diff else None,
        request_id=context.request_id if context else None,
        session_id=context.session_id if context else None,
        branch_id=(context.branch_id if context and context.branch_id else None),
        ip_address=context.ip_address if context else None,
        user_agent=context.user_agent if context else None,
        reason_code=reason_code,
        reason_text=reason_text,
        success=success,
        error_code=error_code,
    )
    repo.add_audit_log(entry)
    return entry

