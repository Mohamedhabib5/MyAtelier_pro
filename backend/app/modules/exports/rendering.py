from __future__ import annotations

import csv
from datetime import UTC, datetime
from io import BytesIO, StringIO

from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User

CUSTOMER_COLUMNS = ['full_name', 'phone', 'email', 'address', 'is_active', 'notes']
BOOKING_COLUMNS = ['booking_number', 'external_code', 'branch_name', 'customer_name', 'customer_phone', 'customer_address', 'booking_date', 'line_count', 'service_summary', 'next_service_date', 'total_amount', 'paid_total', 'remaining_amount', 'status', 'created_by_name', 'cancelled_at', 'cancellation_reason', 'notes']
BOOKING_LINE_COLUMNS = ['booking_number', 'branch_name', 'customer_name', 'customer_phone', 'customer_address', 'line_number', 'department_name', 'service_name', 'dress_code', 'service_date', 'suggested_price', 'line_price', 'paid_total', 'remaining_amount', 'status', 'revenue_journal_entry_number', 'cancelled_at', 'cancellation_reason', 'notes']
PAYMENT_DOCUMENT_COLUMNS = ['payment_number', 'branch_name', 'customer_name', 'customer_phone', 'customer_address', 'payment_date', 'document_kind', 'status', 'total_amount', 'allocation_count', 'booking_numbers', 'journal_entry_number', 'journal_entry_status', 'voided_at', 'void_reason', 'notes']
PAYMENT_ALLOCATION_COLUMNS = ['payment_number', 'branch_name', 'customer_name', 'customer_phone', 'customer_address', 'payment_date', 'document_kind', 'booking_number', 'booking_line_number', 'department_name', 'service_name', 'dress_code', 'service_date', 'line_status', 'line_price', 'allocated_amount']
CUSTODY_COLUMNS = ['case_number', 'status', 'case_type', 'customer_id', 'dress_id', 'compensation_amount', 'compensation_collected_on', 'compensation_payment_document_id', 'notes']
ADVANCED_BI_COLUMNS = ['booking_number', 'booking_date', 'customer_name', 'department_name', 'service_name', 'dress_code', 'line_price', 'paid_amount', 'remaining_amount', 'line_status', 'payment_method', 'payment_type', 'created_by']


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


def build_csv(rows: list[dict], columns: list[str], translations: dict[str, str] | None = None) -> bytes:
    buffer = StringIO()
    # If translations are provided, use them for the header row
    display_columns = [translations.get(c, c) for c in columns] if translations else columns
    
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction='ignore')
    # Custom header writing to use translated names
    if translations:
        writer.writerow(dict(zip(columns, display_columns)))
    else:
        writer.writeheader()
        
    for row in rows:
        writer.writerow({column: row.get(column) for column in columns})
    
    # Return as bytes with UTF-8-SIG (BOM included)
    return buffer.getvalue().encode('utf-8-sig')


def build_xlsx(rows: list[dict], columns: list[str], translations: dict[str, str] | None = None) -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Data'
    
    # If translations are provided, use them for the header row
    display_columns = [translations.get(c, c) for c in columns] if translations else columns
    worksheet.append(display_columns)
    
    for row in rows:
        worksheet.append([row.get(column) for column in columns])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def build_filename(prefix: str, extension: str = 'csv') -> str:
    timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{timestamp}.{extension}'
