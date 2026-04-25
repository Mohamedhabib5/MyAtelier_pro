from __future__ import annotations

import csv
from datetime import UTC, datetime
from io import BytesIO, StringIO

from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User

CUSTOMER_COLUMNS = ['full_name', 'phone', 'email', 'address', 'is_active', 'notes']
BOOKING_COLUMNS = ['booking_number', 'branch_name', 'customer_name', 'booking_date', 'line_count', 'service_summary', 'next_service_date', 'total_amount', 'paid_total', 'remaining_amount', 'status', 'notes']
BOOKING_LINE_COLUMNS = ['booking_number', 'branch_name', 'customer_name', 'line_number', 'department_name', 'service_name', 'dress_code', 'service_date', 'suggested_price', 'line_price', 'paid_total', 'remaining_amount', 'status', 'revenue_journal_entry_number', 'notes']
PAYMENT_DOCUMENT_COLUMNS = ['payment_number', 'branch_name', 'customer_name', 'payment_date', 'document_kind', 'status', 'total_amount', 'allocation_count', 'booking_numbers', 'journal_entry_number', 'journal_entry_status', 'voided_at', 'void_reason', 'notes']
PAYMENT_ALLOCATION_COLUMNS = ['payment_number', 'branch_name', 'customer_name', 'payment_date', 'booking_number', 'booking_line_number', 'department_name', 'service_name', 'dress_code', 'service_date', 'line_status', 'line_price', 'allocated_amount']
CUSTODY_COLUMNS = ['case_number', 'status', 'case_type', 'customer_id', 'dress_id', 'compensation_amount', 'compensation_collected_on', 'compensation_payment_document_id', 'notes']


def record_export_download(
    db: Session,
    actor: User,
    action: str,
    filename: str,
    row_count: int,
    branch_id: str | None = None,
) -> None:
    diff = {'row_count': row_count}
    if branch_id:
        diff['branch_id'] = branch_id
    record_audit(
        db,
        actor_user_id=actor.id,
        action=action,
        target_type='export',
        target_id=None,
        summary=f'Downloaded export {filename}',
        diff=diff,
    )
    db.commit()


def build_csv(rows: list[dict], columns: list[str]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column) for column in columns})
    return '\ufeff' + buffer.getvalue()


def build_xlsx(rows: list[dict], columns: list[str]) -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Data'
    worksheet.append(columns)
    for row in rows:
        worksheet.append([row.get(column) for column in columns])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def build_filename(prefix: str, extension: str = 'csv') -> str:
    timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{timestamp}.{extension}'
