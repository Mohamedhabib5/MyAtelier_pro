from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import JournalEntryStatus
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ChartOfAccount(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chart_of_accounts"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_chart_of_accounts_company_code"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    parent_account_id: Mapped[str | None] = mapped_column(
        ForeignKey("chart_of_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    allows_posting: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    parent = relationship("ChartOfAccount", remote_side="ChartOfAccount.id", lazy="joined")


class JournalEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "journal_entries"
    __table_args__ = (UniqueConstraint("company_id", "entry_number", name="uq_journal_entries_company_number"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    fiscal_period_id: Mapped[str] = mapped_column(ForeignKey("fiscal_periods.id", ondelete="RESTRICT"), nullable=False)
    entry_number: Mapped[str] = mapped_column(String(40), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=JournalEntryStatus.DRAFT.value, nullable=False)
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    journal_entry = relationship("JournalEntry", back_populates="lines", lazy="joined")
    account = relationship("ChartOfAccount", lazy="joined")
