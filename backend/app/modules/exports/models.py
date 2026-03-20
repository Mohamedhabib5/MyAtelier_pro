from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ExportSchedule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'export_schedules'

    company_id: Mapped[str] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    branch_id: Mapped[str | None] = mapped_column(ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    export_type: Mapped[str] = mapped_column(String(40), nullable=False)
    cadence: Mapped[str] = mapped_column(String(20), nullable=False)
    next_run_on: Mapped[date] = mapped_column(Date, nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    branch = relationship('Branch', lazy='joined')
