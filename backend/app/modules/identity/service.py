from __future__ import annotations

import json
import pyotp
import secrets
import string
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.enums import RoleKey
from app.core.language import DEFAULT_LANGUAGE, normalize_language
from app.core.exceptions import AuthenticationError, AuthorizationError, NotFoundError, ValidationAppError
from app.core.security import DEFAULT_ADMIN_SEEDED_KEY, hash_password, norm_text, role_list_contains, verify_password
from app.modules.core_platform.repository import CorePlatformRepository
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import Permission, Role, User, UserRole, UserBackupCode
from app.modules.identity.permission_map import DEFAULT_PERMISSIONS, ROLE_PERMISSION_MAP
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.schemas import (
    AdminUpdateUserRequest, 
    CreateUserRequest, 
    SelfUpdateUserRequest, 
    UserGridPreferenceState,
    CreateRoleRequest,
    UpdateRoleRequest
)
from app.modules.core_platform.security_service import encrypt_secret, decrypt_secret, SecurityNotificationService


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "preferred_language": normalize_language(user.preferred_language),
        "is_active": user.is_active,
        "is_frozen": user.is_frozen_until > datetime.now(UTC) if user.is_frozen_until else False,
        "is_2fa_enabled": user.is_2fa_enabled,
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
            role = Role(name=role_name, description=f"دور النظام: {role_name}", is_preset=True)
            repo.add_role(role)
            db.flush()
        else:
            # Ensure preset roles are marked as such
            role.is_preset = True
        
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
            user.user_roles.append(UserRole(role=admin_role, branch_id=None))
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
    
    # Check if frozen
    if user.is_frozen_until and user.is_frozen_until > datetime.now(UTC):
        raise AuthenticationError("هذا الحساب مجمد مؤقتاً")

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
    for role in roles:
        user.user_roles.append(UserRole(role=role, branch_id=None))
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
        roles = _resolve_roles(repo, payload.role_names)
        user.user_roles.clear()
        for role in roles:
            user.user_roles.append(UserRole(role=role, branch_id=None))

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


def get_user_theme_preference(db: Session, actor: User) -> dict:
    row = IdentityRepository(db).get_user_theme_preference(actor.id)
    if row is None:
        return {"theme_json": "{}", "updated_at": None}
    return {"theme_json": row.theme_json, "updated_at": row.updated_at}


def set_user_theme_preference(db: Session, actor: User, theme_json: str) -> dict:
    row = IdentityRepository(db).upsert_user_theme_preference(
        user_id=actor.id,
        theme_json=theme_json,
    )
    record_audit(
        db,
        actor_user_id=actor.id,
        action="user.theme_preferences_updated",
        target_type="user",
        target_id=actor.id,
        summary=f"Updated theme preferences for {actor.username}",
    )
    db.commit()
    db.refresh(row)
    return {"theme_json": theme_json, "updated_at": row.updated_at}

# --- 2FA Operations ---

def setup_2fa(db: Session, user: User) -> dict:
    """Generates a new TOTP secret for the user but does not enable it yet."""
    secret = pyotp.random_base32()
    user.totp_secret = encrypt_secret(secret)
    db.commit()
    
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="MyAtelier Pro")
    
    return {
        "provisioning_uri": provisioning_uri,
        "secret_plain": secret # Return plain for manual entry if needed
    }

def activate_2fa(db: Session, user: User, code: str) -> list[str]:
    """Verifies the first code and permanently enables 2FA for the user."""
    if not user.totp_secret:
        raise ValidationAppError("لم يتم إعداد التحقق الثنائي لهذا المستخدم")
    
    secret = decrypt_secret(user.totp_secret)
    totp = pyotp.TOTP(secret)
    
    if not totp.verify(code):
        SecurityNotificationService.notify_security_event("2fa_setup_failed", {"user_id": user.id, "username": user.username})
        raise ValidationAppError("رمز التحقق غير صحيح")
    
    user.is_2fa_enabled = True
    
    # Generate Backup Codes
    backup_codes = []
    repo = IdentityRepository(db)
    for _ in range(10):
        raw_code = "".join(secrets.choice(string.digits) for _ in range(8))
        backup_codes.append(raw_code)
        # We hash backup codes for security
        code_hash = hash_password(raw_code)
        repo.add_backup_code(UserBackupCode(user_id=user.id, code_hash=code_hash))
    
    record_audit(db, actor_user_id=user.id, action="auth.2fa_enabled", target_type="user", target_id=user.id, summary="Enabled 2FA")
    db.commit()
    return backup_codes

def verify_2fa_login(db: Session, user: User, code: str) -> bool:
    """Verifies a TOTP code during the login flow."""
    if not user.is_2fa_enabled or not user.totp_secret:
        return True # Fallback if accidentally called
    
    secret = decrypt_secret(user.totp_secret)
    totp = pyotp.TOTP(secret)
    
    if totp.verify(code):
        return True
    
    # Notify on failure
    SecurityNotificationService.notify_security_event("2fa_login_failed", {"user_id": user.id, "username": user.username})
    return False

def verify_backup_code_login(db: Session, user: User, code: str) -> bool:
    """Verifies a backup code and marks it as used."""
    repo = IdentityRepository(db)
    valid_codes = repo.list_user_backup_codes(user.id)
    
    for bc in valid_codes:
        if verify_password(code, bc.code_hash):
            bc.is_used = True
            record_audit(db, actor_user_id=user.id, action="auth.2fa_backup_code_used", target_type="user", target_id=user.id, summary="Used backup code to login")
            db.commit()
            return True
    
    return False

