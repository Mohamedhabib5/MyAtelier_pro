"""add custody compensation linkage and direct payment amount

Revision ID: 20260402_000025
Revises: 20260402_000024
Create Date: 2026-04-02 23:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260402_000025"
down_revision = "20260402_000024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "payment_documents",
        sa.Column("direct_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    op.alter_column("payment_documents", "direct_amount", server_default=None)

    op.add_column("custody_cases", sa.Column("compensation_amount", sa.Numeric(12, 2), nullable=True))
    op.add_column("custody_cases", sa.Column("compensation_collected_on", sa.Date(), nullable=True))
    op.add_column("custody_cases", sa.Column("compensation_payment_document_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        op.f("fk_custody_cases_compensation_payment_document_id_payment_documents"),
        "custody_cases",
        "payment_documents",
        ["compensation_payment_document_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_custody_cases_compensation_payment_document_id_payment_documents"),
        "custody_cases",
        type_="foreignkey",
    )
    op.drop_column("custody_cases", "compensation_payment_document_id")
    op.drop_column("custody_cases", "compensation_collected_on")
    op.drop_column("custody_cases", "compensation_amount")
    op.drop_column("payment_documents", "direct_amount")
