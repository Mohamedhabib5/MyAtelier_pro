from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login


def test_admin_can_create_list_and_update_customer(app_client: TestClient) -> None:
    login(app_client)

    create_response = app_client.post(
        '/api/customers',
        json={'full_name': 'Nour Hassan', 'phone': '01000000001', 'email': 'nour@example.com'},
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created['full_name'] == 'Nour Hassan'

    list_response = app_client.get('/api/customers')
    assert list_response.status_code == 200
    rows = list_response.json()
    assert len(rows) == 1
    assert rows[0]['phone'] == '01000000001'

    update_response = app_client.patch(
        f"/api/customers/{created['id']}",
        json={
            'full_name': 'Nour Hassan Updated',
            'phone': '01000000001',
            'email': 'updated@example.com',
            'address': 'Nasr City',
            'notes': 'VIP bride',
            'is_active': True,
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated['full_name'] == 'Nour Hassan Updated'
    assert updated['address'] == 'Nasr City'


def test_duplicate_customer_phone_is_blocked(app_client: TestClient) -> None:
    login(app_client)
    payload = {'full_name': 'First Customer', 'phone': '01000000002'}

    first_response = app_client.post('/api/customers', json=payload)
    assert first_response.status_code == 201

    second_response = app_client.post('/api/customers', json={'full_name': 'Second Customer', 'phone': '01000000002'})
    assert second_response.status_code == 422
    assert 'مستخدم بالفعل' in second_response.json()['detail']


def test_regular_user_can_manage_customers(app_client: TestClient) -> None:
    login(app_client)
    user_response = app_client.post(
        '/api/users',
        json={'username': 'crm.user', 'full_name': 'CRM User', 'password': 'secret123', 'role_names': ['user']},
    )
    assert user_response.status_code == 201

    app_client.post('/api/auth/logout')
    login(app_client, username='crm.user', password='secret123')

    create_response = app_client.post('/api/customers', json={'full_name': 'Layla Saber', 'phone': '01000000003'})
    assert create_response.status_code == 201, create_response.text

    list_response = app_client.get('/api/customers')
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
