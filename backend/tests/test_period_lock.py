from __future__ import annotations

import json
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.core_platform.models import AuditLog
from .test_bookings import seed_dress
from .test_foundation import login
from .test_payments import seed_booking_context


def _set_period_lock(app_client: TestClient, locked_through: str | None) -> dict:
    response = app_client.put(
        "/api/settings/period-lock",
        json={"locked_through": locked_through, "note": "Checkpoint 9E phase 1 test"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _latest_period_lock_audit(app_client: TestClient) -> AuditLog | None:
    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        return db.scalars(
            select(AuditLog).where(AuditLog.action == "period_lock.updated").order_by(AuditLog.occurred_at.desc())
        ).first()


def _latest_period_lock_override_audit(app_client: TestClient) -> AuditLog | None:
    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        return db.scalars(
            select(AuditLog).where(AuditLog.action == "period_lock.override_used").order_by(AuditLog.occurred_at.desc())
        ).first()


def test_period_lock_settings_update_and_read(app_client: TestClient) -> None:
    login(app_client)
    initial = app_client.get("/api/settings/period-lock")
    assert initial.status_code == 200, initial.text
    assert initial.json()["locked_through"] is None

    locked = _set_period_lock(app_client, "2026-06-30")
    assert locked["locked_through"] == "2026-06-30"
    assert locked["is_locked"] is True

    refreshed = app_client.get("/api/settings/period-lock")
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["locked_through"] == "2026-06-30"

    audit_row = _latest_period_lock_audit(app_client)
    assert audit_row is not None
    payload = json.loads(audit_row.diff_json or "{}")
    assert payload["before_locked_through"] is None
    assert payload["after_locked_through"] == "2026-06-30"


def test_period_lock_update_requires_permission(app_client: TestClient) -> None:
    login(app_client)
    create_user = app_client.post(
        "/api/users",
        json={
            "username": "period.user",
            "full_name": "Period User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_user.status_code == 201, create_user.text
    app_client.post("/api/auth/logout")
    login(app_client, username="period.user", password="secret123")

    response = app_client.put("/api/settings/period-lock", json={"locked_through": "2026-06-30"})
    assert response.status_code == 403


def test_period_lock_blocks_corrective_hard_delete(app_client: TestClient) -> None:
    login(app_client)
    _set_period_lock(app_client, "2099-12-31")
    dress_id = seed_dress(app_client, code="DR-LOCKED-DELETE")

    blocked = app_client.post(
        "/api/settings/destructive-delete",
        json={"entity_type": "dress", "entity_id": dress_id, "reason_code": "entry_mistake"},
    )
    assert blocked.status_code == 422
    assert "period is locked" in blocked.json()["detail"]


def test_period_lock_blocks_payment_void_inside_locked_date(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)
    created = app_client.post(
        "/api/payments",
        json={
            "customer_id": context["customer_id"],
            "payment_date": "2026-06-01",
            "allocations": [
                {
                    "booking_id": context["booking_id"],
                    "booking_line_id": context["line_id"],
                    "allocated_amount": 500,
                }
            ],
        },
    )
    assert created.status_code == 201, created.text
    payment = created.json()
    _set_period_lock(app_client, "2026-06-30")

    blocked = app_client.post(
        f"/api/payments/{payment['id']}/void",
        json={"void_date": "2026-06-15", "reason": "Void inside closed period"},
    )
    assert blocked.status_code == 422
    assert "period is locked" in blocked.json()["detail"]


def test_period_lock_blocks_booking_revenue_reverse(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)
    complete = app_client.post(f"/api/bookings/{context['booking_id']}/lines/{context['line_id']}/complete")
    assert complete.status_code == 200, complete.text

    _set_period_lock(app_client, date.today().isoformat())
    blocked = app_client.post(f"/api/bookings/{context['booking_id']}/lines/{context['line_id']}/reverse-revenue")
    assert blocked.status_code == 422
    assert "period is locked" in blocked.json()["detail"]


def test_period_lock_override_allows_void_and_appears_in_exception_report(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)
    created = app_client.post(
        "/api/payments",
        json={
            "customer_id": context["customer_id"],
            "payment_date": "2026-06-01",
            "allocations": [
                {
                    "booking_id": context["booking_id"],
                    "booking_line_id": context["line_id"],
                    "allocated_amount": 500,
                }
            ],
        },
    )
    assert created.status_code == 201, created.text
    payment = created.json()
    _set_period_lock(app_client, "2026-06-30")

    allowed = app_client.post(
        f"/api/payments/{payment['id']}/void",
        json={
            "void_date": "2026-06-15",
            "reason": "Financial correction with approved override",
            "override_lock": True,
            "override_reason": "Approved by finance lead to fix wrong entry.",
        },
    )
    assert allowed.status_code == 200, allowed.text

    override_audit = _latest_period_lock_override_audit(app_client)
    assert override_audit is not None
    override_payload = json.loads(override_audit.diff_json or "{}")
    assert override_payload["action_key"] == "payment.void"
    assert override_payload["action_date"] == "2026-06-15"
    assert override_payload["locked_through"] == "2026-06-30"

    report = app_client.get("/api/settings/period-lock/exceptions")
    assert report.status_code == 200, report.text
    rows = report.json()
    assert len(rows) >= 1
    assert any(item["action_key"] == "payment.void" for item in rows)


def test_period_lock_override_requires_manage_permission(app_client: TestClient) -> None:
    login(app_client)
    create_user = app_client.post(
        "/api/users",
        json={
            "username": "period.override.user",
            "full_name": "Period Override User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_user.status_code == 201, create_user.text
    context = seed_booking_context(app_client)
    created = app_client.post(
        "/api/payments",
        json={
            "customer_id": context["customer_id"],
            "payment_date": "2026-06-01",
            "allocations": [
                {
                    "booking_id": context["booking_id"],
                    "booking_line_id": context["line_id"],
                    "allocated_amount": 500,
                }
            ],
        },
    )
    assert created.status_code == 201, created.text
    payment = created.json()
    _set_period_lock(app_client, "2026-06-30")

    app_client.post("/api/auth/logout")
    login(app_client, username="period.override.user", password="secret123")
    blocked = app_client.post(
        f"/api/payments/{payment['id']}/void",
        json={
            "void_date": "2026-06-15",
            "reason": "Attempted override without permission",
            "override_lock": True,
            "override_reason": "Need to bypass close date",
        },
    )
    assert blocked.status_code == 403
