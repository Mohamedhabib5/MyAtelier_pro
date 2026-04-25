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
            return

        if self.app_debug:
            raise ValueError("APP_DEBUG must be false in production.")

        if self.app_secret_key.strip() in INSECURE_SECRET_KEYS or len(self.app_secret_key.strip()) < 32:
            raise ValueError("APP_SECRET_KEY is not safe for production. Use a long random value (32+ chars).")

        if self.default_admin_password.strip() == "admin123":
            raise ValueError("DEFAULT_ADMIN_PASSWORD must be changed before production.")

        cors_origins = self.cors_origins()
        if not cors_origins:
            raise ValueError("APP_FRONTEND_ORIGINS must not be empty in production.")
        if "*" in cors_origins:
            raise ValueError("APP_FRONTEND_ORIGINS must not contain '*' in production.")
        if any(origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1") for origin in cors_origins):
            raise ValueError("APP_FRONTEND_ORIGINS must not use localhost origins in production.")

        trusted_hosts = self.trusted_hosts()
        if not trusted_hosts:
            raise ValueError("ALLOWED_HOSTS must not be empty in production.")
        if "*" in trusted_hosts:
            raise ValueError("ALLOWED_HOSTS must not contain '*' in production.")
        if self.ops_alert_webhook_url.strip() and not self.ops_alert_webhook_url.strip().startswith("https://"):
            raise ValueError("OPS_ALERT_WEBHOOK_URL must use https in production.")
        if self.nightly_failure_ingest_token.strip() and len(self.nightly_failure_ingest_token.strip()) < 16:
            raise ValueError("NIGHTLY_FAILURE_INGEST_TOKEN must be at least 16 characters in production.")
        if self.export_delivery_webhook_url.strip() and not self.export_delivery_webhook_url.strip().startswith("https://"):
            raise ValueError("EXPORT_DELIVERY_WEBHOOK_URL must use https in production.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
