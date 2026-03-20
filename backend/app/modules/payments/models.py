from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PaymentReceiptStatus
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PaymentDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'payment_documents'
    __table_args__ = (UniqueConstraint('company_id', 'payment_number', name='uq_payment_documents_company_number'),)

    company_id: Mapped[str] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    branch_id: Mapped[str] = mapped_column(ForeignKey('branches.id', ondelete='RESTRICT'), nullable=False)
    customer_id: Mapped[str] = mapped_column(ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False)
    payment_number: Mapped[str] = mapped_column(String(40), nullable=False)
    payment_date: Mapped[str] = mapped_column(Date, nullable=False)
    document_kind: Mapped[str] = mapped_column(String(20), default='collection', nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=PaymentReceiptStatus.ACTIVE.value, nullable=False)
    journal_entry_id: Mapped[str | None] = mapped_column(ForeignKey('journal_entries.id', ondelete='SET NULL'), nullable=True)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    voided_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    void_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    branch = relationship('Branch', lazy='joined')
    customer = relationship('Customer', lazy='joined')
    journal_entry = relationship('JournalEntry', lazy='joined')
    voided_by = relationship('User', lazy='joined')
    allocations = relationship(
        'PaymentAllocation',
        back_populates='payment_document',
        lazy='selectin',
        cascade='all, delete-orphan',
        order_by='PaymentAllocation.line_number',
    )


class PaymentAllocation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'payment_allocations'
    __table_args__ = (UniqueConstraint('payment_document_id', 'line_number', name='uq_payment_allocations_document_line_number'),)

    payment_document_id: Mapped[str] = mapped_column(ForeignKey('payment_documents.id', ondelete='CASCADE'), nullable=False)
    booking_id: Mapped[str] = mapped_column(ForeignKey('bookings.id', ondelete='RESTRICT'), nullable=False)
    booking_line_id: Mapped[str] = mapped_column(ForeignKey('booking_lines.id', ondelete='RESTRICT'), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    payment_document = relationship('PaymentDocument', back_populates='allocations', lazy='joined')
    booking = relationship('Booking', lazy='joined')
    booking_line = relationship('BookingLine', back_populates='payment_allocations', lazy='joined')
