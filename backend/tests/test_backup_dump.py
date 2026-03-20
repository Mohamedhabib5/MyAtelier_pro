from __future__ import annotations

from pathlib import Path

from app.modules.core_platform.backup_dump import _normalize_postgresql_dump


def test_postgresql_dump_normalization_removes_transaction_timeout(tmp_path: Path) -> None:
    dump_path = tmp_path / 'dump.sql'
    dump_path.write_text(
        'SET statement_timeout = 0;\n'
        'SET transaction_timeout = 0;\n'
        'CREATE TABLE demo(id integer);\n',
        encoding='utf-8',
    )

    _normalize_postgresql_dump(dump_path)

    normalized = dump_path.read_text(encoding='utf-8')
    assert 'SET transaction_timeout = 0;' not in normalized
    assert 'SET statement_timeout = 0;' in normalized
    assert 'CREATE TABLE demo(id integer);' in normalized
