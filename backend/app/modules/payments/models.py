from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PaymentReceiptStatus, PaymentDocumentKind
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PaymentMethod(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payment_methods"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_payment_methods_company_code"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class PaymentDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'payment_documents'
    __table_args__ = (UniqueConstraint('company_id', 'payment_number', name='uq_payment_documents_company_number'),)

    company_id: Mapped[str] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    branch_id: Mapped[str] = mapped_column(ForeignKey('branches.id', ondelete='RESTRICT'), nullable=False)
    customer_id: Mapped[str] = mapped_column(ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False)
    payment_method_id: Mapped[str] = mapped_column(ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    payment_number: Mapped[str] = mapped_column(String(40), nullable=False)
    payment_date: Mapped[str] = mapped_column(Date, nullable=False)
    document_kind: Mapped[str] = mapped_column(String(20), default=PaymentDocumentKind.COLLECTION.value, nullable=False)
    direct_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=PaymentReceiptStatus.ACTIVE.value, nullable=False)
    journal_entry_id: Mapped[str | None] = mapped_column(ForeignKey('journal_entries.id', ondelete='SET NULL'), nullable=True)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    voided_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    void_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    branch = relationship('Branch', lazy='joined')
    customer = relationship('Customer', lazy='joined')
    payment_method = relationship("PaymentMethod", lazy="joined")
    journal_entry = relationship('JournalEntry', lazy='joined')
    voided_by = relationship('User', lazy='joined', foreign_keys=[voided_by_user_id])
    allocations = relationship(
        'PaymentAllocation',
        back_populates='payment_document',
        lazy='selectin',
        cascade='all, delete-orphan',
        order_by='PaymentAllocation.line_number',
    )
    compensation_custody_case = relationship(
        "CustodyCase",
        back_populates="compensation_payment_document",
        uselist=False,
        primaryjoin="PaymentDocument.id == foreign(CustodyCase.compensation_payment_document_id)",
        overlaps="compensation_payment_document",
    )


class PaymentAllocation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = 'payment_allocations'

    payment_document_id: Mapped[str | None] = mapped_column(ForeignKey('payment_documents.id', ondelete='CASCADE'), nullable=True)
    disbursement_voucher_id: Mapped[str | None] = mapped_column(ForeignKey('disbursement_vouchers.id', ondelete='CASCADE'), nullable=True)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    booking_id: Mapped[str] = mapped_column(ForeignKey('bookings.id', ondelete='RESTRICT'), nullable=False)
    booking_line_id: Mapped[str] = mapped_column(ForeignKey('booking_lines.id', ondelete='RESTRICT'), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    payment_document = relationship('PaymentDocument', back_populates='allocations', lazy='joined')
    disbursement_voucher = relationship('DisbursementVoucher', back_populates='allocations', lazy='joined')
    booking = relationship('Booking', lazy='joined')
    booking_line = relationship('BookingLine', back_populates='payment_allocations', lazy='joined')



class DisbursementVoucher(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "disbursement_vouchers"
    __table_args__ = (UniqueConstraint("company_id", "voucher_number", name="uq_disbursement_vouchers_company_number"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    branch_id: Mapped[str] = mapped_column(ForeignKey("branches.id", ondelete="RESTRICT"), nullable=False)
    payment_method_id: Mapped[str] = mapped_column(ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    voucher_number: Mapped[str] = mapped_column(String(40), nullable=False)
    voucher_date: Mapped[str] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    
    # Decoupled Payee properties
    payee_type: Mapped[str] = mapped_column(String(30), nullable=False)  # 'customer', 'supplier', 'employee', 'expense'
    payee_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    payee_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    expense_category_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    journal_entry_id: Mapped[str | None] = mapped_column(ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    voided_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    void_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    branch = relationship("Branch", lazy="joined")
    payment_method = relationship("PaymentMethod", lazy="joined")
    journal_entry = relationship("JournalEntry", lazy="joined")
    voided_by = relationship("User", lazy="joined", foreign_keys=[voided_by_user_id])
    allocations = relationship(
        'PaymentAllocation',
        back_populates='disbursement_voucher',
        lazy='selectin',
        cascade='all, delete-orphan',
        order_by='PaymentAllocation.line_number',
    )


