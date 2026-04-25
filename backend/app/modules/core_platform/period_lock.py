from __future__ import annotations

import json
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity.access import ensure_permission
from app.core.exceptions import ValidationAppError
from app.modules.core_platform.audit import record_audit
from app.modules.core_platform.models import AuditLog
from app.modules.core_platform.repository import CorePlatformRepository
from app.modules.identity.models import User

PERIOD_LOCK_SETTING_KEY = "period_lock.settings"


def get_period_lock_state(db: Session) -> dict:
    repo = CorePlatformRepository(db)
    setting = repo.get_setting(PERIOD_LOCK_SETTING_KEY)
    payload = _parse_setting_value(setting.value if setting else None)
    lock_date = _parse_date(payload.get("locked_through"))
    return {
        "locked_through": lock_date,
        "updated_by_user_id": payload.get("updated_by_user_id"),
        "updated_at": setting.updated_at if setting else None,
        "is_locked": lock_date is not None,
    }


def update_period_lock_state(db: Session, *, actor: User, locked_through: date | None, note: str | None = None) -> dict:
    previous = get_period_lock_state(db)
    payload = {
        "locked_through": locked_through.isoformat() if locked_through else None,
        "updated_by_user_id": actor.id,
    }
    repo = CorePlatformRepository(db)
    repo.set_setting(PERIOD_LOCK_SETTING_KEY, json.dumps(payload, ensure_ascii=False))
    record_audit(
        db,
        actor_user_id=actor.id,
        action="period_lock.updated",
        target_type="period_lock",
        target_id="global",
        summary="Updated period lock settings",
        diff={
            "before_locked_through": previous["locked_through"].isoformat() if previous["locked_through"] else None,
            "after_locked_through": payload["locked_through"],
            "note": note,
        },
    )
    db.commit()
    return get_period_lock_state(db)


def enforce_not_locked(db: Session, *, action_date: date, action_key: str) -> None:
    state = get_period_lock_state(db)
    locked_through = state["locked_through"]
    if locked_through is None:
        return
    if action_date <= locked_through:
        raise ValidationAppError(
            f"Cannot run '{action_key}' on {action_date.isoformat()}: period is locked through {locked_through.isoformat()}."
        )


def enforce_not_locked_with_override(
    db: Session,
    *,
    action_date: date,
    action_key: str,
    actor: User,
    override_lock: bool = False,
    override_reason: str | None = None,
) -> dict | None:
    state = get_period_lock_state(db)
    locked_through = state["locked_through"]
    if locked_through is None or action_date > locked_through:
        return None
    if not override_lock:
        raise ValidationAppError(
            f"Cannot run '{action_key}' on {action_date.isoformat()}: period is locked through {locked_through.isoformat()}."
        )
    ensure_permission(actor, "period_lock.manage")
    normalized_reason = (override_reason or "").strip()
    if len(normalized_reason) < 5:
        raise ValidationAppError("Override reason is required and must be at least 5 characters.")
    return {
        "action_key": action_key,
        "action_date": action_date.isoformat(),
        "locked_through": locked_through.isoformat(),
        "override_reason": normalized_reason,
    }


def record_period_lock_override(
    db: Session,
    *,
    actor_user_id: str,
    entity_type: str,
    entity_id: str | None,
    summary: str,
    override_payload: dict,
) -> None:
    record_audit(
        db,
        actor_user_id=actor_user_id,
        action="period_lock.override_used",
        target_type=entity_type,
        target_id=entity_id,
        summary=summary,
        reason_code="period_lock_override",
        reason_text=override_payload["override_reason"],
        diff=override_payload,
        success=True,
    )


def list_period_lock_exceptions(db: Session, *, limit: int = 100) -> list[dict]:
    rows = db.scalars(
        select(AuditLog)
        .where(AuditLog.action == "period_lock.override_used")
        .order_by(AuditLog.occurred_at.desc())
        .limit(limit)
    ).all()
    payload: list[dict] = []
    for row in rows:
        diff = _parse_setting_value(row.diff_json)
        payload.append(
            {
                "audit_id": row.id,
                "occurred_at": row.occurred_at,
                "actor_user_id": row.actor_user_id,
                "actor_name": row.actor.full_name if row.actor else None,
                "target_type": row.target_type,
                "target_id": row.target_id,
                "action_key": diff.get("action_key"),
                "action_date": diff.get("action_date"),
                "locked_through": diff.get("locked_through"),
                "override_reason": diff.get("override_reason"),
            }
        )
    return payload


def _parse_setting_value(raw_value: str | None) -> dict:
    if not raw_value:
        return {}
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _parse_date(raw_value: str | None) -> date | None:
    if not raw_value:
        return None
    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        return None
