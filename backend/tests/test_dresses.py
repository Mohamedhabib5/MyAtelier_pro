from __future__ import annotations

import uuid
from fastapi.testclient import TestClient

from .test_foundation import login


def get_or_create_dress_service(client: TestClient, service_name: str) -> str:
    # Check if a service with the same name already exists to prevent violating unique constraint
    services_res = client.get('/api/catalog/services')
    assert services_res.status_code == 200
    for service in services_res.json():
        if service['name'] == service_name:
            return service['id']

    # 1. Create a department
    code = f"DR-{uuid.uuid4().hex[:6].upper()}"
    dept_res = client.post('/api/catalog/departments', json={'code': code, 'name': 'قسم فساتين الاختبار'})
    assert dept_res.status_code == 201
    dept_id = dept_res.json()['id']

    # 2. Mark department as operational dresses department
    op_res = client.post('/api/catalog/operational/dresses-department', json={'department_id': dept_id})
    assert op_res.status_code == 200

    # 3. Create service catalog item
    service_res = client.post('/api/catalog/services', json={'department_id': dept_id, 'name': service_name, 'default_price': 100.00, 'display_order': 0})
    assert service_res.status_code == 201
    return service_res.json()['id']


def test_admin_can_create_list_and_update_dress(app_client: TestClient) -> None:
    auth_user = login(app_client)

    service_id = get_or_create_dress_service(app_client, "زفاف")

    create_response = app_client.post(
        '/api/dresses',
        json={
            'code': 'D-001',
            'name': 'فستان زفاف دانتيل كلاسيكي',
            'dress_type_id': service_id,
            'purchase_date': '2026-03-01',
            'status': 'available',
            'description': 'فستان أبيض أساسي',
            'image_path': 'dress_images/d-001.jpg',
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created['code'] == 'D-001'
    assert created['name'] == 'فستان زفاف دانتيل كلاسيكي'
    assert created['dress_type_id'] == service_id
    assert created['dress_type_name'] == 'زفاف'
    assert created['created_by_user_id'] == auth_user['id']
    assert created['updated_by_user_id'] == auth_user['id']
    assert created['entity_version'] == 1

    list_response = app_client.get('/api/dresses')
    assert list_response.status_code == 200
    rows = list_response.json()
    assert len(rows) == 1

    second_service_id = get_or_create_dress_service(app_client, "خطوبة")

    update_response = app_client.patch(
        f"/api/dresses/{created['id']}",
        json={
            'code': 'D-001',
            'name': 'فستان خطوبة منفوش',
            'dress_type_id': second_service_id,
            'purchase_date': '2026-03-02',
            'status': 'maintenance',
            'description': 'تم إرسال الفستان للصيانة',
            'image_path': 'dress_images/d-001-new.jpg',
            'is_active': True,
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated['status'] == 'maintenance'
    assert updated['name'] == 'فستان خطوبة منفوش'
    assert updated['dress_type_id'] == second_service_id
    assert updated['dress_type_name'] == 'خطوبة'
    assert updated['updated_by_user_id'] == auth_user['id']
    assert updated['entity_version'] == 2


def test_duplicate_dress_code_is_blocked(app_client: TestClient) -> None:
    login(app_client)
    service_id = get_or_create_dress_service(app_client, "زفاف")

    payload = {
        'code': 'D-002',
        'name': 'فستان زفاف تجريبي',
        'dress_type_id': service_id,
        'status': 'available',
        'description': 'فستان تجريبي',
    }
    first_response = app_client.post('/api/dresses', json=payload)
    assert first_response.status_code == 201

    second_response = app_client.post('/api/dresses', json=payload)
    assert second_response.status_code == 422
    assert 'مستخدم بالفعل' in second_response.json()['detail']


def test_regular_user_can_manage_dresses(app_client: TestClient) -> None:
    login(app_client)
    user_response = app_client.post(
        '/api/users',
        json={'username': 'dress.user', 'full_name': 'Dress User', 'password': 'secret123', 'role_names': ['admin']},
    )
    assert user_response.status_code == 201

    app_client.post('/api/auth/logout')
    login(app_client, username='dress.user', password='secret123')

    service_id = get_or_create_dress_service(app_client, "سواريه")

    create_response = app_client.post(
        '/api/dresses',
        json={'code': 'D-003', 'name': 'سواريه أسود شيفون', 'dress_type_id': service_id, 'status': 'reserved', 'description': 'جاهز لحجز قادم'},
    )
    assert create_response.status_code == 201, create_response.text

    list_response = app_client.get('/api/dresses')
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_dress_archive_restore_and_status_filter(app_client: TestClient) -> None:
    auth_user = login(app_client)
    service_id = get_or_create_dress_service(app_client, "زفاف")

    create_response = app_client.post(
        '/api/dresses',
        json={'code': 'D-010', 'name': 'فستان اختبار للأرشفة', 'dress_type_id': service_id, 'status': 'available', 'description': 'فستان اختبار للأرشفة'},
    )
    assert create_response.status_code == 201, create_response.text
    dress = create_response.json()

    archive_response = app_client.post(
        f"/api/dresses/{dress['id']}/archive",
        json={'reason': 'Needs maintenance and temporary archive'},
    )
    assert archive_response.status_code == 200, archive_response.text
    archived = archive_response.json()
    assert archived['is_active'] is False
    assert archived['updated_by_user_id'] == auth_user['id']
    assert archived['entity_version'] == 2

    active_rows = app_client.get('/api/dresses?status=active')
    assert active_rows.status_code == 200
    assert dress['id'] not in {row['id'] for row in active_rows.json()}

    inactive_rows = app_client.get('/api/dresses?status=inactive')
    assert inactive_rows.status_code == 200
    assert dress['id'] in {row['id'] for row in inactive_rows.json()}

    restore_response = app_client.post(
        f"/api/dresses/{dress['id']}/restore",
        json={'reason': 'Maintenance completed'},
    )
    assert restore_response.status_code == 200, restore_response.text
    restored = restore_response.json()
    assert restored['is_active'] is True
    assert restored['updated_by_user_id'] == auth_user['id']
    assert restored['entity_version'] == 3
