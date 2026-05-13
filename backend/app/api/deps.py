from __future__ import annotations
from datetime import UTC, datetime

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
    # We skip this check for auth routes to allow the user to verify their 2FA code
    is_2fa_pending = request.session.get("2fa_pending", False)
    
    # Safety: If 2FA is not enabled for the user, it shouldn't be pending
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
    Usage: Depends(PermissionRequired("atelier.view_reservations"))
    """
    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        ensure_permission(current_user, permission_key)
        return current_user
    return _dependency


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not user_has_role(current_user, RoleKey.ADMIN.value):
        raise AuthorizationError(ADMIN_ACCESS_REQUIRED)
    return current_user


def require_users_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("users.manage")(current_user)

def require_self_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("users.self_manage")(current_user)

def require_settings_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("settings.manage")(current_user)

def require_finance_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("finance.view")(current_user)

def require_reports_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("reports.view")(current_user)

def require_exports_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("exports.view")(current_user)

def require_exports_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("exports.manage")(current_user)

def require_accounting_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("accounting.view")(current_user)

def require_accounting_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("accounting.manage")(current_user)

def require_customers_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("customers.view")(current_user)

def require_customers_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("customers.manage")(current_user)

def require_catalog_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("catalog.view")(current_user)

def require_catalog_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("catalog.manage")(current_user)

def require_dresses_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("dresses.view")(current_user)

def require_dresses_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("dresses.manage")(current_user)

def require_bookings_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("bookings.view")(current_user)

def require_bookings_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("bookings.manage")(current_user)

def require_payments_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("payments.view")(current_user)

def require_payments_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("payments.manage")(current_user)

def require_audit_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("audit.view")(current_user)

def require_destructive_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("destructive.manage")(current_user)

def require_period_lock_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("period_lock.manage")(current_user)

def require_custody_view(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("custody.view")(current_user)

def require_custody_manage(current_user: User = Depends(get_current_user)) -> User:
    return PermissionRequired("custody.manage")(current_user)


def limit_api_usage(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not api_rate_limiter.is_allowed(f"api:{client_ip}"):
        raise RateLimitError()


def limit_sensitive_ops(request: Request) -> None:
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
from app.modules.organization.branch_context import ensure_active_branch
from app.modules.organization.models import Branch

def get_active_branch(request: Request, db: Session = Depends(get_db)) -> Branch:
    return ensure_active_branch(db, request.session)


def get_active_branch_id(request: Request, db: Session = Depends(get_db)) -> str:
    branch = ensure_active_branch(db, request.session)
    return branch.id
