"""dresses mode and sale

Revision ID: 84d61507bcfa
Revises: 7b82c1a3f9d0
Create Date: 2026-05-30 20:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '84d61507bcfa'
down_revision = '7b82c1a3f9d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add dresses_mode to companies
    op.add_column('companies', sa.Column('dresses_mode', sa.String(length=20), server_default='free', nullable=False))

    # 2. Make dress_type_id nullable in dress_resources
    op.alter_column('dress_resources', 'dress_type_id', existing_type=sa.String(), nullable=True)

    # 3. Add is_sale to booking_lines
    op.add_column('booking_lines', sa.Column('is_sale', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    op.drop_column('booking_lines', 'is_sale')
    op.alter_column('dress_resources', 'dress_type_id', existing_type=sa.String(), nullable=False)
    op.drop_column('companies', 'dresses_mode')
