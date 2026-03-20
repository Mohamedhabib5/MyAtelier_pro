from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260316_000003'
down_revision = '20260315_000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'customers',
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('full_name', sa.String(length=160), nullable=False),
        sa.Column('phone', sa.String(length=30), nullable=False),
        sa.Column('email', sa.String(length=160), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'phone', name='uq_customers_company_phone'),
    )
    op.create_index('ix_customers_company_id', 'customers', ['company_id'])
    op.create_index('ix_customers_full_name', 'customers', ['full_name'])
    op.create_index('ix_customers_phone', 'customers', ['phone'])


def downgrade() -> None:
    op.drop_index('ix_customers_phone', table_name='customers')
    op.drop_index('ix_customers_full_name', table_name='customers')
    op.drop_index('ix_customers_company_id', table_name='customers')
    op.drop_table('customers')
