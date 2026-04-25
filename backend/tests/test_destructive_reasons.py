from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login


def test_destructive_reasons_endpoint_returns_reason_catalog(app_client: TestClient) -> None:
    login(app_client)

    response = app_client.get('/api/settings/destructive-reasons')
    assert response.status_code == 200, response.text
    items = response.json()
    assert len(items) >= 3
    codes = {item['code'] for item in items}
    assert 'entry_mistake' in codes
    assert 'financial_correction' in codes


def test_destructive_reasons_endpoint_supports_action_filter(app_client: TestClient) -> None:
    login(app_client)

    response = app_client.get('/api/settings/destructive-reasons', params={'action': 'void'})
    assert response.status_code == 200, response.text
    items = response.json()
    assert items
    for item in items:
        assert 'void' in item['actions']
