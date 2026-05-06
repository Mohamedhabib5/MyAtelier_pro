from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.exports.detail_exports import export_booking_lines_csv, export_booking_lines_xlsx, export_payment_allocations_csv, export_payment_allocations_xlsx
from app.modules.exports.master_data_exports import export_custody_csv, export_custody_xlsx, export_customers_csv, export_customers_xlsx
from app.modules.exports.rendering import BOOKING_COLUMNS, PAYMENT_DOCUMENT_COLUMNS, build_csv, build_filename, build_xlsx, record_export_download
from app.modules.exports.row_collectors import filtered_booking_rows, payment_document_rows
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope


def export_bookings_csv(
    db: Session,
    actor: User,
    branch_id: str | None = None,
    *,
    search: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'booking_date',
    sort_dir: str = 'desc',
    page: int | None = None,
    page_size: int | None = None,
) -> tuple[str, str]:
    from app.modules.organization.branch_context import resolve_branch_scope_stateless
    branch = resolve_branch_scope_stateless(db, branch_id)
    rows = filtered_booking_rows(
        db,
        branch.id,
        search=search,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )
    content = build_csv(rows, BOOKING_COLUMNS)
    filename = build_filename(f'bookings_{branch.code.lower()}')
    record_export_download(db, actor, 'export.bookings_csv_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content


def export_bookings_xlsx(
    db: Session,
    actor: User,
    branch_id: str | None = None,
    *,
    search: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'booking_date',
    sort_dir: str = 'desc',
    page: int | None = None,
    page_size: int | None = None,
) -> tuple[str, bytes]:
    from app.modules.organization.branch_context import resolve_branch_scope_stateless
    branch = resolve_branch_scope_stateless(db, branch_id)
    rows = filtered_booking_rows(
        db,
        branch.id,
        search=search,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )
    content = build_xlsx(rows, BOOKING_COLUMNS)
    filename = build_filename(f'bookings_{branch.code.lower()}', extension='xlsx')
    record_export_download(db, actor, 'export.bookings_xlsx_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content


def export_payments_csv(
    db: Session,
    actor: User,
    branch_id: str | None = None,
    *,
    search: str | None = None,
    status: str | None = None,
    document_kind: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'payment_date',
    sort_dir: str = 'desc',
    page: int | None = None,
    page_size: int | None = None,
) -> tuple[str, str]:
    from app.modules.organization.branch_context import resolve_branch_scope_stateless
    branch = resolve_branch_scope_stateless(db, branch_id)
    rows = payment_document_rows(
        db,
        branch.id,
        search=search,
        status=status,
        document_kind=document_kind,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )
    content = build_csv(rows, PAYMENT_DOCUMENT_COLUMNS)
    filename = build_filename(f'payment_documents_{branch.code.lower()}')
    record_export_download(db, actor, 'export.payments_csv_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content


def export_payments_xlsx(
    db: Session,
    actor: User,
    branch_id: str | None = None,
    *,
    search: str | None = None,
    status: str | None = None,
    document_kind: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'payment_date',
    sort_dir: str = 'desc',
    page: int | None = None,
    page_size: int | None = None,
) -> tuple[str, bytes]:
    from app.modules.organization.branch_context import resolve_branch_scope_stateless
    branch = resolve_branch_scope_stateless(db, branch_id)
    rows = payment_document_rows(
        db,
        branch.id,
        search=search,
        status=status,
        document_kind=document_kind,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )
    content = build_xlsx(rows, PAYMENT_DOCUMENT_COLUMNS)
    filename = build_filename(f'payment_documents_{branch.code.lower()}', extension='xlsx')
    record_export_download(db, actor, 'export.payments_xlsx_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content


def export_advanced_bi_csv(
    db: Session,
    actor: User,
    branch_id: str | None = None,
    *,
    date_from: str | None = None,
    date_to: str | None = None,
) -> tuple[str, str]:
    from app.modules.reports.rules import parse_date
    from app.modules.reports.detailed_service import get_detailed_lines_report
    from app.modules.exports.rendering import ADVANCED_BI_COLUMNS
    from app.modules.organization.branch_context import resolve_branch_scope_stateless
    
    branch = resolve_branch_scope_stateless(db, branch_id)
    d_from = parse_date(date_from) if date_from else None
    d_to = parse_date(date_to) if date_to else None
    
    rows = get_detailed_lines_report(db, branch.id, d_from, d_to)
    content = build_csv(rows, ADVANCED_BI_COLUMNS)
    filename = build_filename(f'advanced_bi_{branch.code.lower()}')
    record_export_download(db, actor, 'export.advanced_bi_csv_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content


def export_advanced_bi_xlsx(
    db: Session,
    actor: User,
    branch_id: str | None = None,
    *,
    date_from: str | None = None,
    date_to: str | None = None,
) -> tuple[str, bytes]:
    from app.modules.reports.rules import parse_date
    from app.modules.reports.detailed_service import get_detailed_lines_report
    from app.modules.exports.rendering import ADVANCED_BI_COLUMNS
    from app.modules.organization.branch_context import resolve_branch_scope_stateless
    
    branch = resolve_branch_scope_stateless(db, branch_id)
    d_from = parse_date(date_from) if date_from else None
    d_to = parse_date(date_to) if date_to else None
    
    rows = get_detailed_lines_report(db, branch.id, d_from, d_to)
    content = build_xlsx(rows, ADVANCED_BI_COLUMNS)
    filename = build_filename(f'advanced_bi_{branch.code.lower()}', extension='xlsx')
    record_export_download(db, actor, 'export.advanced_bi_xlsx_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content
