from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.modules.core_platform.audit import record_audit

AUTOMATION_JOB_ACTION = "automation.job_run"
AUTOMATION_TARGET_TYPE = "automation_job"


def normalize_trigger_source(value: str | None) -> str:
    return "automation" if value == "automation" else "manual"


def record_automation_job_run(
    db: Session,
    *,
    actor_user_id: str | None,
    job_key: str,
    summary: str,
    trigger_source: str | None,
    success: bool,
    diff: Mapping[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "job_key": job_key,
        "trigger_source": normalize_trigger_source(trigger_source),
    }
    if diff:
        payload.update(diff)

    record_audit(
        db,
        actor_user_id=actor_user_id,
        action=AUTOMATION_JOB_ACTION,
        target_type=AUTOMATION_TARGET_TYPE,
        target_id=job_key,
        summary=summary,
        success=success,
        diff=payload,
    )
