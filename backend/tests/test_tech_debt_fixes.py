"""Regression tests for PR 2.5: pre-existing tech debt fixes."""
from __future__ import annotations

import subprocess
import pytest


@pytest.mark.guardrail
def test_git_is_available_in_container():
    """PR 2.5 regression: git must be installed in the Docker container.
    
    The test_no_secrets_in_repo.py guardrail test depends on `git ls-files`
    being available. Without git, the test silently fails.
    """
    result = subprocess.run(
        ["git", "--version"],
        capture_output=True, text=True, check=True
    )
    assert "git version" in result.stdout, f"git not available: {result.stderr}"


def test_main_module_does_not_create_app_at_import_time():
    """PR 2.5 regression: app.main should NOT execute create_app() on import.
    
    The module-level `app = create_app()` was removed because it triggered
    engine creation + middleware setup BEFORE conftest.py could set test env vars.
    This caused test_audit_route_inventory_guardrails.py collection errors.
    """
    import app.main as main_module
    
    # Verify create_app is still importable
    assert callable(main_module.create_app), "create_app must be importable"
    
    # Verify NO module-level `app` attribute exists (it was removed)
    assert not hasattr(main_module, 'app'), \
        "main module must NOT have a module-level `app` attribute. " \
        "Use `uvicorn app.main:create_app --factory` instead."


def test_audit_route_inventory_test_can_be_collected():
    """PR 2.5 regression: test_audit_route_inventory_guardrails.py must be collectable.
    
    Before this fix, importing `from app.main import create_app` triggered
    `app = create_app()` at module load time, which failed during pytest
    collection (before conftest env setup).
    """
    # This test simply verifies that the import works without side effects.
    # If the import triggers create_app(), it would fail here.
    from app.main import create_app
    assert callable(create_app)
