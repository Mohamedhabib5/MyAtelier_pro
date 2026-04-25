from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.core_platform.models import AuditLog, BackupRecord
from .conftest import build_test_client
from .test_foundation import login


def test_protected_routes_require_authentication(app_client: TestClient) -> None:
    routes = [
        "/api/users",
        "/api/users/me",
        "/api/settings/company",
        "/api/settings/backups",
        "/api/payment-methods",
    ]
    for route in routes:
        response = app_client.get(route)
        assert response.status_code == 401, route


def test_regular_user_cannot_update_other_user(app_client: TestClient) -> None:
    login(app_client)
    regular_user = app_client.post(
        "/api/users",
        json={
            "username": "regular.user",
            "full_name": "Regular User",
            "password": "secret123",
            "role_names": ["user"],
        },
    ).json()
    second_user = app_client.post(
        "/api/users",
        json={
            "username": "second.user",
            "full_name": "Second User",
            "password": "secret123",
            "role_names": ["user"],
        },
    ).json()

    app_client.post("/api/auth/logout")
    login(app_client, username=regular_user["username"], password="secret123")

    response = app_client.patch(
        f"/api/users/{second_user['id']}",
        json={"full_name": "Tampered User"},
    )
    assert response.status_code == 403


def test_backup_download_requires_authenticated_session(app_client: TestClient) -> None:
    login(app_client)
    backup_response = app_client.post("/api/settings/backups")
    assert backup_response.status_code == 200
    backup = backup_response.json()

    app_client.post("/api/auth/logout")
    download_response = app_client.get(f"/api/settings/backups/{backup['id']}/download")
    assert download_response.status_code == 401


def test_backup_download_records_audit_log(app_client: TestClient) -> None:
    login(app_client)
    backup = app_client.post("/api/settings/backups").json()

    download_response = app_client.get(f"/api/settings/backups/{backup['id']}/download")
    assert download_response.status_code == 200

    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        audit_rows = db.scalars(
            select(AuditLog).where(
                AuditLog.action == "backup.downloaded",
                AuditLog.target_id == backup["id"],
            )
        ).all()
    assert len(audit_rows) == 1


def test_backup_download_rejects_files_outside_backup_directory(app_client: TestClient) -> None:
    login(app_client)
    backup = app_client.post("/api/settings/backups").json()
    settings_obj = app_client.app.state.settings
    outside_file = Path(settings_obj.storage_root) / "outside.zip"
    outside_file.write_bytes(b"outside backup directory")

    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        record = db.get(BackupRecord, backup["id"])
        assert record is not None
        record.file_path = str(outside_file)
        db.commit()

    response = app_client.get(f"/api/settings/backups/{backup['id']}/download")
    assert response.status_code == 404


def test_production_login_cookie_is_secure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "secure-cookie.db"
    storage_root = tmp_path / "storage"
    env_overrides = {
        "APP_ENV": "production",
        "APP_DEBUG": "false",
        "APP_SECRET_KEY": "super-secure-production-secret-key-12345",
        "DEFAULT_ADMIN_PASSWORD": "secure-admin-password-123",
        "APP_FRONTEND_ORIGINS": "https://atelier.example.com",
        "ALLOWED_HOSTS": "api.atelier.example.com,testserver",
        "SESSION_HTTPS_ONLY": "true",
    }

    with build_test_client(db_path, storage_root, monkeypatch, env_overrides=env_overrides) as client:
        response = client.post("/api/auth/login", json={"username": "admin", "password": "secure-admin-password-123"})
        assert response.status_code == 200
        set_cookie_header = response.headers["set-cookie"].lower()
        assert "httponly" in set_cookie_header
        assert "secure" in set_cookie_header
        assert "samesite=lax" in set_cookie_header


def test_production_rejects_default_secret_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "prod-default-secret.db"
    storage_root = tmp_path / "storage"
    env_overrides = {
        "APP_ENV": "production",
        "APP_DEBUG": "false",
        "APP_SECRET_KEY": "change-me",
        "DEFAULT_ADMIN_PASSWORD": "secure-admin-password-123",
        "APP_FRONTEND_ORIGINS": "https://atelier.example.com",
        "ALLOWED_HOSTS": "api.atelier.example.com",
        "SESSION_HTTPS_ONLY": "true",
    }

    with pytest.raises(ValueError, match="APP_SECRET_KEY"):
        with build_test_client(db_path, storage_root, monkeypatch, env_overrides=env_overrides):
            pass


def test_production_rejects_localhost_cors_origin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "prod-localhost-origin.db"
    storage_root = tmp_path / "storage"
    env_overrides = {
        "APP_ENV": "production",
        "APP_DEBUG": "false",
        "APP_SECRET_KEY": "super-secure-production-secret-key-12345",
        "DEFAULT_ADMIN_PASSWORD": "secure-admin-password-123",
        "APP_FRONTEND_ORIGINS": "http://localhost:5173",
        "ALLOWED_HOSTS": "api.atelier.example.com",
        "SESSION_HTTPS_ONLY": "true",
    }

    with pytest.raises(ValueError, match="APP_FRONTEND_ORIGINS"):
        with build_test_client(db_path, storage_root, monkeypatch, env_overrides=env_overrides):
            pass


def test_samesite_none_requires_secure_cookie(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "samesite-none.db"
    storage_root = tmp_path / "storage"
    env_overrides = {
        "SESSION_SAME_SITE": "none",
        "SESSION_HTTPS_ONLY": "false",
    }

    with pytest.raises(ValueError, match="SESSION_SAME_SITE=none"):
        with build_test_client(db_path, storage_root, monkeypatch, env_overrides=env_overrides):
            pass


def test_production_rejects_non_https_alert_webhook(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "prod-webhook-http.db"
    storage_root = tmp_path / "storage"
    env_overrides = {
        "APP_ENV": "production",
        "APP_DEBUG": "false",
        "APP_SECRET_KEY": "super-secure-production-secret-key-12345",
        "DEFAULT_ADMIN_PASSWORD": "secure-admin-password-123",
        "APP_FRONTEND_ORIGINS": "https://atelier.example.com",
        "ALLOWED_HOSTS": "api.atelier.example.com",
        "SESSION_HTTPS_ONLY": "true",
        "OPS_ALERT_WEBHOOK_URL": "http://alerts.example.com/hook",
    }

    with pytest.raises(ValueError, match="OPS_ALERT_WEBHOOK_URL"):
        with build_test_client(db_path, storage_root, monkeypatch, env_overrides=env_overrides):
            pass


def test_production_rejects_non_https_export_delivery_webhook(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "prod-export-delivery-http.db"
    storage_root = tmp_path / "storage"
    env_overrides = {
        "APP_ENV": "production",
        "APP_DEBUG": "false",
        "APP_SECRET_KEY": "super-secure-production-secret-key-12345",
        "DEFAULT_ADMIN_PASSWORD": "secure-admin-password-123",
        "APP_FRONTEND_ORIGINS": "https://atelier.example.com",
        "ALLOWED_HOSTS": "api.atelier.example.com",
        "SESSION_HTTPS_ONLY": "true",
        "EXPORT_DELIVERY_WEBHOOK_URL": "http://delivery.example.com/hook",
    }

    with pytest.raises(ValueError, match="EXPORT_DELIVERY_WEBHOOK_URL"):
        with build_test_client(db_path, storage_root, monkeypatch, env_overrides=env_overrides):
            pass


def test_auth_endpoints_disable_caching(app_client: TestClient) -> None:
    response = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
