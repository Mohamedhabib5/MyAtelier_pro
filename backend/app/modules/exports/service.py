from __future__ import annotations

import csv
from datetime import UTC, datetime
from io import StringIO

from sqlalchemy.orm import Session

from app.modules.bookings.service import get_booking_document, list_bookings
from app.modules.core_platform.service import record_audit
from app.modules.customers.service import list_customers
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope
from app.modules.payments.service import get_payment_document, list_payments

CUSTOMER_COLUMNS = ['full_name', 'phone', 'email', 'address', 'is_active', 'notes']
BOOKING_COLUMNS = ['booking_number', 'branch_name', 'customer_name', 'booking_date', 'line_count', 'service_summary', 'next_service_date', 'total_amount', 'paid_total', 'remaining_amount', 'status', 'notes']
BOOKING_LINE_COLUMNS = ['booking_number', 'branch_name', 'customer_name', 'line_number', 'department_name', 'service_name', 'dress_code', 'service_date', 'suggested_price', 'line_price', 'paid_total', 'remaining_amount', 'status', 'revenue_journal_entry_number', 'notes']
PAYMENT_DOCUMENT_COLUMNS = ['payment_number', 'branch_name', 'customer_name', 'payment_date', 'document_kind', 'status', 'total_amount', 'allocation_count', 'booking_numbers', 'journal_entry_number', 'journal_entry_status', 'voided_at', 'void_reason', 'notes']
PAYMENT_ALLOCATION_COLUMNS = ['payment_number', 'branch_name', 'customer_name', 'payment_date', 'booking_number', 'booking_line_number', 'department_name', 'service_name', 'dress_code', 'service_date', 'line_status', 'line_price', 'allocated_amount']


def export_customers_csv(db: Session, actor: User) -> tuple[str, str]:
    rows = list_customers(db)
    content = _build_csv(rows, CUSTOMER_COLUMNS)
    filename = _filename('customers')
    record_audit(db, actor_user_id=actor.id, action='export.customers_csv_downloaded', target_type='export', target_id=None, summary=f'Downloaded customers export {filename}', diff={'row_count': len(rows)})
    db.commit()
    return filename, content


def export_bookings_csv(db: Session, actor: User, session: dict, branch_id: str | None = None) -> tuple[str, str]:
    branch = resolve_branch_scope(db, session, branch_id)
    rows = list_bookings(db, session, branch.id)
    content = _build_csv(rows, BOOKING_COLUMNS)
    filename = _filename(f'bookings_{branch.code.lower()}')
    record_audit(db, actor_user_id=actor.id, action='export.bookings_csv_downloaded', target_type='export', target_id=None, summary=f'Downloaded bookings export {filename}', diff={'branch_id': branch.id, 'row_count': len(rows)})
    db.commit()
    return filename, content


def export_booking_lines_csv(db: Session, actor: User, session: dict, branch_id: str | None = None) -> tuple[str, str]:
    branch = resolve_branch_scope(db, session, branch_id)
    summaries = list_bookings(db, session, branch.id)
    rows = []
    for summary in summaries:
        document = get_booking_document(db, summary['id'], session)
        for line in document['lines']:
            rows.append({**{key: document[key] for key in ['booking_number', 'branch_name', 'customer_name']}, **line})
    content = _build_csv(rows, BOOKING_LINE_COLUMNS)
    filename = _filename(f'booking_lines_{branch.code.lower()}')
    record_audit(db, actor_user_id=actor.id, action='export.booking_lines_csv_downloaded', target_type='export', target_id=None, summary=f'Downloaded booking lines export {filename}', diff={'branch_id': branch.id, 'row_count': len(rows)})
    db.commit()
    return filename, content


def export_payments_csv(db: Session, actor: User, session: dict, branch_id: str | None = None) -> tuple[str, str]:
    branch = resolve_branch_scope(db, session, branch_id)
    rows = list_payments(db, session, branch.id)
    normalized = [{**row, 'booking_numbers': ' | '.join(row['booking_numbers'])} for row in rows]
    content = _build_csv(normalized, PAYMENT_DOCUMENT_COLUMNS)
    filename = _filename(f'payment_documents_{branch.code.lower()}')
    record_audit(db, actor_user_id=actor.id, action='export.payments_csv_downloaded', target_type='export', target_id=None, summary=f'Downloaded payment documents export {filename}', diff={'branch_id': branch.id, 'row_count': len(rows)})
    db.commit()
    return filename, content


def export_payment_allocations_csv(db: Session, actor: User, session: dict, branch_id: str | None = None) -> tuple[str, str]:
    branch = resolve_branch_scope(db, session, branch_id)
    summaries = list_payments(db, session, branch.id)
    rows = []
    for summary in summaries:
        document = get_payment_document(db, summary['id'], session)
        for allocation in document['allocations']:
            rows.append({**{key: document[key] for key in ['payment_number', 'branch_name', 'customer_name', 'payment_date']}, **allocation})
    content = _build_csv(rows, PAYMENT_ALLOCATION_COLUMNS)
    filename = _filename(f'payment_allocations_{branch.code.lower()}')
    record_audit(db, actor_user_id=actor.id, action='export.payment_allocations_csv_downloaded', target_type='export', target_id=None, summary=f'Downloaded payment allocations export {filename}', diff={'branch_id': branch.id, 'row_count': len(rows)})
    db.commit()
    return filename, content


def _build_csv(rows: list[dict], columns: list[str]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column) for column in columns})
    return '﻿' + buffer.getvalue()


def _filename(prefix: str) -> str:
    timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{timestamp}.csv'
