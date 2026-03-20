"""booking revenue recognition on completion

Revision ID: 20260316_000013
Revises: 20260316_000012
Create Date: 2026-03-16 22:45:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '20260316_000013'
down_revision = '20260316_000012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('bookings', sa.Column('revenue_journal_entry_id', sa.String(length=36), nullable=True))
    op.add_column('bookings', sa.Column('revenue_recognized_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_bookings_revenue_journal_entry', 'bookings', 'journal_entries', ['revenue_journal_entry_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_bookings_revenue_journal_entry', 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'revenue_recognized_at')
    op.drop_column('bookings', 'revenue_journal_entry_id')
