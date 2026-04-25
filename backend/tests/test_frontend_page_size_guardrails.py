from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.guardrail


def test_operational_frontend_pages_stay_within_size_target() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    limits = {
        "frontend/src/pages/BookingsPage.tsx": 250,
        "frontend/src/pages/PaymentsPage.tsx": 250,
        "frontend/src/pages/ExportsPage.tsx": 250,
        "frontend/src/pages/CustodyPage.tsx": 250,
        "frontend/src/pages/SettingsPage.tsx": 250,
        "frontend/src/pages/UsersPage.tsx": 250,
    }
    for relative_path, max_lines in limits.items():
        path = repo_root / relative_path
        line_count = len(path.read_text(encoding="utf-8-sig").splitlines())
        assert line_count <= max_lines, f"{relative_path} is {line_count} lines (limit: {max_lines})"
