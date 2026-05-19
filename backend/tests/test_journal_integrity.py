"""Phase 3: Integration tests for journal entry integrity and reversals."""
from __future__ import annotations

import logging
from datetime import date
from fastapi.testclient import TestClient

from .test_bookings import seed_customer
from .test_foundation import login
from .test_payments import seed_booking_context

logger = logging.getLogger(__name__)


def _get_journal(client: TestClient, entry_id: str) -> dict:
    response = client.get(f"/api/accounting/journal-entries/{entry_id}")
    assert response.status_code == 200, response.text
    return response.json()


def _get_journals_list(client: TestClient) -> list[dict]:
    response = client.get("/api/accounting/journal-entries")
    assert response.status_code == 200, response.text
    return response.json()


def test_reversal_preserves_branch_and_party_and_reference(app_client: TestClient) -> None:
    """Payment update triggers auto-reversal. The reversed entry must preserve branch_id, party, reference, and traceability."""
    login(app_client)
    context = seed_booking_context(app_client)

    # 1. Create original payment
    created = app_client.post(
        "/api/payments",
        json={
            "customer_id": context["customer_id"],
            "payment_date": "2026-06-01",
            "allocations": [
                {
                    "booking_id": context["booking_id"],
                    "booking_line_id": context["line_id"],
                    "allocated_amount": 1000,
                }
            ],
        },
    )
    assert created.status_code == 201, created.text
    original_payment = created.json()
    original_journal_id = original_payment["journal_entry_id"]

    # 2. Update payment to trigger a reversal
    updated = app_client.patch(
        f"/api/payments/{original_payment['id']}",
        json={
            "customer_id": context["customer_id"],
            "payment_date": "2026-06-02",
            "allocations": [
                {
                    "booking_id": context["booking_id"],
                    "booking_line_id": context["line_id"],
                    "allocated_amount": 1200,
                }
            ],
        },
    )
    assert updated.status_code == 200, updated.text

    # 3. Retrieve all journal entries to find the reversal
    journals = _get_journals_list(app_client)
    # The reversal entry has status="posted" (or reversed), entry_number similar, let's find the one referencing f"REV-"
    reversal_entry = None
    for j in journals:
        if j["reference"] == f"REV-{original_payment['journal_entry_number']}":
            reversal_entry = j
            break

    assert reversal_entry is not None, "Reversal journal entry not found"
    
    # 4. Verify reversal integrity
    # Retrieve the full details including lines
    reversal = _get_journal(app_client, reversal_entry["id"])
    assert reversal["branch_id"] == original_payment["branch_id"]
    assert reversal["reference_type"] == "payment_document"
    assert reversal["reference_id"] == original_payment["id"]
    
    # Check that lines have reversed debit/credit but kept party
    # The original line on credit has party. Reversal has credit on cash, debit on advances (with party).
    for line in reversal["lines"]:
        if line["account_code"] == "2110":  # Advances line
            assert line["party_type"] == "customer"
            assert line["party_id"] == context["customer_id"]
            # Reversal debit amount should be original credit amount
            assert line["debit_amount"] == "1000.00"
            assert line["credit_amount"] == "0.00"


def test_disbursement_reversal_preserves_traceability(app_client: TestClient) -> None:
    """Disbursement reversal must preserve branch_id, party, reference, and traceability."""
    login(app_client)
    customer_id = seed_customer(app_client)

    # Seed a payment method
    pm_resp = app_client.post('/api/payment-methods', json={'name': 'Cash Method', 'code': 'cash_method'})
    assert pm_resp.status_code == 201, pm_resp.text
    pm_id = pm_resp.json()['id']

    # 1. Create a disbursement voucher
    created = app_client.post(
        "/api/disbursements",
        json={
            "payment_method_id": pm_id,
            "payee_type": "customer",
            "payee_id": customer_id,
            "amount": 500.00,
            "voucher_date": "2026-06-01",
            "notes": "Refund Custody Deposit",
        },
    )
    assert created.status_code == 201, created.text
    disbursement = created.json()
    assert disbursement["journal_entry_id"] is not None

    # 2. Void (reverse) the disbursement
    reversed_resp = app_client.post(
        f"/api/disbursements/{disbursement['id']}/void",
        json={"void_date": "2026-06-02", "reason": "Voiding disbursement"},
    )
    assert reversed_resp.status_code == 200, reversed_resp.text

    # Retrieve all journal entries to find the reversal
    journals = _get_journals_list(app_client)
    reversal_entry = None
    for j in journals:
        if j["reference"] == f"REV-{disbursement['journal_entry_number']}":
            reversal_entry = j
            break

    assert reversal_entry is not None, "Reversal journal entry not found"
    reversal = _get_journal(app_client, reversal_entry["id"])
    
    # Check integrity
    assert reversal["branch_id"] == disbursement["branch_id"]
    assert reversal["reference_type"] == "disbursement_voucher"
    assert reversal["reference_id"] == disbursement["id"]
    
    # The debit line on customer must be reversed to credit with party preserved
    found_party_line = False
    for line in reversal["lines"]:
        if line["party_type"] == "customer":
            assert line["party_id"] == customer_id
            assert line["credit_amount"] == "500.00"
            assert line["debit_amount"] == "0.00"
            found_party_line = True
            
    assert found_party_line, "Party line not found in reversal"


