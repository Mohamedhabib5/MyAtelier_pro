import time
import pytest
from app.core.rate_limiter import InMemoryRateLimiter
from app.core.exceptions import RateLimitError
from app.core.config import get_settings


@pytest.fixture(autouse=True)
def disable_security_bypass():
    settings = get_settings()
    old_val = settings.security_bypass_for_tests
    settings.security_bypass_for_tests = False
    yield
    settings.security_bypass_for_tests = old_val


def test_rate_limiter_allows_requests():
    limiter = InMemoryRateLimiter(requests=3, window_seconds=1)
    key = "test_user"
    
    assert limiter.is_allowed(key) is True
    assert limiter.is_allowed(key) is True
    assert limiter.is_allowed(key) is True
    assert limiter.is_allowed(key) is False


def test_rate_limiter_resets_after_window():
    limiter = InMemoryRateLimiter(requests=1, window_seconds=1)
    key = "test_user"
    
    assert limiter.is_allowed(key) is True
    assert limiter.is_allowed(key) is False
    
    time.sleep(1.1)
    assert limiter.is_allowed(key) is True


def test_rate_limiter_is_thread_safe():
    import threading
    
    limiter = InMemoryRateLimiter(requests=100, window_seconds=60)
    key = "test_user"
    
    def worker():
        for _ in range(10):
            limiter.is_allowed(key)
            
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert len(limiter.history[key]) == 100


def test_production_cors_rejects_localhost_8080(monkeypatch):
    """H1 regression: localhost:8080 يجب أن يُرفض في الإنتاج."""
    from app.core.config import Settings
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("APP_SECRET_KEY", "a" * 64)
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", "not-admin123")
    monkeypatch.setenv("APP_FRONTEND_ORIGINS", "http://localhost:8080")
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@db:5432/x")
    monkeypatch.setenv("SESSION_HTTPS_ONLY", "true")
    
    Settings._initialized = False  # reset cache
    settings = Settings()
    with pytest.raises(ValueError, match="Localhost origins are not allowed"):
        settings.validate_runtime_settings()


def test_2fa_setup_response_does_not_leak_secret(app_client):
    """C5 regression: setup_2fa response يجب ألا يحوي secret_plain."""
    from .test_foundation import login
    login(app_client)
    response = app_client.post("/api/auth/2fa/setup")
    assert response.status_code == 200
    response_json = response.json()
    assert "secret_plain" not in response_json, "secret_plain must not be exposed in 2FA setup response"
    assert "secret_base32" in response_json, "secret_base32 must be returned for manual configuration"
    assert "provisioning_uri" in response_json
