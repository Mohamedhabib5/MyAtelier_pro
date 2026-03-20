from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260316_000005'
down_revision = '20260316_000004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'dress_resources',
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=60), nullable=False),
        sa.Column('dress_type', sa.String(length=80), nullable=False),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=40), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('image_path', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'code', name='uq_dress_resources_company_code'),
    )
    op.create_index('ix_dress_resources_company_id', 'dress_resources', ['company_id'])
    op.create_index('ix_dress_resources_code', 'dress_resources', ['code'])
    op.create_index('ix_dress_resources_status', 'dress_resources', ['status'])


def downgrade() -> None:
    op.drop_index('ix_dress_resources_status', table_name='dress_resources')
    op.drop_index('ix_dress_resources_code', table_name='dress_resources')
    op.drop_index('ix_dress_resources_company_id', table_name='dress_resources')
    op.drop_table('dress_resources')
