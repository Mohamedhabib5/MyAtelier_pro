from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import seed_customer, seed_service_bundle
from .test_branch_scope import create_booking_in_current_branch, create_second_branch
from .test_foundation import login


def test_admin_can_download_customers_booking_and_payment_exports(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-001', '2026-08-10')
    payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-01',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 700}],
        },
    )
    assert payment.status_code == 201, payment.text

    customers_export = app_client.get('/api/exports/customers.csv')
    bookings_export = app_client.get('/api/exports/bookings.csv')
    booking_lines_export = app_client.get('/api/exports/booking-lines.csv')
    payments_export = app_client.get('/api/exports/payments.csv')
    payment_allocations_export = app_client.get('/api/exports/payment-allocations.csv')

    assert customers_export.status_code == 200
    assert 'attachment; filename=' in customers_export.headers['content-disposition']
    assert 'full_name,phone' in customers_export.text
    assert 'Bride One' in customers_export.text

    assert bookings_export.status_code == 200
    assert 'booking_number,branch_name' in bookings_export.text
    assert 'BK' in bookings_export.text

    assert booking_lines_export.status_code == 200
    assert 'booking_number,branch_name,customer_name,line_number' in booking_lines_export.text
    assert 'تجربة فستان' in booking_lines_export.text

    assert payments_export.status_code == 200
    assert 'payment_number,branch_name,customer_name,payment_date' in payments_export.text
    assert 'PAY' in payments_export.text
    assert 'JV' in payments_export.text

    assert payment_allocations_export.status_code == 200
    assert 'payment_number,branch_name,customer_name,payment_date,booking_number,booking_line_number' in payment_allocations_export.text
    assert booking['booking_number'] in payment_allocations_export.text


def test_branch_switch_scopes_booking_and_payment_exports(app_client: TestClient) -> None:
    login(app_client)
    second_branch_id = create_second_branch(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-002', '2026-08-15')
    payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-03',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 500}],
        },
    )
    assert payment.status_code == 201, payment.text
    default_booking_number = app_client.get('/api/bookings').json()[0]['booking_number']
    default_payment_number = app_client.get('/api/payments').json()[0]['payment_number']

    switch_response = app_client.post('/api/settings/branches/active', json={'branch_id': second_branch_id})
    assert switch_response.status_code == 200, switch_response.text

    bookings_export = app_client.get('/api/exports/bookings.csv')
    payments_export = app_client.get('/api/exports/payments.csv')
    customers_export = app_client.get('/api/exports/customers.csv')

    assert default_booking_number not in bookings_export.text
    assert default_payment_number not in payments_export.text
    assert 'Bride One' in customers_export.text
