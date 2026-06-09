from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.accounting.models import ChartOfAccount
from app.modules.organization.models import DocumentSequence
from .conftest import build_test_client
from .test_foundation import login


def test_chart_of_accounts_seeded_and_exposed(app_client: TestClient) -> None:
    login(app_client)
    response = app_client.get("/api/accounting/chart-of-accounts")
    assert response.status_code == 200, response.text

    rows = response.json()
    expected_codes = [
        "1000", "1100", "1110", "1111", "1111001", "1112", "1112001", "1120", "1121", "1121001",
        "1200", "2000", "2100", "2110", "2120", "2121", "2121001", "2200", "3000", "3100", "4000",
        "4100", "4110", "5000", "5100", "5110", "5120", "5130", "5140", "5150"
    ]
    assert [row["code"] for row in rows] == expected_codes
    assert rows[0]["account_type"] == "asset"
    assert rows[-1]["account_type"] == "expense"

    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        sequence = db.scalars(
            select(DocumentSequence).where(DocumentSequence.key == "journal_entry")
        ).first()
    assert sequence is not None
    assert sequence.prefix == "JV"


def test_regular_user_can_view_accounting_foundation(app_client: TestClient) -> None:
    login(app_client)
    create_user = app_client.post(
        "/api/users",
        json={
            "username": "account.viewer",
            "full_name": "Account Viewer",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_user.status_code == 201

    app_client.post("/api/auth/logout")
    login(app_client, username="account.viewer", password="secret123")

    response = app_client.get("/api/accounting/chart-of-accounts")
    assert response.status_code == 200
    assert len(response.json()) == 30


def test_accounting_foundation_seeded_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "accounting-seed.db"
    storage_root = tmp_path / "storage"

    with build_test_client(db_path, storage_root, monkeypatch) as first_client:
        login(first_client)
        first_rows = first_client.get("/api/accounting/chart-of-accounts").json()
        assert len(first_rows) == 30

    with build_test_client(db_path, storage_root, monkeypatch) as second_client:
        login(second_client)
        second_rows = second_client.get("/api/accounting/chart-of-accounts").json()
        assert len(second_rows) == 30
        assert [row["code"] for row in second_rows] == [row["code"] for row in first_rows]

        session_factory = second_client.app.state.session_factory
        with session_factory() as db:
            accounts = db.scalars(select(ChartOfAccount)).all()
        assert len(accounts) == 30


def test_accounting_tree_level_and_posting_rules(app_client: TestClient) -> None:
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    from decimal import Decimal
    from app.modules.accounting.tree_service import validate_account_creation
    from app.core.exceptions import ValidationAppError
    from app.modules.organization.service import get_company_settings
    
    with session_factory() as db:
        company = get_company_settings(db)
        
        # Find Level 5 leaf account (e.g. 1111001)
        level5_acc = db.query(ChartOfAccount).filter(
            ChartOfAccount.code == "1111001",
            ChartOfAccount.company_id == company.id
        ).first()
        
        assert level5_acc is not None
        assert level5_acc.level == 5
        assert level5_acc.allows_posting is True
        
        # 1. Tree Level Check: Attempt to create a level 6 account under a level 5 account must fail
        with pytest.raises(ValidationAppError) as exc_info:
            validate_account_creation(
                db, 
                company_id=company.id, 
                code="1111002", 
                parent_account_id=level5_acc.id
            )
        assert "لا يمكن إنشاء حساب في مستوى يتعدى 5 مستويات" in str(exc_info.value)
        
        # 2. Dynamic Parent Transition: Let's create a dummy Level 4 account that is initially a leaf:
        dummy_acc = ChartOfAccount(
            company_id=company.id,
            code="1113",
            name="صندوق افتراضي",
            account_type=level5_acc.account_type,
            parent_account_id=level5_acc.parent_account_id, # Parent is 1110 (Level 3)
            level=4,
            allows_posting=True,
            is_active=True
        )
        db.add(dummy_acc)
        db.commit()
        
        # Now, create a child under dummy_acc (Level 5 child)
        new_child_level = validate_account_creation(
            db, 
            company_id=company.id, 
            code="1113001", 
            parent_account_id=dummy_acc.id
        )
        assert new_child_level == 5
        
        # Ensure parent allows_posting transitioned to False!
        assert dummy_acc.allows_posting is False
        
        # 3. Summary Account Block Check: Attempting to create a journal entry line using a summary account (allows_posting = False) must raise ValidationAppError
        # We have a summary account "1000" which has allows_posting = False.
        from app.modules.accounting.journal_service import _build_lines
        from app.modules.accounting.repository import AccountingRepository
        from app.modules.accounting.schemas import JournalEntryLineWriteRequest
        
        repo = AccountingRepository(db)
        summary_acc = db.query(ChartOfAccount).filter(
            ChartOfAccount.code == "1000",
            ChartOfAccount.company_id == company.id
        ).first()
        
        assert summary_acc is not None
        assert summary_acc.allows_posting is False
        
        # Construct payload with a summary account
        line_payloads = [
            JournalEntryLineWriteRequest(
                account_id=summary_acc.id,
                description="Invalid line",
                debit_amount=Decimal("100.00"),
                credit_amount=Decimal("0.00")
            ),
            JournalEntryLineWriteRequest(
                account_id=level5_acc.id,
                description="Valid line",
                debit_amount=Decimal("0.00"),
                credit_amount=Decimal("100.00")
            )
        ]
        
        with pytest.raises(ValidationAppError) as exc_info2:
            _build_lines(repo, company.id, line_payloads)
        assert "غير متاح للترحيل" in str(exc_info2.value)
