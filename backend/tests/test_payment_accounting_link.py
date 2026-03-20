from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import build_booking_line_payload, create_booking_document, seed_customer, seed_service_bundle
from .test_foundation import login
from .test_payments import seed_booking_context


def _get_journal(client: TestClient, entry_id: str) -> dict:
    response = client.get(f'/api/accounting/journal-entries/{entry_id}')
    assert response.status_code == 200, response.text
    return response.json()


def test_payment_creation_auto_posts_linked_journal_entry(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)

    created = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-01',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 1000}],
        },
    )
    assert created.status_code == 201, created.text
    payment = created.json()
    assert payment['journal_entry_id'] is not None
    assert payment['journal_entry_number'].startswith('JV')
    assert payment['journal_entry_status'] == 'posted'

    journal = _get_journal(app_client, payment['journal_entry_id'])
    assert journal['reference'] == payment['payment_number']
    assert journal['status'] == 'posted'
    assert journal['lines'][0]['account_code'] == '1000'
    assert journal['lines'][0]['debit_amount'] == '1000.00'
    assert journal['lines'][1]['account_code'] == '2100'
    assert journal['lines'][1]['credit_amount'] == '1000.00'


def test_payment_update_reverses_old_journal_and_relinks_payment(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)

    created = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-01',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 800}],
        },
    )
    assert created.status_code == 201, created.text
    original_payment = created.json()
    original_journal_id = original_payment['journal_entry_id']

    updated = app_client.patch(
        f"/api/payments/{original_payment['id']}",
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-02',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 900}],
        },
    )
    assert updated.status_code == 200, updated.text
    updated_payment = updated.json()
    assert updated_payment['journal_entry_id'] != original_journal_id
    assert updated_payment['journal_entry_status'] == 'posted'

    original_journal = _get_journal(app_client, original_journal_id)
    assert original_journal['status'] == 'reversed'
    replacement_journal = _get_journal(app_client, updated_payment['journal_entry_id'])
    assert replacement_journal['status'] == 'posted'
    assert replacement_journal['reference'] == updated_payment['payment_number']


def test_mixed_payment_document_splits_advances_and_receivables(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client, department_code='MAKEUP', department_name='قسم المكياج', service_name='خدمة تجريبية', default_price=1200)

    booking_one = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-07-01', line_price=1800)],
    )
    booking_two = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-07-02', line_price=2000)],
    )
    second_line_id = booking_two['lines'][0]['id']

    complete_second = app_client.post(f"/api/bookings/{booking_two['id']}/lines/{second_line_id}/complete")
    assert complete_second.status_code == 200, complete_second.text

    created = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-06-05',
            'allocations': [
                {'booking_id': booking_one['id'], 'booking_line_id': booking_one['lines'][0]['id'], 'allocated_amount': 250},
                {'booking_id': booking_two['id'], 'booking_line_id': second_line_id, 'allocated_amount': 400},
            ],
        },
    )
    assert created.status_code == 201, created.text
    payment = created.json()

    journal = _get_journal(app_client, payment['journal_entry_id'])
    lines = {line['account_code']: line for line in journal['lines']}
    assert str(lines['1000']['debit_amount']) == '650.00'
    assert str(lines['2100']['credit_amount']) == '250.00'
    assert str(lines['1200']['credit_amount']) == '400.00'
