from __future__ import annotations

import json

from sqlalchemy import select

from app.modules.core_platform.models import AuditLog
from .test_foundation import login


def test_authenticated_user_can_save_and_load_own_grid_preference(app_client) -> None:
    login(app_client)
    table_key = "bookings-list"
    payload = {
        "state": {
            "pageSize": 25,
            "columnState": [{"colId": "booking_number", "hide": False, "pinned": "left"}],
            "filterModel": {"status": {"type": "equals", "filter": "draft"}},
        }
    }

    saved = app_client.put(f"/api/users/me/grid-preferences/{table_key}", json=payload)
    assert saved.status_code == 200, saved.text
    body = saved.json()
    assert body["table_key"] == table_key
    assert body["state"]["pageSize"] == 25

    loaded = app_client.get(f"/api/users/me/grid-preferences/{table_key}")
    assert loaded.status_code == 200, loaded.text
    loaded_body = loaded.json()
    assert loaded_body["table_key"] == table_key
    assert loaded_body["state"]["pageSize"] == 25
    assert loaded_body["state"]["columnState"][0]["colId"] == "booking_number"
    assert loaded_body["state"]["filterModel"]["status"]["filter"] == "draft"


def test_grid_preference_is_scoped_per_user(app_client) -> None:
    login(app_client)
    create_user = app_client.post(
        "/api/users",
        json={
            "username": "grid.pref.user",
            "full_name": "Grid Pref User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_user.status_code == 201, create_user.text

    set_admin_pref = app_client.put(
        "/api/users/me/grid-preferences/payments-list",
        json={"state": {"pageSize": 50}},
    )
    assert set_admin_pref.status_code == 200, set_admin_pref.text

    app_client.post("/api/auth/logout")
    login(app_client, username="grid.pref.user", password="secret123")
    loaded = app_client.get("/api/users/me/grid-preferences/payments-list")
    assert loaded.status_code == 200, loaded.text
    assert loaded.json()["state"]["pageSize"] == 10


def test_grid_preference_persists_after_logout_and_login(app_client) -> None:
    login(app_client)
    saved = app_client.put(
        "/api/users/me/grid-preferences/bookings-list",
        json={"state": {"pageSize": 75}},
    )
    assert saved.status_code == 200, saved.text

    app_client.post("/api/auth/logout")
    login(app_client)
    loaded = app_client.get("/api/users/me/grid-preferences/bookings-list")
    assert loaded.status_code == 200, loaded.text
    assert loaded.json()["state"]["pageSize"] == 75


def test_updating_grid_preference_is_audited(app_client) -> None:
    login(app_client)
    response = app_client.put(
        "/api/users/me/grid-preferences/customers-list",
        json={"state": {"pageSize": 100}},
    )
    assert response.status_code == 200, response.text

    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        row = db.scalars(
            select(AuditLog)
            .where(AuditLog.action == "user.grid_preferences_updated")
            .order_by(AuditLog.occurred_at.desc())
        ).first()
    assert row is not None
    assert row.target_type == "user"
    assert row.request_id == response.headers.get("x-request-id")
    payload = json.loads(row.diff_json or "{}")
    assert payload.get("table_key") == "customers-list"
    assert payload.get("page_size") == 100
