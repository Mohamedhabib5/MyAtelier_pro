from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import build_booking_line_payload, create_booking_document, seed_customer, seed_dress, seed_service_bundle
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
    custody_export = app_client.get('/api/exports/custody.csv')
    customers_xlsx = app_client.get('/api/exports/customers.xlsx')
    bookings_xlsx = app_client.get('/api/exports/bookings.xlsx')
    payments_xlsx = app_client.get('/api/exports/payment-documents.xlsx')
    custody_xlsx = app_client.get('/api/exports/custody.xlsx')

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
    assert customers_xlsx.status_code == 200
    assert customers_xlsx.headers['content-type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert customers_xlsx.content[:2] == b'PK'
    assert bookings_xlsx.status_code == 200
    assert bookings_xlsx.content[:2] == b'PK'
    assert payments_xlsx.status_code == 200
    assert payments_xlsx.content[:2] == b'PK'
    assert custody_export.status_code == 200
    assert 'case_number,status,case_type' in custody_export.text
    assert custody_xlsx.status_code == 200
    assert custody_xlsx.content[:2] == b'PK'


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


def test_admin_can_download_finance_and_reports_pdf_exports(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    _ = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-PDF-001', '2026-09-01')

    finance_pdf = app_client.get('/api/exports/finance.pdf')
    reports_pdf = app_client.get('/api/exports/reports.pdf')

    assert finance_pdf.status_code == 200, finance_pdf.text
    assert finance_pdf.headers['content-type'] == 'application/pdf'
    assert 'attachment; filename=' in finance_pdf.headers['content-disposition']
    assert finance_pdf.content.startswith(b'%PDF-1.4')

    assert reports_pdf.status_code == 200, reports_pdf.text
    assert reports_pdf.headers['content-type'] == 'application/pdf'
    assert 'attachment; filename=' in reports_pdf.headers['content-disposition']
    assert reports_pdf.content.startswith(b'%PDF-1.4')


def test_bookings_export_honors_table_filters(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    keep_dress = seed_dress(app_client, code='EXP-FLT-KEEP')
    drop_dress = seed_dress(app_client, code='EXP-FLT-DROP')
    keep_booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-08-20', dress_id=keep_dress, line_price=2500)],
        booking_date='2026-08-20',
    )
    drop_booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-08-25', dress_id=drop_dress, line_price=2500)],
        booking_date='2026-08-25',
    )
    cancel_response = app_client.post(f"/api/bookings/{drop_booking['id']}/lines/{drop_booking['lines'][0]['id']}/cancel")
    assert cancel_response.status_code == 200, cancel_response.text

    status_export = app_client.get('/api/exports/bookings.csv?status=cancelled')
    assert status_export.status_code == 200, status_export.text
    assert drop_booking['booking_number'] in status_export.text
    assert keep_booking['booking_number'] not in status_export.text

    ranged_export = app_client.get('/api/exports/bookings.csv?date_from=2026-08-24&date_to=2026-08-31')
    assert ranged_export.status_code == 200, ranged_export.text
    assert drop_booking['booking_number'] in ranged_export.text
    assert keep_booking['booking_number'] not in ranged_export.text


def test_payments_export_honors_table_filters(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-PAY-001', '2026-08-10')

    keep_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-10',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 200}],
        },
    )
    assert keep_payment.status_code == 201, keep_payment.text
    keep_payment_id = keep_payment.json()['id']
    keep_payment_number = keep_payment.json()['payment_number']

    drop_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-11',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 100}],
        },
    )
    assert drop_payment.status_code == 201, drop_payment.text
    drop_payment_number = drop_payment.json()['payment_number']

    void_response = app_client.post(
        f'/api/payments/{keep_payment_id}/void',
        json={'void_date': '2026-07-12', 'reason': 'تصحيح إدخال'},
    )
    assert void_response.status_code == 200, void_response.text

    status_export = app_client.get('/api/exports/payments.csv?status=voided')
    assert status_export.status_code == 200, status_export.text
    assert keep_payment_number in status_export.text
    assert drop_payment_number not in status_export.text

    ranged_export = app_client.get('/api/exports/payments.csv?date_from=2026-07-11&date_to=2026-07-11')
    assert ranged_export.status_code == 200, ranged_export.text
    assert drop_payment_number in ranged_export.text
    assert keep_payment_number not in ranged_export.text

    alias_export = app_client.get('/api/exports/payment-documents.csv?status=voided')
    assert alias_export.status_code == 200, alias_export.text
    assert keep_payment_number in alias_export.text
    assert drop_payment_number not in alias_export.text


def test_bookings_export_honors_sort_direction(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    first_dress = seed_dress(app_client, code='EXP-SORT-001')
    second_dress = seed_dress(app_client, code='EXP-SORT-002')
    first_booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-04-10', dress_id=first_dress, line_price=2000)],
        booking_date='2026-04-10',
    )
    second_booking = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-04-11', dress_id=second_dress, line_price=2000)],
        booking_date='2026-04-11',
    )

    asc_export = app_client.get('/api/exports/bookings.csv?sort_by=booking_date&sort_dir=asc')
    assert asc_export.status_code == 200, asc_export.text
    lines = [line for line in asc_export.text.splitlines() if line.strip()]
    assert len(lines) >= 3
    assert first_booking['booking_number'] in lines[1]
    assert second_booking['booking_number'] in lines[2]


def test_booking_lines_export_honors_booking_filters(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    keep_booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-LINE-KEEP', '2026-08-10')
    drop_booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-LINE-DROP', '2026-08-12')
    cancel_response = app_client.post(f"/api/bookings/{drop_booking['id']}/lines/{drop_booking['lines'][0]['id']}/cancel")
    assert cancel_response.status_code == 200, cancel_response.text

    filtered_export = app_client.get('/api/exports/booking-lines.csv?status=cancelled')
    assert filtered_export.status_code == 200, filtered_export.text
    assert drop_booking['booking_number'] in filtered_export.text
    assert keep_booking['booking_number'] not in filtered_export.text


def test_payment_allocations_export_honors_payment_filters(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'EXP-ALLOC-001', '2026-08-10')

    keep_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-10',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 200}],
        },
    )
    assert keep_payment.status_code == 201, keep_payment.text
    keep_payment_number = keep_payment.json()['payment_number']

    drop_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-11',
            'allocations': [{'booking_id': booking['id'], 'booking_line_id': booking['lines'][0]['id'], 'allocated_amount': 100}],
        },
    )
    assert drop_payment.status_code == 201, drop_payment.text
    drop_payment_number = drop_payment.json()['payment_number']

    filtered_export = app_client.get('/api/exports/payment-allocations.csv?date_from=2026-07-11&date_to=2026-07-11')
    assert filtered_export.status_code == 200, filtered_export.text
    assert drop_payment_number in filtered_export.text
    assert keep_payment_number not in filtered_export.text
