from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()