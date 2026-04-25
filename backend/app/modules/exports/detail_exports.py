from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.exports.rendering import BOOKING_LINE_COLUMNS, PAYMENT_ALLOCATION_COLUMNS, build_csv, build_filename, build_xlsx, record_export_download
from app.modules.exports.row_collectors import booking_line_rows, payment_allocation_rows
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope


def export_booking_lines_csv(
    db: Session,
    actor: User,
    session: dict,
    branch_id: str | None = None,
    *,
    search: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'booking_date',
    sort_dir: str = 'desc',
) -> tuple[str, str]:
    branch = resolve_branch_scope(db, session, branch_id)
    rows = booking_line_rows(
        db,
        session,
        branch.id,
        search=search,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    content = build_csv(rows, BOOKING_LINE_COLUMNS)
    filename = build_filename(f'booking_lines_{branch.code.lower()}')
    record_export_download(db, actor, 'export.booking_lines_csv_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content


def export_booking_lines_xlsx(
    db: Session,
    actor: User,
    session: dict,
    branch_id: str | None = None,
    *,
    search: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'booking_date',
    sort_dir: str = 'desc',
) -> tuple[str, bytes]:
    branch = resolve_branch_scope(db, session, branch_id)
    rows = booking_line_rows(
        db,
        session,
        branch.id,
        search=search,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    content = build_xlsx(rows, BOOKING_LINE_COLUMNS)
    filename = build_filename(f'booking_lines_{branch.code.lower()}', extension='xlsx')
    record_export_download(db, actor, 'export.booking_lines_xlsx_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content


def export_payment_allocations_csv(
    db: Session,
    actor: User,
    session: dict,
    branch_id: str | None = None,
    *,
    search: str | None = None,
    status: str | None = None,
    document_kind: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'payment_date',
    sort_dir: str = 'desc',
) -> tuple[str, str]:
    branch = resolve_branch_scope(db, session, branch_id)
    rows = payment_allocation_rows(
        db,
        session,
        branch.id,
        search=search,
        status=status,
        document_kind=document_kind,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    content = build_csv(rows, PAYMENT_ALLOCATION_COLUMNS)
    filename = build_filename(f'payment_allocations_{branch.code.lower()}')
    record_export_download(db, actor, 'export.payment_allocations_csv_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content


def export_payment_allocations_xlsx(
    db: Session,
    actor: User,
    session: dict,
    branch_id: str | None = None,
    *,
    search: str | None = None,
    status: str | None = None,
    document_kind: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = 'payment_date',
    sort_dir: str = 'desc',
) -> tuple[str, bytes]:
    branch = resolve_branch_scope(db, session, branch_id)
    rows = payment_allocation_rows(
        db,
        session,
        branch.id,
        search=search,
        status=status,
        document_kind=document_kind,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    content = build_xlsx(rows, PAYMENT_ALLOCATION_COLUMNS)
    filename = build_filename(f'payment_allocations_{branch.code.lower()}', extension='xlsx')
    record_export_download(db, actor, 'export.payment_allocations_xlsx_downloaded', filename, len(rows), branch_id=branch.id)
    return filename, content
