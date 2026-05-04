"""add_cancellation_fields

Revision ID: c5e8a7f4b321
Revises: 4b30bac70b86
Create Date: 2026-05-02 17:18:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'c5e8a7f4b321'
down_revision = '4b30bac70b86'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add columns to bookings
    op.add_column('bookings', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('bookings', sa.Column('cancellation_reason', sa.Text(), nullable=True))
    op.add_column('bookings', sa.Column('cancelled_by_user_id', sa.String(), nullable=True))
    op.create_foreign_key(op.f('fk_bookings_cancelled_by_user_id_users'), 'bookings', 'users', ['cancelled_by_user_id'], ['id'], ondelete='SET NULL')

    # Add columns to booking_lines
    op.add_column('booking_lines', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('booking_lines', sa.Column('cancellation_reason', sa.Text(), nullable=True))
    op.add_column('booking_lines', sa.Column('cancelled_by_user_id', sa.String(), nullable=True))
    op.create_foreign_key(op.f('fk_booking_lines_cancelled_by_user_id_users'), 'booking_lines', 'users', ['cancelled_by_user_id'], ['id'], ondelete='SET NULL')

def downgrade() -> None:
    # Drop columns from booking_lines
    op.drop_constraint(op.f('fk_booking_lines_cancelled_by_user_id_users'), 'booking_lines', type_='foreignkey')
    op.drop_column('booking_lines', 'cancelled_by_user_id')
    op.drop_column('booking_lines', 'cancellation_reason')
    op.drop_column('booking_lines', 'cancelled_at')

    # Drop columns from bookings
    op.drop_constraint(op.f('fk_bookings_cancelled_by_user_id_users'), 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'cancelled_by_user_id')
    op.drop_column('bookings', 'cancellation_reason')
    op.drop_column('bookings', 'cancelled_at')
