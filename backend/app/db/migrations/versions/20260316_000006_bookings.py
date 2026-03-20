from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260316_000006'
down_revision = '20260316_000005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'bookings',
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('booking_number', sa.String(length=40), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('service_id', sa.String(length=36), nullable=False),
        sa.Column('dress_id', sa.String(length=36), nullable=True),
        sa.Column('booking_date', sa.Date(), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('quoted_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('status', sa.String(length=40), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['service_id'], ['service_catalog_items.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['dress_id'], ['dress_resources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'booking_number', name='uq_bookings_company_number'),
    )
    op.create_index('ix_bookings_company_id', 'bookings', ['company_id'])
    op.create_index('ix_bookings_customer_id', 'bookings', ['customer_id'])
    op.create_index('ix_bookings_event_date', 'bookings', ['event_date'])
    op.create_index('ix_bookings_status', 'bookings', ['status'])


def downgrade() -> None:
    op.drop_index('ix_bookings_status', table_name='bookings')
    op.drop_index('ix_bookings_event_date', table_name='bookings')
    op.drop_index('ix_bookings_customer_id', table_name='bookings')
    op.drop_index('ix_bookings_company_id', table_name='bookings')
    op.drop_table('bookings')
