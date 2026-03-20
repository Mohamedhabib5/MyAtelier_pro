"""make legacy booking detail columns nullable

Revision ID: 20260317_000015
Revises: 20260316_000014
Create Date: 2026-03-17 00:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '20260317_000015'
down_revision = '20260316_000014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('bookings', 'service_id', existing_type=sa.String(length=36), nullable=True)
    op.alter_column('bookings', 'event_date', existing_type=sa.Date(), nullable=True)
    op.alter_column('bookings', 'quoted_price', existing_type=sa.Numeric(12, 2), nullable=True)
    op.alter_column('bookings', 'revenue_journal_entry_id', existing_type=sa.String(length=36), nullable=True)
    op.alter_column('bookings', 'revenue_recognized_at', existing_type=sa.DateTime(timezone=True), nullable=True)


def downgrade() -> None:
    op.alter_column('bookings', 'revenue_recognized_at', existing_type=sa.DateTime(timezone=True), nullable=False)
    op.alter_column('bookings', 'revenue_journal_entry_id', existing_type=sa.String(length=36), nullable=False)
    op.alter_column('bookings', 'quoted_price', existing_type=sa.Numeric(12, 2), nullable=False)
    op.alter_column('bookings', 'event_date', existing_type=sa.Date(), nullable=False)
    op.alter_column('bookings', 'service_id', existing_type=sa.String(length=36), nullable=False)
