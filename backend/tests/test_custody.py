from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import (
    build_booking_line_payload,
    create_booking_document,
    seed_customer,
    seed_service_bundle,
)
from .test_foundation import login
from .test_payments import seed_booking_context


def test_admin_can_create_list_and_get_custody_case_from_booking_line(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client, dress_code="DR-CUSTODY-001")

    created = app_client.post(
        "/api/custody",
        json={
            "booking_line_id": context["line_id"],
            "custody_date": "2026-04-20",
            "case_type": "handover",
            "notes": "Customer handover started",
            "security_deposit_amount": 300,
            "security_deposit_document_text": "National ID Card",
        },
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["case_number"].startswith("CUS-")
    assert payload["status"] == "open"
    assert payload["booking_line_id"] == context["line_id"]
    assert payload["dress_id"] == context["dress_id"]
    assert payload["custody_date"] == "2026-04-20"
    assert payload["security_deposit_amount"] == 300.0

    listed = app_client.get("/api/custody?view=all")
    assert listed.status_code == 200, listed.text
    assert len(listed.json()) == 1
    row = listed.json()[0]
    assert row["id"] == payload["id"]
    assert row["customer_name"]
    assert row["booking_number"]
    assert row["dress_code"]

    detail = app_client.get(f"/api/custody/{payload['id']}")
    assert detail.status_code == 200, detail.text
    assert detail.json()["id"] == payload["id"]


def test_custody_case_requires_custody_date(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client, dress_code="DR-CUSTODY-DATE")
    created = app_client.post("/api/custody", json={"booking_line_id": context["line_id"]})
    assert created.status_code == 422


def test_custody_case_blocks_duplicate_booking_line(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client, dress_code="DR-CUSTODY-DUP")

    first = app_client.post(
        "/api/custody",
        json={
            "booking_line_id": context["line_id"],
            "custody_date": "2026-04-20",
            "security_deposit_amount": 150,
            "security_deposit_document_text": "Driver License",
        },
    )
    assert first.status_code == 201, first.text

    duplicate = app_client.post(
        "/api/custody",
        json={
            "booking_line_id": context["line_id"],
            "custody_date": "2026-04-21",
            "security_deposit_amount": 150,
            "security_deposit_document_text": "Driver License",
        },
    )
    assert duplicate.status_code == 422


def test_regular_user_can_manage_custody_case(app_client: TestClient) -> None:
    login(app_client)
    create_user = app_client.post(
        "/api/users",
        json={
            "username": "custody.user",
            "full_name": "Custody User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_user.status_code == 201, create_user.text
    context = seed_booking_context(app_client, dress_code="DR-CUSTODY-USER")

    app_client.post("/api/auth/logout")
    login(app_client, username="custody.user", password="secret123")

    created = app_client.post("/api/custody", json={"booking_line_id": context["line_id"], "custody_date": "2026-04-20"})
    assert created.status_code == 201, created.text
    listed = app_client.get("/api/custody")
    assert listed.status_code == 200, listed.text
    assert len(listed.json()) == 1


def test_custody_routes_require_authentication(app_client: TestClient) -> None:
    list_response = app_client.get("/api/custody")
    assert list_response.status_code == 401

    create_response = app_client.post("/api/custody", json={"booking_line_id": "missing", "custody_date": "2026-04-20"})
    assert create_response.status_code == 401


def test_custody_action_requires_action_date(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client, dress_code="DR-CUSTODY-ACT-DATE")
    created = app_client.post("/api/custody", json={"booking_line_id": context["line_id"], "custody_date": "2026-04-20"})
    assert created.status_code == 201, created.text
    case_id = created.json()["id"]

    blocked = app_client.post(f"/api/custody/{case_id}/actions", json={"action": "handover"})
    assert blocked.status_code == 422


def test_custody_action_customer_return_good_refunds_security_deposit(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client, dress_code="DR-CUSTODY-GOOD")
    created = app_client.post(
        "/api/custody",
        json={
            "booking_line_id": context["line_id"],
            "custody_date": "2026-04-20",
            "security_deposit_amount": 400,
            "security_deposit_document_text": "Passport",
        },
    )
    assert created.status_code == 201, created.text
    case_id = created.json()["id"]

    handover = app_client.post(
        f"/api/custody/{case_id}/actions",
        json={"action": "handover", "action_date": "2026-04-21", "note": "Delivered to customer"},
    )
    assert handover.status_code == 200, handover.text
    assert handover.json()["status"] == "handed_over"

    returned = app_client.post(
        f"/api/custody/{case_id}/actions",
        json={"action": "customer_return", "action_date": "2026-04-22", "return_outcome": "good", "note": "Returned in good condition"},
    )
    assert returned.status_code == 200, returned.text
    payload = returned.json()
    assert payload["status"] == "returned"
    assert payload["return_outcome"] == "good"
    assert payload["security_deposit_refund_payment_document_id"] is None
    assert payload["compensation_payment_document_id"] is None


def test_custody_action_customer_return_damaged_collects_compensation_by_action_date(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client, dress_code="DR-CUSTODY-DMG")
    created = app_client.post(
        "/api/custody",
        json={
            "booking_line_id": context["line_id"],
            "custody_date": "2026-04-20",
            "security_deposit_amount": 500,
            "security_deposit_document_text": "National ID",
        },
    )
    assert created.status_code == 201, created.text
    case_id = created.json()["id"]

    handover = app_client.post(f"/api/custody/{case_id}/actions", json={"action": "handover", "action_date": "2026-04-21"})
    assert handover.status_code == 200, handover.text

    returned = app_client.post(
        f"/api/custody/{case_id}/actions",
        json={
            "action": "customer_return",
            "action_date": "2026-04-24",
            "return_outcome": "damaged",
            "compensation_amount": 350,
            "note": "Damage compensation",
        },
    )
    assert returned.status_code == 200, returned.text
    payload = returned.json()
    assert payload["status"] == "returned"
    assert payload["return_outcome"] == "damaged"
    assert payload["compensation_amount"] == 350.0
    assert payload["compensation_collected_on"] == "2026-04-24"
    assert payload["compensation_payment_document_id"]


def test_custody_case_without_dress_requires_notes(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(
        app_client,
        department_code="MAKEUP",
        department_name="قسم المكياج",
        service_name="خدمة ميكب",
        default_price=1000,
    )
    booking = create_booking_document(
        app_client,
        customer_id,
        [
            build_booking_line_payload(
                service_bundle,
                service_date="2026-08-10",
                dress_id=None,
                line_price=1000,
            )
        ],
    )
    line_id = booking["lines"][0]["id"]

    blocked = app_client.post("/api/custody", json={"booking_line_id": line_id, "custody_date": "2026-08-10"})
    assert blocked.status_code == 422

    created = app_client.post(
        "/api/custody",
        json={"booking_line_id": line_id, "custody_date": "2026-08-10", "notes": "Accessory set - tiara and veil"},
    )
    assert created.status_code == 201, created.text
    assert created.json()["dress_id"] is None


def test_custody_action_blocks_invalid_transition(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client, dress_code="DR-CUSTODY-INVALID")
    created = app_client.post("/api/custody", json={"booking_line_id": context["line_id"], "custody_date": "2026-04-20", "notes": "workflow test"})
    assert created.status_code == 201, created.text
    case_id = created.json()["id"]

    invalid = app_client.post(f"/api/custody/{case_id}/actions", json={"action": "laundry_receive", "action_date": "2026-04-21"})
    assert invalid.status_code == 422


def test_custody_list_supports_open_settled_all_views(app_client: TestClient) -> None:
    login(app_client)
    context_open = seed_booking_context(app_client, dress_code="DR-CUSTODY-VIEW-OPEN")
    context_settled = seed_booking_context(
        app_client,
        customer_id=context_open["customer_id"],
        dress_code="DR-CUSTODY-VIEW-SET",
    )

    created_open = app_client.post("/api/custody", json={"booking_line_id": context_open["line_id"], "custody_date": "2026-04-20"})
    assert created_open.status_code == 201, created_open.text
    created_settled = app_client.post("/api/custody", json={"booking_line_id": context_settled["line_id"], "custody_date": "2026-04-20"})
    assert created_settled.status_code == 201, created_settled.text

    settled_case_id = created_settled.json()["id"]
    settled_action = app_client.post(
        f"/api/custody/{settled_case_id}/actions",
        json={"action": "settlement", "action_date": "2026-04-21", "note": "Closed"},
    )
    assert settled_action.status_code == 200, settled_action.text
    assert settled_action.json()["status"] == "settled"

    open_rows = app_client.get("/api/custody?view=open")
    assert open_rows.status_code == 200, open_rows.text
    assert all(item["status"] != "settled" for item in open_rows.json())

    settled_rows = app_client.get("/api/custody?view=settled")
    assert settled_rows.status_code == 200, settled_rows.text
    assert len(settled_rows.json()) == 1
    assert settled_rows.json()[0]["id"] == settled_case_id

    all_rows = app_client.get("/api/custody?view=all")
    assert all_rows.status_code == 200, all_rows.text
    assert len(all_rows.json()) == 2
