from __future__ import annotations

from datetime import date

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


def test_trial_balance_ignores_draft_entries(app_client: TestClient) -> None:
    login(app_client)
    account_ids = _chart_map(app_client)
    created = app_client.post("/api/accounting/journal-entries", json=_draft_payload(account_ids))
    assert created.status_code == 201

    response = app_client.get("/api/accounting/trial-balance")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["entry_count"] == 0
    assert payload["summary"]["balance_debit_total"] == "0.00"
    assert payload["summary"]["balance_credit_total"] == "0.00"



def test_trial_balance_reports_posted_balances(app_client: TestClient) -> None:
    login(app_client)
    account_ids = _chart_map(app_client)
    created = app_client.post("/api/accounting/journal-entries", json=_draft_payload(account_ids, amount="300.00"))
    assert created.status_code == 201
    entry_id = created.json()["id"]
    posted = app_client.post(f"/api/accounting/journal-entries/{entry_id}/post")
    assert posted.status_code == 200

    response = app_client.get("/api/accounting/trial-balance")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["entry_count"] == 1
    assert payload["summary"]["movement_debit_total"] == "300.00"
    assert payload["summary"]["movement_credit_total"] == "300.00"
    assert payload["summary"]["balance_debit_total"] == "300.00"
    assert payload["summary"]["balance_credit_total"] == "300.00"
    cash_row = next(row for row in payload["rows"] if row["account_code"] == "1000")
    revenue_row = next(row for row in payload["rows"] if row["account_code"] == "4100")
    assert cash_row["balance_debit"] == "300.00"
    assert revenue_row["balance_credit"] == "300.00"



def test_trial_balance_nets_reversed_entries(app_client: TestClient) -> None:
    login(app_client)
    account_ids = _chart_map(app_client)
    created = app_client.post("/api/accounting/journal-entries", json=_draft_payload(account_ids, amount="200.00"))
    assert created.status_code == 201
    entry_id = created.json()["id"]
    assert app_client.post(f"/api/accounting/journal-entries/{entry_id}/post").status_code == 200
    assert app_client.post(
        f"/api/accounting/journal-entries/{entry_id}/reverse",
        json={"notes": "TB reverse"},
    ).status_code == 200

    response = app_client.get("/api/accounting/trial-balance?include_zero_accounts=true")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["entry_count"] == 2
    assert payload["summary"]["balance_debit_total"] == "0.00"
    assert payload["summary"]["balance_credit_total"] == "0.00"
    cash_row = next(row for row in payload["rows"] if row["account_code"] == "1000")
    assert cash_row["movement_debit"] == "200.00"
    assert cash_row["movement_credit"] == "200.00"
    assert cash_row["balance_debit"] == "0.00"
    assert cash_row["balance_credit"] == "0.00"



def test_regular_user_can_view_trial_balance(app_client: TestClient) -> None:
    login(app_client)
    create_user = app_client.post(
        "/api/users",
        json={
            "username": "trial.viewer",
            "full_name": "Trial Viewer",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_user.status_code == 201
    app_client.post("/api/auth/logout")
    login(app_client, username="trial.viewer", password="secret123")

    response = app_client.get("/api/accounting/trial-balance")
    assert response.status_code == 200
