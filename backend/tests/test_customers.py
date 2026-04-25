from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login


def test_admin_can_create_list_and_update_customer(app_client: TestClient) -> None:
    auth_user = login(app_client)

    create_response = app_client.post(
        '/api/customers',
        json={'full_name': 'Nour Hassan', 'phone': '01000000001', 'email': 'nour@example.com'},
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created['full_name'] == 'Nour Hassan'
    assert created['created_by_user_id'] == auth_user['id']
    assert created['updated_by_user_id'] == auth_user['id']
    assert created['entity_version'] == 1

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
    assert updated['updated_by_user_id'] == auth_user['id']
    assert updated['entity_version'] == 2


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


def test_customer_archive_restore_and_status_filter(app_client: TestClient) -> None:
    auth_user = login(app_client)

    first_create = app_client.post('/api/customers', json={'full_name': 'Archived Customer', 'phone': '01000000004'})
    assert first_create.status_code == 201, first_create.text
    first_customer = first_create.json()

    second_create = app_client.post('/api/customers', json={'full_name': 'Active Customer', 'phone': '01000000005'})
    assert second_create.status_code == 201, second_create.text
    second_customer = second_create.json()

    archive_response = app_client.post(
        f"/api/customers/{first_customer['id']}/archive",
        json={'reason': 'Duplicate entry correction'},
    )
    assert archive_response.status_code == 200, archive_response.text
    archived = archive_response.json()
    assert archived['is_active'] is False
    assert archived['updated_by_user_id'] == auth_user['id']
    assert archived['entity_version'] == 2

    archive_again = app_client.post(f"/api/customers/{first_customer['id']}/archive", json={})
    assert archive_again.status_code == 422
    assert 'مؤرشف بالفعل' in archive_again.json()['detail']

    active_rows = app_client.get('/api/customers?status=active')
    assert active_rows.status_code == 200
    active_ids = {row['id'] for row in active_rows.json()}
    assert second_customer['id'] in active_ids
    assert first_customer['id'] not in active_ids

    inactive_rows = app_client.get('/api/customers?status=inactive')
    assert inactive_rows.status_code == 200
    inactive_ids = {row['id'] for row in inactive_rows.json()}
    assert first_customer['id'] in inactive_ids
    assert second_customer['id'] not in inactive_ids

    restore_response = app_client.post(
        f"/api/customers/{first_customer['id']}/restore",
        json={'reason': 'Reviewed and reactivated'},
    )
    assert restore_response.status_code == 200, restore_response.text
    restored = restore_response.json()
    assert restored['is_active'] is True
    assert restored['updated_by_user_id'] == auth_user['id']
    assert restored['entity_version'] == 3

    active_after_restore = app_client.get('/api/customers?status=active')
    assert active_after_restore.status_code == 200
    active_after_restore_ids = {row['id'] for row in active_after_restore.json()}
    assert first_customer['id'] in active_after_restore_ids
    assert second_customer['id'] in active_after_restore_ids
