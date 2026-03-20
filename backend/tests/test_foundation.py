from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from .conftest import build_test_client


def login(client: TestClient, username: str = "admin", password: str = "admin123") -> dict:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response.json()


def test_health_and_default_admin_login(app_client: TestClient) -> None:
    health_response = app_client.get("/api/health")
    assert health_response.status_code == 200
    assert health_response.json()["database_ok"] is True
    assert health_response.json()["migrations_ok"] is True

    payload = login(app_client)
    assert payload["username"] == "admin"
    assert "admin" in payload["role_names"]


def test_default_admin_seeded_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "seed-once.db"
    storage_root = tmp_path / "storage"

    with build_test_client(db_path, storage_root, monkeypatch) as first_client:
        login(first_client)
        users_first = first_client.get("/api/users").json()
        assert len(users_first) == 1
        assert users_first[0]["username"] == "admin"

    with build_test_client(db_path, storage_root, monkeypatch) as second_client:
        login(second_client)
        users_second = second_client.get("/api/users").json()
        assert len(users_second) == 1
        assert users_second[0]["username"] == "admin"


def test_login_failure(app_client: TestClient) -> None:
    response = app_client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_admin_can_create_and_edit_user(app_client: TestClient) -> None:
    login(app_client)

    create_response = app_client.post(
        "/api/users",
        json={
            "username": "team.user",
            "full_name": "Team User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_response.status_code == 201, create_response.text
    created_user = create_response.json()
    assert created_user["username"] == "team.user"

    update_response = app_client.patch(
        f"/api/users/{created_user['id']}",
        json={
            "username": "team.updated",
            "full_name": "Updated User",
            "role_names": ["admin"],
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated_user = update_response.json()
    assert updated_user["username"] == "team.updated"
    assert updated_user["full_name"] == "Updated User"
    assert "admin" in updated_user["role_names"]


def test_regular_user_sees_self_only_and_updates_profile(app_client: TestClient) -> None:
    login(app_client)
    create_response = app_client.post(
        "/api/users",
        json={
            "username": "regular.user",
            "full_name": "Regular User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_response.status_code == 201

    app_client.post("/api/auth/logout")
    login(app_client, username="regular.user", password="secret123")

    list_response = app_client.get("/api/users")
    assert list_response.status_code == 200
    rows = list_response.json()
    assert len(rows) == 1
    assert rows[0]["username"] == "regular.user"

    forbidden_create = app_client.post(
        "/api/users",
        json={"username": "xuser", "full_name": "X User", "password": "secret123", "role_names": ["user"]},
    )
    assert forbidden_create.status_code == 403

    update_me = app_client.patch(
        "/api/users/me",
        json={"full_name": "Regular User Updated", "password": "new-secret123"},
    )
    assert update_me.status_code == 200
    assert update_me.json()["full_name"] == "Regular User Updated"

    app_client.post("/api/auth/logout")
    relogin = app_client.post("/api/auth/login", json={"username": "regular.user", "password": "new-secret123"})
    assert relogin.status_code == 200


def test_company_settings_and_backup_flow(app_client: TestClient) -> None:
    login(app_client)

    company_response = app_client.patch(
        "/api/settings/company",
        json={"name": "Beauty Atelier", "legal_name": "Beauty Atelier LLC", "default_currency": "EGP"},
    )
    assert company_response.status_code == 200
    assert company_response.json()["name"] == "Beauty Atelier"

    backup_response = app_client.post("/api/settings/backups")
    assert backup_response.status_code == 200, backup_response.text
    backup = backup_response.json()
    assert backup["filename"].endswith(".zip")

    list_backups = app_client.get("/api/settings/backups")
    assert list_backups.status_code == 200
    assert len(list_backups.json()) >= 1

    download_response = app_client.get(f"/api/settings/backups/{backup['id']}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/zip"