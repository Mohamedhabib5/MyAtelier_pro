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
    assert [row["code"] for row in rows] == ["1000", "1100", "1200", "2100", "2200", "3100", "4100", "5100"]
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
    assert len(response.json()) == 8


def test_accounting_foundation_seeded_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "accounting-seed.db"
    storage_root = tmp_path / "storage"

    with build_test_client(db_path, storage_root, monkeypatch) as first_client:
        login(first_client)
        first_rows = first_client.get("/api/accounting/chart-of-accounts").json()
        assert len(first_rows) == 8

    with build_test_client(db_path, storage_root, monkeypatch) as second_client:
        login(second_client)
        second_rows = second_client.get("/api/accounting/chart-of-accounts").json()
        assert len(second_rows) == 8
        assert [row["code"] for row in second_rows] == [row["code"] for row in first_rows]

        session_factory = second_client.app.state.session_factory
        with session_factory() as db:
            accounts = db.scalars(select(ChartOfAccount)).all()
        assert len(accounts) == 8
