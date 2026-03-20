from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import build_booking_line_payload, create_booking_document, seed_customer, seed_dress, seed_service_bundle
from .test_foundation import login


def seed_reports_data(client: TestClient) -> None:
    customer_id = seed_customer(client)
    service_bundle = seed_service_bundle(client)
    dress_id = seed_dress(client, code='REP-DR-001')
    second_dress = client.post(
        '/api/dresses',
        json={'code': 'REP-DR-002', 'dress_type': 'زفاف', 'status': 'maintenance', 'description': 'فستان صيانة'},
    )
    assert second_dress.status_code == 201, second_dress.text

    first_booking = create_booking_document(
        client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-07-05', dress_id=dress_id, line_price=3200)],
    )
    create_booking_document(
        client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-07-10', line_price=1800, status='cancelled')],
    )

    booking_id = first_booking['id']
    line_id = first_booking['lines'][0]['id']
    for amount in (1000, 400):
        response = client.post(
            '/api/payments',
            json={
                'customer_id': customer_id,
                'payment_date': '2026-06-20',
                'allocations': [{'booking_id': booking_id, 'booking_line_id': line_id, 'allocated_amount': amount}],
            },
        )
        assert response.status_code == 201, response.text


def test_reports_overview_returns_operational_summary(app_client: TestClient) -> None:
    login(app_client)
    seed_reports_data(app_client)

    response = app_client.get('/api/reports/overview')
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['active_customers'] == 1
    assert payload['active_services'] == 1
    assert payload['available_dresses'] == 1
    assert payload['upcoming_bookings'] == 1
    assert payload['booking_status_counts'][0]['count'] >= 1
    assert payload['payment_type_totals'][0]['key'] == 'collection'
    assert payload['payment_type_totals'][0]['value'] == 1400.0
    assert payload['department_service_counts'][0]['count'] == 1
    assert payload['upcoming_booking_items'][0]['status'] == 'confirmed'


def test_regular_user_can_view_reports(app_client: TestClient) -> None:
    login(app_client)
    created = app_client.post(
        '/api/users',
        json={'username': 'reports.user', 'full_name': 'Reports User', 'password': 'secret123', 'role_names': ['user']},
    )
    assert created.status_code == 201, created.text

    app_client.post('/api/auth/logout')
    login(app_client, username='reports.user', password='secret123')

    response = app_client.get('/api/reports/overview')
    assert response.status_code == 200, response.text
