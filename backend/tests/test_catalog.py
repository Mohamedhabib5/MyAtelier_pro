from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login


def test_admin_can_manage_departments_and_services(app_client: TestClient) -> None:
    login(app_client)

    department_response = app_client.post('/api/catalog/departments', json={'code': 'BRIDE', 'name': 'قسم العرائس'})
    assert department_response.status_code == 201, department_response.text
    department = department_response.json()

    service_response = app_client.post(
        '/api/catalog/services',
        json={
            'department_id': department['id'],
            'name': 'مكياج عروس',
            'default_price': 1500,
            'duration_minutes': 120,
            'notes': 'الخدمة الأساسية',
        },
    )
    assert service_response.status_code == 201, service_response.text
    service = service_response.json()
    assert service['department_name'] == 'قسم العرائس'

    list_departments_response = app_client.get('/api/catalog/departments')
    list_services_response = app_client.get('/api/catalog/services')
    assert list_departments_response.status_code == 200
    assert list_services_response.status_code == 200
    assert len(list_departments_response.json()) == 1
    assert len(list_services_response.json()) == 1

    update_service_response = app_client.patch(
        f"/api/catalog/services/{service['id']}",
        json={
            'department_id': department['id'],
            'name': 'مكياج عروس VIP',
            'default_price': 1800,
            'duration_minutes': 150,
            'notes': 'نسخة مطورة',
            'is_active': True,
        },
    )
    assert update_service_response.status_code == 200, update_service_response.text
    assert update_service_response.json()['name'] == 'مكياج عروس VIP'


def test_duplicate_department_code_is_blocked(app_client: TestClient) -> None:
    login(app_client)
    first_response = app_client.post('/api/catalog/departments', json={'code': 'HAIR', 'name': 'الشعر'})
    assert first_response.status_code == 201

    second_response = app_client.post('/api/catalog/departments', json={'code': 'HAIR', 'name': 'قسم الشعر'})
    assert second_response.status_code == 422
    assert 'مستخدم بالفعل' in second_response.json()['detail']


def test_regular_user_can_manage_catalog(app_client: TestClient) -> None:
    login(app_client)
    user_response = app_client.post(
        '/api/users',
        json={'username': 'catalog.user', 'full_name': 'Catalog User', 'password': 'secret123', 'role_names': ['user']},
    )
    assert user_response.status_code == 201

    app_client.post('/api/auth/logout')
    login(app_client, username='catalog.user', password='secret123')

    department_response = app_client.post('/api/catalog/departments', json={'code': 'SKIN', 'name': 'البشرة'})
    assert department_response.status_code == 201, department_response.text
    department = department_response.json()

    service_response = app_client.post(
        '/api/catalog/services',
        json={'department_id': department['id'], 'name': 'تنظيف بشرة', 'default_price': 500, 'duration_minutes': 60},
    )
    assert service_response.status_code == 201, service_response.text

    list_response = app_client.get('/api/catalog/services')
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
