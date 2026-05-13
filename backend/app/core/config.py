from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_SECRET_KEYS = {"change-me", "change-me-before-production", "test-secret"}
VALID_SAMESITE_VALUES = {"lax", "strict", "none"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "MyAtelier Pro"
    app_env: str = "development"
    app_debug: bool = True
    app_secret_key: str = "change-me"
    app_frontend_origin: str = "http://localhost:5173"
    app_frontend_origins: str = "http://localhost:5173"
    allowed_hosts: str = "localhost,127.0.0.1,backend,testserver"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/myatelier_pro"

    storage_root: str = "./storage"
    backup_storage_dir: str = "./storage/backups"
    attachment_storage_dir: str = "./storage/attachments"

    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"
    default_company_name: str = "MyAtelier Pro"
    session_cookie_name: str = "myatelier_pro_session"
    session_same_site: str = "lax"
    session_https_only: bool = False
    session_max_age_seconds: int = 43200
    ops_backup_stale_threshold_hours: int = 30
    ops_alert_webhook_url: str = ""
    nightly_failure_ingest_token: str = ""
    export_delivery_webhook_url: str = ""
    max_image_size_bytes: int = 307200  # 300 KB
    redis_url: str = "redis://localhost:6379/0"

    csrf_cookie_name: str = "myatelier_pro_csrf"
    csrf_header_name: str = "X-CSRF-Token"
    csrf_secret_key: str | None = None  # If None, will fallback to app_secret_key


    def resolved_storage_root(self) -> Path:
        return Path(self.storage_root).resolve()

    def resolved_backup_dir(self) -> Path:
        return Path(self.backup_storage_dir).resolve()

    def resolved_attachment_dir(self) -> Path:
        return Path(self.attachment_storage_dir).resolve()

    def cors_origins(self) -> list[str]:
        raw_value = self.app_frontend_origins or self.app_frontend_origin
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    def trusted_hosts(self) -> list[str]:
        return [item.strip() for item in self.allowed_hosts.split(",") if item.strip()]

    def is_production(self) -> bool:
        return self.app_env.strip().lower() == "production"

    def effective_session_https_only(self) -> bool:
        return self.session_https_only or self.is_production()

    def normalized_session_same_site(self) -> str:
        return self.session_same_site.strip().lower()

    def validate_runtime_settings(self) -> None:
        same_site = self.normalized_session_same_site()
        if same_site not in VALID_SAMESITE_VALUES:
            raise ValueError("SESSION_SAME_SITE must be one of: lax, strict, none.")

        if same_site == "none" and not self.effective_session_https_only():
            raise ValueError("SESSION_SAME_SITE=none requires SESSION_HTTPS_ONLY=true.")

        if not self.is_production():
            # In development, warn but don't block
            import logging
            logger = logging.getLogger(__name__)
            if self.app_secret_key in INSECURE_SECRET_KEYS:
                logger.warning("Using insecure APP_SECRET_KEY in non-production environment.")
            return

        # STRICT PRODUCTION CHECKS
        if self.app_debug:
            raise ValueError("CRITICAL: APP_DEBUG must be false in production.")

        if self.app_secret_key.strip() in INSECURE_SECRET_KEYS:
            raise ValueError("CRITICAL: APP_SECRET_KEY is insecure. Change it for production.")
        
        if len(self.app_secret_key.strip()) < 32:
            raise ValueError("CRITICAL: APP_SECRET_KEY must be at least 32 characters in production.")

        if self.default_admin_password.strip() == "admin123":
            raise ValueError("CRITICAL: DEFAULT_ADMIN_PASSWORD must be changed from default.")

        cors_origins = self.cors_origins()
        if not cors_origins or "*" in cors_origins:
            raise ValueError("CRITICAL: Valid APP_FRONTEND_ORIGINS (no '*') are required in production.")
        
        if any(origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1") for origin in cors_origins):
            # Allow localhost only if it is explicitly on port 8080 (Nginx proxy) to facilitate easy production testing
            if not any(":8080" in origin for origin in cors_origins):
                raise ValueError("CRITICAL: Localhost origins are not allowed in production (except via port 8080 proxy).")

        trusted_hosts = self.trusted_hosts()
        if not trusted_hosts or "*" in trusted_hosts:
            raise ValueError("CRITICAL: Specific ALLOWED_HOSTS (no '*') are required in production.")

        if self.database_url.startswith("sqlite"):
            raise ValueError("CRITICAL: SQLite is not allowed in production. Use PostgreSQL.")

        if not self.effective_session_https_only():
             raise ValueError("CRITICAL: SESSION_HTTPS_ONLY must be true in production.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
