from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260316_000012'
down_revision = '20260316_000011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'export_schedules',
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('branch_id', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('export_type', sa.String(length=40), nullable=False),
        sa.Column('cadence', sa.String(length=20), nullable=False),
        sa.Column('next_run_on', sa.Date(), nullable=False),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_export_schedules')),
    )
    op.create_index(op.f('ix_export_schedules_company_id'), 'export_schedules', ['company_id'])
    op.create_index(op.f('ix_export_schedules_next_run_on'), 'export_schedules', ['next_run_on'])


def downgrade() -> None:
    op.drop_index(op.f('ix_export_schedules_next_run_on'), table_name='export_schedules')
    op.drop_index(op.f('ix_export_schedules_company_id'), table_name='export_schedules')
    op.drop_table('export_schedules')
