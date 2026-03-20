from __future__ import annotations

from fastapi.testclient import TestClient

from .test_branch_scope import create_second_branch
from .test_foundation import login


def test_admin_can_create_list_run_and_toggle_export_schedule(app_client: TestClient) -> None:
    login(app_client)

    created = app_client.post(
        '/api/exports/schedules',
        json={'name': 'جدول مدفوعات يومي', 'export_type': 'payments_csv', 'cadence': 'daily', 'start_on': '2026-03-20'},
    )
    assert created.status_code == 200, created.text
    schedule = created.json()
    assert schedule['export_type'] == 'payments_csv'
    assert schedule['branch_id'] is not None
    assert schedule['next_run_on'] == '2026-03-20'

    listed = app_client.get('/api/exports/schedules')
    assert listed.status_code == 200, listed.text
    assert len(listed.json()) == 1

    run_now = app_client.post(f"/api/exports/schedules/{schedule['id']}/run")
    assert run_now.status_code == 200, run_now.text
    run_payload = run_now.json()
    assert run_payload['run_url'].startswith('/api/exports/payment-documents.csv?branch_id=')
    assert run_payload['schedule']['next_run_on'] == '2026-03-21'
    assert run_payload['schedule']['last_run_at'] is not None

    toggled = app_client.post(f"/api/exports/schedules/{schedule['id']}/toggle")
    assert toggled.status_code == 200, toggled.text
    assert toggled.json()['schedule']['is_active'] is False

    rerun = app_client.post(f"/api/exports/schedules/{schedule['id']}/run")
    assert rerun.status_code == 422
    assert 'غير النشطة' in rerun.json()['detail']


def test_company_and_print_schedules_return_expected_urls(app_client: TestClient) -> None:
    login(app_client)

    customers = app_client.post(
        '/api/exports/schedules',
        json={'name': 'عملاء أسبوعي', 'export_type': 'customers_csv', 'cadence': 'weekly'},
    )
    assert customers.status_code == 200, customers.text
    customers_run = app_client.post(f"/api/exports/schedules/{customers.json()['id']}/run")
    assert customers_run.status_code == 200
    assert customers_run.json()['run_url'] == '/api/exports/customers.csv'

    finance_print = app_client.post(
        '/api/exports/schedules',
        json={'name': 'مالية أسبوعية', 'export_type': 'finance_print', 'cadence': 'weekly'},
    )
    assert finance_print.status_code == 200, finance_print.text
    print_run = app_client.post(f"/api/exports/schedules/{finance_print.json()['id']}/run")
    assert print_run.status_code == 200
    assert print_run.json()['run_url'].startswith('/print/finance?branchId=')


def test_regular_user_cannot_manage_export_schedules(app_client: TestClient) -> None:
    login(app_client)
    user_response = app_client.post(
        '/api/users',
        json={'username': 'exports.user', 'full_name': 'Exports User', 'password': 'secret123', 'role_names': ['user']},
    )
    assert user_response.status_code == 201

    app_client.post('/api/auth/logout')
    login(app_client, username='exports.user', password='secret123')

    listed = app_client.get('/api/exports/schedules')
    assert listed.status_code == 403

    created = app_client.post(
        '/api/exports/schedules',
        json={'name': 'غير مصرح', 'export_type': 'customers_csv', 'cadence': 'daily'},
    )
    assert created.status_code == 403
