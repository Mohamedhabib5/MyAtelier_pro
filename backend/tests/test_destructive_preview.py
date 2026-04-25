from __future__ import annotations

from fastapi.testclient import TestClient

from .test_bookings import seed_dress
from .test_foundation import login
from .test_payments import seed_booking_context


def test_destructive_preview_allows_unlinked_dress_hard_delete(app_client: TestClient) -> None:
    login(app_client)
    dress_id = seed_dress(app_client, code='DR-PREVIEW-FREE')

    response = app_client.post(
        '/api/settings/destructive-preview',
        json={
            'entity_type': 'dress',
            'entity_id': dress_id,
            'reason_code': 'entry_mistake',
            'reason_text': 'تم إدخال الفستان بالخطأ',
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['entity_type'] == 'dress'
    assert payload['eligible_for_hard_delete'] is True
    assert payload['impact']['booking_lines_count'] == 0


def test_destructive_preview_blocks_service_with_booking_history(app_client: TestClient) -> None:
    login(app_client)
    context = seed_booking_context(app_client)
    service_id = context['service_bundle']['service_id']

    response = app_client.post(
        '/api/settings/destructive-preview',
        json={
            'entity_type': 'service',
            'entity_id': service_id,
            'reason_code': 'entry_mistake',
            'reason_text': 'تصحيح بيانات',
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['entity_type'] == 'service'
    assert payload['eligible_for_hard_delete'] is False
    assert payload['impact']['booking_lines_count'] >= 1
    assert payload['blockers']


def test_destructive_preview_rejects_invalid_reason_code(app_client: TestClient) -> None:
    login(app_client)
    dress_id = seed_dress(app_client, code='DR-PREVIEW-BAD-REASON')

    response = app_client.post(
        '/api/settings/destructive-preview',
        json={'entity_type': 'dress', 'entity_id': dress_id, 'reason_code': 'wrong_code'},
    )
    assert response.status_code == 422
    assert 'رمز السبب غير صالح' in response.json()['detail']
