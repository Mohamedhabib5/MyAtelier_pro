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


def test_reverse_revenue_recognition_reopens_booking_line_and_marks_journal_reversed(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client, department_code='MAKEUP', department_name='قسم المكياج', service_name='تجربة عكس إيراد', default_price=800)

    booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-09-01', line_price=2000)],
    )
    line_id = booking['lines'][0]['id']

    pay_before_complete = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-03-18',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': line_id, 'allocated_amount': 700}],
        },
    )
    assert pay_before_complete.status_code == 201, pay_before_complete.text

    completed = app_client.post(f"/api/bookings/{booking['id']}/lines/{line_id}/complete")
    assert completed.status_code == 200, completed.text
    completed_line = completed.json()['lines'][0]
    original_journal_id = completed_line['revenue_journal_entry_id']
    assert original_journal_id is not None

    reverse_response = app_client.post(f"/api/bookings/{booking['id']}/lines/{line_id}/reverse-revenue")
    assert reverse_response.status_code == 200, reverse_response.text
    reversed_document = reverse_response.json()
    reversed_line = reversed_document['lines'][0]
    assert reversed_line['status'] == 'confirmed'
    assert reversed_line['revenue_journal_entry_id'] is None
    assert reversed_line['revenue_journal_entry_number'] is None
    assert reversed_line['revenue_journal_entry_status'] is None

    journal_response = app_client.get(f'/api/accounting/journal-entries/{original_journal_id}')
    assert journal_response.status_code == 200, journal_response.text
    assert journal_response.json()['status'] == 'reversed'


def test_reverse_revenue_recognition_is_blocked_when_post_completion_payment_exists(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client, department_code='MAKEUP', department_name='قسم المكياج', service_name='تحصيل لاحق', default_price=900)

    booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-10-01', line_price=2200)],
    )
    line_id = booking['lines'][0]['id']

    complete_response = app_client.post(f"/api/bookings/{booking['id']}/lines/{line_id}/complete")
    assert complete_response.status_code == 200, complete_response.text

    pay_after_complete = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-03-19',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': line_id, 'allocated_amount': 300}],
        },
    )
    assert pay_after_complete.status_code == 201, pay_after_complete.text

    reverse_response = app_client.post(f"/api/bookings/{booking['id']}/lines/{line_id}/reverse-revenue")
    assert reverse_response.status_code == 422
    assert 'قبل معالجة التحصيلات اللاحقة' in reverse_response.json()['detail']


def test_complete_booking_line_with_tax_splits_revenue_and_tax_payable(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(
        app_client,
        department_code='MAKEUP',
        department_name='قسم المكياج',
        service_name='خدمة خاضعة للضريبة',
        default_price=1000,
        tax_rate_percent=14,
    )

    booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-11-01', line_price=2280)],
    )
    line_id = booking['lines'][0]['id']

    payment_response = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-03-20',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': line_id, 'allocated_amount': 1000}],
        },
    )
    assert payment_response.status_code == 201, payment_response.text

    complete_response = app_client.post(f"/api/bookings/{booking['id']}/lines/{line_id}/complete")
    assert complete_response.status_code == 200, complete_response.text
    completed_line = complete_response.json()['lines'][0]
    assert completed_line['tax_rate_percent'] == 14.0
    assert completed_line['tax_amount'] == 319.2

    journal_response = app_client.get(f"/api/accounting/journal-entries/{completed_line['revenue_journal_entry_id']}")
    assert journal_response.status_code == 200, journal_response.text
    journal = journal_response.json()
    lines = {line['account_code']: line for line in journal['lines']}
    assert str(lines['2100']['debit_amount']) == '1000.00'
    assert str(lines['1200']['debit_amount']) == '1280.00'
    assert str(lines['4100']['credit_amount']) == '1960.80'
    assert str(lines['2200']['credit_amount']) == '319.20'
