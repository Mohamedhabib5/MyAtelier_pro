from __future__ import annotations

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DressResource(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'dress_resources'
    __table_args__ = (UniqueConstraint('company_id', 'code', name='uq_dress_resources_company_code'),)

    company_id: Mapped[str] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    dress_type: Mapped[str] = mapped_column(String(80), nullable=False)
    purchase_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
