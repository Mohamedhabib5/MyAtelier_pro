from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import (
    build_booking_line_payload,
    create_booking_document,
    seed_customer,
    seed_dress,
    seed_service_bundle,
)
from .test_foundation import login


def seed_booking_context(
    client: TestClient,
    *,
    customer_id: str | None = None,
    service_bundle: dict | None = None,
    dress_code: str = 'PAY-DR-001',
    service_date: str = '2026-07-01',
    line_price: float = 3000,
    initial_payment_amount: float | None = None,
) -> dict:
    customer_id = customer_id or seed_customer(client)
    service_bundle = service_bundle or seed_service_bundle(client)
    dress_id = seed_dress(client, code=dress_code)
    booking = create_booking_document(
        client,
        customer_id,
        [
            build_booking_line_payload(
                service_bundle,
                service_date=service_date,
                dress_id=dress_id,
                line_price=line_price,
                initial_payment_amount=initial_payment_amount,
            )
        ],
    )
    return {
        'customer_id': customer_id,
        'service_bundle': service_bundle,
        'dress_id': dress_id,
        'booking': booking,
        'booking_id': booking['id'],
        'line_id': booking['lines'][0]['id'],
    }


def test_admin_can_create_list_and_update_payment_document(app_client: TestClient) -> None:
    auth_user = login(app_client)
    context = seed_booking_context(app_client)

    create_response = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-01',
            'notes': 'عربون الحجز',
            'allocations': [
                {
                    'booking_id': context['booking_id'],
                    'booking_line_id': context['line_id'],
                    'allocated_amount': 1000,
                }
            ],
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created['payment_number'].startswith('PAY')
    assert created['total_amount'] == 1000.0
    assert created['allocation_count'] == 1
    assert created['payment_method_id']
    assert created['payment_method_name']
    assert created['allocations'][0]['booking_line_id'] == context['line_id']
    assert created['created_by_user_id'] == auth_user['id']
    assert created['updated_by_user_id'] == auth_user['id']
    assert created['entity_version'] == 1
    assert created['allocations'][0]['created_by_user_id'] == auth_user['id']
    assert created['allocations'][0]['updated_by_user_id'] == auth_user['id']
    assert created['allocations'][0]['entity_version'] == 1

    update_response = app_client.patch(
        f"/api/payments/{created['id']}",
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-02',
            'notes': 'دفعة محدثة',
            'allocations': [
                {
                    'booking_id': context['booking_id'],
                    'booking_line_id': context['line_id'],
                    'allocated_amount': 1200,
                }
            ],
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated['total_amount'] == 1200.0
    assert updated['allocations'][0]['allocated_amount'] == 1200.0
    assert updated['payment_method_id']
    assert updated['payment_method_name']
    assert updated['updated_by_user_id'] == auth_user['id']
    assert updated['entity_version'] == 2
    assert updated['allocations'][0]['created_by_user_id'] == auth_user['id']
    assert updated['allocations'][0]['updated_by_user_id'] == auth_user['id']
    assert updated['allocations'][0]['entity_version'] == 1

    list_response = app_client.get('/api/payments')
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_payment_document_can_allocate_across_multiple_lines_and_bookings(app_client: TestClient) -> None:
    login(app_client)
    customer_id = seed_customer(app_client)
    service_bundle = seed_service_bundle(app_client)
    first_dress_id = seed_dress(app_client, code='PAY-MULTI-1')
    second_dress_id = seed_dress(app_client, code='PAY-MULTI-2')
    third_dress_id = seed_dress(app_client, code='PAY-MULTI-3')

    booking_one = create_booking_document(
        app_client,
        customer_id,
        [
            build_booking_line_payload(service_bundle, service_date='2026-07-10', dress_id=first_dress_id, line_price=1800),
            build_booking_line_payload(service_bundle, service_date='2026-07-11', dress_id=second_dress_id, line_price=2200),
        ],
    )
    booking_two = create_booking_document(
        app_client,
        customer_id,
        [build_booking_line_payload(service_bundle, service_date='2026-07-12', dress_id=third_dress_id, line_price=2600)],
    )

    create_response = app_client.post(
        '/api/payments',
        json={
            'customer_id': customer_id,
            'payment_date': '2026-06-05',
            'allocations': [
                {'booking_id': booking_one['id'], 'booking_line_id': booking_one['lines'][0]['id'], 'allocated_amount': 300},
                {'booking_id': booking_one['id'], 'booking_line_id': booking_one['lines'][1]['id'], 'allocated_amount': 450},
                {'booking_id': booking_two['id'], 'booking_line_id': booking_two['lines'][0]['id'], 'allocated_amount': 700},
            ],
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created['allocation_count'] == 3
    assert created['total_amount'] == 1450.0
    assert set(created['booking_numbers']) == {booking_one['booking_number'], booking_two['booking_number']}


def test_payment_document_uses_selected_payment_method(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client, dress_code='PAY-METHOD-1')
    payment_method = app_client.post('/api/payment-methods', json={'name': 'Bank Transfer', 'code': 'bank_transfer'})
    assert payment_method.status_code == 201, payment_method.text
    payment_method_id = payment_method.json()['id']

    create_response = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_method_id': payment_method_id,
            'payment_date': '2026-06-09',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 900}],
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created['payment_method_id'] == payment_method_id
    assert created['payment_method_name'] == 'Bank Transfer'


def test_overallocation_and_cross_customer_mix_are_blocked(app_client: TestClient) -> None:
    login(app_client)
    primary = seed_booking_context(app_client)

    first_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': primary['customer_id'],
            'payment_date': '2026-06-01',
            'allocations': [{'booking_id': primary['booking_id'], 'booking_line_id': primary['line_id'], 'allocated_amount': 500}],
        },
    )
    assert first_payment.status_code == 201

    overpay = app_client.post(
        '/api/payments',
        json={
            'customer_id': primary['customer_id'],
            'payment_date': '2026-06-02',
            'allocations': [{'booking_id': primary['booking_id'], 'booking_line_id': primary['line_id'], 'allocated_amount': 2600}],
        },
    )
    assert overpay.status_code == 422
    assert 'المتبقي' in overpay.json()['detail']

    second_customer = app_client.post('/api/customers', json={'full_name': 'Bride Two', 'phone': '01010010011'})
    assert second_customer.status_code == 201, second_customer.text
    second_context = seed_booking_context(app_client, customer_id=second_customer.json()['id'], dress_code='PAY-DR-002')

    mixed_customer = app_client.post(
        '/api/payments',
        json={
            'customer_id': primary['customer_id'],
            'payment_date': '2026-06-03',
            'allocations': [
                {'booking_id': primary['booking_id'], 'booking_line_id': primary['line_id'], 'allocated_amount': 200},
                {'booking_id': second_context['booking_id'], 'booking_line_id': second_context['line_id'], 'allocated_amount': 200},
            ],
        },
    )
    assert mixed_customer.status_code == 404
    assert 'لم يتم العثور' in mixed_customer.json()['detail']


