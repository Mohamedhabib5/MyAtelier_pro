from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login
from .test_payment_accounting_link import _get_journal
from .test_payments import seed_booking_context


def test_void_payment_reverses_linked_journal_and_updates_summaries(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)

    created = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-01',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 700}],
        },
    )
    assert created.status_code == 201, created.text
    payment = created.json()

    voided = app_client.post(
        f"/api/payments/{payment['id']}/void",
        json={'void_date': '2026-06-02', 'reason': 'تم الإلغاء بطلب العميل'},
    )
    assert voided.status_code == 200, voided.text
    voided_payment = voided.json()
    assert voided_payment['status'] == 'voided'
    assert voided_payment['void_reason'] == 'تم الإلغاء بطلب العميل'
    assert voided_payment['journal_entry_status'] == 'reversed'

    journal = _get_journal(app_client, payment['journal_entry_id'])
    assert journal['status'] == 'reversed'

    dashboard = app_client.get('/api/dashboard/finance')
    assert dashboard.status_code == 200, dashboard.text
    assert dashboard.json()['total_income'] == 0.0
    assert dashboard.json()['total_remaining'] == 3000.0


def test_voided_payment_cannot_be_updated_and_replacement_collection_updates_remaining(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)

    created = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-01',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 500}],
        },
    )
    assert created.status_code == 201, created.text
    payment = created.json()

    voided = app_client.post(
        f"/api/payments/{payment['id']}/void",
        json={'void_date': '2026-06-02', 'reason': 'دفعة أُدخلت بالخطأ'},
    )
    assert voided.status_code == 200, voided.text

    updated = app_client.patch(
        f"/api/payments/{payment['id']}",
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-03',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 600}],
        },
    )
    assert updated.status_code == 422
    assert 'المبطلة' in updated.json()['detail']

    replacement = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-03',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 3000}],
        },
    )
    assert replacement.status_code == 201, replacement.text

    booking = app_client.get(f"/api/bookings/{context['booking_id']}")
    assert booking.status_code == 200, booking.text
    line = booking.json()['lines'][0]
    assert line['paid_total'] == 3000.0
    assert line['remaining_amount'] == 0.0


def test_void_payment_rejects_invalid_reason_code(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)

    created = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-01',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 700}],
        },
    )
    assert created.status_code == 201, created.text
    payment = created.json()

    invalid = app_client.post(
        f"/api/payments/{payment['id']}/void",
        json={'void_date': '2026-06-02', 'reason_code': 'not_allowed', 'reason': 'سند تم إدخاله بطريقة خاطئة'},
    )
    assert invalid.status_code == 422
    assert 'رمز السبب غير صالح' in invalid.json()['detail']
