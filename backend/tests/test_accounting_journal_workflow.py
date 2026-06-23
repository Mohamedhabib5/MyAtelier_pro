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
                "account_id": account_ids["1111001"],
                "description": "Cash received",
                "debit_amount": amount,
                "credit_amount": "0.00",
            },
            {
                "account_id": account_ids["4110"],
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


def test_document_sequence_no_race_condition(app_client: TestClient) -> None:
    if app_client.app.state.engine.dialect.name == "sqlite":
        import pytest
        pytest.skip("SQLite does not support with_for_update locking for concurrency tests")
        
    import concurrent.futures
    login(app_client)
    account_ids = _chart_map(app_client)
    payload = _draft_payload(account_ids)

    def create_journal() -> str | None:
        res = app_client.post("/api/accounting/journal-entries", json=payload)
        if res.status_code == 201:
            return res.json().get("entry_number")
        return None

    # Simulate concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_journal) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    valid_results = [r for r in results if r]
    # Check that all generated sequence numbers are unique
    assert len(set(valid_results)) == len(valid_results), "Duplicate document sequence generated!"

def test_db_level_journal_balance_constraint(db_session, setup_company_and_admin) -> None:
    if db_session.bind.dialect.name == "sqlite":
        import pytest
        pytest.skip("Database-level balance check trigger only works on PostgreSQL")
        
    import uuid
    from psycopg.errors import RaiseException
    from sqlalchemy.exc import IntegrityError, InternalError, ProgrammingError
    from app.modules.accounting.models import JournalEntry, JournalEntryLine
    from app.modules.organization.models import FiscalPeriod

    company = setup_company_and_admin["company"]
    fp = db_session.query(FiscalPeriod).first()
    
    # 1. Create a balanced entry directly in DB
    je_balanced = JournalEntry(
        id=str(uuid.uuid4()),
        company_id=company.id,
        fiscal_period_id=fp.id,
        entry_number="JV-BAL-1",
        entry_date=date.today(),
        status="draft",
    )
    db_session.add(je_balanced)
    db_session.flush()

    line1 = JournalEntryLine(
        id=str(uuid.uuid4()),
        journal_entry_id=je_balanced.id,
        account_id=setup_company_and_admin["admin_user"].id, # just a dummy string for account_id for test
        line_number=1,
        debit_amount=Decimal("100"),
        credit_amount=Decimal("0")
    )
    line2 = JournalEntryLine(
        id=str(uuid.uuid4()),
        journal_entry_id=je_balanced.id,
        account_id=setup_company_and_admin["admin_user"].id,
        line_number=2,
        debit_amount=Decimal("0"),
        credit_amount=Decimal("100")
    )
    db_session.add(line1)
    db_session.add(line2)
    
    # Should commit successfully (balanced)
    db_session.commit()
    
    # 2. Create an UNBALANCED entry directly in DB
    je_unbalanced = JournalEntry(
        id=str(uuid.uuid4()),
        company_id=company.id,
        fiscal_period_id=fp.id,
        entry_number="JV-UNBAL-2",
        entry_date=date.today(),
        status="draft",
    )
    db_session.add(je_unbalanced)
    db_session.flush()

    line3 = JournalEntryLine(
        id=str(uuid.uuid4()),
        journal_entry_id=je_unbalanced.id,
        account_id=setup_company_and_admin["admin_user"].id,
        line_number=1,
        debit_amount=Decimal("100"),
        credit_amount=Decimal("0")
    )
    db_session.add(line3)
    db_session.flush() # Should NOT fail here because initially deferred
    
    # Try to commit unbalanced
    import pytest
    with pytest.raises(Exception) as exc:
        db_session.commit()
    
    assert "not balanced" in str(exc.value) or "Journal entry" in str(exc.value)
    db_session.rollback()

