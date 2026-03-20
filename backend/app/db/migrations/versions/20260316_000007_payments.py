from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260316_000007'
down_revision = '20260316_000006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'payment_receipts',
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('payment_number', sa.String(length=40), nullable=False),
        sa.Column('booking_id', sa.String(length=36), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_type', sa.String(length=40), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('remaining_after', sa.Numeric(12, 2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'payment_number', name='uq_payment_receipts_company_number'),
    )
    op.create_index('ix_payment_receipts_booking_id', 'payment_receipts', ['booking_id'])
    op.create_index('ix_payment_receipts_company_id', 'payment_receipts', ['company_id'])
    op.create_index('ix_payment_receipts_payment_date', 'payment_receipts', ['payment_date'])


def downgrade() -> None:
    op.drop_index('ix_payment_receipts_payment_date', table_name='payment_receipts')
    op.drop_index('ix_payment_receipts_company_id', table_name='payment_receipts')
    op.drop_index('ix_payment_receipts_booking_id', table_name='payment_receipts')
    op.drop_table('payment_receipts')
