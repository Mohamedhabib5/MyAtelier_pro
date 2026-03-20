"""booking lines and payment documents redesign

Revision ID: 20260316_000014
Revises: 20260316_000013
Create Date: 2026-03-16 23:40:00
"""

from __future__ import annotations

import uuid

from alembic import op
import sqlalchemy as sa


revision = '20260316_000014'
down_revision = '20260316_000013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'booking_lines',
        sa.Column('booking_id', sa.String(length=36), nullable=False),
        sa.Column('department_id', sa.String(length=36), nullable=False),
        sa.Column('service_id', sa.String(length=36), nullable=False),
        sa.Column('dress_id', sa.String(length=36), nullable=True),
        sa.Column('revenue_journal_entry_id', sa.String(length=36), nullable=True),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('service_date', sa.Date(), nullable=False),
        sa.Column('suggested_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('line_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('status', sa.String(length=40), nullable=False),
        sa.Column('revenue_recognized_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['service_id'], ['service_catalog_items.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['dress_id'], ['dress_resources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['revenue_journal_entry_id'], ['journal_entries.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_id', 'line_number', name='uq_booking_lines_booking_line_number'),
    )
    op.create_index('ix_booking_lines_booking_id', 'booking_lines', ['booking_id'])
    op.create_index('ix_booking_lines_service_date', 'booking_lines', ['service_date'])
    op.create_index('ix_booking_lines_dress_id', 'booking_lines', ['dress_id'])

    op.create_table(
        'payment_documents',
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('branch_id', sa.String(length=36), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('payment_number', sa.String(length=40), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('document_kind', sa.String(length=20), nullable=False, server_default='collection'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='active'),
        sa.Column('journal_entry_id', sa.String(length=36), nullable=True),
        sa.Column('voided_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('voided_by_user_id', sa.String(length=36), nullable=True),
        sa.Column('void_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['voided_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'payment_number', name='uq_payment_documents_company_number'),
    )
    op.create_index('ix_payment_documents_company_id', 'payment_documents', ['company_id'])
    op.create_index('ix_payment_documents_branch_id', 'payment_documents', ['branch_id'])
    op.create_index('ix_payment_documents_customer_id', 'payment_documents', ['customer_id'])
    op.create_index('ix_payment_documents_payment_date', 'payment_documents', ['payment_date'])

    op.create_table(
        'payment_allocations',
        sa.Column('payment_document_id', sa.String(length=36), nullable=False),
        sa.Column('booking_id', sa.String(length=36), nullable=False),
        sa.Column('booking_line_id', sa.String(length=36), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('allocated_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['payment_document_id'], ['payment_documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['booking_line_id'], ['booking_lines.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_document_id', 'line_number', name='uq_payment_allocations_document_line_number'),
    )
    op.create_index('ix_payment_allocations_payment_document_id', 'payment_allocations', ['payment_document_id'])
    op.create_index('ix_payment_allocations_booking_id', 'payment_allocations', ['booking_id'])
    op.create_index('ix_payment_allocations_booking_line_id', 'payment_allocations', ['booking_line_id'])

    op.alter_column('payment_documents', 'document_kind', server_default=None)
    op.alter_column('payment_documents', 'status', server_default=None)
    _migrate_existing_bookings()
    _migrate_existing_payments()


def downgrade() -> None:
    op.drop_index('ix_payment_allocations_booking_line_id', table_name='payment_allocations')
    op.drop_index('ix_payment_allocations_booking_id', table_name='payment_allocations')
    op.drop_index('ix_payment_allocations_payment_document_id', table_name='payment_allocations')
    op.drop_table('payment_allocations')
    op.drop_index('ix_payment_documents_payment_date', table_name='payment_documents')
    op.drop_index('ix_payment_documents_customer_id', table_name='payment_documents')
    op.drop_index('ix_payment_documents_branch_id', table_name='payment_documents')
    op.drop_index('ix_payment_documents_company_id', table_name='payment_documents')
    op.drop_table('payment_documents')
    op.drop_index('ix_booking_lines_dress_id', table_name='booking_lines')
    op.drop_index('ix_booking_lines_service_date', table_name='booking_lines')
    op.drop_index('ix_booking_lines_booking_id', table_name='booking_lines')
    op.drop_table('booking_lines')


def _migrate_existing_bookings() -> None:
    connection = op.get_bind()
    service_rows = {
        row.id: row
        for row in connection.execute(sa.text('SELECT id, department_id, default_price FROM service_catalog_items')).mappings()
    }
    existing_booking_ids = {
        row.booking_id
        for row in connection.execute(sa.text('SELECT booking_id FROM booking_lines')).mappings()
    }
    booking_rows = connection.execute(
        sa.text(
            'SELECT id, service_id, dress_id, booking_date, event_date, quoted_price, status, notes, revenue_journal_entry_id, revenue_recognized_at, created_at, updated_at '
            'FROM bookings'
        )
    ).mappings()
    for booking in booking_rows:
        if booking.id in existing_booking_ids:
            continue
        service = service_rows.get(booking.service_id)
        if service is None:
            continue
        connection.execute(
            sa.text(
                'INSERT INTO booking_lines (id, booking_id, department_id, service_id, dress_id, revenue_journal_entry_id, line_number, service_date, suggested_price, line_price, status, revenue_recognized_at, notes, created_at, updated_at) '
                'VALUES (:id, :booking_id, :department_id, :service_id, :dress_id, :revenue_journal_entry_id, :line_number, :service_date, :suggested_price, :line_price, :status, :revenue_recognized_at, :notes, :created_at, :updated_at)'
            ),
            {
                'id': str(uuid.uuid4()),
                'booking_id': booking.id,
                'department_id': service.department_id,
                'service_id': booking.service_id,
                'dress_id': booking.dress_id,
                'revenue_journal_entry_id': booking.revenue_journal_entry_id,
                'line_number': 1,
                'service_date': booking.event_date,
                'suggested_price': service.default_price or booking.quoted_price,
                'line_price': booking.quoted_price,
                'status': booking.status,
                'revenue_recognized_at': booking.revenue_recognized_at,
                'notes': None,
                'created_at': booking.created_at,
                'updated_at': booking.updated_at,
            },
        )


def _migrate_existing_payments() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if 'payment_receipts' not in inspector.get_table_names():
        return
    booking_rows = {
        row.id: row
        for row in connection.execute(sa.text('SELECT id, company_id, branch_id, customer_id FROM bookings')).mappings()
    }
    booking_line_rows = {
        row.booking_id: row.id
        for row in connection.execute(sa.text('SELECT id, booking_id FROM booking_lines WHERE line_number = 1')).mappings()
    }
    existing_numbers = {
        row.payment_number
        for row in connection.execute(sa.text('SELECT payment_number FROM payment_documents')).mappings()
    }
    payment_rows = connection.execute(
        sa.text(
            'SELECT id, company_id, branch_id, booking_id, payment_number, payment_date, payment_type, status, amount, journal_entry_id, voided_at, voided_by_user_id, void_reason, notes, created_at, updated_at '
            'FROM payment_receipts'
        )
    ).mappings()
    for payment in payment_rows:
        if payment.payment_number in existing_numbers:
            continue
        booking = booking_rows.get(payment.booking_id)
        booking_line_id = booking_line_rows.get(payment.booking_id)
        if booking is None or booking_line_id is None:
            continue
        document_id = str(uuid.uuid4())
        allocation_amount = -payment.amount if payment.payment_type == 'refund' else payment.amount
        connection.execute(
            sa.text(
                'INSERT INTO payment_documents (id, company_id, branch_id, customer_id, payment_number, payment_date, document_kind, status, journal_entry_id, voided_at, voided_by_user_id, void_reason, notes, created_at, updated_at) '
                'VALUES (:id, :company_id, :branch_id, :customer_id, :payment_number, :payment_date, :document_kind, :status, :journal_entry_id, :voided_at, :voided_by_user_id, :void_reason, :notes, :created_at, :updated_at)'
            ),
            {
                'id': document_id,
                'company_id': booking.company_id,
                'branch_id': booking.branch_id,
                'customer_id': booking.customer_id,
                'payment_number': payment.payment_number,
                'payment_date': payment.payment_date,
                'document_kind': 'refund' if payment.payment_type == 'refund' else 'collection',
                'status': payment.status or 'active',
                'journal_entry_id': payment.journal_entry_id,
                'voided_at': payment.voided_at,
                'voided_by_user_id': payment.voided_by_user_id,
                'void_reason': payment.void_reason,
                'notes': payment.notes,
                'created_at': payment.created_at,
                'updated_at': payment.updated_at,
            },
        )
        connection.execute(
            sa.text(
                'INSERT INTO payment_allocations (id, payment_document_id, booking_id, booking_line_id, line_number, allocated_amount, created_at, updated_at) '
                'VALUES (:id, :payment_document_id, :booking_id, :booking_line_id, :line_number, :allocated_amount, :created_at, :updated_at)'
            ),
            {
                'id': str(uuid.uuid4()),
                'payment_document_id': document_id,
                'booking_id': payment.booking_id,
                'booking_line_id': booking_line_id,
                'line_number': 1,
                'allocated_amount': allocation_amount,
                'created_at': payment.created_at,
                'updated_at': payment.updated_at,
            },
        )
