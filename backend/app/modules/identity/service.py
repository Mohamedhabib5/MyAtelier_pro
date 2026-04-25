from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.enums import RoleKey
from app.core.language import DEFAULT_LANGUAGE, normalize_language
from app.core.exceptions import AuthenticationError, AuthorizationError, NotFoundError, ValidationAppError
from app.core.security import DEFAULT_ADMIN_SEEDED_KEY, hash_password, norm_text, role_list_contains, verify_password
from app.modules.core_platform.repository import CorePlatformRepository
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import Permission, Role, User
from app.modules.identity.permission_map import DEFAULT_PERMISSIONS, ROLE_PERMISSION_MAP
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.schemas import AdminUpdateUserRequest, CreateUserRequest, SelfUpdateUserRequest, UserGridPreferenceState


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "preferred_language": normalize_language(user.preferred_language),
        "is_active": user.is_active,
        "last_login_at": user.last_login_at,
        "role_names": sorted(role.name for role in user.roles),
    }


def ensure_identity_foundation(db: Session, *, default_admin_username: str, default_admin_password: str) -> None:
    repo = IdentityRepository(db)
    core_repo = CorePlatformRepository(db)

    permissions_by_key: dict[str, Permission] = {}
    for key, description in DEFAULT_PERMISSIONS.items():
        permission = repo.get_permission_by_key(key)
        if permission is None:
            permission = Permission(key=key, description=description)
            repo.add_permission(permission)
            db.flush()
        permissions_by_key[key] = permission

    for role_name, permission_keys in ROLE_PERMISSION_MAP.items():
        role = repo.get_role_by_name(role_name)
        if role is None:
            role = Role(name=role_name, description=f"System role: {role_name}")
            repo.add_role(role)
            db.flush()
        existing_keys = {permission.key for permission in role.permissions}
        for permission_key in permission_keys:
            if permission_key not in existing_keys:
                role.permissions.append(permissions_by_key[permission_key])

    seed_setting = core_repo.get_setting(DEFAULT_ADMIN_SEEDED_KEY)
    if seed_setting is not None:
        db.commit()
        return

    if repo.count_users() == 0:
        admin_role = repo.get_role_by_name(RoleKey.ADMIN.value)
        user = User(
            username=norm_text(default_admin_username),
            full_name="Administrator",
            password_hash=hash_password(default_admin_password),
            preferred_language=DEFAULT_LANGUAGE,
            is_active=True,
        )
        if admin_role is not None:
            user.roles.append(admin_role)
        repo.add_user(user)
        db.flush()
        record_audit(db, actor_user_id=None, action="auth.default_admin_seeded", target_type="user", target_id=user.id, summary=f"Seeded default admin user {user.username}")

    core_repo.set_setting(DEFAULT_ADMIN_SEEDED_KEY, "1")
    db.commit()


def authenticate_user(db: Session, username: str, password: str) -> User:
    repo = IdentityRepository(db)
    user = repo.get_user_by_username(norm_text(username))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise AuthenticationError("اسم المستخدم أو كلمة المرور غير صحيحة")
    user.last_login_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user


def get_user_or_404(db: Session, user_id: str) -> User:
    repo = IdentityRepository(db)
    user = repo.get_user_by_id(user_id)
    if user is None:
        raise NotFoundError("لم يتم العثور على المستخدم")
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    return IdentityRepository(db).get_user_by_username(norm_text(username))


def user_has_role(user: User, role_name: str) -> bool:
    return role_list_contains([role.name for role in user.roles], role_name)


def list_visible_users(db: Session, actor: User) -> list[dict]:
    repo = IdentityRepository(db)
    if user_has_role(actor, RoleKey.ADMIN.value):
        return [serialize_user(user) for user in repo.list_users()]
    return [serialize_user(actor)]


def create_user(db: Session, actor: User, payload: CreateUserRequest) -> dict:
    if not user_has_role(actor, RoleKey.ADMIN.value):
        raise AuthorizationError("يقتصر إنشاء المستخدمين على المدير")
    repo = IdentityRepository(db)
    username = norm_text(payload.username)
    if repo.get_user_by_username(username) is not None:
        raise ValidationAppError("اسم المستخدم مستخدم بالفعل")

    user = User(
        username=username,
        full_name=norm_text(payload.full_name),
        password_hash=hash_password(payload.password),
        preferred_language=DEFAULT_LANGUAGE,
        is_active=True,
    )
    roles = _resolve_roles(repo, payload.role_names)
    user.roles = roles
    repo.add_user(user)
    db.flush()
    record_audit(db, actor_user_id=actor.id, action="user.created", target_type="user", target_id=user.id, summary=f"Created user {user.username}", diff={"roles": [role.name for role in roles]})
    db.commit()
    db.refresh(user)
    return serialize_user(user)


