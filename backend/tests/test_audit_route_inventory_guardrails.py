from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.main import create_app
from app.modules.core_platform.write_route_audit_policy import WRITE_ROUTE_AUDIT_POLICY, discover_write_routes

pytestmark = pytest.mark.guardrail


def test_write_route_inventory_matches_registered_routes() -> None:
    app = create_app()
    discovered = discover_write_routes(app)
    declared = set(WRITE_ROUTE_AUDIT_POLICY.keys())
    assert discovered == declared


def test_write_route_inventory_requires_explicit_audit_expectations() -> None:
    for route, actions in WRITE_ROUTE_AUDIT_POLICY.items():
        assert actions, f"Write route {route} must declare at least one expected audit action."
        for action in actions:
            assert action.strip(), f"Write route {route} includes an empty audit action token."


def test_expected_audit_actions_exist_in_backend_code() -> None:
    literal_actions = _collect_record_audit_actions()
    for route, actions in WRITE_ROUTE_AUDIT_POLICY.items():
        for action in actions:
            if action.endswith("*"):
                prefix = action[:-1]
                assert any(item.startswith(prefix) for item in literal_actions), (
                    f"Route {route} expects wildcard action prefix '{action}', "
                    "but no matching record_audit action literal was found."
                )
                continue
            assert action in literal_actions, (
                f"Route {route} expects audit action '{action}', "
                "but no matching record_audit action literal was found."
            )


def _collect_record_audit_actions() -> set[str]:
    actions: set[str] = set()
    root = Path(__file__).resolve().parents[1] / "app"
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        module = ast.parse(path.read_text(encoding="utf-8-sig"))
        constants = _collect_module_string_constants(module)
        for node in ast.walk(module):
            if not isinstance(node, ast.Call):
                continue
            if not _is_record_audit_call(node.func):
                continue
            for keyword in node.keywords:
                if keyword.arg != "action":
                    continue
                if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                    actions.add(keyword.value.value)
                if isinstance(keyword.value, ast.Name):
                    value = constants.get(keyword.value.id)
                    if value:
                        actions.add(value)
    return actions


def _collect_module_string_constants(module: ast.Module) -> dict[str, str]:
    constants: dict[str, str] = {}
    for node in module.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
            continue
        constants[target.id] = node.value.value
    return constants


def _is_record_audit_call(func: ast.AST) -> bool:
    if isinstance(func, ast.Name):
        return func.id == "record_audit"
    if isinstance(func, ast.Attribute):
        return func.attr == "record_audit"
    return False
