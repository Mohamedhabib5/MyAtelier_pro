from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.core_platform.models import AuditLog
from .test_foundation import login
from .test_payments import seed_booking_context

pytestmark = pytest.mark.guardrail


def _latest_audit_for_target(app_client: TestClient, *, action: str, target_id: str) -> AuditLog | None:
    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        statement = (
            select(AuditLog)
            .where(AuditLog.action == action, AuditLog.target_id == target_id)
            .order_by(AuditLog.occurred_at.desc())
        )
        return db.scalars(statement).first()


def _assert_audit_written(
    app_client: TestClient,
    *,
    action: str,
    target_type: str,
    target_id: str,
    request_id: str | None,
) -> AuditLog:
    row = _latest_audit_for_target(app_client, action=action, target_id=target_id)
    assert row is not None
    assert row.target_type == target_type
    assert row.actor_user_id is not None
    assert row.success is not False
    assert row.request_id == request_id
    return row


def test_customer_write_actions_always_leave_audit_evidence(app_client: TestClient) -> None:
    login(app_client)

    create_response = app_client.post(
        "/api/customers",
        json={"full_name": "Audit Guardrail Customer", "phone": "01019000011"},
    )
    assert create_response.status_code == 201, create_response.text
    customer_id = create_response.json()["id"]
    _assert_audit_written(
        app_client,
        action="customer.created",
        target_type="customer",
        target_id=customer_id,
        request_id=create_response.headers.get("x-request-id"),
    )

    update_response = app_client.patch(
        f"/api/customers/{customer_id}",
        json={
            "full_name": "Audit Guardrail Customer Updated",
            "phone": "01019000011",
            "email": "guardrail@example.com",
            "address": "Cairo",
            "notes": "audit test",
            "is_active": True,
        },
    )
    assert update_response.status_code == 200, update_response.text
    _assert_audit_written(
        app_client,
        action="customer.updated",
        target_type="customer",
        target_id=customer_id,
        request_id=update_response.headers.get("x-request-id"),
    )

    archive_response = app_client.post(
        f"/api/customers/{customer_id}/archive",
        json={"reason": "archive guardrail"},
    )
    assert archive_response.status_code == 200, archive_response.text
    archived = _assert_audit_written(
        app_client,
        action="customer.archived",
        target_type="customer",
        target_id=customer_id,
        request_id=archive_response.headers.get("x-request-id"),
    )
    archived_payload = json.loads(archived.diff_json or "{}")
    assert archived_payload.get("is_active") is False

    restore_response = app_client.post(
        f"/api/customers/{customer_id}/restore",
        json={"reason": "restore guardrail"},
    )
    assert restore_response.status_code == 200, restore_response.text
    restored = _assert_audit_written(
        app_client,
        action="customer.restored",
        target_type="customer",
        target_id=customer_id,
        request_id=restore_response.headers.get("x-request-id"),
    )
    restored_payload = json.loads(restored.diff_json or "{}")
    assert restored_payload.get("is_active") is True


def test_payment_void_keeps_audit_evidence_with_reason_code(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)

    payment_response = app_client.post(
        "/api/payments",
        json={
            "customer_id": context["customer_id"],
            "payment_date": "2026-04-02",
            "allocations": [
                {
                    "booking_id": context["booking_id"],
                    "booking_line_id": context["line_id"],
                    "allocated_amount": 300,
                }
            ],
        },
    )
    assert payment_response.status_code == 201, payment_response.text
    payment_id = payment_response.json()["id"]

    void_response = app_client.post(
        f"/api/payments/{payment_id}/void",
        json={"void_date": "2026-04-03", "reason": "void guardrail", "reason_code": "entry_mistake"},
    )
    assert void_response.status_code == 200, void_response.text
    row = _assert_audit_written(
        app_client,
        action="payment_document.voided",
        target_type="payment_document",
        target_id=payment_id,
        request_id=void_response.headers.get("x-request-id"),
    )
    payload = json.loads(row.diff_json or "{}")
    assert payload.get("reason_code") == "entry_mistake"
