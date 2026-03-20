from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260316_000004'
down_revision = '20260316_000003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'departments',
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=40), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'code', name='uq_departments_company_code'),
    )
    op.create_index('ix_departments_company_id', 'departments', ['company_id'])
    op.create_index('ix_departments_name', 'departments', ['name'])

    op.create_table(
        'service_catalog_items',
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('department_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('default_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'name', name='uq_service_catalog_company_name'),
    )
    op.create_index('ix_service_catalog_company_id', 'service_catalog_items', ['company_id'])
    op.create_index('ix_service_catalog_department_id', 'service_catalog_items', ['department_id'])
    op.create_index('ix_service_catalog_name', 'service_catalog_items', ['name'])


def downgrade() -> None:
    op.drop_index('ix_service_catalog_name', table_name='service_catalog_items')
    op.drop_index('ix_service_catalog_department_id', table_name='service_catalog_items')
    op.drop_index('ix_service_catalog_company_id', table_name='service_catalog_items')
    op.drop_table('service_catalog_items')
    op.drop_index('ix_departments_name', table_name='departments')
    op.drop_index('ix_departments_company_id', table_name='departments')
    op.drop_table('departments')