def test_manual_journal_without_branch_succeeds_with_warning(app_client: TestClient, caplog) -> None:
    """Creating a manual journal entry without branch_id must succeed but log a warning."""
    login(app_client)
    
    # Retrieve chart of accounts to find leaf accounts
    resp = app_client.get("/api/accounting/chart-of-accounts")
    assert resp.status_code == 200, resp.text
    accounts = {row["code"]: row["id"] for row in resp.json()}

    with caplog.at_level(logging.WARNING):
        response = app_client.post(
            "/api/accounting/journal-entries",
            json={
                "entry_date": str(date.today()),
                "reference": "MANUAL-NO-BRANCH",
                "lines": [
                    {
                        "account_id": accounts["1111001"],
                        "debit_amount": "150.00",
                        "credit_amount": "0.00",
                    },
                    {
                        "account_id": accounts["4110"],
                        "debit_amount": "0.00",
                        "credit_amount": "150.00",
                    },
                ],
            },
        )
        assert response.status_code == 201, response.text
        
        # Verify warning log was triggered
        assert any("created without branch_id" in record.message for record in caplog.records)


def test_period_locking_and_lockout_rules(app_client: TestClient) -> None:
    """Validate backend closing controls: block locking if draft exists, block entries in locked period, and restrict unlock permissions."""
    login(app_client)
    
    # 1. Get active fiscal period
    fp_resp = app_client.get("/api/settings/fiscal-periods")
    assert fp_resp.status_code == 200, fp_resp.text
    periods = fp_resp.json()
    assert len(periods) > 0, "No fiscal periods found"
    period = periods[0]
    period_id = period["id"]

    # Ensure it's unlocked initially
    if period["is_locked"]:
        unlock_init = app_client.patch(f"/api/settings/fiscal-periods/{period_id}", json={"is_locked": False})
        assert unlock_init.status_code == 200, unlock_init.text

    # Retrieve chart of accounts to find leaf accounts
    resp = app_client.get("/api/accounting/chart-of-accounts")
    assert resp.status_code == 200, resp.text
    accounts = {row["code"]: row["id"] for row in resp.json()}

    # 2. Create a draft journal entry in that period
    draft_resp = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": "2026-06-01",
            "fiscal_period_id": period_id,
            "lines": [
                {"account_id": accounts["1111001"], "debit_amount": "100.00", "credit_amount": "0.00"},
                {"account_id": accounts["4110"], "debit_amount": "0.00", "credit_amount": "100.00"},
            ],
        },
    )
    assert draft_resp.status_code == 201, draft_resp.text
    draft_entry = draft_resp.json()

    # 3. Try to lock the period. It must fail because there is a draft entry!
    lock_resp = app_client.patch(f"/api/settings/fiscal-periods/{period_id}", json={"is_locked": True})
    assert lock_resp.status_code == 422, lock_resp.text
    assert "لا يمكن إغلاق" in lock_resp.text or "draft" in lock_resp.text.lower()

    # 4. Post the draft entry
    post_resp = app_client.post(f"/api/accounting/journal-entries/{draft_entry['id']}/post")
    assert post_resp.status_code == 200, post_resp.text

    # 5. Lock the period again. It must succeed now!
    lock_resp2 = app_client.patch(f"/api/settings/fiscal-periods/{period_id}", json={"is_locked": True})
    assert lock_resp2.status_code == 200, lock_resp2.text
    assert lock_resp2.json()["is_locked"] is True

    # 6. Try to create another draft entry inside the locked period. It must fail!
    draft_resp2 = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": "2026-06-01",
            "fiscal_period_id": period_id,
            "lines": [
                {"account_id": accounts["1111001"], "debit_amount": "50.00", "credit_amount": "0.00"},
                {"account_id": accounts["4110"], "debit_amount": "0.00", "credit_amount": "50.00"},
            ],
        },
    )
    assert draft_resp2.status_code == 422, draft_resp2.text
    assert "مقفلة" in draft_resp2.text or "locked" in draft_resp2.text.lower()

    # 7. Create a regular user who has "user" role (no period_lock.manage)
    app_client.post(
        "/api/users",
        json={
            "username": "regular.accountant",
            "full_name": "Regular Accountant",
            "password": "password123",
            "role_names": ["user"],
        },
    )
    # Log out admin and log in as regular user
    app_client.post("/api/auth/logout")
    login(app_client, username="regular.accountant", password="password123")

    # 8. Try to unlock the locked period. It must fail with 403 Forbidden!
    unlock_resp = app_client.patch(f"/api/settings/fiscal-periods/{period_id}", json={"is_locked": False})
    assert unlock_resp.status_code in [403, 401], unlock_resp.text

