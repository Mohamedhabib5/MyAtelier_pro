from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.core.request_context import get_audit_request_context
from app.modules.core_platform.models import AuditLog
from app.modules.core_platform.repository import CorePlatformRepository
from app.modules.core_platform.security_service import calculate_log_hash


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
    
    last_log = repo.get_latest_audit_log()
    prev_hash = last_log.log_hash if last_log else None
    
    diff_json = json.dumps(diff, ensure_ascii=False) if diff else None
    current_hash = calculate_log_hash(prev_hash, action, target_id, summary, diff_json)
    
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        summary=summary,
        diff_json=diff_json,
        request_id=context.request_id if context else None,
        session_id=context.session_id if context else None,
        branch_id=(context.branch_id if context and context.branch_id else None),
        ip_address=context.ip_address if context else None,
        user_agent=context.user_agent if context else None,
        reason_code=reason_code,
        reason_text=reason_text,
        success=success,
        error_code=error_code,
        previous_log_hash=prev_hash,
        log_hash=current_hash,
    )
    repo.add_audit_log(entry)
    return entry

def verify_chain_integrity(db: Session) -> dict:
    """
    Verifies the integrity of the audit log hash chain.
    Returns a status report.
    """
    repo = CorePlatformRepository(db)
    logs = repo.list_audit_logs_ascending() # Need to ensure this exists or use query
    
    issues = []
    last_hash = None
    count = 0
    
    for log in logs:
        # 1. Verify previous_log_hash matches our last_hash
        if log.previous_log_hash != last_hash:
            issues.append({
                "log_id": log.id,
                "error": "Mismatched previous_log_hash",
                "expected": last_hash,
                "actual": log.previous_log_hash
            })
        
        # 2. Recalculate hash and verify
        recalculated = calculate_log_hash(
            log.previous_log_hash,
            log.action,
            log.target_id,
            log.summary,
            log.diff_json
        )
        
        if log.log_hash != recalculated:
            issues.append({
                "log_id": log.id,
                "error": "Invalid log_hash (recalculation mismatch)",
                "expected": recalculated,
                "actual": log.log_hash
            })
            
        last_hash = log.log_hash
        count += 1
        
    return {
        "success": len(issues) == 0,
        "total_verified": count,
        "issues": issues
    }
