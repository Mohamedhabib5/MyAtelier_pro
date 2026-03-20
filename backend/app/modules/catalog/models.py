from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Department(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'departments'
    __table_args__ = (UniqueConstraint('company_id', 'code', name='uq_departments_company_code'),)

    company_id: Mapped[str] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    services = relationship('ServiceCatalogItem', back_populates='department', lazy='selectin')


class ServiceCatalogItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'service_catalog_items'
    __table_args__ = (UniqueConstraint('company_id', 'name', name='uq_service_catalog_company_name'),)

    company_id: Mapped[str] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    department_id: Mapped[str] = mapped_column(ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    default_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department = relationship('Department', back_populates='services', lazy='joined')
