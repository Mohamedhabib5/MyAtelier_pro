from __future__ import annotations

from sqlalchemy import select
from fastapi.testclient import TestClient

from app.modules.core_platform.models import AuditLog
from .test_foundation import login


def test_ops_endpoints_require_authentication(app_client: TestClient) -> None:
    metrics_response = app_client.get("/api/settings/ops/metrics")
    assert metrics_response.status_code == 401

    alert_response = app_client.post("/api/settings/ops/alerts/test", json={"message": "x", "dry_run": True})
    assert alert_response.status_code == 401

    check_response = app_client.post("/api/settings/ops/alerts/run-backup-check", json={"dry_run": True})
    assert check_response.status_code == 401


def test_ops_metrics_returns_operational_snapshot(app_client: TestClient) -> None:
    login(app_client)
    app_client.post("/api/settings/backups")

    response = app_client.get("/api/settings/ops/metrics")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["backups_total"] >= 1
    assert payload["backups_last_24h"] >= 1
    assert payload["backup_stale_threshold_hours"] > 0
    assert isinstance(payload["backup_stale"], bool)


def test_ops_alert_test_dry_run_records_audit(app_client: TestClient) -> None:
    login(app_client)

    response = app_client.post(
        "/api/settings/ops/alerts/test",
        json={"severity": "p2", "message": "Manual test alert", "dry_run": True},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["sent"] is False
    assert payload["channel"] == "webhook"
    assert "Dry-run" in payload["detail"]

    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        rows = db.scalars(select(AuditLog).where(AuditLog.action == "ops.alert_test")).all()
    assert len(rows) == 1


def test_backup_stale_check_sends_dry_run_when_no_backups(app_client: TestClient) -> None:
    login(app_client)

    response = app_client.post("/api/settings/ops/alerts/run-backup-check", json={"dry_run": True})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["stale"] is True
    assert payload["sent"] is False
    assert payload["severity"] == "P1"
    assert "Dry-run" in payload["detail"]

    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        rows = db.scalars(
            select(AuditLog).where(
                AuditLog.action == "automation.job_run",
                AuditLog.target_type == "automation_job",
                AuditLog.target_id == "ops.backup_stale_check",
            )
        ).all()
    assert len(rows) == 1


def test_backup_stale_check_skips_alert_when_recent_backup_exists(app_client: TestClient) -> None:
    login(app_client)
    app_client.post("/api/settings/backups")

    response = app_client.post("/api/settings/ops/alerts/run-backup-check", json={"dry_run": False, "force": False})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["stale"] is False
    assert payload["sent"] is False
    assert "No alert needed" in payload["detail"]
