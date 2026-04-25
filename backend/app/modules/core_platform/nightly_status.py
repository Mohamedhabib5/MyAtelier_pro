from __future__ import annotations

import json
from datetime import UTC, datetime
from hmac import compare_digest

from sqlalchemy.orm import Session

from app.modules.core_platform.audit import record_audit
from app.modules.core_platform.repository import CorePlatformRepository
from app.modules.core_platform.schemas import NightlyFailureReportRequest

NIGHTLY_FAILURE_ACTION = "ops.nightly_failure_reported"
NIGHTLY_FAILURE_SETTING_KEY = "ops.nightly.latest_failure"


def is_valid_nightly_ingest_token(*, expected_token: str, provided_token: str | None) -> bool:
    expected = expected_token.strip()
    if not expected:
        return False
    candidate = (provided_token or "").strip()
    if not candidate:
        return False
    return compare_digest(expected, candidate)


def ingest_nightly_failure_report(
    db: Session,
    *,
    payload: NightlyFailureReportRequest,
    source_ip: str | None,
    user_agent: str | None,
) -> dict:
    now = datetime.now(UTC)
    body = {
        "event": payload.event,
        "repository": payload.repository,
        "ref": payload.ref,
        "run_id": payload.run_id,
        "run_attempt": payload.run_attempt,
        "run_url": payload.run_url,
        "results": payload.results,
        "failed_at_utc": payload.failed_at_utc,
        "reported_at": now.isoformat(),
    }
    repo = CorePlatformRepository(db)
    repo.set_setting(NIGHTLY_FAILURE_SETTING_KEY, json.dumps(body, ensure_ascii=False))
    record_audit(
        db,
        actor_user_id=None,
        action=NIGHTLY_FAILURE_ACTION,
        target_type="automation_job",
        target_id="nightly_full_regression",
        summary=f"Received nightly failure report for run {payload.run_id}",
        diff={
            "source": "nightly_webhook",
            "run_id": payload.run_id,
            "run_attempt": payload.run_attempt,
            "results": payload.results,
            "failed_at_utc": payload.failed_at_utc,
            "ip_address": source_ip,
            "user_agent": user_agent,
        },
    )
    db.commit()
    return {"accepted": True, "run_id": payload.run_id, "stored_at": now}


def get_latest_nightly_snapshot(db: Session) -> dict:
    setting = CorePlatformRepository(db).get_setting(NIGHTLY_FAILURE_SETTING_KEY)
    if setting is None or not setting.value.strip():
        return _empty_snapshot()
    try:
        payload = json.loads(setting.value)
    except json.JSONDecodeError:
        return _empty_snapshot()
    if not isinstance(payload, dict):
        return _empty_snapshot()
    results = payload.get("results")
    return {
        "available": True,
        "event": _safe_str(payload.get("event")),
        "repository": _safe_str(payload.get("repository")),
        "ref": _safe_str(payload.get("ref")),
        "run_id": _safe_str(payload.get("run_id")),
        "run_attempt": _safe_str(payload.get("run_attempt")),
        "run_url": _safe_str(payload.get("run_url")),
        "failed_at_utc": _safe_str(payload.get("failed_at_utc")),
        "results": results if isinstance(results, dict) else {},
        "reported_at": _parse_datetime(payload.get("reported_at")),
    }


def _empty_snapshot() -> dict:
    return {
        "available": False,
        "event": None,
        "repository": None,
        "ref": None,
        "run_id": None,
        "run_attempt": None,
        "run_url": None,
        "failed_at_utc": None,
        "results": {},
        "reported_at": None,
    }


def _safe_str(value: object) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return None


def _parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed
