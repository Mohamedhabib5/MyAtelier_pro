from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.core_platform.models import AuditLog
from .test_foundation import login
from .test_payments import seed_booking_context


def test_admin_can_list_and_filter_audit_events(app_client: TestClient) -> None:
    login(app_client)
    create_customer = app_client.post(
        "/api/customers",
        json={"full_name": "Audit Explorer Customer", "phone": "01019000001"},
    )
    assert create_customer.status_code == 201, create_customer.text
    customer_id = create_customer.json()["id"]

    listed = app_client.get("/api/audit/events", params={"target_type": "customer", "target_id": customer_id, "page_size": 10})
    assert listed.status_code == 200, listed.text
    payload = listed.json()
    assert payload["total"] >= 1
    assert any(item["target_id"] == customer_id for item in payload["items"])

    action_filtered = app_client.get("/api/audit/events", params={"action": "customer.created", "page_size": 20})
    assert action_filtered.status_code == 200, action_filtered.text
    assert any(item["action"] == "customer.created" for item in action_filtered.json()["items"])


def test_regular_user_cannot_access_audit_explorer(app_client: TestClient) -> None:
    login(app_client)
    create_user = app_client.post(
        "/api/users",
        json={
            "username": "audit.explorer.user",
            "full_name": "Audit Explorer User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_user.status_code == 201, create_user.text

    app_client.post("/api/auth/logout")
    login(app_client, username="audit.explorer.user", password="secret123")
    denied = app_client.get("/api/audit/events")
    assert denied.status_code == 403


def test_admin_can_list_destructive_actions_report(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)
    payment = app_client.post(
        "/api/payments",
        json={
            "customer_id": context["customer_id"],
            "payment_date": "2026-04-02",
            "allocations": [
                {
                    "booking_id": context["booking_id"],
                    "booking_line_id": context["line_id"],
                    "allocated_amount": 250,
                }
            ],
        },
    )
    assert payment.status_code == 201, payment.text
    payment_id = payment.json()["id"]
    voided = app_client.post(
        f"/api/payments/{payment_id}/void",
        json={"void_date": "2026-04-03", "reason": "Destructive report check"},
    )
    assert voided.status_code == 200, voided.text

    report = app_client.get("/api/audit/destructive-actions", params={"target_type": "payment_document", "page_size": 20})
    assert report.status_code == 200, report.text
    payload = report.json()
    assert payload["total"] >= 1
    assert any(item["action"] == "payment_document.voided" and item["target_id"] == payment_id for item in payload["items"])


def test_admin_can_list_nightly_ops_events_preset(app_client: TestClient) -> None:
    login(app_client)
    backup_check = app_client.post("/api/settings/ops/alerts/run-backup-check", json={"dry_run": True})
    assert backup_check.status_code == 200, backup_check.text

    report = app_client.get("/api/audit/nightly-ops", params={"page_size": 20})
    assert report.status_code == 200, report.text
    payload = report.json()
    assert payload["total"] >= 1
    assert any(item["action"] == "automation.job_run" for item in payload["items"])
    assert all(item["action"] in {"automation.job_run", "ops.nightly_failure_reported", "audit.nightly_ops_exported"} for item in payload["items"])

    csv_report = app_client.get("/api/audit/nightly-ops.csv", params={"limit": 200, "export_reason": "Monthly compliance handoff"})
    assert csv_report.status_code == 200, csv_report.text
    assert csv_report.headers["content-type"].startswith("text/csv")
    assert csv_report.headers.get("x-exported-rows") is not None
    assert csv_report.headers.get("x-active-filters") is not None
    assert "# exported_rows" in csv_report.text
    assert "# active_filters" in csv_report.text
    assert "automation.job_run" in csv_report.text

    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        export_events = db.scalars(
            select(AuditLog).where(
                AuditLog.action == "audit.nightly_ops_exported",
                AuditLog.target_type == "audit_export",
                AuditLog.target_id == "nightly_ops_csv",
            )
        ).all()
    assert len(export_events) >= 1
    assert any((row.reason_text or "") == "Monthly compliance handoff" for row in export_events)

    refreshed = app_client.get("/api/audit/nightly-ops", params={"page_size": 50})
    assert refreshed.status_code == 200, refreshed.text
    assert any(item["action"] == "audit.nightly_ops_exported" for item in refreshed.json()["items"])