def test_regular_user_can_manage_payments(app_client: TestClient) -> None:
    login(app_client)
    user_response = app_client.post(
        '/api/users',
        json={'username': 'payment.user', 'full_name': 'Payment User', 'password': 'secret123', 'role_names': ['user']},
    )
    assert user_response.status_code == 201
    context = seed_booking_context(app_client)

    app_client.post('/api/auth/logout')
    login(app_client, username='payment.user', password='secret123')

    create_response = app_client.post(
        '/api/payments',
        json={
            'customer_id': context['customer_id'],
            'payment_date': '2026-06-10',
            'allocations': [{'booking_id': context['booking_id'], 'booking_line_id': context['line_id'], 'allocated_amount': 750}],
        },
    )
    assert create_response.status_code == 201, create_response.text

    list_response = app_client.get('/api/payments')
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_payment_table_endpoint_supports_search_filters_and_paging(app_client: TestClient) -> None:
    login(app_client)
    primary = seed_booking_context(app_client, dress_code='PAY-TABLE-1')
    secondary_customer = app_client.post('/api/customers', json={'full_name': 'Payment Search', 'phone': '01010010013'})
    assert secondary_customer.status_code == 201, secondary_customer.text
    secondary = seed_booking_context(app_client, customer_id=secondary_customer.json()['id'], dress_code='PAY-TABLE-2', service_date='2026-07-02')

    first_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': primary['customer_id'],
            'payment_date': '2026-06-01',
            'notes': 'سند أول',
            'allocations': [{'booking_id': primary['booking_id'], 'booking_line_id': primary['line_id'], 'allocated_amount': 700}],
        },
    )
    assert first_payment.status_code == 201, first_payment.text
    second_payment = app_client.post(
        '/api/payments',
        json={
            'customer_id': secondary['customer_id'],
            'payment_date': '2026-06-02',
            'notes': 'سند للبحث',
            'allocations': [{'booking_id': secondary['booking_id'], 'booking_line_id': secondary['line_id'], 'allocated_amount': 800}],
        },
    )
    assert second_payment.status_code == 201, second_payment.text

    list_response = app_client.get('/api/payments/table', params={'search': 'Search', 'page': 1, 'page_size': 1, 'sort_by': 'customer_name', 'sort_dir': 'asc'})
    assert list_response.status_code == 200, list_response.text
    payload = list_response.json()
    assert payload['total'] == 1
    assert payload['items'][0]['id'] == second_payment.json()['id']

    filtered_response = app_client.get('/api/payments/table', params={'status': 'active', 'date_from': '2026-06-01', 'date_to': '2026-06-01'})
    assert filtered_response.status_code == 200, filtered_response.text
    filtered_payload = filtered_response.json()
    assert filtered_payload['total'] == 1
    assert filtered_payload['items'][0]['id'] == first_payment.json()['id']
