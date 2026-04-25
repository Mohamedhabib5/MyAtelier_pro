from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import require_exports_manage, require_exports_view
from app.db.session import get_db
from app.modules.exports.schemas import ExportScheduleCreateRequest, ExportScheduleResponse, ExportScheduleRunDueRequest, ExportScheduleRunDueResponse, ExportScheduleRunResponse, ExportScheduleToggleResponse
from app.modules.exports.schedule_service import create_export_schedule, list_export_schedules, run_due_export_schedules, run_export_schedule, toggle_export_schedule
from app.modules.exports.pdf_service import build_simple_pdf_report, finance_pdf_lines, reports_pdf_lines
from app.modules.exports.service import export_booking_lines_csv, export_booking_lines_xlsx, export_bookings_csv, export_bookings_xlsx, export_custody_csv, export_custody_xlsx, export_customers_csv, export_customers_xlsx, export_payment_allocations_csv, export_payment_allocations_xlsx, export_payments_csv, export_payments_xlsx
from app.modules.dashboard.service import get_finance_dashboard
from app.modules.reports.service import get_reports_overview
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_scope

router = APIRouter(prefix='/exports', tags=['exports'])


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


def _payment_export_filters(
    search: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias='status'),
    document_kind: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    sort_by: str = Query(default='payment_date'),
    sort_dir: str = Query(default='desc'),
) -> dict:
    return {
        'search': search,
        'status': status_value,
        'document_kind': document_kind,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'sort_dir': sort_dir,
    }


@router.get('/customers.csv')
def download_customers_export(db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_customers_csv(db, current_user)
    return _csv_response(filename, content)


@router.get('/customers.xlsx')
def download_customers_export_xlsx(db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_customers_xlsx(db, current_user)
    return _xlsx_response(filename, content)


@router.get('/bookings.csv')
def download_bookings_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_booking_export_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    filename, content = export_bookings_csv(db, current_user, request.session, branch_id, **filters)
    return _csv_response(filename, content)


@router.get('/bookings.xlsx')
def download_bookings_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_booking_export_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    filename, content = export_bookings_xlsx(db, current_user, request.session, branch_id, **filters)
    return _xlsx_response(filename, content)


@router.get('/booking-lines.csv')
def download_booking_lines_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_booking_export_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    filename, content = export_booking_lines_csv(db, current_user, request.session, branch_id, **filters)
    return _csv_response(filename, content)


@router.get('/booking-lines.xlsx')
def download_booking_lines_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_booking_export_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    filename, content = export_booking_lines_xlsx(db, current_user, request.session, branch_id, **filters)
    return _xlsx_response(filename, content)


@router.get('/payments.csv')
@router.get('/payment-documents.csv')
def download_payments_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_payment_export_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    filename, content = export_payments_csv(db, current_user, request.session, branch_id, **filters)
    return _csv_response(filename, content)


@router.get('/payments.xlsx')
@router.get('/payment-documents.xlsx')
def download_payments_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_payment_export_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    filename, content = export_payments_xlsx(db, current_user, request.session, branch_id, **filters)
    return _xlsx_response(filename, content)


@router.get('/payment-allocations.csv')
def download_payment_allocations_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_payment_export_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    filename, content = export_payment_allocations_csv(db, current_user, request.session, branch_id, **filters)
    return _csv_response(filename, content)


@router.get('/payment-allocations.xlsx')
def download_payment_allocations_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_payment_export_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    filename, content = export_payment_allocations_xlsx(db, current_user, request.session, branch_id, **filters)
    return _xlsx_response(filename, content)


@router.get('/custody.csv')
def download_custody_export(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_custody_csv(db, current_user, request.session)
    return _csv_response(filename, content)


@router.get('/custody.xlsx')
def download_custody_export_xlsx(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_custody_xlsx(db, current_user, request.session)
    return _xlsx_response(filename, content)


@router.get('/schedules', response_model=list[ExportScheduleResponse])
def list_export_schedules_route(db: Session = Depends(get_db), _: User = Depends(require_exports_view)) -> list[ExportScheduleResponse]:
    return [ExportScheduleResponse.model_validate(item) for item in list_export_schedules(db)]


@router.post('/schedules', response_model=ExportScheduleResponse)
def create_export_schedule_route(payload: ExportScheduleCreateRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_exports_manage)) -> ExportScheduleResponse:
    return ExportScheduleResponse.model_validate(create_export_schedule(db, current_user, payload, request.session))


@router.post('/schedules/{schedule_id}/run', response_model=ExportScheduleRunResponse)
def run_export_schedule_route(schedule_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_exports_manage)) -> ExportScheduleRunResponse:
    return ExportScheduleRunResponse.model_validate(run_export_schedule(db, current_user, schedule_id))


@router.post('/schedules/{schedule_id}/toggle', response_model=ExportScheduleToggleResponse)
def toggle_export_schedule_route(schedule_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_exports_manage)) -> ExportScheduleToggleResponse:
    return ExportScheduleToggleResponse.model_validate({'schedule': toggle_export_schedule(db, current_user, schedule_id)})


@router.post('/schedules/run-due', response_model=ExportScheduleRunDueResponse)
def run_due_export_schedules_route(
    request: Request,
    payload: ExportScheduleRunDueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_manage),
) -> ExportScheduleRunDueResponse:
    settings_obj = request.app.state.settings
    result = run_due_export_schedules(
        db,
        current_user,
        dry_run=payload.dry_run,
        limit=payload.limit,
        notify=payload.notify,
        delivery_webhook_url=settings_obj.export_delivery_webhook_url,
        delivery_dry_run=payload.delivery_dry_run,
        trigger_source=payload.trigger_source,
    )
    return ExportScheduleRunDueResponse.model_validate(result)


@router.get('/finance.pdf')
def download_finance_pdf(
    request: Request,
    branch_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    payload = get_finance_dashboard(db, branch.id)
    pdf_bytes = build_simple_pdf_report(title='Finance Summary PDF', lines=finance_pdf_lines(payload))
    return _pdf_response('finance-summary.pdf', pdf_bytes)


@router.get('/reports.pdf')
def download_reports_pdf(
    request: Request,
    branch_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    payload = get_reports_overview(db, branch.id)
    pdf_bytes = build_simple_pdf_report(title='Reports Overview PDF', lines=reports_pdf_lines(payload))
    return _pdf_response('reports-overview.pdf', pdf_bytes)


def _csv_response(filename: str, content: str) -> Response:
    disposition = f'attachment; filename="{filename}"'
    return Response(content=content, media_type='text/csv; charset=utf-8', headers={'Content-Disposition': disposition})


def _pdf_response(filename: str, content: bytes) -> Response:
    disposition = f'attachment; filename="{filename}"'
    return Response(content=content, media_type='application/pdf', headers={'Content-Disposition': disposition})


def _xlsx_response(filename: str, content: bytes) -> Response:
    disposition = f'attachment; filename="{filename}"'
    return Response(content=content, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': disposition})
