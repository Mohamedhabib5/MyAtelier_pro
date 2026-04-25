"""tax-aware revenue recognition foundation

Revision ID: 20260322_000017
Revises: 20260317_000016
Create Date: 2026-03-22 02:40:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260322_000017"
down_revision = "20260317_000016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "service_catalog_items",
        sa.Column("tax_rate_percent", sa.Numeric(5, 2), nullable=False, server_default="0.00"),
    )
    op.add_column(
        "booking_lines",
        sa.Column("tax_rate_percent", sa.Numeric(5, 2), nullable=False, server_default="0.00"),
    )
    op.add_column(
        "booking_lines",
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
    )

    op.execute(
        sa.text(
            """
            UPDATE booking_lines
            SET
              tax_rate_percent = COALESCE((
                SELECT s.tax_rate_percent
                FROM service_catalog_items s
                WHERE s.id = booking_lines.service_id
              ), 0),
              tax_amount = ROUND(
                line_price * COALESCE((
                  SELECT s.tax_rate_percent
                  FROM service_catalog_items s
                  WHERE s.id = booking_lines.service_id
                ), 0) / 100.0,
                2
              )
            """
        )
    )

    op.alter_column("service_catalog_items", "tax_rate_percent", server_default=None)
    op.alter_column("booking_lines", "tax_rate_percent", server_default=None)
    op.alter_column("booking_lines", "tax_amount", server_default=None)


def downgrade() -> None:
    op.drop_column("booking_lines", "tax_amount")
    op.drop_column("booking_lines", "tax_rate_percent")
    op.drop_column("service_catalog_items", "tax_rate_percent")
