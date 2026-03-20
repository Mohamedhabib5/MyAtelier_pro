from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login


def test_admin_can_create_list_and_update_dress(app_client: TestClient) -> None:
    login(app_client)

    create_response = app_client.post(
        '/api/dresses',
        json={
            'code': 'D-001',
            'dress_type': 'زفاف',
            'purchase_date': '2026-03-01',
            'status': 'available',
            'description': 'فستان أبيض أساسي',
            'image_path': 'dress_images/d-001.jpg',
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created['code'] == 'D-001'

    list_response = app_client.get('/api/dresses')
    assert list_response.status_code == 200
    rows = list_response.json()
    assert len(rows) == 1

    update_response = app_client.patch(
        f"/api/dresses/{created['id']}",
        json={
            'code': 'D-001',
            'dress_type': 'خطوبة',
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
    assert updated['dress_type'] == 'خطوبة'


def test_duplicate_dress_code_is_blocked(app_client: TestClient) -> None:
    login(app_client)
    payload = {
        'code': 'D-002',
        'dress_type': 'زفاف',
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
        json={'username': 'dress.user', 'full_name': 'Dress User', 'password': 'secret123', 'role_names': ['user']},
    )
    assert user_response.status_code == 201

    app_client.post('/api/auth/logout')
    login(app_client, username='dress.user', password='secret123')

    create_response = app_client.post(
        '/api/dresses',
        json={'code': 'D-003', 'dress_type': 'سواريه', 'status': 'reserved', 'description': 'جاهز لحجز قادم'},
    )
    assert create_response.status_code == 201, create_response.text

    list_response = app_client.get('/api/dresses')
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
