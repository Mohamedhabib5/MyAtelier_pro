from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

from sqlalchemy.engine import make_url


def create_database_dump(database_url: str, output_path: Path) -> dict[str, str]:
    url = make_url(database_url)
    backend_name = url.get_backend_name()
    if backend_name == 'sqlite':
        return _create_sqlite_dump(url.database, output_path)
    if backend_name == 'postgresql':
        return _create_postgresql_dump(url, output_path)
    raise RuntimeError(f'Unsupported database backend for backup: {backend_name}')


def _create_sqlite_dump(database_path: str | None, output_path: Path) -> dict[str, str]:
    if not database_path or database_path == ':memory:':
        raise RuntimeError('SQLite backup requires a file-based database')
    with sqlite3.connect(database_path) as connection:
        dump_sql = '\n'.join(connection.iterdump()) + '\n'
    output_path.write_text(dump_sql, encoding='utf-8')
    return {'dialect': 'sqlite', 'format': 'sql', 'path_in_archive': 'database/dump.sql'}


def _create_postgresql_dump(url, output_path: Path) -> dict[str, str]:
    command = [
        'pg_dump',
        '--host',
        url.host or 'localhost',
        '--port',
        str(url.port or 5432),
        '--username',
        url.username or 'postgres',
        '--dbname',
        url.database or 'postgres',
        '--no-owner',
        '--no-privileges',
        '--file',
        str(output_path),
    ]
    env = {
        'PGPASSWORD': url.password or '',
    }
    subprocess.run(command, check=True, capture_output=True, text=True, env=env)
    _normalize_postgresql_dump(output_path)
    return {'dialect': 'postgresql', 'format': 'sql', 'path_in_archive': 'database/dump.sql'}


def _normalize_postgresql_dump(output_path: Path) -> None:
    content = output_path.read_text(encoding='utf-8')
    normalized_lines = [
        line
        for line in content.splitlines()
        if line.strip() != 'SET transaction_timeout = 0;'
    ]
    output_path.write_text('\n'.join(normalized_lines) + '\n', encoding='utf-8')
