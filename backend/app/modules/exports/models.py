from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Integer, Text, UniqueConstraint
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


class DailyEmailReportConfig(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'daily_email_report_configs'

    company_id: Mapped[str] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sender_email: Mapped[str] = mapped_column(String(120), nullable=False)
    sender_password: Mapped[str] = mapped_column(String(500), nullable=False)
    smtp_server: Mapped[str] = mapped_column(String(120), default='smtp.gmail.com', server_default='smtp.gmail.com', nullable=False)
    smtp_port: Mapped[int] = mapped_column(Integer, default=587, server_default='587', nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    send_hour: Mapped[int] = mapped_column(Integer, default=21, server_default='21', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)

    send_daily_summary: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)
    notify_booking_created: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false', nullable=False)
    notify_booking_modified: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false', nullable=False)
    notify_payment_captured: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false', nullable=False)
    notify_payment_refunded: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false', nullable=False)
    notify_entity_deleted: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)
    notify_operations_daily: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)
    notify_financial_critical: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)
    notify_backup_warnings: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)
    booking_email_template: Mapped[str] = mapped_column(String(40), default='detailed', server_default="'detailed'", nullable=False)
    payment_email_template: Mapped[str] = mapped_column(String(40), default='detailed', server_default="'detailed'", nullable=False)

    company = relationship('Company', lazy='select')


class DailyEmailReportLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'daily_email_report_logs'
    __table_args__ = (UniqueConstraint('config_id', 'report_date', name='uq_daily_report_config_date'),)

    config_id: Mapped[str] = mapped_column(ForeignKey('daily_email_report_configs.id', ondelete='CASCADE'), nullable=False, index=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), default='pending', nullable=False, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    config = relationship('DailyEmailReportConfig', lazy='select')

