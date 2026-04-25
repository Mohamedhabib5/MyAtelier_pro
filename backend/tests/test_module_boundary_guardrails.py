from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.guardrail


def test_service_files_stay_within_size_target() -> None:
    limits = {
        "backend/app/modules/bookings/service.py": 250,
        "backend/app/modules/payments/service.py": 250,
        "backend/app/modules/exports/service.py": 250,
    }
    repo_root = Path(__file__).resolve().parents[1]
    for relative_path, max_lines in limits.items():
        path = repo_root.parent / relative_path
        line_count = len(path.read_text(encoding="utf-8-sig").splitlines())
        assert line_count <= max_lines, f"{relative_path} is {line_count} lines (limit: {max_lines})"


def test_routes_do_not_import_helper_modules_directly() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    helper_module_imports = {
        "app.modules.bookings.document_access",
        "app.modules.bookings.query_service",
        "app.modules.payments.custody_compensation",
        "app.modules.exports.rendering",
        "app.modules.exports.master_data_exports",
        "app.modules.exports.row_collectors",
    }
    route_files = [
        repo_root / "app" / "api" / "routes" / "bookings.py",
        repo_root / "app" / "api" / "routes" / "payments.py",
        repo_root / "app" / "api" / "routes" / "exports.py",
    ]
    for route_path in route_files:
        imported_modules = _collect_imported_modules(route_path)
        direct_helpers = imported_modules.intersection(helper_module_imports)
        assert not direct_helpers, (
            f"{route_path.name} imports helper modules directly: {sorted(direct_helpers)}. "
            "Routes should import stable service entrypoints only."
        )


def _collect_imported_modules(path: Path) -> set[str]:
    module = ast.parse(path.read_text(encoding="utf-8-sig"))
    imports: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports
