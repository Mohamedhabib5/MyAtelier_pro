import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from starlette.requests import Request
from .test_foundation import login
from app.core.config import get_settings


@pytest.fixture(autouse=True)
def disable_security_bypass(app_client, monkeypatch):
    monkeypatch.setenv("SECURITY_BYPASS_FOR_TESTS", "false")
    get_settings.cache_clear()
    yield
    monkeypatch.setenv("SECURITY_BYPASS_FOR_TESTS", "true")
    get_settings.cache_clear()


def test_verify_backup_endpoint_is_rate_limited(app_client):
    """C4 regression: /verify-backup يجب أن يطبق rate limiter."""
    # Retrieve CSRF token first to authenticate
    app_client.get("/api/auth/me")
    csrf_token = app_client.cookies.get("myatelier_pro_csrf")
    
    settings = get_settings()
    login_response = app_client.post(
        "/api/auth/login",
        json={
            "username": settings.default_admin_username,
            "password": settings.default_admin_password
        },
        headers={"X-CSRF-Token": csrf_token or ""}
    )
    assert login_response.status_code == 200
    user_info = login_response.json()
    user_id = user_info["id"]
    
    # Enable 2FA on the user in the database
    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        from app.modules.identity.models import User
        user = db.query(User).filter(User.id == user_id).first()
        user.is_2fa_enabled = True
        user.totp_secret = "some_encrypted_secret"
        db.commit()

    headers = {"X-CSRF-Token": "dummy_csrf"}
        
    # Mock request.session using patch.object
    with patch.object(Request, "session", new_callable=PropertyMock) as mock_session:
        mock_session.return_value = {
            "user_id": user_id,
            "2fa_pending": True,
            "csrf_token": "dummy_csrf"
        }
        
        # Send multiple requests to trigger the rate limiter
        responses = []
        for _ in range(6):
            responses.append(app_client.post(
                "/api/auth/2fa/verify-backup",
                json={"code": "12345678"},
                headers=headers
            ))

        # At least one request (the 6th one) should be rate limited (429 RateLimitError)
        status_codes = [r.status_code for r in responses]
        if 429 not in status_codes:
            print("RESPONSES:", [r.status_code for r in responses], [r.json() for r in responses])
        assert 429 in status_codes, f"Expected 429 in response status codes, got: {status_codes}"


def test_verify_2fa_login_returns_false_when_2fa_disabled():
    """C4 regression: verify_2fa_login يجب أن ترجع False (لا True) عند تعطيل 2FA."""
    from app.modules.identity.security_service import verify_2fa_login
    
    user = MagicMock()
    user.is_2fa_enabled = False
    user.totp_secret = None
    user.id = "test-id"
    user.username = "test-user"
    
    db = MagicMock()
    result = verify_2fa_login(db, user, "123456")
    assert result is False, "verify_2fa_login must return False (fail-closed) when 2FA is disabled"


def test_verify_2fa_login_returns_false_when_secret_missing():
    """C4 regression: verify_2fa_login يجب أن ترجع False عند فقدان السر."""
    from app.modules.identity.security_service import verify_2fa_login
    
    user = MagicMock()
    user.is_2fa_enabled = True
    user.totp_secret = None
    user.id = "test-id"
    user.username = "test-user"
    
    db = MagicMock()
    result = verify_2fa_login(db, user, "123456")
    assert result is False
