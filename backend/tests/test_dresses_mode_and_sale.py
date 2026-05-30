from __future__ import annotations

import uuid
from fastapi.testclient import TestClient
from .test_foundation import login
from .test_bookings import seed_customer, seed_service_bundle, build_booking_line_payload, build_booking_document_payload


def seed_dress_without_validation(client: TestClient, code: str) -> str:
    # 1. Create a department
    unique_code = f"DRESS-{uuid.uuid4().hex[:6].upper()}"
    dept_res = client.post('/api/catalog/departments', json={'code': unique_code, 'name': 'قسم فساتين الاختبار'})
    assert dept_res.status_code == 201
    dept_id = dept_res.json()['id']

    # 2. Mark department as operational dresses department
    op_res = client.post('/api/catalog/operational/dresses-department', json={'department_id': dept_id})
    assert op_res.status_code == 200

    # 3. Create a dress without dress_type_id (Free mode)
    response = client.post(
        '/api/dresses',
        json={
            'code': code,
            'name': 'فستان اختبار حر',
            'dress_type_id': None,
            'status': 'available',
            'description': 'فستان حر للاختبار'
        },
    )
    assert response.status_code == 201, response.text
    return response.json()['id']


def test_dresses_mode_locking_on_first_dress(app_client: TestClient) -> None:
    login(app_client)

    # 1. Check company settings and assert default mode is 'free'
    company_res = app_client.get('/api/settings/company')
    assert company_res.status_code == 200, company_res.text
    company = company_res.json()
    assert company['dresses_mode'] == 'free'

    # 2. Try updating company mode to 'coupled' (Success since no dresses yet)
    update_res = app_client.patch(
        '/api/settings/company',
        json={
            'name': company['name'],
            'default_currency': company['default_currency'],
            'dresses_mode': 'coupled',
        },
    )
    assert update_res.status_code == 200, update_res.text
    assert update_res.json()['dresses_mode'] == 'coupled'

    # 3. Change it back to 'free'
    app_client.patch(
        '/api/settings/company',
        json={
            'name': company['name'],
            'default_currency': company['default_currency'],
            'dresses_mode': 'free',
        },
    )

    # 4. Seed first dress (locks the setting)
    dress_id = seed_dress_without_validation(app_client, "LOCK-D-1")

    # 5. Try updating company mode to 'coupled' now (Must be BLOCKED!)
    update_failed_res = app_client.patch(
        '/api/settings/company',
        json={
            'name': company['name'],
            'default_currency': company['default_currency'],
            'dresses_mode': 'coupled',
        },
    )
    assert update_failed_res.status_code == 422, update_failed_res.text
    assert "لا يمكن تغيير نظام تشغيل الفساتين" in update_failed_res.json()['detail']


def test_dress_sale_lifecycle_and_exclusion(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    dress_id = seed_dress_without_validation(app_client, "SALE-D-1")

    # 1. Create a booking and mark the line as a sale (is_sale=True)
    booking_payload = build_booking_document_payload(
        customer_id,
        [
            {
                **build_booking_line_payload(service_bundle, service_date='2026-06-01', dress_id=dress_id),
                'is_sale': True,
                'status': 'confirmed',
            }
        ],
    )
    booking_res = app_client.post('/api/bookings', json=booking_payload)
    assert booking_res.status_code == 201, booking_res.text
    booking = booking_res.json()
    assert booking['lines'][0]['is_sale'] is True

    # 2. Assert dress status is updated to 'sold'
    dress_res = app_client.get(f"/api/dresses/{dress_id}")
    assert dress_res.status_code == 200
    assert dress_res.json()['status'] == 'sold'

    # 3. Assert trying to book or sell the sold dress again in a new invoice raises a validation error
    booking_failed_res = app_client.post(
        '/api/bookings',
        json=build_booking_document_payload(
            customer_id,
            [build_booking_line_payload(service_bundle, service_date='2026-06-02', dress_id=dress_id)],
        ),
    )
    assert booking_failed_res.status_code == 422, booking_failed_res.text
    assert "مباع بالفعل" in booking_failed_res.json()['detail']

    # 4. Assert delete booking line reverts dress status to 'available'
    delete_line_res = app_client.delete(f"/api/bookings/{booking['id']}/lines/{booking['lines'][0]['id']}")
    assert delete_line_res.status_code == 200, delete_line_res.text

    dress_reverted_res = app_client.get(f"/api/dresses/{dress_id}")
    assert dress_reverted_res.json()['status'] == 'available'
