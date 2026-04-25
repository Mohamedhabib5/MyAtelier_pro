"""add custody date column

Revision ID: 20260423_000028
Revises: 20260423_000027
Create Date: 2026-04-23 17:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260423_000028"
down_revision = "20260423_000027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("custody_cases", sa.Column("custody_date", sa.Date(), nullable=True))
    bind = op.get_bind()
    bind.execute(sa.text("UPDATE custody_cases SET custody_date = DATE(created_at) WHERE custody_date IS NULL"))
    op.alter_column("custody_cases", "custody_date", existing_type=sa.Date(), nullable=False)


def downgrade() -> None:
    op.drop_column("custody_cases", "custody_date")