# --- Role CRUD Operations ---

def list_roles(db: Session) -> list[Role]:
    return IdentityRepository(db).list_roles()

def list_all_permissions(db: Session) -> list[Permission]:
    return IdentityRepository(db).list_permissions()

def get_role_or_404(db: Session, role_id: str) -> Role:
    role = IdentityRepository(db).get_role_by_id(role_id)
    if role is None:
        raise NotFoundError("لم يتم العثور على الدور")
    return role

def create_role(db: Session, actor: User, payload: CreateRoleRequest) -> Role:
    repo = IdentityRepository(db)
    if repo.get_role_by_name(norm_text(payload.name).lower()):
        raise ValidationAppError("اسم الدور موجود بالفعل")
    
    role = Role(
        name=norm_text(payload.name).lower(),
        description=norm_text(payload.description) if payload.description else None,
        is_preset=False
    )
    if payload.permission_keys:
        for key in payload.permission_keys:
            perm = repo.get_permission_by_key(key)
            if perm:
                role.permissions.append(perm)
                
    repo.add_role(role)
    db.flush()
    record_audit(db, actor_user_id=actor.id, action="role.created", target_type="role", target_id=role.id, summary=f"Created role {role.name}")
    db.commit()
    return role

def update_role(db: Session, actor: User, role_id: str, payload: UpdateRoleRequest) -> Role:
    repo = IdentityRepository(db)
    role = get_role_or_404(db, role_id)
    
    if role.is_preset and payload.name is not None:
        raise ValidationAppError("لا يمكن تعديل اسم الأدوار النظامية")

    if payload.name is not None:
        name = norm_text(payload.name).lower()
        existing = repo.get_role_by_name(name)
        if existing and existing.id != role.id:
            raise ValidationAppError("اسم الدور موجود بالفعل")
        role.name = name
        
    if payload.description is not None:
        role.description = norm_text(payload.description)
        
    if payload.permission_keys is not None:
        old_keys = [p.key for p in role.permissions]
        role.permissions = []
        for key in payload.permission_keys:
            perm = repo.get_permission_by_key(key)
            if perm:
                role.permissions.append(perm)
        
        # Notify on permission changes
        SecurityNotificationService.notify_security_event("role_permissions_changed", {
            "role_name": role.name,
            "old_permissions": old_keys,
            "new_permissions": payload.permission_keys,
            "actor_id": actor.id
        })
                
    record_audit(db, actor_user_id=actor.id, action="role.updated", target_type="role", target_id=role.id, summary=f"Updated role {role.name}")
    db.commit()
    return role

def delete_role(db: Session, actor: User, role_id: str) -> None:
    repo = IdentityRepository(db)
    role = get_role_or_404(db, role_id)
    
    if role.is_preset:
        raise ValidationAppError("لا يمكن حذف الأدوار النظامية")
        
    record_audit(db, actor_user_id=actor.id, action="role.deleted", target_type="role", target_id=role.id, summary=f"Deleted role {role.name}")
    repo.delete_role(role)
    db.commit()

def clone_role(db: Session, actor: User, role_id: str, new_name: str) -> Role:
    repo = IdentityRepository(db)
    source_role = get_role_or_404(db, role_id)
    
    if repo.get_role_by_name(norm_text(new_name).lower()):
        raise ValidationAppError("الاسم الجديد للدور موجود بالفعل")
        
    new_role = Role(
        name=norm_text(new_name).lower(),
        description=f"نسخة من {source_role.name}",
        is_preset=False
    )
    new_role.permissions = list(source_role.permissions)
    
    repo.add_role(new_role)
    db.flush()
    record_audit(db, actor_user_id=actor.id, action="role.cloned", target_type="role", target_id=new_role.id, summary=f"Cloned role {source_role.name} to {new_role.name}")
    db.commit()
    return new_role

# --- Account Freezing ---

def freeze_user(db: Session, actor: User, user_id: str, payload: FreezeUserRequest) -> User:
    repo = IdentityRepository(db)
    user = repo.get_user_by_id(user_id)
    if not user:
        raise NotFoundError("المستخدم غير موجود")
        
    if user.id == actor.id:
        raise ValidationAppError("لا يمكنك تجميد حسابك الخاص")
        
    user.is_frozen_until = payload.frozen_until or datetime.now(UTC).replace(year=9999)
    
    # Notify
    SecurityNotificationService.notify_security_event("account_frozen", {
        "user_id": user.id, 
        "username": user.username,
        "frozen_until": str(user.is_frozen_until),
        "reason": payload.reason,
        "actor_id": actor.id
    })
    
    record_audit(db, actor_user_id=actor.id, action="user.frozen", target_type="user", target_id=user.id, summary=f"Frozen user {user.username} until {user.is_frozen_until}")
    db.commit()
    return user

def unfreeze_user(db: Session, actor: User, user_id: str) -> User:
    repo = IdentityRepository(db)
    user = repo.get_user_by_id(user_id)
    if not user:
        raise NotFoundError("المستخدم غير موجود")
        
    user.is_frozen_until = None
    
    record_audit(db, actor_user_id=actor.id, action="user.unfrozen", target_type="user", target_id=user.id, summary=f"Unfrozen user {user.username}")
    db.commit()
    return user
