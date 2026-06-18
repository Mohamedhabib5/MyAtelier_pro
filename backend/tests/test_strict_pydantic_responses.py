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
