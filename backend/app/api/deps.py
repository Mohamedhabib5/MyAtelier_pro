from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.enums import RoleKey
from app.core.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from app.core.messages import ACTIVE_ACCOUNT_REQUIRED, ADMIN_ACCESS_REQUIRED
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
    if not current_user.is_active:
        request.session.clear()
        raise AuthenticationError(ACTIVE_ACCOUNT_REQUIRED)
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not user_has_role(current_user, RoleKey.ADMIN.value):
        raise AuthorizationError(ADMIN_ACCESS_REQUIRED)
    return current_user


def require_users_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "users.manage")
    return current_user


def require_self_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "users.self_manage")
    return current_user


def require_settings_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "settings.manage")
    return current_user


def require_finance_view(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "finance.view")
    return current_user


def require_reports_view(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "reports.view")
    return current_user


def require_exports_view(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "exports.view")
    return current_user


def require_exports_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "exports.manage")
    return current_user


def require_accounting_view(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "accounting.view")
    return current_user


def require_accounting_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "accounting.manage")
    return current_user


def require_customers_view(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "customers.view")
    return current_user


def require_customers_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "customers.manage")
    return current_user


def require_catalog_view(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "catalog.view")
    return current_user


def require_catalog_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "catalog.manage")
    return current_user


def require_dresses_view(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "dresses.view")
    return current_user


def require_dresses_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "dresses.manage")
    return current_user


def require_bookings_view(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "bookings.view")
    return current_user


def require_bookings_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "bookings.manage")
    return current_user


def require_payments_view(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "payments.view")
    return current_user


def require_payments_manage(current_user: User = Depends(get_current_user)) -> User:
    ensure_permission(current_user, "payments.manage")
    return current_user