def update_user_by_admin(db: Session, actor: User, target_user_id: str, payload: AdminUpdateUserRequest) -> dict:
    if not user_has_role(actor, RoleKey.ADMIN.value):
        raise AuthorizationError("يقتصر تعديل المستخدمين الآخرين على المدير")
    repo = IdentityRepository(db)
    user = get_user_or_404(db, target_user_id)

    if payload.username is not None:
        username = norm_text(payload.username)
        existing = repo.get_user_by_username(username)
        if existing is not None and existing.id != user.id:
            raise ValidationAppError("اسم المستخدم مستخدم بالفعل")
        user.username = username
    if payload.full_name is not None:
        user.full_name = norm_text(payload.full_name)
    if payload.password:
        user.password_hash = hash_password(payload.password)
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role_names is not None:
        user.roles = _resolve_roles(repo, payload.role_names)

    record_audit(db, actor_user_id=actor.id, action="user.updated_by_admin", target_type="user", target_id=user.id, summary=f"Updated user {user.username}", diff={"roles": [role.name for role in user.roles]})
    db.commit()
    db.refresh(user)
    return serialize_user(user)


def update_own_profile(db: Session, actor: User, payload: SelfUpdateUserRequest) -> dict:
    if payload.full_name is not None:
        actor.full_name = norm_text(payload.full_name)
    if payload.password:
        actor.password_hash = hash_password(payload.password)
    if payload.preferred_language is not None:
        actor.preferred_language = normalize_language(payload.preferred_language)
    record_audit(db, actor_user_id=actor.id, action="user.updated_self", target_type="user", target_id=actor.id, summary=f"Updated own profile for {actor.username}")
    db.commit()
    db.refresh(actor)
    return serialize_user(actor)


def get_user_profile(actor: User) -> dict:
    return serialize_user(actor)


def _resolve_roles(repo: IdentityRepository, role_names: list[str] | None) -> list[Role]:
    names = role_names or [RoleKey.USER.value]
    resolved: list[Role] = []
    seen: set[str] = set()
    for role_name in names:
        normalized = norm_text(role_name).lower()
        if normalized in seen:
            continue
        role = repo.get_role_by_name(normalized)
        if role is None:
            raise ValidationAppError(f"الدور غير معروف: {role_name}")
        resolved.append(role)
        seen.add(normalized)
    return resolved


def get_user_grid_preference(db: Session, actor: User, table_key: str) -> dict:
    normalized_key = _normalize_table_key(table_key)
    row = IdentityRepository(db).get_user_grid_preference(actor.id, normalized_key)
    if row is None:
        state = UserGridPreferenceState().model_dump()
        updated_at = None
    else:
        state = _parse_grid_state(row.state_json)
        updated_at = row.updated_at
    return {"table_key": normalized_key, "state": state, "updated_at": updated_at}


def set_user_grid_preference(db: Session, actor: User, table_key: str, state: UserGridPreferenceState) -> dict:
    normalized_key = _normalize_table_key(table_key)
    payload = state.model_dump()
    row = IdentityRepository(db).upsert_user_grid_preference(
        user_id=actor.id,
        table_key=normalized_key,
        state_json=json.dumps(payload, ensure_ascii=False),
    )
    record_audit(
        db,
        actor_user_id=actor.id,
        action="user.grid_preferences_updated",
        target_type="user",
        target_id=actor.id,
        summary=f"Updated grid preferences for {actor.username}",
        diff={"table_key": normalized_key, "page_size": payload.get("pageSize")},
    )
    db.commit()
    db.refresh(row)
    return {"table_key": normalized_key, "state": payload, "updated_at": row.updated_at}


def _normalize_table_key(value: str) -> str:
    normalized = norm_text(value)
    if not normalized:
        raise ValidationAppError("اسم الجدول مطلوب")
    if len(normalized) > 120:
        raise ValidationAppError("اسم الجدول طويل جدًا")
    return normalized


def _parse_grid_state(raw_value: str) -> dict:
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        return UserGridPreferenceState().model_dump()
    if not isinstance(parsed, dict):
        return UserGridPreferenceState().model_dump()
    return UserGridPreferenceState.model_validate(parsed).model_dump()
