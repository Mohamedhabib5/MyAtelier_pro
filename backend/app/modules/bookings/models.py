from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Booking(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'bookings'
    __table_args__ = (UniqueConstraint('company_id', 'booking_number', name='uq_bookings_company_number'),)

    company_id: Mapped[str] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    branch_id: Mapped[str] = mapped_column(ForeignKey('branches.id', ondelete='RESTRICT'), nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    booking_number: Mapped[str] = mapped_column(String(40), nullable=False)
    customer_id: Mapped[str] = mapped_column(ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False)
    booking_date: Mapped[str] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    branch = relationship('Branch', lazy='joined')
    customer = relationship('Customer', lazy='joined')
    lines = relationship(
        'BookingLine',
        back_populates='booking',
        lazy='selectin',
        cascade='all, delete-orphan',
        order_by='BookingLine.line_number',
    )


class BookingLine(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'booking_lines'
    __table_args__ = (UniqueConstraint('booking_id', 'line_number', name='uq_booking_lines_booking_line_number'),)

    booking_id: Mapped[str] = mapped_column(ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    department_id: Mapped[str] = mapped_column(ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    service_id: Mapped[str] = mapped_column(ForeignKey('service_catalog_items.id', ondelete='RESTRICT'), nullable=False)
    dress_id: Mapped[str | None] = mapped_column(ForeignKey('dress_resources.id', ondelete='SET NULL'), nullable=True)
    revenue_journal_entry_id: Mapped[str | None] = mapped_column(ForeignKey('journal_entries.id', ondelete='SET NULL'), nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    service_date: Mapped[str] = mapped_column(Date, nullable=False)
    suggested_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_rate_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    revenue_recognized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    booking = relationship('Booking', back_populates='lines', lazy='joined')
    department = relationship('Department', lazy='joined')
    service = relationship('ServiceCatalogItem', lazy='joined')
    dress = relationship('DressResource', lazy='joined')
    revenue_journal_entry = relationship('JournalEntry', lazy='joined')
    payment_allocations = relationship('PaymentAllocation', back_populates='booking_line', lazy='selectin')
