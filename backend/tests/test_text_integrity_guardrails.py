from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import build_booking_document_payload, build_booking_line_payload, seed_customer, seed_dress, seed_service_bundle
from .test_foundation import login


def test_booking_date_validation_message_is_arabic(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(
        app_client,
        department_code='MAKEUP',
        department_name='قسم المكياج',
        service_name='خدمة عربية',
        default_price=1200,
    )

    response = app_client.post(
        '/api/bookings',
        json=build_booking_document_payload(
            customer_id,
            [build_booking_line_payload(service_bundle, service_date='', line_price=1200)],
            booking_date='',
        ),
    )
    assert response.status_code == 422
    assert 'التاريخ مطلوب' in response.json()['detail']


def test_dress_department_detection_uses_department_code(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(
        app_client,
        department_code='DRESS-CODE',
        department_name='Bridal Rentals',
        service_name='Dress Fitting',
        default_price=900,
    )
    dress_id = seed_dress(app_client, code='TXT-DR-001')

    response = app_client.post(
        '/api/bookings',
        json=build_booking_document_payload(
            customer_id,
            [build_booking_line_payload(service_bundle, service_date='2026-08-22', dress_id=dress_id, line_price=1800)],
        ),
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload['lines'][0]['dress_id'] == dress_id
