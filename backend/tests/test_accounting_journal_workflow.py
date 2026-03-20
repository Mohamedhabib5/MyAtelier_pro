from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from .test_foundation import login


def _chart_map(client: TestClient) -> dict[str, str]:
    response = client.get("/api/accounting/chart-of-accounts")
    assert response.status_code == 200, response.text
    return {row["code"]: row["id"] for row in response.json()}


def _draft_payload(account_ids: dict[str, str], amount: str = "500.00") -> dict:
    return {
        "entry_date": str(date.today()),
        "reference": "BOOKING-DEPOSIT",
        "notes": "Initial accounting checkpoint journal",
        "lines": [
            {
                "account_id": account_ids["1000"],
                "description": "Cash received",
                "debit_amount": amount,
                "credit_amount": "0.00",
            },
            {
                "account_id": account_ids["4100"],
                "description": "Service revenue",
                "debit_amount": "0.00",
                "credit_amount": amount,
            },
        ],
    }


def test_admin_can_create_post_and_reverse_journal_entry(app_client: TestClient) -> None:
    login(app_client)
    account_ids = _chart_map(app_client)

    created = app_client.post("/api/accounting/journal-entries", json=_draft_payload(account_ids))
    assert created.status_code == 201, created.text
    draft = created.json()
    assert draft["status"] == "draft"
    assert draft["entry_number"].startswith("JV")
    assert draft["total_debit"] == "500.00"
    assert draft["total_credit"] == "500.00"

    posted = app_client.post(f"/api/accounting/journal-entries/{draft['id']}/post")
    assert posted.status_code == 200, posted.text
    posted_entry = posted.json()
    assert posted_entry["status"] == "posted"
    assert posted_entry["posted_by_user_id"] is not None

    blocked_update = app_client.patch(
        f"/api/accounting/journal-entries/{draft['id']}",
        json=_draft_payload(account_ids, amount="700.00"),
    )
    assert blocked_update.status_code == 422

    reversed_response = app_client.post(
        f"/api/accounting/journal-entries/{draft['id']}/reverse",
        json={"notes": "Reversing posted entry"},
    )
    assert reversed_response.status_code == 200, reversed_response.text
    reversal = reversed_response.json()
    assert reversal["status"] == "posted"
    assert reversal["reference"] == f"REV-{posted_entry['entry_number']}"
    assert reversal["lines"][0]["debit_amount"] == "0.00"
    assert reversal["lines"][0]["credit_amount"] == "500.00"

    original = app_client.get(f"/api/accounting/journal-entries/{draft['id']}")
    assert original.status_code == 200
    assert original.json()["status"] == "reversed"


def test_unbalanced_journal_entry_is_rejected(app_client: TestClient) -> None:
    login(app_client)
    account_ids = _chart_map(app_client)
    payload = _draft_payload(account_ids)
    payload["lines"][1]["credit_amount"] = "400.00"

    response = app_client.post("/api/accounting/journal-entries", json=payload)
    assert response.status_code == 422
    assert "غير متوازن" in response.json()["detail"]



def test_regular_user_cannot_manage_journal_entries(app_client: TestClient) -> None:
    login(app_client)
    create_user = app_client.post(
        "/api/users",
        json={
            "username": "finance.user",
            "full_name": "Finance User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_user.status_code == 201
    account_ids = _chart_map(app_client)

    app_client.post("/api/auth/logout")
    login(app_client, username="finance.user", password="secret123")

    response = app_client.post("/api/accounting/journal-entries", json=_draft_payload(account_ids))
    assert response.status_code == 403



def test_journal_list_and_lookup_are_available(app_client: TestClient) -> None:
    login(app_client)
    account_ids = _chart_map(app_client)
    created = app_client.post("/api/accounting/journal-entries", json=_draft_payload(account_ids))
    assert created.status_code == 201
    entry_id = created.json()["id"]

    listing = app_client.get("/api/accounting/journal-entries")
    assert listing.status_code == 200
    assert any(item["id"] == entry_id for item in listing.json())

    detail = app_client.get(f"/api/accounting/journal-entries/{entry_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == entry_id
