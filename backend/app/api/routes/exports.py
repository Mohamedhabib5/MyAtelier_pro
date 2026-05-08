from __future__ import annotations

from urllib.parse import quote
from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import require_exports_manage, require_exports_view
from app.db.session import get_db
from app.modules.exports.schemas import ExportScheduleCreateRequest, ExportScheduleResponse, ExportScheduleRunDueRequest, ExportScheduleRunDueResponse, ExportScheduleRunResponse, ExportScheduleToggleResponse
from app.modules.exports.schedule_service import create_export_schedule, list_export_schedules, run_due_export_schedules, run_export_schedule, toggle_export_schedule
from app.modules.exports.pdf_service import build_simple_pdf_report, finance_pdf_lines, reports_pdf_lines
from app.modules.exports.service import (
    export_advanced_bi_csv,
    export_advanced_bi_xlsx,
    export_booking_lines_csv,
    export_booking_lines_xlsx,
    export_bookings_csv,
    export_bookings_xlsx,
    export_custody_csv,
    export_custody_xlsx,
    export_customers_csv,
    export_customers_xlsx,
    export_payment_allocations_csv,
    export_payment_allocations_xlsx,
    export_payments_csv,
    export_payments_xlsx,
)
from app.modules.exports.ticket_service import ticket_store
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
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_booking_export_filters),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    filename, content = export_booking_lines_xlsx(db, current_user, branch_id, page=page, page_size=page_size, **filters)
    return _xlsx_response(filename, content)


@router.get('/payments.csv')
@router.get('/payment-documents.csv')
def download_payments_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_payment_export_filters),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_payments_csv(db, current_user, branch.id, page=page, page_size=page_size, **filters)
    return _csv_response(filename, content)


@router.get('/payments.xlsx')
@router.get('/payment-documents.xlsx')
def download_payments_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_payment_export_filters),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_payments_xlsx(db, current_user, branch.id, page=page, page_size=page_size, **filters)
    return _xlsx_response(filename, content)


@router.get('/payment-allocations.csv')
def download_payment_allocations_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_payment_export_filters),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_payment_allocations_csv(db, current_user, branch.id, page=page, page_size=page_size, **filters)
    return _csv_response(filename, content)


@router.get('/payment-allocations.xlsx')
def download_payment_allocations_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    filters: dict = Depends(_payment_export_filters),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_payment_allocations_xlsx(db, current_user, branch.id, page=page, page_size=page_size, **filters)
    return _xlsx_response(filename, content)


