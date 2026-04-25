from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.identity.models import Permission, Role
from .test_foundation import login


def test_permission_keys_seeded_and_assigned_to_admin(app_client: TestClient) -> None:
    login(app_client)

    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        keys = {item.key for item in db.scalars(select(Permission)).all()}
        assert "audit.view" in keys
        assert "destructive.manage" in keys
        assert "period_lock.manage" in keys

        admin_role = db.scalar(select(Role).where(Role.name == "admin"))
        assert admin_role is not None
        admin_keys = {permission.key for permission in admin_role.permissions}
        assert "audit.view" in admin_keys
        assert "destructive.manage" in admin_keys
        assert "period_lock.manage" in admin_keys


def test_regular_user_does_not_receive_new_admin_permissions(app_client: TestClient) -> None:
    login(app_client)
    create_response = app_client.post(
        "/api/users",
        json={
            "username": "permission.user",
            "full_name": "Permission User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_response.status_code == 201

    app_client.post("/api/auth/logout")
    login(app_client, username="permission.user", password="secret123")

    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        user_role = db.scalar(select(Role).where(Role.name == "user"))
        assert user_role is not None
        user_keys = {permission.key for permission in user_role.permissions}
        assert "audit.view" not in user_keys
        assert "destructive.manage" not in user_keys
        assert "period_lock.manage" not in user_keys
