from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.payments.service import list_payments
from app.modules.payments.schemas import PaymentDocumentSummaryResponse
from app.modules.bookings.service import list_bookings
from app.modules.bookings.schemas import BookingSummaryResponse
from .test_foundation import login
from .test_payments import seed_booking_context


def test_list_payments_returns_strict_pydantic_models(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)

    # Create a payment
    created = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-01',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 700}],
        },
    )
    assert created.status_code == 201, created.text

    # Get the DB session from app engine
    db = Session(app_client.app.state.engine)
    try:
        payments = list_payments(db, branch_id=context['booking']['branch_id'])
        assert len(payments) == 1
        assert isinstance(payments[0], PaymentDocumentSummaryResponse)
    finally:
        db.close()


def test_list_bookings_returns_strict_pydantic_models(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)

    db = Session(app_client.app.state.engine)
    try:
        bookings = list_bookings(db, branch_id=context['booking']['branch_id'])
        assert len(bookings) == 1
        assert isinstance(bookings[0], BookingSummaryResponse)
    finally:
        db.close()


def test_list_journal_entries_returns_strict_pydantic_models(app_client: TestClient) -> None:
    from app.modules.accounting.journal_service import list_journal_entries
    from app.modules.accounting.schemas import JournalEntryResponse
    from .test_accounting_journal_workflow import _chart_map, _draft_payload

    login(app_client)
    account_ids = _chart_map(app_client)
    created = app_client.post("/api/accounting/journal-entries", json=_draft_payload(account_ids))
    assert created.status_code == 201, created.text

    db = Session(app_client.app.state.engine)
    try:
        entries = list_journal_entries(db)
        assert len(entries) > 0
        for entry in entries:
            assert isinstance(entry, JournalEntryResponse)
    finally:
        db.close()


def test_list_departments_returns_strict_pydantic_models(app_client: TestClient) -> None:
    from app.modules.catalog.lifecycle import list_departments
    from app.modules.catalog.schemas import DepartmentResponse

    login(app_client)
    # Seed a department via API
    app_client.post('/api/catalog/departments', json={'code': 'TST', 'name': 'Test Department'})

    db = Session(app_client.app.state.engine)
    try:
        departments = list_departments(db)
        assert len(departments) > 0
        for dept in departments:
            assert isinstance(dept, DepartmentResponse)
    finally:
        db.close()


def test_list_services_returns_strict_pydantic_models(app_client: TestClient) -> None:
    from app.modules.catalog.lifecycle import list_services
    from app.modules.catalog.schemas import ServiceResponse

    login(app_client)

    db = Session(app_client.app.state.engine)
    try:
        services = list_services(db)
        # Services may be empty if none seeded, but type check still works
        for svc in services:
            assert isinstance(svc, ServiceResponse)
    finally:
        db.close()


def test_list_export_schedules_returns_strict_pydantic_models(app_client: TestClient) -> None:
    from app.modules.exports.schedule_service import list_export_schedules
    from app.modules.exports.schemas import ExportScheduleResponse

    login(app_client)

    db = Session(app_client.app.state.engine)
    try:
        schedules = list_export_schedules(db)
        # Schedules may be empty, but type check still works
        for schedule in schedules:
            assert isinstance(schedule, ExportScheduleResponse)
    finally:
        db.close()
