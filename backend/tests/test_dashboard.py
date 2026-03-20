from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import build_booking_line_payload, create_booking_document, seed_customer, seed_dress, seed_service_bundle
from .test_foundation import login


def seed_finance_data(client: TestClient) -> None:
    customer_id = seed_customer(client)
    service_bundle = seed_service_bundle(client)
    dress_id = seed_dress(client, code='FIN-DR-001')
    booking = create_booking_document(
        client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-07-01', dress_id=dress_id, line_price=3000)],
    )
    line_id = booking['lines'][0]['id']

    for amount, date_value in [(1000, '2026-06-01'), (700, '2026-06-02')]:
        response = client.post(
            '/api/payments',
            json={
                'customer_id': customer_id,
                'payment_date': date_value,
                'allocations': [{'booking_id': booking['id'], 'booking_line_id': line_id, 'allocated_amount': amount}],
            },
        )
        assert response.status_code == 201, response.text


def test_dashboard_summary_returns_finance_metrics(app_client: TestClient) -> None:
    login(app_client)
    seed_finance_data(app_client)

    response = app_client.get('/api/dashboard/finance')
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['total_income'] == 1700.0
    assert payload['total_remaining'] == 1300.0
    assert payload['total_bookings'] == 1
    assert payload['daily_income'][0]['label'] == '2026-06-01'
    assert payload['department_income'][0]['value'] == 1700.0
    assert payload['top_services'][0]['count'] == 1


def test_regular_user_can_view_finance_dashboard(app_client: TestClient) -> None:
    login(app_client)
    create_user = app_client.post(
        '/api/users',
        json={'username': 'dashboard.user', 'full_name': 'Dashboard User', 'password': 'secret123', 'role_names': ['user']},
    )
    assert create_user.status_code == 201, create_user.text

    app_client.post('/api/auth/logout')
    login(app_client, username='dashboard.user', password='secret123')

    response = app_client.get('/api/dashboard/finance')
    assert response.status_code == 200, response.text
