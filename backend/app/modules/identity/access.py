from __future__ import annotations

from app.core.messages import missing_permission_message
from app.core.exceptions import AuthorizationError
from app.modules.identity.models import User


def permission_keys_for_user(user: User) -> set[str]:
    return {
        permission.key
        for role in user.roles
        for permission in role.permissions
    }


def user_has_permission(user: User, permission_key: str) -> bool:
    return permission_key in permission_keys_for_user(user)


def ensure_permission(user: User, permission_key: str, message: str | None = None) -> None:
    if not user_has_permission(user, permission_key):
        raise AuthorizationError(message or missing_permission_message(permission_key))
