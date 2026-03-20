from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260316_000011'
down_revision = '20260316_000010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('payment_receipts', sa.Column('status', sa.String(length=30), server_default='active', nullable=False))
    op.add_column('payment_receipts', sa.Column('voided_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('payment_receipts', sa.Column('voided_by_user_id', sa.String(length=36), nullable=True))
    op.add_column('payment_receipts', sa.Column('void_reason', sa.Text(), nullable=True))
    op.create_foreign_key(
        'fk_payment_receipts_voided_by_user_id_users',
        'payment_receipts',
        'users',
        ['voided_by_user_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.alter_column('payment_receipts', 'status', server_default=None)


def downgrade() -> None:
    op.drop_constraint('fk_payment_receipts_voided_by_user_id_users', 'payment_receipts', type_='foreignkey')
    op.drop_column('payment_receipts', 'void_reason')
    op.drop_column('payment_receipts', 'voided_by_user_id')
    op.drop_column('payment_receipts', 'voided_at')
    op.drop_column('payment_receipts', 'status')
