from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from .test_foundation import login


def seed_customer(client: TestClient) -> str:
    response = client.post('/api/customers', json={'full_name': 'Bride One', 'phone': '01010010010'})
    assert response.status_code == 201, response.text
    return response.json()['id']


def seed_service_bundle(
    client: TestClient,
    *,
    department_code: str = 'DRESS',
    department_name: str = 'قسم الفساتين',
    service_name: str = 'تجربة فستان',
    default_price: float = 700,
    tax_rate_percent: float = 0,
) -> dict:
    unique_code = f"{department_code}-{uuid4().hex[:6]}"
    dept = client.post('/api/catalog/departments', json={'code': unique_code, 'name': department_name})
    assert dept.status_code == 201, dept.text
    department_id = dept.json()['id']
    unique_service_name = f"{service_name} {uuid4().hex[:4]}"
    service = client.post(
        '/api/catalog/services',
        json={'department_id': department_id, 'name': unique_service_name, 'default_price': default_price, 'tax_rate_percent': tax_rate_percent},
    )
    assert service.status_code == 201, service.text
    return {
        'department_id': department_id,
        'service_id': service.json()['id'],
        'default_price': default_price,
        'tax_rate_percent': tax_rate_percent,
        'service_name': unique_service_name,
        'department_name': department_name,
    }


def seed_service(client: TestClient) -> str:
    return seed_service_bundle(client)['service_id']


def seed_dress(client: TestClient, code: str = 'DR-001') -> str:
    response = client.post(
        '/api/dresses',
        json={'code': code, 'dress_type': 'زفاف', 'status': 'available', 'description': 'فستان للاختبار'},
    )
    assert response.status_code == 201, response.text
    return response.json()['id']


def build_booking_line_payload(
    service_bundle: dict,
    *,
    service_date: str,
    dress_id: str | None = None,
    line_price: float = 2500,
    status: str = 'confirmed',
    initial_payment_amount: float | None = None,
    notes: str | None = None,
) -> dict:
    return {
        'department_id': service_bundle['department_id'],
        'service_id': service_bundle['service_id'],
        'service_date': service_date,
        'dress_id': dress_id,
        'suggested_price': service_bundle['default_price'],
        'line_price': line_price,
        'initial_payment_amount': initial_payment_amount,
        'status': status,
        'notes': notes,
    }


def build_booking_document_payload(
    customer_id: str,
    lines: list[dict],
    *,
    booking_date: str = '2026-03-16',
    notes: str | None = None,
) -> dict:
    return {
        'customer_id': customer_id,
        'booking_date': booking_date,
        'notes': notes,
        'lines': lines,
    }


def create_booking_document(
    client: TestClient,
    customer_id: str,
    lines: list[dict],
    *,
    booking_date: str = '2026-03-16',
    notes: str | None = None,
) -> dict:
    response = client.post(
        '/api/bookings',
        json=build_booking_document_payload(customer_id, lines, booking_date=booking_date, notes=notes),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_admin_can_create_list_and_update_booking_document(app_client: TestClient) -> None:
    auth_user = login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    dress_id = seed_dress(app_client)

    created = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-04-01', dress_id=dress_id, line_price=2500)],
        notes='حجز أساسي',
    )
    assert created['booking_number'].startswith('BK')
    assert created['line_count'] == 1
    assert created['lines'][0]['service_date'] == '2026-04-01'
    assert created['created_by_user_id'] == auth_user['id']
    assert created['updated_by_user_id'] == auth_user['id']
    assert created['entity_version'] == 1
    assert created['lines'][0]['created_by_user_id'] == auth_user['id']
    assert created['lines'][0]['updated_by_user_id'] == auth_user['id']
    assert created['lines'][0]['entity_version'] == 1

    list_response = app_client.get('/api/bookings')
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    updated = app_client.patch(
        f"/api/bookings/{created['id']}",
        json=build_booking_document_payload(
            customer_id,
            [
                {
                    **build_booking_line_payload(service_bundle, service_date='2026-04-02', dress_id=dress_id, line_price=2700),
                    'id': created['lines'][0]['id'],
                }
            ],
            notes='تم التحديث',
        ),
    )
    assert updated.status_code == 200, updated.text
    payload = updated.json()
    assert payload['status'] == 'confirmed'
    assert payload['notes'] == 'تم التحديث'
    assert payload['lines'][0]['line_price'] == 2700.0
    assert payload['updated_by_user_id'] == auth_user['id']
    assert payload['entity_version'] == 2
    assert payload['lines'][0]['updated_by_user_id'] == auth_user['id']
    assert payload['lines'][0]['entity_version'] == 2


