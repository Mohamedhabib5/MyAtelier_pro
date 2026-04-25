from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.modules.core_platform.repository import CorePlatformRepository

DESTRUCTIVE_ACTION_KEYS = (
    "destructive.deleted",
    "payment_document.voided",
    "booking.line_revenue_reversed",
    "period_lock.override_used",
)
NIGHTLY_OPS_ACTION_KEYS = (
    "ops.nightly_failure_reported",
    "automation.job_run",
    "audit.nightly_ops_exported",
)


def list_audit_events(
    db: Session,
    *,
    actor_user_id: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    branch_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    parsed_from = _parse_datetime(date_from, is_end=False)
    parsed_to = _parse_datetime(date_to, is_end=True)
    rows, total = CorePlatformRepository(db).list_audit_events_page(
        actions=None,
        actor_user_id=_clean(actor_user_id),
        action=_clean(action),
        target_type=_clean(target_type),
        target_id=_clean(target_id),
        branch_id=_clean(branch_id),
        date_from=parsed_from,
        date_to=parsed_to,
        search=_clean(search),
        page=page,
        page_size=page_size,
    )
    return {
        "items": [
            {
                "id": row.id,
                "occurred_at": row.occurred_at,
                "actor_user_id": row.actor_user_id,
                "actor_name": row.actor.full_name if row.actor else None,
                "action": row.action,
                "target_type": row.target_type,
                "target_id": row.target_id,
                "branch_id": row.branch_id,
                "summary": row.summary,
                "reason_code": row.reason_code,
                "reason_text": row.reason_text,
                "success": row.success,
                "error_code": row.error_code,
                "diff": _parse_diff(row.diff_json),
            }
            for row in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def list_destructive_actions(
    db: Session,
    *,
    actor_user_id: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    branch_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    parsed_from = _parse_datetime(date_from, is_end=False)
    parsed_to = _parse_datetime(date_to, is_end=True)
    rows, total = CorePlatformRepository(db).list_audit_events_page(
        actions=DESTRUCTIVE_ACTION_KEYS,
        actor_user_id=_clean(actor_user_id),
        action=None,
        target_type=_clean(target_type),
        target_id=_clean(target_id),
        branch_id=_clean(branch_id),
        date_from=parsed_from,
        date_to=parsed_to,
        search=_clean(search),
        page=page,
        page_size=page_size,
    )
    return {
        "items": [
            {
                "id": row.id,
                "occurred_at": row.occurred_at,
                "actor_user_id": row.actor_user_id,
                "actor_name": row.actor.full_name if row.actor else None,
                "action": row.action,
                "target_type": row.target_type,
                "target_id": row.target_id,
                "branch_id": row.branch_id,
                "summary": row.summary,
                "reason_code": row.reason_code,
                "reason_text": row.reason_text,
                "success": row.success,
                "error_code": row.error_code,
                "diff": _parse_diff(row.diff_json),
            }
            for row in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def list_nightly_ops_events(
    db: Session,
    *,
    actor_user_id: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    branch_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    parsed_from = _parse_datetime(date_from, is_end=False)
    parsed_to = _parse_datetime(date_to, is_end=True)
    rows, total = CorePlatformRepository(db).list_audit_events_page(
        actions=NIGHTLY_OPS_ACTION_KEYS,
        actor_user_id=_clean(actor_user_id),
        action=None,
        target_type=_clean(target_type),
        target_id=_clean(target_id),
        branch_id=_clean(branch_id),
        date_from=parsed_from,
        date_to=parsed_to,
        search=_clean(search),
        page=page,
        page_size=page_size,
    )
    return {
        "items": [
            {
                "id": row.id,
                "occurred_at": row.occurred_at,
                "actor_user_id": row.actor_user_id,
                "actor_name": row.actor.full_name if row.actor else None,
                "action": row.action,
                "target_type": row.target_type,
                "target_id": row.target_id,
                "branch_id": row.branch_id,
                "summary": row.summary,
                "reason_code": row.reason_code,
                "reason_text": row.reason_text,
                "success": row.success,
                "error_code": row.error_code,
                "diff": _parse_diff(row.diff_json),
            }
            for row in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _parse_datetime(value: str | None, *, is_end: bool) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    if len(raw) == 10:
        suffix = "T23:59:59.999999+00:00" if is_end else "T00:00:00+00:00"
        return datetime.fromisoformat(f"{raw}{suffix}")
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _parse_diff(raw_value: str | None) -> dict:
    if not raw_value:
        return {}
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}
