from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.core_platform.models import AuditLog
from .conftest import build_test_client
from .test_foundation import login


def _sample_failure_payload() -> dict:
    return {
        "event": "nightly_full_regression_failed",
        "repository": "example-org/myatelier_pro",
        "ref": "refs/heads/main",
        "run_id": "10001",
        "run_attempt": "1",
        "run_url": "https://github.com/example-org/myatelier_pro/actions/runs/10001",
        "results": {
            "backend_focused_tests": "success",
            "frontend_build": "failure",
            "e2e_smoke": "skipped",
        },
        "failed_at_utc": "2026-04-03T10:30:00Z",
    }


def test_nightly_failure_ingest_requires_valid_token(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "app.db"
    storage_root = tmp_path / "storage"
    env_overrides = {"NIGHTLY_FAILURE_INGEST_TOKEN": "nightly-secret-token-1234"}
    with build_test_client(db_path, storage_root, monkeypatch, env_overrides=env_overrides) as client:
        response_without_token = client.post("/api/settings/ops/nightly/failure-report", json=_sample_failure_payload())
        assert response_without_token.status_code == 403

        response_wrong_token = client.post(
            "/api/settings/ops/nightly/failure-report",
            json=_sample_failure_payload(),
            headers={"X-Nightly-Token": "wrong-token"},
        )
        assert response_wrong_token.status_code == 403


def test_nightly_failure_ingest_and_latest_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "app.db"
    storage_root = tmp_path / "storage"
    env_overrides = {"NIGHTLY_FAILURE_INGEST_TOKEN": "nightly-secret-token-1234"}
    with build_test_client(db_path, storage_root, monkeypatch, env_overrides=env_overrides) as client:
        ingest_response = client.post(
            "/api/settings/ops/nightly/failure-report",
            json=_sample_failure_payload(),
            headers={"X-Nightly-Token": "nightly-secret-token-1234"},
        )
        assert ingest_response.status_code == 200, ingest_response.text
        ingest_payload = ingest_response.json()
        assert ingest_payload["accepted"] is True
        assert ingest_payload["run_id"] == "10001"

        login(client)
        latest_response = client.get("/api/settings/ops/nightly/latest")
        assert latest_response.status_code == 200, latest_response.text
        latest_payload = latest_response.json()
        assert latest_payload["available"] is True
        assert latest_payload["event"] == "nightly_full_regression_failed"
        assert latest_payload["run_id"] == "10001"
        assert latest_payload["results"]["frontend_build"] == "failure"

        _assert_nightly_audit_written(client)


def _assert_nightly_audit_written(client: TestClient) -> None:
    session_factory = client.app.state.session_factory
    with session_factory() as db:
        rows = db.scalars(select(AuditLog).where(AuditLog.action == "ops.nightly_failure_reported")).all()
    assert len(rows) == 1
