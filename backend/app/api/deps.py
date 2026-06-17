from __future__ import annotations
from datetime import UTC, datetime
import json

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.enums import RoleKey
from app.core.exceptions import AuthenticationError, AuthorizationError, NotFoundError, RateLimitError
from app.core.messages import ACTIVE_ACCOUNT_REQUIRED, ADMIN_ACCESS_REQUIRED
from app.core.rate_limiter import api_rate_limiter, sensitive_ops_rate_limiter
from app.db.session import get_db
from app.modules.identity.access import ensure_permission
from app.modules.identity.models import User
from app.modules.identity.service import get_user_or_404, user_has_role
from app.core.redis_client import redis_client
from app.modules.organization.branch_context import ensure_active_branch
from app.modules.organization.models import Branch


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise AuthenticationError()
    try:
        current_user = get_user_or_404(db, user_id)
    except NotFoundError as exc:
        request.session.clear()
        raise AuthenticationError() from exc

    # 1. Check if account is frozen
    if current_user.is_frozen_until and current_user.is_frozen_until > datetime.now(UTC):
        request.session.clear()
        raise AuthenticationError("هذا الحساب مجمد مؤقتاً")

    # 2. Check if account is active
    if not current_user.is_active:
        request.session.clear()
        raise AuthenticationError(ACTIVE_ACCOUNT_REQUIRED)

    # 3. Check for 2FA pending state (Stateful Security)
    is_2fa_pending = request.session.get("2fa_pending", False)
    
    if not current_user.is_2fa_enabled and is_2fa_pending:
        is_2fa_pending = False
        request.session["2fa_pending"] = False

    is_auth_route = request.url.path.startswith("/api/auth")
    
    if is_2fa_pending and not is_auth_route:
        raise AuthorizationError("يرجى إكمال التحقق بخطوتين للوصول إلى هذا المورد")

    return current_user


def PermissionRequired(permission_key: str):
    """
    Unified Permission Factory to replace individual requirement functions.
    Usage: Depends(PermissionRequired("payments.view"))
    """
    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        from app.core.config import get_settings
        if get_settings().security_bypass_for_tests:
            from app.modules.identity.access import permission_keys_for_user
            perms = permission_keys_for_user(current_user)
        else:
            cache_key = f"user_perms:{current_user.id}"
            try:
                cached_perms = redis_client.get(cache_key)
                if cached_perms:
                    perms = set(json.loads(cached_perms))
                else:
                    from app.modules.identity.access import permission_keys_for_user
                    perms_set = permission_keys_for_user(current_user)
                    perms = list(perms_set)
                    redis_client.setex(cache_key, 300, json.dumps(perms))
                    perms = perms_set
            except Exception:
                from app.modules.identity.access import permission_keys_for_user
                perms = permission_keys_for_user(current_user)

        from app.core.messages import missing_permission_message
        if permission_key not in perms:
            raise AuthorizationError(missing_permission_message(permission_key))
            
        return current_user
    return _dependency


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not user_has_role(current_user, RoleKey.ADMIN.value):
        raise AuthorizationError(ADMIN_ACCESS_REQUIRED)
    return current_user


# Unified Direct Factory Assignments to support OpenAPI dependency introspection
require_users_manage = PermissionRequired("users.manage")
require_self_manage = PermissionRequired("users.self_manage")
require_settings_manage = PermissionRequired("settings.manage")
require_finance_view = PermissionRequired("finance.view")
require_reconcile_cash = PermissionRequired("finance.reconcile_cash")
require_reports_view = PermissionRequired("reports.view")
require_exports_view = PermissionRequired("exports.view")
require_exports_manage = PermissionRequired("exports.manage")
require_accounting_view = PermissionRequired("accounting.view")
require_accounting_manage = PermissionRequired("accounting.manage")
require_customers_view = PermissionRequired("customers.view")
require_customers_manage = PermissionRequired("customers.manage")
require_catalog_view = PermissionRequired("catalog.view")
require_catalog_manage = PermissionRequired("catalog.manage")
require_dresses_view = PermissionRequired("dresses.view")
require_dresses_manage = PermissionRequired("dresses.manage")
require_bookings_view = PermissionRequired("bookings.view")
require_bookings_manage = PermissionRequired("bookings.manage")
require_payments_view = PermissionRequired("payments.view")
require_payments_manage = PermissionRequired("payments.manage")
require_audit_view = PermissionRequired("audit.view")
require_destructive_manage = PermissionRequired("destructive.manage")
require_period_lock_manage = PermissionRequired("period_lock.manage")
require_custody_view = PermissionRequired("custody.view")
require_custody_manage = PermissionRequired("custody.manage")


def limit_api_usage(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not api_rate_limiter.is_allowed(f"api:{client_ip}"):
        raise RateLimitError()


def limit_sensitive_ops(request: Request) -> None:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    client_ip = request.client.host if request.client else "unknown"
    if not sensitive_ops_rate_limiter.is_allowed(f"sensitive:{client_ip}"):
        raise RateLimitError()


def require_identity_view(current_user: User = Depends(get_current_user)) -> User:
    """
    Requirement for basic identity/profile view access.
    Maps to users.self_manage as the baseline permission for all active users.
    """
    ensure_permission(current_user, "users.self_manage")
    return current_user


def get_active_branch(request: Request, db: Session = Depends(get_db)) -> Branch:
    return ensure_active_branch(db, request.session)


def get_active_branch_id(request: Request, db: Session = Depends(get_db)) -> str:
    branch = ensure_active_branch(db, request.session)
    return branch.id
