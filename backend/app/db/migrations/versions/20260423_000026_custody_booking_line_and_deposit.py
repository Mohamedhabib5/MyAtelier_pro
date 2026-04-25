"""custody booking-line linkage and security deposit tracking

Revision ID: 20260423_000026
Revises: 5f084ff4ae34
Create Date: 2026-04-23 09:40:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260423_000026"
down_revision = "5f084ff4ae34"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("custody_cases", sa.Column("booking_id", sa.String(length=36), nullable=True))
    op.add_column("custody_cases", sa.Column("booking_line_id", sa.String(length=36), nullable=True))
    op.add_column("custody_cases", sa.Column("return_outcome", sa.String(length=20), nullable=True))
    op.add_column("custody_cases", sa.Column("security_deposit_amount", sa.Numeric(12, 2), nullable=True))
    op.add_column("custody_cases", sa.Column("security_deposit_document_text", sa.Text(), nullable=True))
    op.add_column("custody_cases", sa.Column("security_deposit_payment_document_id", sa.String(length=36), nullable=True))
    op.add_column("custody_cases", sa.Column("security_deposit_refund_payment_document_id", sa.String(length=36), nullable=True))

    op.create_foreign_key(
        op.f("fk_custody_cases_booking_id_bookings"),
        "custody_cases",
        "bookings",
        ["booking_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_custody_cases_booking_line_id_booking_lines"),
        "custody_cases",
        "booking_lines",
        ["booking_line_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_custody_cases_security_deposit_payment_document_id_payment_documents"),
        "custody_cases",
        "payment_documents",
        ["security_deposit_payment_document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_custody_cases_security_deposit_refund_payment_document_id_payment_documents"),
        "custody_cases",
        "payment_documents",
        ["security_deposit_refund_payment_document_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint("uq_custody_cases_booking_line_id", "custody_cases", ["booking_line_id"])


def downgrade() -> None:
    op.drop_constraint("uq_custody_cases_booking_line_id", "custody_cases", type_="unique")
    op.drop_constraint(op.f("fk_custody_cases_security_deposit_refund_payment_document_id_payment_documents"), "custody_cases", type_="foreignkey")
    op.drop_constraint(op.f("fk_custody_cases_security_deposit_payment_document_id_payment_documents"), "custody_cases", type_="foreignkey")
    op.drop_constraint(op.f("fk_custody_cases_booking_line_id_booking_lines"), "custody_cases", type_="foreignkey")
    op.drop_constraint(op.f("fk_custody_cases_booking_id_bookings"), "custody_cases", type_="foreignkey")
    op.drop_column("custody_cases", "security_deposit_refund_payment_document_id")
    op.drop_column("custody_cases", "security_deposit_payment_document_id")
    op.drop_column("custody_cases", "security_deposit_document_text")
    op.drop_column("custody_cases", "security_deposit_amount")
    op.drop_column("custody_cases", "return_outcome")
    op.drop_column("custody_cases", "booking_line_id")
    op.drop_column("custody_cases", "booking_id")
