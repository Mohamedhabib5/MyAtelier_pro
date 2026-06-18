from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import require_exports_view
from app.db.session import get_db
from app.modules.exports.service import (
    export_bookings_csv,
    export_bookings_xlsx,
    export_booking_lines_csv,
    export_booking_lines_xlsx,
)
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope
from app.api.routes.exports.helpers import _csv_response, _xlsx_response

router = APIRouter()

def _booking_export_filters(
    search: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias='status'),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    sort_by: str = Query(default='booking_date'),
    sort_dir: str = Query(default='desc'),
) -> dict:
    return {
        'search': search,
        'status': status_value,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'sort_dir': sort_dir,
    }


@router.get('/bookings.csv')
def download_bookings_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_booking_export_filters),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_bookings_csv(db, current_user, branch.id, page=page, page_size=page_size, **filters)
    return _csv_response(filename, content)


@router.get('/bookings.xlsx')
def download_bookings_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_booking_export_filters),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_bookings_xlsx(db, current_user, branch.id, page=page, page_size=page_size, **filters)
    return _xlsx_response(filename, content)


@router.get('/booking-lines.csv')
def download_booking_lines_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_booking_export_filters),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_booking_lines_csv(db, current_user, branch.id, page=page, page_size=page_size, **filters)
    return _csv_response(filename, content)


@router.get('/booking-lines.xlsx')
def download_booking_lines_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_booking_export_filters),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_booking_lines_xlsx(db, current_user, branch.id, page=page, page_size=page_size, **filters)
    return _xlsx_response(filename, content)
