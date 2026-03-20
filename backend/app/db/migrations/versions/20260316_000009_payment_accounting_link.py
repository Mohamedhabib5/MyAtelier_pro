from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260316_000009'
down_revision = '20260316_000008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('payment_receipts', sa.Column('journal_entry_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(
        'fk_payment_receipts_journal_entry_id_journal_entries',
        'payment_receipts',
        'journal_entries',
        ['journal_entry_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_index('ix_payment_receipts_journal_entry_id', 'payment_receipts', ['journal_entry_id'])


def downgrade() -> None:
    op.drop_index('ix_payment_receipts_journal_entry_id', table_name='payment_receipts')
    op.drop_constraint('fk_payment_receipts_journal_entry_id_journal_entries', 'payment_receipts', type_='foreignkey')
    op.drop_column('payment_receipts', 'journal_entry_id')
