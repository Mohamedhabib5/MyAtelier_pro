from __future__ import annotations

from fastapi.testclient import TestClient

from app.modules.organization.models import Branch
from app.modules.organization.service import get_company_settings

from .test_bookings import build_booking_line_payload, create_booking_document, seed_customer, seed_dress, seed_service_bundle
from .test_foundation import login


def create_second_branch(client: TestClient) -> str:
    with client.app.state.session_factory() as db:
        company = get_company_settings(db)
        branch = Branch(company_id=company.id, code='WEST', name='West Branch', is_default=False, is_active=True)
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch.id


def create_booking_in_current_branch(client: TestClient, customer_id: str, service_bundle: dict, dress_code: str, service_date: str) -> dict:
    dress_id = seed_dress(client, code=dress_code)
    return create_booking_document(
        client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date=service_date, dress_id=dress_id, line_price=2500)],
    )


def test_switching_active_branch_scopes_documents_and_reports(app_client: TestClient) -> None:
    login(app_client)
    second_branch_id = create_second_branch(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    default_booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'BR-001', '2026-08-01')

    default_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-01',
            'allocations': [{'booking_id': default_booking['id'], 'booking_line_id': default_booking['lines'][0]['id'], 'allocated_amount': 500}],
        },
    )
    assert default_payment.status_code == 201, default_payment.text

    switch_response = app_client.post('/api/settings/branches/active', json={'branch_id': second_branch_id})
    assert switch_response.status_code == 200, switch_response.text

    bookings_in_second = app_client.get('/api/bookings')
    assert bookings_in_second.status_code == 200
    assert bookings_in_second.json() == []

    dashboard_in_second = app_client.get('/api/dashboard/finance')
    assert dashboard_in_second.status_code == 200
    assert dashboard_in_second.json()['total_bookings'] == 0

    second_booking = create_booking_in_current_branch(app_client, customer_id, service_bundle, 'BR-002', '2026-08-05')
    payments_in_second_before = app_client.get('/api/payments')
    assert payments_in_second_before.status_code == 200
    assert payments_in_second_before.json() == []

    second_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-07-02',
            'allocations': [{'booking_id': second_booking['id'], 'booking_line_id': second_booking['lines'][0]['id'], 'allocated_amount': 800}],
        },
    )
    assert second_payment.status_code == 201, second_payment.text

    reports_in_second = app_client.get('/api/reports/overview')
    assert reports_in_second.status_code == 200
    assert reports_in_second.json()['upcoming_bookings'] == 1

    company_response = app_client.get('/api/settings/company')
    default_branch_id = next(branch['id'] for branch in company_response.json()['branches'] if branch['is_default'])
    back_to_default = app_client.post('/api/settings/branches/active', json={'branch_id': default_branch_id})
    assert back_to_default.status_code == 200

    bookings_in_default = app_client.get('/api/bookings')
    assert len(bookings_in_default.json()) == 1
    payments_in_default = app_client.get('/api/payments')
    assert len(payments_in_default.json()) == 1


def test_login_sets_active_branch_context(app_client: TestClient) -> None:
    payload = login(app_client)
    assert payload['active_branch_id']
    assert payload['active_branch_name']
