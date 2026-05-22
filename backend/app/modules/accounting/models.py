from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import JournalEntryStatus
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ChartOfAccount(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chart_of_accounts"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_chart_of_accounts_company_code"),
        CheckConstraint("level >= 1 AND level <= 5", name="ck_chart_of_accounts_level_range"),
        CheckConstraint("NOT (parent_account_id IS NULL AND level > 1)", name="ck_chart_of_accounts_root_level"),
        CheckConstraint("NOT (parent_account_id IS NOT NULL AND level = 1)", name="ck_chart_of_accounts_child_level"),
    )

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    parent_account_id: Mapped[str | None] = mapped_column(
        ForeignKey("chart_of_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    allows_posting: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    parent = relationship("ChartOfAccount", remote_side="ChartOfAccount.id", lazy="joined")


class JournalEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "journal_entries"
    __table_args__ = (UniqueConstraint("company_id", "entry_number", name="uq_journal_entries_company_number"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    fiscal_period_id: Mapped[str] = mapped_column(ForeignKey("fiscal_periods.id", ondelete="RESTRICT"), nullable=False)
    # Phase 1: Branch scoping – NULL for historical entries created before Phase 1.
    branch_id: Mapped[str | None] = mapped_column(
        ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    entry_number: Mapped[str] = mapped_column(String(40), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=JournalEntryStatus.DRAFT.value, nullable=False)
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Phase 1: Source document traceability (e.g. payment_document, disbursement_voucher, booking_line).
    reference_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reversed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reversed_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    lines = relationship(
        "JournalEntryLine",
        back_populates="journal_entry",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="JournalEntryLine.line_number",
    )


class JournalEntryLine(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "journal_entry_lines"
    __table_args__ = (
        UniqueConstraint("journal_entry_id", "line_number", name="uq_journal_entry_lines_entry_line_number"),
        CheckConstraint("debit_amount >= 0", name="ck_journal_entry_lines_debit_non_negative"),
        CheckConstraint("credit_amount >= 0", name="ck_journal_entry_lines_credit_non_negative"),
        CheckConstraint("NOT (debit_amount = 0 AND credit_amount = 0)", name="ck_journal_entry_lines_not_zero"),
        CheckConstraint("NOT (debit_amount > 0 AND credit_amount > 0)", name="ck_journal_entry_lines_single_side"),
    )

    journal_entry_id: Mapped[str] = mapped_column(ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[str] = mapped_column(ForeignKey("chart_of_accounts.id", ondelete="RESTRICT"), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    # Phase 1: Party Ledger – decoupled, no FK (same pattern as DisbursementVoucher.payee_type/payee_id).
    party_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    party_id: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)

    journal_entry = relationship("JournalEntry", back_populates="lines", lazy="joined")
    account = relationship("ChartOfAccount", lazy="joined")


class AccountingBridgeConfig(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "accounting_bridge_configs"
    __table_args__ = (
        UniqueConstraint("company_id", "bridge_key", name="uq_accounting_bridge_configs_company_key"),
    )

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    bridge_key: Mapped[str] = mapped_column(String(60), nullable=False)
    account_code: Mapped[str] = mapped_column(String(20), nullable=False)
    label_ar: Mapped[str] = mapped_column(String(120), nullable=False)
    label_en: Mapped[str] = mapped_column(String(120), nullable=False)
    is_required: Mapped[bool] = mapped_column(default=True, nullable=False)

