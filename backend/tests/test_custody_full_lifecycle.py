from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login
from .test_payments import seed_booking_context


def test_custody_full_delivery_and_receipt_lifecycle(app_client: TestClient) -> None:
    """
    Tests the full lifecycle of a custody case:
    Open -> Handover -> Return (Good) -> Laundry Send -> Laundry Receive -> Settle
    """
    login(app_client)

    # 1. Setup: Create a booking with a dress
    context = seed_booking_context(app_client, dress_code="DR-LIFECYCLE-001")
    line_id = context["line_id"]
    dress_id = context["dress_id"]

    # 2. Open Custody Case (التسليم)
    created = app_client.post(
        "/api/custody",
        json={
            "booking_line_id": line_id,
            "custody_date": "2026-04-20",
            "case_type": "handover",
            "notes": "Full lifecycle test case",
            "security_deposit_amount": 500,
            "security_deposit_document_text": "National ID",
        },
    )
    assert created.status_code == 201, created.text
    case = created.json()
    case_id = case["id"]
    assert case["status"] == "open"

    # Check dress status (service.py says it should be 'reserved' after case creation)
    dress_detail = app_client.get(f"/api/dresses/{dress_id}")
    assert dress_detail.status_code == 200
    assert dress_detail.json()["status"] == "reserved"

    # 3. Handover Action (التسليم للعميل)
    handover = app_client.post(
        f"/api/custody/{case_id}/actions",
        json={"action": "handover", "action_date": "2026-04-21", "note": "Dress handed over to customer"},
    )
    assert handover.status_code == 200, handover.text
    assert handover.json()["status"] == "handed_over"

    # Verify dress status -> with_customer
    dress_detail = app_client.get(f"/api/dresses/{dress_id}")
    assert dress_detail.json()["status"] == "with_customer"

    # 4. Customer Return (الاستلام من العميل)
    return_action = app_client.post(
        f"/api/custody/{case_id}/actions",
        json={
            "action": "customer_return",
            "action_date": "2026-04-24",
            "return_outcome": "good",
            "note": "Returned in perfect condition",
        },
    )
    assert return_action.status_code == 200, return_action.text
    assert return_action.json()["status"] == "returned"

    # Verify dress status -> maintenance (laundry/ghusl)
    dress_detail = app_client.get(f"/api/dresses/{dress_id}")
    assert dress_detail.json()["status"] == "maintenance"

    # 5. Laundry Flow (الغسيل والمكواة)
    # Send to laundry
    send_laundry = app_client.post(
        f"/api/custody/{case_id}/actions",
        json={"action": "laundry_send", "action_date": "2026-04-25", "note": "Sent to dry clean"},
    )
    assert send_laundry.status_code == 200, send_laundry.text
    assert send_laundry.json()["status"] == "laundry_sent"

    dress_detail = app_client.get(f"/api/dresses/{dress_id}")
    assert dress_detail.json()["status"] == "maintenance"

    # Receive from laundry
    receive_laundry = app_client.post(
        f"/api/custody/{case_id}/actions",
        json={"action": "laundry_receive", "action_date": "2026-04-26", "note": "Received back clean"},
    )
    assert receive_laundry.status_code == 200, receive_laundry.text
    assert receive_laundry.json()["status"] == "laundry_received"

    # Dress status should be available now
    dress_detail = app_client.get(f"/api/dresses/{dress_id}")
    assert dress_detail.json()["status"] == "available"

    # 6. Final Settlement (التسوية والإغلاق)
    settle = app_client.post(
        f"/api/custody/{case_id}/actions",
        json={"action": "settlement", "action_date": "2026-04-27", "note": "Case closed"},
    )
    assert settle.status_code == 200, settle.text
    assert settle.json()["status"] == "settled"


def test_custody_damage_compensation_and_accounting(app_client: TestClient) -> None:
    """
    Tests handling of damaged returns, compensation collection, and accounting auto-posting.
    """
    login(app_client)

    context = seed_booking_context(app_client, dress_code="DR-DAMAGE-001")
    line_id = context["line_id"]

    created = app_client.post(
        "/api/custody",
        json={"booking_line_id": line_id, "custody_date": "2026-04-20"},
    )
    assert created.status_code == 201, created.text
    case_id = created.json()["id"]

    # Handover
    app_client.post(f"/api/custody/{case_id}/actions", json={"action": "handover", "action_date": "2026-04-21"})

    # Get a valid payment method
    pm_list = app_client.get("/api/payment-methods")
    assert pm_list.status_code == 200
    pm_id = pm_list.json()[0]["id"]

    # Return Damaged with Compensation
    damage_return = app_client.post(
        f"/api/custody/{case_id}/actions",
        json={
            "action": "customer_return",
            "action_date": "2026-04-22",
            "return_outcome": "damaged",
            "compensation_amount": 150.50,
            "payment_method_id": pm_id,
            "note": "Tear in the lace",
        },
    )
    assert damage_return.status_code == 200, damage_return.text
    payload = damage_return.json()
    assert payload["compensation_amount"] == 150.50
    assert payload["compensation_payment_document_id"] is not None

    # Verify Accounting Journal Entry
    pay_doc_id = payload["compensation_payment_document_id"]
    pay_doc_resp = app_client.get(f"/api/payments/{pay_doc_id}")
    assert pay_doc_resp.status_code == 200
    pay_doc = pay_doc_resp.json()
    journal_id = pay_doc["journal_entry_id"]
    assert journal_id is not None

    journal_resp = app_client.get(f"/api/accounting/journal-entries/{journal_id}")
    assert journal_resp.status_code == 200
    journal = journal_resp.json()
    assert journal["status"] == "posted"

    # Verify lines (Cash debit, Revenue credit)
    lines = journal["lines"]
    assert any(float(l["debit_amount"]) == 150.50 for l in lines)
    assert any(float(l["credit_amount"]) == 150.50 for l in lines)
