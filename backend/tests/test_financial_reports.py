from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient

from app.modules.organization.service import get_company_settings
from app.modules.organization.models import Branch
from .test_bookings import seed_customer
from .test_foundation import login


def _chart_map(client: TestClient) -> dict[str, str]:
    response = client.get("/api/accounting/chart-of-accounts")
    assert response.status_code == 200, response.text
    return {row["code"]: row["id"] for row in response.json()}


def create_second_branch(client: TestClient) -> str:
    with client.app.state.session_factory() as db:
        company = get_company_settings(db)
        branch = Branch(
            company_id=company.id,
            code='WEST',
            name='West Branch',
            is_default=False,
            is_active=True,
        )
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch.id


def test_multi_branch_trial_balance_and_income_statement(app_client: TestClient) -> None:
    """
    Test Step 1: Multi-Branch Trial Balance
    and Step 2: Branch-Specific Income Statement.
    """
    auth = login(app_client)
    default_branch_id = auth["active_branch_id"]
    second_branch_id = create_second_branch(app_client)
    account_ids = _chart_map(app_client)

    today_str = str(date.today())

    # 1. Post Revenue of 300 to Branch A (Default Branch)
    created_a1 = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": today_str,
            "reference": "REV-BRANCH-A",
            "branch_id": default_branch_id,
            "lines": [
                {
                    "account_id": account_ids["1111001"],  # main cash
                    "debit_amount": "300.00",
                    "credit_amount": "0.00",
                },
                {
                    "account_id": account_ids["4110"],  # service revenue
                    "debit_amount": "0.00",
                    "credit_amount": "300.00",
                },
            ],
        },
    )
    assert created_a1.status_code == 201, created_a1.text
    entry_a1_id = created_a1.json()["id"]
    post_a1 = app_client.post(f"/api/accounting/journal-entries/{entry_a1_id}/post")
    assert post_a1.status_code == 200, post_a1.text

    # 2. Post Expense of 100 to Branch A (Default Branch)
    created_a2 = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": today_str,
            "reference": "EXP-BRANCH-A",
            "branch_id": default_branch_id,
            "lines": [
                {
                    "account_id": account_ids["5100"],  # operating expense
                    "debit_amount": "100.00",
                    "credit_amount": "0.00",
                },
                {
                    "account_id": account_ids["1111001"],  # main cash
                    "debit_amount": "0.00",
                    "credit_amount": "100.00",
                },
            ],
        },
    )
    assert created_a2.status_code == 201, created_a2.text
    entry_a2_id = created_a2.json()["id"]
    post_a2 = app_client.post(f"/api/accounting/journal-entries/{entry_a2_id}/post")
    assert post_a2.status_code == 200, post_a2.text

    # 3. Post Revenue of 500 to Branch B (West Branch)
    created_b = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": today_str,
            "reference": "REV-BRANCH-B",
            "branch_id": second_branch_id,
            "lines": [
                {
                    "account_id": account_ids["1111001"],  # main cash
                    "debit_amount": "500.00",
                    "credit_amount": "0.00",
                },
                {
                    "account_id": account_ids["4110"],  # service revenue
                    "debit_amount": "0.00",
                    "credit_amount": "500.00",
                },
            ],
        },
    )
    assert created_b.status_code == 201, created_b.text
    entry_b_id = created_b.json()["id"]
    post_b = app_client.post(f"/api/accounting/journal-entries/{entry_b_id}/post")
    assert post_b.status_code == 200, post_b.text

    # --- VERIFY TRIAL BALANCE ---

    # A. Consolidated Trial Balance (No branch_id)
    response_tb_con = app_client.get("/api/accounting/trial-balance")
    assert response_tb_con.status_code == 200, response_tb_con.text
    tb_con = response_tb_con.json()
    assert tb_con["summary"]["entry_count"] == 3
    # Main cash (1111001): 300 debit - 100 credit + 500 debit = 700 debit net balance
    cash_con = next(r for r in tb_con["rows"] if r["account_code"] == "1111001")
    assert cash_con["balance_debit"] == "700.00"
    assert cash_con["balance_credit"] == "0.00"

    # B. Branch A Trial Balance
    response_tb_a = app_client.get(f"/api/accounting/trial-balance?branch_id={default_branch_id}")
    assert response_tb_a.status_code == 200, response_tb_a.text
    tb_a = response_tb_a.json()
    assert tb_a["branch_id"] == default_branch_id
    assert tb_a["summary"]["entry_count"] == 2
    cash_a = next(r for r in tb_a["rows"] if r["account_code"] == "1111001")
    assert cash_a["balance_debit"] == "200.00"  # 300 - 100

    # C. Branch B Trial Balance
    response_tb_b = app_client.get(f"/api/accounting/trial-balance?branch_id={second_branch_id}")
    assert response_tb_b.status_code == 200, response_tb_b.text
    tb_b = response_tb_b.json()
    assert tb_b["branch_id"] == second_branch_id
    assert tb_b["summary"]["entry_count"] == 1
    cash_b = next(r for r in tb_b["rows"] if r["account_code"] == "1111001")
    assert cash_b["balance_debit"] == "500.00"

    # --- VERIFY INCOME STATEMENT ---

    # A. Branch A Income Statement
    response_is_a = app_client.get(f"/api/accounting/income-statement?branch_id={default_branch_id}")
    assert response_is_a.status_code == 200, response_is_a.text
    is_a = response_is_a.json()
    assert is_a["branch_id"] == default_branch_id
    assert is_a["revenues"]["total"] == "300.00"
    assert is_a["expenses"]["total"] == "100.00"
    assert is_a["net_income"] == "200.00"

    # B. Branch B Income Statement
    response_is_b = app_client.get(f"/api/accounting/income-statement?branch_id={second_branch_id}")
    assert response_is_b.status_code == 200, response_is_b.text
    is_b = response_is_b.json()
    assert is_b["branch_id"] == second_branch_id
    assert is_b["revenues"]["total"] == "500.00"
    assert is_b["expenses"]["total"] == "0.00"
    assert is_b["net_income"] == "500.00"

    # C. Consolidated Income Statement
    response_is_con = app_client.get("/api/accounting/income-statement")
    assert response_is_con.status_code == 200, response_is_con.text
    is_con = response_is_con.json()
    assert is_con["branch_id"] is None
    assert is_con["revenues"]["total"] == "800.00"
    assert is_con["expenses"]["total"] == "100.00"
    assert is_con["net_income"] == "700.00"


