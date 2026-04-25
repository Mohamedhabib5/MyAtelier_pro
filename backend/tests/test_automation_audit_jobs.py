from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.core_platform.models import AuditLog
from .test_foundation import login


def _latest_job_audit(app_client: TestClient, *, job_key: str) -> AuditLog | None:
    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        statement = (
            select(AuditLog)
            .where(
                AuditLog.action == "automation.job_run",
                AuditLog.target_type == "automation_job",
                AuditLog.target_id == job_key,
            )
            .order_by(AuditLog.occurred_at.desc())
        )
        return db.scalars(statement).first()


def test_run_due_export_schedules_records_standardized_automation_audit(app_client: TestClient) -> None:
    login(app_client)
    created = app_client.post(
        "/api/exports/schedules",
        json={"name": "Automation Due", "export_type": "customers_csv", "cadence": "daily", "start_on": "2020-01-01"},
    )
    assert created.status_code == 200, created.text

    response = app_client.post(
        "/api/exports/schedules/run-due",
        json={"dry_run": True, "limit": 20, "trigger_source": "automation"},
    )
    assert response.status_code == 200, response.text
    row = _latest_job_audit(app_client, job_key="exports.run_due_schedules")
    assert row is not None
    assert row.request_id == response.headers.get("x-request-id")
    assert row.success is True
    payload = json.loads(row.diff_json or "{}")
    assert payload.get("trigger_source") == "automation"
    assert payload.get("job_key") == "exports.run_due_schedules"
    assert payload.get("dry_run") is True


def test_backup_stale_check_records_standardized_automation_audit(app_client: TestClient) -> None:
    login(app_client)
    response = app_client.post(
        "/api/settings/ops/alerts/run-backup-check",
        json={"dry_run": True, "trigger_source": "automation"},
    )
    assert response.status_code == 200, response.text

    row = _latest_job_audit(app_client, job_key="ops.backup_stale_check")
    assert row is not None
    assert row.request_id == response.headers.get("x-request-id")
    assert row.success is True
    payload = json.loads(row.diff_json or "{}")
    assert payload.get("trigger_source") == "automation"
    assert payload.get("job_key") == "ops.backup_stale_check"
    assert payload.get("dry_run") is True
