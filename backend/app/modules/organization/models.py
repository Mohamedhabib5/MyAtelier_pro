from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Company(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    default_currency: Mapped[str] = mapped_column(String(3), default="EGP", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    branches = relationship("Branch", back_populates="company", lazy="selectin")


class Branch(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "branches"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_branches_company_code"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    company = relationship("Company", back_populates="branches")


class FiscalPeriod(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "fiscal_periods"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class DocumentSequence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "document_sequences"
    __table_args__ = (UniqueConstraint("company_id", "key", name="uq_document_sequences_company_key"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    key: Mapped[str] = mapped_column(String(80), nullable=False)
    prefix: Mapped[str] = mapped_column(String(30), nullable=False)
    next_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    padding: Mapped[int] = mapped_column(Integer, default=6, nullable=False)