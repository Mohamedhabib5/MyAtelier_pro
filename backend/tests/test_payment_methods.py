from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login


def test_payment_methods_default_cash_is_available_for_authenticated_user(app_client: TestClient) -> None:
    login(app_client)
    response = app_client.get('/api/payment-methods')
    assert response.status_code == 200, response.text
    rows = response.json()
    assert len(rows) >= 1
    assert rows[0]['code'] == 'cash'
    assert rows[0]['is_active'] is True


def test_payment_method_routes_require_authentication_for_manage(app_client: TestClient) -> None:
    login(app_client)
    seed_response = app_client.post('/api/payment-methods', json={'name': 'Seed Method', 'code': 'seed_method'})
    assert seed_response.status_code == 201, seed_response.text
    method_id = seed_response.json()['id']

    app_client.post('/api/auth/logout')

    list_response = app_client.get('/api/payment-methods')
    assert list_response.status_code == 401

    create_response = app_client.post('/api/payment-methods', json={'name': 'Card'})
    assert create_response.status_code == 401

    update_response = app_client.patch(f'/api/payment-methods/{method_id}', json={'name': 'Updated'})
    assert update_response.status_code == 401


def test_admin_can_create_and_update_payment_method(app_client: TestClient) -> None:
    login(app_client)
    create_response = app_client.post('/api/payment-methods', json={'name': 'Bank Transfer', 'code': 'bank_transfer'})
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created['code'] == 'bank_transfer'
    assert created['name'] == 'Bank Transfer'
    assert created['is_active'] is True

    update_response = app_client.patch(
        f"/api/payment-methods/{created['id']}",
        json={'name': 'Bank Transfer Updated', 'display_order': 5, 'is_active': False},
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated['name'] == 'Bank Transfer Updated'
    assert updated['display_order'] == 5
    assert updated['is_active'] is False
