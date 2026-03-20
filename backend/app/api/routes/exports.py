from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import require_exports_manage, require_exports_view
from app.db.session import get_db
from app.modules.exports.schemas import ExportScheduleCreateRequest, ExportScheduleResponse, ExportScheduleRunResponse, ExportScheduleToggleResponse
from app.modules.exports.schedule_service import create_export_schedule, list_export_schedules, run_export_schedule, toggle_export_schedule
from app.modules.exports.service import export_booking_lines_csv, export_bookings_csv, export_customers_csv, export_payment_allocations_csv, export_payments_csv
from app.modules.identity.models import User

router = APIRouter(prefix='/exports', tags=['exports'])


@router.get('/customers.csv')
def download_customers_export(db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_customers_csv(db, current_user)
    return _csv_response(filename, content)


@router.get('/bookings.csv')
def download_bookings_export(request: Request, branch_id: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_bookings_csv(db, current_user, request.session, branch_id)
    return _csv_response(filename, content)


@router.get('/booking-lines.csv')
def download_booking_lines_export(request: Request, branch_id: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_booking_lines_csv(db, current_user, request.session, branch_id)
    return _csv_response(filename, content)


@router.get('/payments.csv')
@router.get('/payment-documents.csv')
def download_payments_export(request: Request, branch_id: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_payments_csv(db, current_user, request.session, branch_id)
    return _csv_response(filename, content)


@router.get('/payment-allocations.csv')
def download_payment_allocations_export(request: Request, branch_id: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_exports_view)) -> Response:
    filename, content = export_payment_allocations_csv(db, current_user, request.session, branch_id)
    return _csv_response(filename, content)


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


def _csv_response(filename: str, content: str) -> Response:
    disposition = f'attachment; filename="{filename}"'
    return Response(content=content, media_type='text/csv; charset=utf-8', headers={'Content-Disposition': disposition})
