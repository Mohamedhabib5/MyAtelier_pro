"""Regression tests for PR 3 (P3.5): complete H6 refactor for require_accounting_bridge_manage."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from fastapi import Depends
from fastapi.testclient import TestClient

from app.core.exceptions import AuthorizationError
from app.modules.identity.models import User
from app.api.routes.accounting import require_accounting_bridge_manage


@pytest.mark.guardrail
def test_bridge_manage_permission_grants_access():
    """1. User having 'accounting.bridge_manage' must be granted access."""
    user = MagicMock(spec=User)
    with patch("app.api.routes.accounting.permission_keys_for_user", return_value={"accounting.bridge_manage"}) as mock_perms:
        result = require_accounting_bridge_manage(current_user=user)
        assert result == user
        mock_perms.assert_called_once_with(user)


def test_accounting_manage_permission_grants_access():
    """2. User having 'accounting.manage' (fallback) must be granted access."""
    user = MagicMock(spec=User)
    with patch("app.api.routes.accounting.permission_keys_for_user", return_value={"accounting.manage"}) as mock_perms:
        result = require_accounting_bridge_manage(current_user=user)
        assert result == user
        mock_perms.assert_called_once_with(user)


def test_no_permission_raises_authorization_error():
    """3. User with neither permission must raise AuthorizationError."""
    user = MagicMock(spec=User)
    with patch("app.api.routes.accounting.permission_keys_for_user", return_value={"other.permission"}) as mock_perms:
        with pytest.raises(AuthorizationError) as exc_info:
            require_accounting_bridge_manage(current_user=user)
        assert "accounting.bridge_manage" in str(exc_info.value)
        mock_perms.assert_called_once_with(user)


def test_endpoints_use_require_accounting_bridge_manage():
    """4. Endpoints must use require_accounting_bridge_manage as a dependency."""
    from app.api.routes.accounting import router
    import inspect
    from fastapi.routing import APIRoute

    checked_routes = {
        "/accounting/bridge-configs/{bridge_key}": "PATCH",
        "/accounting/bridge-configs/{bridge_key}/reset": "POST",
        "/accounting/chart-of-accounts/import": "POST",
    }

    found_count = 0
    for route in router.routes:
        if isinstance(route, APIRoute) and route.path in checked_routes and checked_routes[route.path] in route.methods:
            # Check route endpoint signature for Depends(require_accounting_bridge_manage)
            sig = inspect.signature(route.endpoint)
            has_dep = False
            for param in sig.parameters.values():
                if param.default and hasattr(param.default, "dependency"):
                    if param.default.dependency == require_accounting_bridge_manage:
                        has_dep = True
                        break
            assert has_dep, f"Route {route.methods} {route.path} does not use require_accounting_bridge_manage dependency"
            found_count += 1

    assert found_count == len(checked_routes), f"Expected {len(checked_routes)} matching routes, found {found_count}"


def test_api_endpoint_grants_access_with_permission(app_client: TestClient):
    """5. Verify endpoint grants access when require_accounting_bridge_manage dependency is satisfied."""
    from .test_foundation import login
    login(app_client)
    
    session_factory = app_client.app.state.session_factory
    with session_factory() as db:
        from app.modules.identity.models import User
        # Retrieve a real user from database to avoid MagicMock database insertion errors
        user = db.query(User).filter_by(username="admin").first()
        assert user is not None
    
    app_client.app.dependency_overrides[require_accounting_bridge_manage] = lambda: user
    
    try:
        response = app_client.post("/api/accounting/bridge-configs/cash/reset")
        # Since require_accounting_bridge_manage is overridden with a valid user, it should succeed or return 200
        assert response.status_code == 200
    finally:
        app_client.app.dependency_overrides.clear()