def test_customer_aging_fifo_calculation(app_client: TestClient) -> None:
    """
    Test Step 3: FIFO Customer Aging Report
    """
    login(app_client)
    customer_id = seed_customer(app_client)
    account_ids = _chart_map(app_client)

    today = date.today()
    date_10_days_ago = str(today - timedelta(days=10))
    date_40_days_ago = str(today - timedelta(days=40))
    date_100_days_ago = str(today - timedelta(days=100))

    # 1. Post Charge 1: 100 days ago, amount 300.00
    c1 = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": date_100_days_ago,
            "reference": "SALE-INV-1",
            "lines": [
                {
                    "account_id": account_ids["1121001"],  # Receivable
                    "debit_amount": "300.00",
                    "credit_amount": "0.00",
                    "party_type": "customer",
                    "party_id": customer_id,
                },
                {
                    "account_id": account_ids["4110"],  # Service Revenue
                    "debit_amount": "0.00",
                    "credit_amount": "300.00",
                },
            ],
        },
    )
    assert c1.status_code == 201, c1.text
    app_client.post(f"/api/accounting/journal-entries/{c1.json()['id']}/post")

    # 2. Post Charge 2: 40 days ago, amount 200.00
    c2 = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": date_40_days_ago,
            "reference": "SALE-INV-2",
            "lines": [
                {
                    "account_id": account_ids["1121001"],  # Receivable
                    "debit_amount": "200.00",
                    "credit_amount": "0.00",
                    "party_type": "customer",
                    "party_id": customer_id,
                },
                {
                    "account_id": account_ids["4110"],  # Service Revenue
                    "debit_amount": "0.00",
                    "credit_amount": "200.00",
                },
            ],
        },
    )
    assert c2.status_code == 201, c2.text
    app_client.post(f"/api/accounting/journal-entries/{c2.json()['id']}/post")

    # 3. Post Charge 3: 10 days ago, amount 100.00
    c3 = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": date_10_days_ago,
            "reference": "SALE-INV-3",
            "lines": [
                {
                    "account_id": account_ids["1121001"],  # Receivable
                    "debit_amount": "100.00",
                    "credit_amount": "0.00",
                    "party_type": "customer",
                    "party_id": customer_id,
                },
                {
                    "account_id": account_ids["4110"],  # Service Revenue
                    "debit_amount": "0.00",
                    "credit_amount": "100.00",
                },
            ],
        },
    )
    assert c3.status_code == 201, c3.text
    app_client.post(f"/api/accounting/journal-entries/{c3.json()['id']}/post")

    # 4. Post Payment: today, amount 350.00 (credit to receivable)
    pay = app_client.post(
        "/api/accounting/journal-entries",
        json={
            "entry_date": str(today),
            "reference": "CUST-PAYMENT",
            "lines": [
                {
                    "account_id": account_ids["1111001"],  # main cash
                    "debit_amount": "350.00",
                    "credit_amount": "0.00",
                },
                {
                    "account_id": account_ids["1121001"],  # Receivable credit
                    "debit_amount": "0.00",
                    "credit_amount": "350.00",
                    "party_type": "customer",
                    "party_id": customer_id,
                },
            ],
        },
    )
    assert pay.status_code == 201, pay.text
    app_client.post(f"/api/accounting/journal-entries/{pay.json()['id']}/post")

    # --- QUERY AGING REPORT ---
    response = app_client.get(f"/api/accounting/aging?party_type=customer&as_of_date={str(today)}")
    assert response.status_code == 200, response.text
    aging = response.json()

    assert aging["party_type"] == "customer"
    assert aging["total_receivable_or_payable"] == "250.00"  # (300 + 200 + 100) - 350 = 250
    assert len(aging["rows"]) == 1

    row = aging["rows"][0]
    assert row["party_id"] == customer_id
    assert row["party_name"] == "Bride One"
    assert row["total_outstanding"] == "250.00"

    # FIFO application:
    # 350 total decreases applied to:
    # - 300 (100 days ago) -> 300 satisfied, 0 remaining outstanding. 50 remaining payment.
    # - 200 (40 days ago) -> 50 satisfied, 150 remaining outstanding. 0 remaining payment.
    # - 100 (10 days ago) -> 0 satisfied, 100 remaining outstanding.
    # Buckets:
    # - current (0-30 days): 10 days ago -> 100.00
    # - 31-60 days: 40 days ago -> 150.00
    # - 61-90 days: 0.00
    # - 91+ days: 100 days ago -> 0.00
    buckets = row["buckets"]
    assert buckets["current"] == "100.00"
    assert buckets["31-60"] == "150.00"
    assert buckets["61-90"] == "0.00"
    assert buckets["91+"] == "0.00"
