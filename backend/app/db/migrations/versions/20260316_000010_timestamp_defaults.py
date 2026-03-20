from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260316_000010'
down_revision = '20260316_000009'
branch_labels = None
depends_on = None

TABLES = [
    'customers',
    'departments',
    'service_catalog_items',
    'dress_resources',
    'bookings',
    'payment_receipts',
]


def upgrade() -> None:
    for table_name in TABLES:
        op.alter_column(table_name, 'created_at', existing_type=sa.DateTime(timezone=True), server_default=sa.text('now()'), existing_nullable=False)
        op.alter_column(table_name, 'updated_at', existing_type=sa.DateTime(timezone=True), server_default=sa.text('now()'), existing_nullable=False)


def downgrade() -> None:
    for table_name in TABLES:
        op.alter_column(table_name, 'updated_at', existing_type=sa.DateTime(timezone=True), server_default=None, existing_nullable=False)
        op.alter_column(table_name, 'created_at', existing_type=sa.DateTime(timezone=True), server_default=None, existing_nullable=False)
