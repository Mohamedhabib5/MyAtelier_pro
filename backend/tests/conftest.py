from __future__ import annotations

import importlib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@contextmanager
def build_test_client(
    db_path: Path,
    storage_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_overrides: dict[str, str] | None = None,
) -> Iterator[TestClient]:
    import os
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    monkeypatch.setenv("STORAGE_ROOT", storage_root.as_posix())
    monkeypatch.setenv("BACKUP_STORAGE_DIR", (storage_root / "backups").as_posix())
    monkeypatch.setenv("ATTACHMENT_STORAGE_DIR", (storage_root / "attachments").as_posix())
    if env_overrides:
        for key, value in env_overrides.items():
            monkeypatch.setenv(key, value)

    import app.core.config as config_module

    config_module.get_settings.cache_clear()

    import app.main as main_module
    main_module = importlib.reload(main_module)

    from app.db.base import Base

    app = main_module.create_app(config_module.get_settings())
    Base.metadata.create_all(app.state.engine)

    with TestClient(app) as client:
        yield client


@pytest.fixture()
def app_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    db_path = tmp_path / "app.db"
    storage_root = tmp_path / "storage"

    with build_test_client(db_path, storage_root, monkeypatch) as client:
        yield client