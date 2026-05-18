from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CashReconciliation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cash_reconciliations"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    branch_id: Mapped[str] = mapped_column(ForeignKey("branches.id", ondelete="RESTRICT"), nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    reconciliation_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_method_id: Mapped[str] = mapped_column(ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=False)

    # "من استلم النقدية من الكاشير"
    receiver_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Summaries
    total_expected_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    total_actual_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    difference_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    branch = relationship("Branch", lazy="joined")
    payment_method = relationship("PaymentMethod", lazy="joined")
    created_by = relationship("User", foreign_keys=[created_by_user_id], lazy="joined")

    items = relationship(
        "ReconciliationItem",
        back_populates="reconciliation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ReconciliationItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reconciliation_items"

    reconciliation_id: Mapped[str] = mapped_column(ForeignKey("cash_reconciliations.id", ondelete="CASCADE"), nullable=False)
    payment_document_id: Mapped[str | None] = mapped_column(ForeignKey("payment_documents.id", ondelete="RESTRICT"), nullable=True)
    disbursement_voucher_id: Mapped[str | None] = mapped_column(ForeignKey("disbursement_vouchers.id", ondelete="RESTRICT"), nullable=True)

    expected_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    actual_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_reconciled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    reconciliation = relationship("CashReconciliation", back_populates="items")
    payment_document = relationship("PaymentDocument", lazy="joined")
    disbursement_voucher = relationship("DisbursementVoucher", lazy="joined")

