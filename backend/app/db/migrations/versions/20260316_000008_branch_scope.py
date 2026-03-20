"""branch scope for bookings and payments

Revision ID: 20260316_000008
Revises: 20260316_000007
Create Date: 2026-03-16 22:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '20260316_000008'
down_revision = '20260316_000007'
branch_labels = None
depends_on = None


BRANCH_ID_COL = sa.String(length=36)


def upgrade() -> None:
    op.add_column('bookings', sa.Column('branch_id', BRANCH_ID_COL, nullable=True))
    op.add_column('payment_receipts', sa.Column('branch_id', BRANCH_ID_COL, nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE bookings
            SET branch_id = branches.id
            FROM branches
            WHERE branches.company_id = bookings.company_id
              AND branches.is_default = true
              AND bookings.branch_id IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE payment_receipts
            SET branch_id = bookings.branch_id
            FROM bookings
            WHERE bookings.id = payment_receipts.booking_id
              AND payment_receipts.branch_id IS NULL
            """
        )
    )

    op.alter_column('bookings', 'branch_id', nullable=False)
    op.alter_column('payment_receipts', 'branch_id', nullable=False)
    op.create_foreign_key('fk_bookings_branch_id_branches', 'bookings', 'branches', ['branch_id'], ['id'], ondelete='RESTRICT')
    op.create_foreign_key('fk_payment_receipts_branch_id_branches', 'payment_receipts', 'branches', ['branch_id'], ['id'], ondelete='RESTRICT')
    op.create_index('ix_bookings_branch_id', 'bookings', ['branch_id'])
    op.create_index('ix_payment_receipts_branch_id', 'payment_receipts', ['branch_id'])


def downgrade() -> None:
    op.drop_index('ix_payment_receipts_branch_id', table_name='payment_receipts')
    op.drop_index('ix_bookings_branch_id', table_name='bookings')
    op.drop_constraint('fk_payment_receipts_branch_id_branches', 'payment_receipts', type_='foreignkey')
    op.drop_constraint('fk_bookings_branch_id_branches', 'bookings', type_='foreignkey')
    op.drop_column('payment_receipts', 'branch_id')
    op.drop_column('bookings', 'branch_id')
