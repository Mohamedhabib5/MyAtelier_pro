from __future__ import annotations

import sqlite3
from pathlib import Path
from zipfile import ZipFile

import pytest

from .conftest import build_test_client
from .test_foundation import login


def test_backup_archive_contains_restorable_database_dump(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / 'app.db'
    storage_root = tmp_path / 'storage'

    with build_test_client(db_path, storage_root, monkeypatch) as client:
        login(client)
        create_customer = client.post(
            '/api/customers',
            json={'full_name': 'Backup Restore User', 'phone': '01000000099'},
        )
        assert create_customer.status_code == 201, create_customer.text

        backup_response = client.post('/api/settings/backups')
        assert backup_response.status_code == 200, backup_response.text
        backup = backup_response.json()
        backup_path = storage_root / 'backups' / backup['filename']
        assert backup_path.is_file()

        with ZipFile(backup_path) as archive:
            names = set(archive.namelist())
            assert 'manifest.json' in names
            assert 'database/dump.sql' in names
            dump_sql = archive.read('database/dump.sql').decode('utf-8')
            manifest = archive.read('manifest.json').decode('utf-8')

        assert '"dialect": "sqlite"' in manifest
        assert 'Backup Restore User' in dump_sql

    restored_db_path = tmp_path / 'restored.db'
    with sqlite3.connect(restored_db_path) as restored:
        restored.executescript(dump_sql)
        restored.commit()
        restored_customer = restored.execute(
            'SELECT full_name, phone FROM customers WHERE phone = ?',
            ('01000000099',),
        ).fetchone()
        table_names = {
            row[0]
            for row in restored.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }

    assert restored_customer == ('Backup Restore User', '01000000099')
    assert 'users' in table_names
    assert 'backup_records' in table_names
