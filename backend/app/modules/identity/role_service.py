from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import norm_text
from app.core.exceptions import NotFoundError, ValidationAppError
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import Permission, Role, User
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.schemas import CreateRoleRequest, UpdateRoleRequest
from app.core.security import SecurityNotificationService
from app.core.redis_client import redis_client


def invalidate_all_user_perms_cache():
    try:
        keys = redis_client.keys("user_perms:*")
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass


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
    invalidate_all_user_perms_cache()
    return role


def delete_role(db: Session, actor: User, role_id: str) -> None:
    repo = IdentityRepository(db)
    role = get_role_or_404(db, role_id)
    
    if role.is_preset:
        raise ValidationAppError("لا يمكن حذف الأدوار النظامية")
        
    record_audit(db, actor_user_id=actor.id, action="role.deleted", target_type="role", target_id=role.id, summary=f"Deleted role {role.name}")
    repo.delete_role(role)
    db.commit()
    invalidate_all_user_perms_cache()


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
