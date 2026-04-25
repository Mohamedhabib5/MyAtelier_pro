from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login


def test_admin_can_manage_departments_and_services(app_client: TestClient) -> None:
    auth_user = login(app_client)

    department_response = app_client.post('/api/catalog/departments', json={'code': 'BRIDE', 'name': 'قسم العرائس'})
    assert department_response.status_code == 201, department_response.text
    department = department_response.json()
    assert department['created_by_user_id'] == auth_user['id']
    assert department['updated_by_user_id'] == auth_user['id']
    assert department['entity_version'] == 1

    service_response = app_client.post(
        '/api/catalog/services',
        json={
            'department_id': department['id'],
            'name': 'مكياج عروس',
            'default_price': 1500,
            'tax_rate_percent': 14,
            'duration_minutes': 120,
            'notes': 'الخدمة الأساسية',
        },
    )
    assert service_response.status_code == 201, service_response.text
    service = service_response.json()
    assert service['department_name'] == 'قسم العرائس'
    assert service['tax_rate_percent'] == 14.0
    assert service['created_by_user_id'] == auth_user['id']
    assert service['updated_by_user_id'] == auth_user['id']
    assert service['entity_version'] == 1

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
            'tax_rate_percent': 10,
            'duration_minutes': 150,
            'notes': 'نسخة مطورة',
            'is_active': True,
        },
    )
    assert update_service_response.status_code == 200, update_service_response.text
    assert update_service_response.json()['name'] == 'مكياج عروس VIP'
    assert update_service_response.json()['tax_rate_percent'] == 10.0
    assert update_service_response.json()['updated_by_user_id'] == auth_user['id']
    assert update_service_response.json()['entity_version'] == 2


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


def test_catalog_archive_restore_and_status_filter(app_client: TestClient) -> None:
    auth_user = login(app_client)

    dept_response = app_client.post('/api/catalog/departments', json={'code': 'SPA', 'name': 'السبا'})
    assert dept_response.status_code == 201, dept_response.text
    department = dept_response.json()

    service_response = app_client.post(
        '/api/catalog/services',
        json={'department_id': department['id'], 'name': 'حمام مغربي', 'default_price': 700, 'duration_minutes': 90},
    )
    assert service_response.status_code == 201, service_response.text
    service = service_response.json()

    archive_department = app_client.post(
        f"/api/catalog/departments/{department['id']}/archive",
        json={'reason': 'Temporarily inactive'},
    )
    assert archive_department.status_code == 200, archive_department.text
    archived_department = archive_department.json()
    assert archived_department['is_active'] is False
    assert archived_department['updated_by_user_id'] == auth_user['id']
    assert archived_department['entity_version'] == 2

    archive_service = app_client.post(
        f"/api/catalog/services/{service['id']}/archive",
        json={'reason': 'Out of seasonal menu'},
    )
    assert archive_service.status_code == 200, archive_service.text
    archived_service = archive_service.json()
    assert archived_service['is_active'] is False
    assert archived_service['updated_by_user_id'] == auth_user['id']
    assert archived_service['entity_version'] == 2

    active_departments = app_client.get('/api/catalog/departments?status=active')
    assert active_departments.status_code == 200
    assert department['id'] not in {row['id'] for row in active_departments.json()}

    inactive_departments = app_client.get('/api/catalog/departments?status=inactive')
    assert inactive_departments.status_code == 200
    assert department['id'] in {row['id'] for row in inactive_departments.json()}

    active_services = app_client.get('/api/catalog/services?status=active')
    assert active_services.status_code == 200
    assert service['id'] not in {row['id'] for row in active_services.json()}

    inactive_services = app_client.get('/api/catalog/services?status=inactive')
    assert inactive_services.status_code == 200
    assert service['id'] in {row['id'] for row in inactive_services.json()}

    restore_department = app_client.post(
        f"/api/catalog/departments/{department['id']}/restore",
        json={'reason': 'Reactivated'},
    )
    assert restore_department.status_code == 200, restore_department.text
    restored_department = restore_department.json()
    assert restored_department['is_active'] is True
    assert restored_department['entity_version'] == 3

    restore_service = app_client.post(
        f"/api/catalog/services/{service['id']}/restore",
        json={'reason': 'Back to active services'},
    )
    assert restore_service.status_code == 200, restore_service.text
    restored_service = restore_service.json()
    assert restored_service['is_active'] is True
    assert restored_service['entity_version'] == 3