@router.get('/custody.csv')
def download_custody_export(
    request: Request,
    branch_id: str | None = Query(default=None),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_custody_csv(db, current_user, branch.id, page=page, page_size=page_size)
    return _csv_response(filename, content)


@router.get('/custody.xlsx')
def download_custody_export_xlsx(
    request: Request,
    branch_id: str | None = Query(default=None),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> Response:
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_custody_xlsx(db, current_user, branch.id, page=page, page_size=page_size)
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


@router.post('/tickets')
def generate_download_ticket(
    request: Request,
    target_path: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
) -> dict:
    # Parse query parameters from the target path if any
    from urllib.parse import parse_qs, urlparse
    parsed = urlparse(target_path)
    params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
    
    # Store the ticket
    ticket_id = ticket_store.create_ticket(
        user_id=str(current_user.id),
        path=parsed.path,
        params=params
    )
    
    from app.modules.core_platform.audit import record_audit
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="export.ticket_created",
        target_type="export_ticket",
        target_id=ticket_id,
        summary=f"Generated download ticket for {parsed.path}",
        diff={"path": parsed.path, "params": params}
    )
    
    return {"ticket": ticket_id, "download_url": f"/api/exports/download/{ticket_id}"}


@router.get('/download/{ticket_id}')
def consume_download_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
) -> Response:
    ticket = ticket_store.consume_ticket(ticket_id)
    if not ticket:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Invalid or expired download ticket")

    # Re-fetch user to verify permissions if necessary (ticket store has user_id)
    # For now, having the valid UUID ticket is proof of authorized generation
    user_id = ticket["user_id"]
    path = ticket["path"]
    params = ticket["params"]
    
    # Cast pagination parameters to int to avoid TypeError in repository calculations
    if 'page' in params and params['page'] is not None:
        try:
            params['page'] = int(params['page'])
        except (ValueError, TypeError):
            params.pop('page')
    if 'page_size' in params and params['page_size'] is not None:
        try:
            params['page_size'] = int(params['page_size'])
        except (ValueError, TypeError):
            params.pop('page_size')
    
    # Map path to service function
    if path.endswith('customers.csv'):
        from app.modules.exports.service import export_customers_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        filename, content = export_customers_csv(db, user)
        return _csv_response(filename, content)
    
    elif path.endswith('customers.xlsx'):
        from app.modules.exports.service import export_customers_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        filename, content = export_customers_xlsx(db, user)
        return _xlsx_response(filename, content)

    elif path.endswith('bookings.csv'):
        from app.modules.exports.service import export_bookings_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        # Resolve branch from params
        branch_id = params.get('branch_id')
        filename, content = export_bookings_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('bookings.xlsx'):
        from app.modules.exports.service import export_bookings_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_bookings_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('booking-lines.csv'):
        from app.modules.exports.service import export_booking_lines_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_booking_lines_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('booking-lines.xlsx'):
        from app.modules.exports.service import export_booking_lines_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_booking_lines_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('payment-documents.csv') or path.endswith('payments.csv'):
        from app.modules.exports.service import export_payments_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_payments_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('payment-documents.xlsx') or path.endswith('payments.xlsx'):
        from app.modules.exports.service import export_payments_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_payments_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('payment-allocations.csv'):
        from app.modules.exports.service import export_payment_allocations_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_payment_allocations_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('payment-allocations.xlsx'):
        from app.modules.exports.service import export_payment_allocations_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_payment_allocations_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('custody.csv'):
        from app.modules.exports.service import export_custody_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_custody_csv(db, user, branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('custody.xlsx'):
        from app.modules.exports.service import export_custody_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_custody_xlsx(db, user, branch_id, **params)
        return _xlsx_response(filename, content)

    elif path.endswith('advanced-bi.csv'):
        from app.modules.exports.service import export_advanced_bi_csv
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_advanced_bi_csv(db, user, branch_id=branch_id, **params)
        return _csv_response(filename, content)

    elif path.endswith('advanced-bi.xlsx'):
        from app.modules.exports.service import export_advanced_bi_xlsx
        from app.modules.identity.service import get_user_or_404
        user = get_user_or_404(db, user_id)
        branch_id = params.get('branch_id')
        filename, content = export_advanced_bi_xlsx(db, user, branch_id=branch_id, **params)
        return _xlsx_response(filename, content)

    from fastapi import HTTPException
    raise HTTPException(status_code=400, detail="Unsupported export path in ticket")


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


@router.get('/advanced-bi.csv')
def download_advanced_bi_export_csv(
    request: Request,
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
):
    from app.modules.exports.service import export_advanced_bi_csv
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_advanced_bi_csv(
        db,
        current_user,
        branch_id=branch.id,
        date_from=date_from,
        date_to=date_to,
    )
    return _csv_response(filename, content)


@router.get('/advanced-bi.xlsx')
def download_advanced_bi_export_xlsx(
    request: Request,
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view),
):
    from app.modules.exports.service import export_advanced_bi_xlsx
    branch = resolve_branch_scope(db, request.session, branch_id)
    filename, content = export_advanced_bi_xlsx(
        db,
        current_user,
        branch_id=branch.id,
        date_from=date_from,
        date_to=date_to,
    )
    return _xlsx_response(filename, content)


def _csv_response(filename: str, content: str) -> Response:
    # RFC 6266 compliant Content-Disposition
    ascii_filename = filename.encode('ascii', 'ignore').decode('ascii') or 'download.csv'
    encoded_filename = quote(filename)
    disposition = f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    headers = {
        'Content-Disposition': disposition,
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    return Response(content=content, media_type='text/csv; charset=utf-8', headers=headers)


def _pdf_response(filename: str, content: bytes) -> Response:
    ascii_filename = filename.encode('ascii', 'ignore').decode('ascii') or 'download.pdf'
    encoded_filename = quote(filename)
    disposition = f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    headers = {
        'Content-Disposition': disposition,
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    return Response(content=content, media_type='application/pdf', headers=headers)


def _xlsx_response(filename: str, content: bytes) -> Response:
    ascii_filename = filename.encode('ascii', 'ignore').decode('ascii') or 'download.xlsx'
    encoded_filename = quote(filename)
    # Ensure quotes around filename for compatibility with filenames containing spaces
    disposition = f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    headers = {
        'Content-Disposition': disposition,
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    return Response(content=content, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)
