"""Phase 2: Party validation + customer statement integration tests."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from .test_bookings import build_booking_line_payload, create_booking_document, seed_customer, seed_service_bundle
from .test_foundation import login
from .test_payments import seed_booking_context


def _chart_map(client: TestClient) -> dict[str, str]:
    response = client.get("/api/accounting/chart-of-accounts")
    assert response.status_code == 200, response.text
    return {row["code"]: row["id"] for row in response.json()}


# ---------------------------------------------------------------------------
# Party Validation Tests
# ---------------------------------------------------------------------------


def test_party_type_validation_rejects_invalid_type(app_client: TestClient) -> None:
    """Manual journal entry with party_type='unknown' must be rejected."""
    login(app_client)
    accounts = _chart_map(app_client)

    response = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": str(date.today()),
            "reference": "PARTY-BAD-TYPE",
            "lines": [
                {
                    "account_id": accounts["1111001"],
                    "debit_amount": "100.00",
                    "credit_amount": "0.00",
                    "party_type": "unknown",
                    "party_id": "some-id",
                },
                {
                    "account_id": accounts["4110"],
                    "debit_amount": "0.00",
                    "credit_amount": "100.00",
                },
            ],
        },
    )
    assert response.status_code == 422, response.text
    assert "غير مدعوم" in response.json()["detail"]


def test_party_type_validation_rejects_partial_party(app_client: TestClient) -> None:
    """party_type without party_id (or vice versa) must be rejected."""
    login(app_client)
    accounts = _chart_map(app_client)

    # party_type without party_id
    response = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": str(date.today()),
            "reference": "PARTY-PARTIAL",
            "lines": [
                {
                    "account_id": accounts["1111001"],
                    "debit_amount": "200.00",
                    "credit_amount": "0.00",
                    "party_type": "customer",
                },
                {
                    "account_id": accounts["4110"],
                    "debit_amount": "0.00",
                    "credit_amount": "200.00",
                },
            ],
        },
    )
    assert response.status_code == 422, response.text
    assert "معًا" in response.json()["detail"]


def test_party_type_validation_allows_valid_types(app_client: TestClient) -> None:
    """Manual journal entry with party_type='customer' and valid party_id must succeed."""
    login(app_client)
    accounts = _chart_map(app_client)
    customer_id = seed_customer(app_client)

    response = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": str(date.today()),
            "reference": "PARTY-VALID",
            "lines": [
                {
                    "account_id": accounts["1121001"],
                    "debit_amount": "300.00",
                    "credit_amount": "0.00",
                    "party_type": "customer",
                    "party_id": customer_id,
                },
                {
                    "account_id": accounts["4110"],
                    "debit_amount": "0.00",
                    "credit_amount": "300.00",
                },
            ],
        },
    )
    assert response.status_code == 201, response.text
    journal = response.json()
    assert journal["lines"][0]["party_type"] == "customer"
    assert journal["lines"][0]["party_id"] == customer_id
    assert journal["lines"][1]["party_type"] is None


# ---------------------------------------------------------------------------
# Customer Statement Tests
# ---------------------------------------------------------------------------


def test_customer_statement_after_payment_and_revenue(app_client: TestClient) -> None:
    """Full flow: create payment + complete booking → customer statement must show both."""
    login(app_client)
    context = seed_booking_context(app_client)
    customer_id = context["customer_id"]

    # 1. Create a payment (advances entry)
    payment = app_client.post(
        "/api/payments",
        json={
            "customer_id": customer_id,
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
    assert payment.status_code == 201, payment.text

    # 2. Complete the booking line (revenue recognition entry)
    complete = app_client.post(
        f"/api/bookings/{context['booking_id']}/lines/{context['line_id']}/complete"
    )
    assert complete.status_code == 200, complete.text

    # 3. Query the customer statement via the service
    from app.modules.accounting.party_ledger_service import get_party_statement
    from app.modules.organization.service import get_company_settings

    from sqlalchemy.orm import Session
    engine = app_client.app.state.engine
    with Session(engine) as db:
        company = get_company_settings(db)
        statement = get_party_statement(db, company.id, "customer", customer_id)

    assert statement["party_type"] == "customer"
    assert statement["party_id"] == customer_id
    assert statement["party_name"] is not None
    assert len(statement["movements"]) > 0
    assert statement["closing_balance"] == statement["opening_balance"] + statement["total_debit"] - statement["total_credit"]

    # Verify numeric consistency: each movement has a running balance
    running = statement["opening_balance"]
    for movement in statement["movements"]:
        running += movement["debit_amount"] - movement["credit_amount"]
        assert movement["running_balance"] == running
    assert running == statement["closing_balance"]


def test_customer_statement_date_filtering(app_client: TestClient) -> None:
    """Statement with date filters should only include movements in range."""
    login(app_client)
    context = seed_booking_context(app_client)
    customer_id = context["customer_id"]

    # Create two payments on different dates
    for pay_date in ["2026-06-01", "2026-06-10"]:
        resp = app_client.post(
            "/api/payments",
            json={
                "customer_id": customer_id,
                "payment_date": pay_date,
                "allocations": [
                    {
                        "booking_id": context["booking_id"],
                        "booking_line_id": context["line_id"],
                        "allocated_amount": 500,
                    }
                ],
            },
        )
        assert resp.status_code == 201, resp.text

    from app.modules.accounting.party_ledger_service import get_party_statement
    from app.modules.organization.service import get_company_settings
    from sqlalchemy.orm import Session

    engine = app_client.app.state.engine

    # Full statement (no date filter)
    with Session(engine) as db:
        company = get_company_settings(db)
        full_statement = get_party_statement(db, company.id, "customer", customer_id)

    # Filtered: only June 10
    with Session(engine) as db:
        company = get_company_settings(db)
        filtered = get_party_statement(
            db, company.id, "customer", customer_id,
            from_date=date(2026, 6, 10),
            to_date=date(2026, 6, 10),
        )

    # Full should have more movements than filtered
    assert len(full_statement["movements"]) > len(filtered["movements"])
    # Filtered should have an opening balance (from the June 1 payment)
    assert filtered["opening_balance"] != Decimal("0.00")
    # All filtered movement dates should be June 10
    for m in filtered["movements"]:
        assert str(m["entry_date"]) == "2026-06-10"