def test_multi_line_booking_can_create_single_initial_payment_document(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    first_dress_id = seed_dress(app_client, code='DR-MULTI-1')
    second_dress_id = seed_dress(app_client, code='DR-MULTI-2')

    created = create_booking_document(
        app_client,
        customer_id,
        [
            build_booking_line_payload(
                service_bundle,
                service_date='2026-04-10',
                dress_id=first_dress_id,
                line_price=2000,
                initial_payment_amount=200,
            ),
            build_booking_line_payload(
                service_bundle,
                service_date='2026-04-11',
                dress_id=second_dress_id,
                line_price=3000,
                initial_payment_amount=300,
            ),
        ],
    )
    assert created['line_count'] == 2
    assert created['paid_total'] == 500.0
    assert created['remaining_amount'] == 4500.0

    payments = app_client.get('/api/payments')
    assert payments.status_code == 200, payments.text
    payment_rows = payments.json()
    assert len(payment_rows) == 1
    assert payment_rows[0]['allocation_count'] == 2
    assert payment_rows[0]['total_amount'] == 500.0
    assert payment_rows[0]['booking_numbers'] == [created['booking_number']]


def test_booking_initial_payment_uses_selected_payment_method(app_client: TestClient) -> None:
    login(app_client)
    payment_method = app_client.post('/api/payment-methods', json={'name': 'Wallet', 'code': 'wallet'})
    assert payment_method.status_code == 201, payment_method.text
    payment_method_id = payment_method.json()['id']
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    dress_id = seed_dress(app_client, code='DR-PM-BOOK-1')

    create_response = app_client.post(
        '/api/bookings',
        json=build_booking_document_payload(
            customer_id,
            [
                build_booking_line_payload(
                    service_bundle,
                    service_date='2026-07-01',
                    dress_id=dress_id,
                    line_price=2200,
                    initial_payment_amount=300,
                )
            ],
            notes='booking with payment method',
        )
        | {'initial_payment_method_id': payment_method_id},
    )
    assert create_response.status_code == 201, create_response.text

    payments = app_client.get('/api/payments')
    assert payments.status_code == 200, payments.text
    rows = payments.json()
    assert len(rows) >= 1
    assert any(row['payment_method_id'] == payment_method_id for row in rows)


def test_duplicate_dress_same_date_is_blocked(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    second_customer = app_client.post('/api/customers', json={'full_name': 'Bride Two', 'phone': '01010010011'})
    assert second_customer.status_code == 201
    second_customer_id = second_customer.json()['id']
    service_bundle = seed_service_bundle(app_client)
    dress_id = seed_dress(app_client, code='DR-002')

    first_booking = app_client.post(
        '/api/bookings',
        json=build_booking_document_payload(
            customer_id,
            [build_booking_line_payload(service_bundle, service_date='2026-05-01', dress_id=dress_id, line_price=2000)],
        ),
    )
    assert first_booking.status_code == 201

    second_booking = app_client.post(
        '/api/bookings',
        json=build_booking_document_payload(
            second_customer_id,
            [build_booking_line_payload(service_bundle, service_date='2026-05-01', dress_id=dress_id, line_price=2100)],
        ),
    )
    assert second_booking.status_code == 422
    assert 'محجوز بالفعل' in second_booking.json()['detail']


def test_regular_user_can_manage_bookings(app_client: TestClient) -> None:
    login(app_client)
    user_response = app_client.post(
        '/api/users',
        json={'username': 'booking.user', 'full_name': 'Booking User', 'password': 'secret123', 'role_names': ['user']},
    )
    assert user_response.status_code == 201
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client, department_code='MAKEUP', department_name='قسم المكياج', service_name='مكياج مناسب', default_price=1800)

    app_client.post('/api/auth/logout')
    login(app_client, username='booking.user', password='secret123')

    create_response = app_client.post(
        '/api/bookings',
        json=build_booking_document_payload(
            customer_id,
            [build_booking_line_payload(service_bundle, service_date='2026-06-10', line_price=1800, status='draft')],
        ),
    )
    assert create_response.status_code == 201, create_response.text

    list_response = app_client.get('/api/bookings')
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_booking_table_endpoint_supports_search_filters_and_paging(app_client: TestClient) -> None:
    login(app_client)
    first_customer = seed_customer(app_client)
    second_customer_response = app_client.post('/api/customers', json={'full_name': 'Bride Search', 'phone': '01010010012'})
    assert second_customer_response.status_code == 201, second_customer_response.text
    second_customer = second_customer_response.json()['id']
    service_bundle = seed_service_bundle(app_client)
    first_dress_id = seed_dress(app_client, code='DR-TABLE-1')
    second_dress_id = seed_dress(app_client, code='DR-TABLE-2')

    first_booking = create_booking_document(
        app_client,
        first_customer,
        [build_booking_line_payload(service_bundle, service_date='2026-04-15', dress_id=first_dress_id, line_price=2100)],
        booking_date='2026-04-10',
        notes='ملاحظة أولى',
    )
    second_booking = create_booking_document(
        app_client,
        second_customer,
        [build_booking_line_payload(service_bundle, service_date='2026-05-10', dress_id=second_dress_id, line_price=2600, status='draft')],
        booking_date='2026-05-01',
        notes='ملاحظة بحث',
    )

    list_response = app_client.get('/api/bookings/table', params={'search': 'Search', 'page': 1, 'page_size': 1, 'sort_by': 'customer_name', 'sort_dir': 'asc'})
    assert list_response.status_code == 200, list_response.text
    payload = list_response.json()
    assert payload['total'] == 1
    assert payload['page'] == 1
    assert payload['page_size'] == 1
    assert payload['items'][0]['id'] == second_booking['id']

    filtered_response = app_client.get('/api/bookings/table', params={'status': 'confirmed', 'date_from': '2026-04-01', 'date_to': '2026-04-30'})
    assert filtered_response.status_code == 200, filtered_response.text
    filtered_payload = filtered_response.json()
    assert filtered_payload['total'] == 1
    assert filtered_payload['items'][0]['id'] == first_booking['id']
