from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.identity.models import Permission, Role, User


class IdentityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: str) -> User | None:
        stmt = select(User).where(User.id == user_id).options(selectinload(User.roles))
        return self.db.scalars(stmt).first()

    def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username).options(selectinload(User.roles))
        return self.db.scalars(stmt).first()

    def list_users(self) -> list[User]:
        stmt = select(User).options(selectinload(User.roles)).order_by(User.username.asc())
        return list(self.db.scalars(stmt))

    def count_users(self) -> int:
        stmt = select(func.count()).select_from(User)
        return int(self.db.scalar(stmt) or 0)

    def add_user(self, user: User) -> User:
        self.db.add(user)
        return user

    def get_role_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name).options(selectinload(Role.permissions))
        return self.db.scalars(stmt).first()

    def add_role(self, role: Role) -> Role:
        self.db.add(role)
        return role

    def get_permission_by_key(self, key: str) -> Permission | None:
        stmt = select(Permission).where(Permission.key == key)
        return self.db.scalars(stmt).first()

    def add_permission(self, permission: Permission) -> Permission:
        self.db.add(permission)
        return permission