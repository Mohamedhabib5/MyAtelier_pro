import pytest
from fastapi.testclient import TestClient
from app.core.config import get_settings


@pytest.fixture(autouse=True)
def disable_security_bypass(app_client, monkeypatch):
    monkeypatch.setenv("SECURITY_BYPASS_FOR_TESTS", "false")
    get_settings.cache_clear()
    yield
    monkeypatch.setenv("SECURITY_BYPASS_FOR_TESTS", "true")
    get_settings.cache_clear()


@pytest.mark.guardrail
def test_post_without_csrf_token_returns_403(app_client):
    """C3 regression: POST بدون توكن CSRF يجب أن يُرفض بـ 403."""
    response = app_client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 403
    assert "CSRF" in response.json()["detail"]


def test_post_with_valid_csrf_token_succeeds(app_client):
    """C3 regression: POST بتوكن CSRF صحيح يجب أن يُعالَج."""
    # الحصول على توكن CSRF من cookie
    response = app_client.get("/api/auth/me")  # يعين الـ cookie
    csrf_token = None
    for cookie_name, cookie_value in app_client.cookies.items():
        if cookie_name == "myatelier_pro_csrf":
            csrf_token = cookie_value
            break

    # نفِّذ POST مع الـ header
    response = app_client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    }, headers={"X-CSRF-Token": csrf_token or ""})
    # قد يفشل بـ 401 (credentials خاطئة) لكن لا يجب أن يفشل بـ 403 CSRF
    assert response.status_code != 403


def test_get_does_not_require_csrf(app_client):
    """C3 regression: GET لا يجب أن يتطلب CSRF."""
    response = app_client.get("/api/health")
    assert response.status_code != 403
