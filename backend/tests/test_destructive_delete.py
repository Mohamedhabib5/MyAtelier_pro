from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.core_platform.models import AuditLog
from .test_bookings import seed_dress
from .test_foundation import login
from .test_payments import seed_booking_context


def _latest_audit(app_client: TestClient, action: str) -> AuditLog | None:
    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        return db.scalars(select(AuditLog).where(AuditLog.action == action).order_by(AuditLog.occurred_at.desc())).first()


def test_destructive_delete_removes_unlinked_dress(app_client: TestClient) -> None:
    login(app_client)
    dress_id = seed_dress(app_client, code='DR-DELETE-OK')

    delete_response = app_client.post(
        '/api/settings/destructive-delete',
        json={
            'entity_type': 'dress',
            'entity_id': dress_id,
            'reason_code': 'entry_mistake',
            'reason_text': 'تم الإدخال بشكل خاطئ',
        },
    )
    assert delete_response.status_code == 200, delete_response.text
    payload = delete_response.json()
    assert payload['deleted'] is True
    assert payload['entity_type'] == 'dress'
    assert payload['entity_id'] == dress_id

    dresses_response = app_client.get('/api/dresses', params={'status': 'all'})
    assert dresses_response.status_code == 200, dresses_response.text
    ids = {row['id'] for row in dresses_response.json()}
    assert dress_id not in ids

    row = _latest_audit(app_client, 'destructive.deleted')
    assert row is not None
    assert row.target_type == 'dress'
    assert row.target_id == dress_id
    assert row.reason_code == 'entry_mistake'
    payload = json.loads(row.diff_json or '{}')
    assert payload.get('tombstone_before', {}).get('id') == dress_id
    assert payload.get('tombstone_before', {}).get('code') == 'DR-DELETE-OK'
    assert payload.get('deleted_at')


def test_destructive_delete_blocks_service_with_booking_links(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)
    service_id = context['service_bundle']['service_id']

    delete_response = app_client.post(
        '/api/settings/destructive-delete',
        json={'entity_type': 'service', 'entity_id': service_id, 'reason_code': 'entry_mistake'},
    )
    assert delete_response.status_code == 422
    assert 'لا يمكن الحذف' in delete_response.json()['detail']


def test_destructive_delete_requires_permission(app_client: TestClient) -> None:
    login(app_client)
    create_user = app_client.post(
        '/api/users',
        json={'username': 'destructive.user', 'full_name': 'Destructive User', 'password': 'secret123', 'role_names': ['user']},
    )
    assert create_user.status_code == 201, create_user.text
    dress_id = seed_dress(app_client, code='DR-DELETE-PERM')

    app_client.post('/api/auth/logout')
    login(app_client, username='destructive.user', password='secret123')

    delete_response = app_client.post(
        '/api/settings/destructive-delete',
        json={'entity_type': 'dress', 'entity_id': dress_id, 'reason_code': 'entry_mistake'},
    )
    assert delete_response.status_code == 403
