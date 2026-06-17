"""Regression tests for P3 fixes (Phase 2)."""
from __future__ import annotations

import pytest


class TestP31TopLevelImports:
    """P3.1: Verify that security.py imports are all top-level."""

    def test_any_is_importable(self):
        """Any should be importable directly from security module scope."""
        from app.core.security import Any  # noqa: F401

    def test_fernet_is_importable(self):
        """Fernet should be importable directly from security module scope."""
        from app.core.security import Fernet  # noqa: F401

    def test_base64_is_importable(self):
        """base64 should be importable directly from security module scope."""
        from app.core.security import base64  # noqa: F401

    def test_encrypt_decrypt_roundtrip(self, monkeypatch):
        """Encryption/decryption should still work after import refactor."""
        import app.core.config as config_module
        monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key-for-encryption-test-1234")
        config_module.get_settings.cache_clear()
        try:
            from app.core.security import encrypt_secret, decrypt_secret
            original = "حساب سري للاختبار"
            encrypted = encrypt_secret(original)
            assert encrypted != original
            assert decrypt_secret(encrypted) == original
        finally:
            config_module.get_settings.cache_clear()


class TestP32PermissionRequiredName:
    """P3.2: PermissionRequired closure should have a descriptive __name__."""

    def test_closure_has_descriptive_name(self):
        from app.api.deps import PermissionRequired
        dep = PermissionRequired("payments.view")
        assert dep.__name__ == "require_payments_view"

    def test_different_permissions_have_different_names(self):
        from app.api.deps import PermissionRequired
        dep1 = PermissionRequired("payments.view")
        dep2 = PermissionRequired("accounting.manage")
        assert dep1.__name__ != dep2.__name__
        assert dep1.__name__ == "require_payments_view"
        assert dep2.__name__ == "require_accounting_manage"

    def test_factory_assigned_deps_have_correct_names(self):
        """The pre-assigned factory variables should also carry __name__."""
        from app.api.deps import require_payments_view, require_accounting_manage
        assert require_payments_view.__name__ == "require_payments_view"
        assert require_accounting_manage.__name__ == "require_accounting_manage"


class TestP33EffectiveRedisUrl:
    """P3.3: effective_redis_url should handle all URL patterns correctly."""

    def _make_settings(self, monkeypatch, redis_url, redis_password=None, env_password=None):
        import app.core.config as config_module
        monkeypatch.setenv("REDIS_URL", redis_url)
        monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
        if redis_password:
            monkeypatch.setenv("REDIS_PASSWORD", redis_password)
        elif env_password:
            monkeypatch.setenv("REDIS_PASSWORD", env_password)
        else:
            monkeypatch.delenv("REDIS_PASSWORD", raising=False)
        config_module.get_settings.cache_clear()
        try:
            return config_module.get_settings()
        finally:
            config_module.get_settings.cache_clear()

    def test_no_password_returns_url_unchanged(self, monkeypatch):
        s = self._make_settings(monkeypatch, "redis://localhost:6379/0")
        assert s.effective_redis_url() == "redis://localhost:6379/0"

    def test_inject_password_into_simple_url(self, monkeypatch):
        s = self._make_settings(monkeypatch, "redis://localhost:6379/0", redis_password="secret123")
        assert s.effective_redis_url() == "redis://:secret123@localhost:6379/0"

    def test_preserve_existing_password(self, monkeypatch):
        s = self._make_settings(monkeypatch, "redis://:existingpass@redis-host:6379/0", redis_password="newpass")
        # Should keep existing password, not override
        assert s.effective_redis_url() == "redis://:existingpass@redis-host:6379/0"

    def test_fill_empty_password_slot(self, monkeypatch):
        s = self._make_settings(monkeypatch, "redis://:@redis-host:6379/0", redis_password="secret123")
        assert s.effective_redis_url() == "redis://:secret123@redis-host:6379/0"

    def test_fill_bare_at_sign(self, monkeypatch):
        s = self._make_settings(monkeypatch, "redis://@redis-host:6379/0", redis_password="secret123")
        assert s.effective_redis_url() == "redis://:secret123@redis-host:6379/0"


class TestP34TicketServiceRedisErrorHandling:
    """P3.4: ticket_service should fail-loud in production, fallback in dev/test."""

    def test_create_ticket_fallback_in_dev(self, monkeypatch):
        """In non-production, Redis failure should fall back to in-memory."""
        import app.core.config as config_module
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
        config_module.get_settings.cache_clear()
        try:
            from app.modules.exports.ticket_service import DownloadTicketStore
            store = DownloadTicketStore(expires_in_seconds=30)
            # Force _use_redis to return False (no Redis in test)
            store._use_redis = lambda: False
            ticket_id = store.create_ticket("user1", "/test/path", {"key": "value"})
            assert ticket_id is not None
            assert len(ticket_id) > 0
            # Verify ticket is consumable
            data = store.consume_ticket(ticket_id)
            assert data is not None
            assert data["user_id"] == "user1"
            assert data["path"] == "/test/path"
        finally:
            config_module.get_settings.cache_clear()

    def test_consume_ticket_returns_none_for_invalid(self, monkeypatch):
        """Consuming a non-existent ticket should return None."""
        import app.core.config as config_module
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
        config_module.get_settings.cache_clear()
        try:
            from app.modules.exports.ticket_service import DownloadTicketStore
            store = DownloadTicketStore(expires_in_seconds=30)
            store._use_redis = lambda: False
            result = store.consume_ticket("nonexistent-ticket-id")
            assert result is None
        finally:
            config_module.get_settings.cache_clear()

    def test_ticket_single_use(self, monkeypatch):
        """A ticket should only be consumable once."""
        import app.core.config as config_module
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
        config_module.get_settings.cache_clear()
        try:
            from app.modules.exports.ticket_service import DownloadTicketStore
            store = DownloadTicketStore(expires_in_seconds=30)
            store._use_redis = lambda: False
            ticket_id = store.create_ticket("user1", "/test", {})
            first = store.consume_ticket(ticket_id)
            assert first is not None
            second = store.consume_ticket(ticket_id)
            assert second is None
        finally:
            config_module.get_settings.cache_clear()
