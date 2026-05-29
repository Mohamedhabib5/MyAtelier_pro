"""add product_condition to custody_cases

Revision ID: 7b82c1a3f9d0
Revises: 6a69985e7cd6
Create Date: 2026-05-29 22:48:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '7b82c1a3f9d0'
down_revision = '6a69985e7cd6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('custody_cases', sa.Column('product_condition', sa.String(length=200), nullable=True))


def downgrade() -> None:
    op.drop_column('custody_cases', 'product_condition')
