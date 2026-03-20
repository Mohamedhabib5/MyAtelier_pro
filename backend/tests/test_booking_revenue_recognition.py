from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import (
    build_booking_document_payload,
    build_booking_line_payload,
    create_booking_document,
    seed_customer,
    seed_service_bundle,
)
from .test_foundation import login


def test_complete_booking_line_recognizes_revenue_and_locks_line(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client, department_code='MAKEUP', department_name='قسم المكياج', service_name='مكياج مناسبات', default_price=900)

    booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-07-01', line_price=2500)],
    )
    line_id = booking['lines'][0]['id']

    payment_response = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-03-16',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': line_id, 'allocated_amount': 1000}],
        },
    )
    assert payment_response.status_code == 201, payment_response.text

    complete_response = app_client.post(f"/api/bookings/{booking['id']}/lines/{line_id}/complete")
    assert complete_response.status_code == 200, complete_response.text
    completed = complete_response.json()
    completed_line = completed['lines'][0]
    assert completed['status'] == 'completed'
    assert completed_line['status'] == 'completed'
    assert completed_line['revenue_journal_entry_number'].startswith('JV')

    journal_response = app_client.get(f"/api/accounting/journal-entries/{completed_line['revenue_journal_entry_id']}")
    assert journal_response.status_code == 200, journal_response.text
    journal = journal_response.json()
    lines = {line['account_code']: line for line in journal['lines']}
    assert str(lines['2100']['debit_amount']) == '1000.00'
    assert str(lines['1200']['debit_amount']) == '1500.00'
    assert str(lines['4100']['credit_amount']) == '2500.00'

    update_response = app_client.patch(
        f"/api/bookings/{booking['id']}",
        json=build_booking_document_payload(
            customer_id,
            [
                {
                    **build_booking_line_payload(service_bundle, service_date='2026-07-05', line_price=2600),
                    'id': line_id,
                }
            ],
        ),
    )
    assert update_response.status_code == 422
    assert 'مقفلة' in update_response.json()['detail']


def test_booking_line_cannot_be_completed_twice_or_directly_marked_completed(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client, department_code='MAKEUP', department_name='قسم المكياج', service_name='خدمة اختبار', default_price=800)

    booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-08-01', line_price=1800)],
    )
    line_id = booking['lines'][0]['id']

    direct_complete_status = app_client.patch(
        f"/api/bookings/{booking['id']}",
        json=build_booking_document_payload(
            customer_id,
            [
                {
                    **build_booking_line_payload(service_bundle, service_date='2026-08-01', line_price=1800, status='completed'),
                    'id': line_id,
                }
            ],
        ),
    )
    assert direct_complete_status.status_code == 422
    assert 'إجراءات السطر' in direct_complete_status.json()['detail']

    first_complete = app_client.post(f"/api/bookings/{booking['id']}/lines/{line_id}/complete")
    assert first_complete.status_code == 200, first_complete.text

    second_complete = app_client.post(f"/api/bookings/{booking['id']}/lines/{line_id}/complete")
    assert second_complete.status_code == 422
    assert 'تم الاعتراف بالإيراد' in second_complete.json()['detail']
