from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.core_platform.models import AuditLog
from .test_foundation import login


def _latest_audit(app_client: TestClient, action: str) -> AuditLog | None:
    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        return db.scalars(select(AuditLog).where(AuditLog.action == action).order_by(AuditLog.occurred_at.desc())).first()


def test_login_success_is_audited_with_request_context(app_client: TestClient) -> None:
    response = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200

    row = _latest_audit(app_client, "auth.login_success")
    assert row is not None
    assert row.target_type == "user"
    assert row.target_id is not None
    assert row.request_id == response.headers.get("x-request-id")
    assert row.success is True
    assert row.ip_address is not None


def test_login_failure_is_audited(app_client: TestClient) -> None:
    response = app_client.post("/api/auth/login", json={"username": "admin", "password": "wrong-password"})
    assert response.status_code == 401

    row = _latest_audit(app_client, "auth.login_failed")
    assert row is not None
    assert row.target_type == "auth_session"
    assert row.success is False
    assert row.error_code == "invalid_credentials"
    payload = json.loads(row.diff_json or "{}")
    assert payload.get("username") == "admin"


def test_logout_is_audited(app_client: TestClient) -> None:
    login(app_client)
    response = app_client.post("/api/auth/logout")
    assert response.status_code == 204

    row = _latest_audit(app_client, "auth.logout")
    assert row is not None
    assert row.target_type == "user"
    assert row.target_id is not None
    assert row.success is True


def test_session_language_change_is_audited(app_client: TestClient) -> None:
    login(app_client)
    response = app_client.post("/api/auth/language", json={"language": "en"})
    assert response.status_code == 200, response.text

    row = _latest_audit(app_client, "auth.session_language_changed")
    assert row is not None
    assert row.target_type == "user"
    assert row.success is True
    payload = json.loads(row.diff_json or "{}")
    assert payload.get("next_language") == "en"
    assert row.request_id == response.headers.get("x-request-id")


def test_permission_denied_is_audited(app_client: TestClient) -> None:
    login(app_client)
    regular_user = app_client.post(
        "/api/users",
        json={
            "username": "audit.regular",
            "full_name": "Audit Regular",
            "password": "secret123",
            "role_names": ["user"],
        },
    ).json()
    second_user = app_client.post(
        "/api/users",
        json={
            "username": "audit.second",
            "full_name": "Audit Second",
            "password": "secret123",
            "role_names": ["user"],
        },
    ).json()

    app_client.post("/api/auth/logout")
    login(app_client, username=regular_user["username"], password="secret123")
    forbidden = app_client.patch(f"/api/users/{second_user['id']}", json={"full_name": "Tampered"})
    assert forbidden.status_code == 403

    row = _latest_audit(app_client, "auth.permission_denied")
    assert row is not None
    assert row.target_type == "route"
    assert row.target_id == f"/api/users/{second_user['id']}"
    assert row.success is False
