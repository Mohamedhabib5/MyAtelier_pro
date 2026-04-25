from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CustodyCase(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "custody_cases"
    __table_args__ = (UniqueConstraint("booking_line_id", name="uq_custody_cases_booking_line_id"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    branch_id: Mapped[str] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    booking_id: Mapped[str | None] = mapped_column(ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    booking_line_id: Mapped[str | None] = mapped_column(ForeignKey("booking_lines.id", ondelete="SET NULL"), nullable=True)
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    dress_id: Mapped[str | None] = mapped_column(ForeignKey("dress_resources.id", ondelete="SET NULL"), nullable=True)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    entity_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    case_number: Mapped[str] = mapped_column(String(40), nullable=False)
    custody_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)
    case_type: Mapped[str] = mapped_column(String(30), default="handover", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_condition: Mapped[str | None] = mapped_column(String(200), nullable=True)
    return_outcome: Mapped[str | None] = mapped_column(String(20), nullable=True)
    security_deposit_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    security_deposit_document_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    security_deposit_payment_document_id: Mapped[str | None] = mapped_column(
        ForeignKey("payment_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    security_deposit_refund_payment_document_id: Mapped[str | None] = mapped_column(
        ForeignKey("payment_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    compensation_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    compensation_collected_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    compensation_payment_document_id: Mapped[str | None] = mapped_column(
        ForeignKey("payment_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
