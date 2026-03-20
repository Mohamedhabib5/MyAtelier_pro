from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from urllib.parse import quote

from sqlalchemy.orm import Session

from app.core.enums import ExportCadenceKey, ExportTypeKey
from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.core_platform.service import record_audit
from app.modules.exports.models import ExportSchedule
from app.modules.exports.repository import ExportSchedulesRepository
from app.modules.exports.schemas import ExportScheduleCreateRequest
from app.modules.identity.models import User
from app.modules.organization.branch_context import ensure_active_branch
from app.modules.organization.service import get_company_settings

BRANCH_SCOPED_EXPORTS = {ExportTypeKey.BOOKINGS_CSV.value, ExportTypeKey.BOOKING_LINES_CSV.value, ExportTypeKey.PAYMENTS_CSV.value, ExportTypeKey.PAYMENT_ALLOCATIONS_CSV.value, ExportTypeKey.FINANCE_PRINT.value, ExportTypeKey.REPORTS_PRINT.value}
VALID_EXPORT_TYPES = {item.value for item in ExportTypeKey}
VALID_CADENCES = {item.value for item in ExportCadenceKey}


def list_export_schedules(db: Session) -> list[dict]:
    company = get_company_settings(db)
    rows = ExportSchedulesRepository(db).list_schedules(company.id)
    return [_serialize_schedule(row) for row in rows]


def create_export_schedule(db: Session, actor: User, payload: ExportScheduleCreateRequest, session: dict) -> dict:
    company = get_company_settings(db)
    export_type = _clean_export_type(payload.export_type)
    cadence = _clean_cadence(payload.cadence)
    branch = ensure_active_branch(db, session) if export_type in BRANCH_SCOPED_EXPORTS else None
    schedule = ExportSchedule(company_id=company.id, branch_id=branch.id if branch else None, name=norm_text(payload.name), export_type=export_type, cadence=cadence, next_run_on=_parse_start_on(payload.start_on), is_active=True)
    repo = ExportSchedulesRepository(db)
    repo.add_schedule(schedule)
    db.flush()
    record_audit(db, actor_user_id=actor.id, action='export.schedule_created', target_type='export_schedule', target_id=schedule.id, summary=f'Created export schedule {schedule.name}', diff={'export_type': schedule.export_type, 'cadence': schedule.cadence, 'branch_id': schedule.branch_id})
    db.commit()
    return _load_schedule_or_404(repo, schedule.id)


def toggle_export_schedule(db: Session, actor: User, schedule_id: str) -> dict:
    schedule = _get_company_schedule(db, schedule_id)
    schedule.is_active = not schedule.is_active
    record_audit(db, actor_user_id=actor.id, action='export.schedule_toggled', target_type='export_schedule', target_id=schedule.id, summary=f'Toggled export schedule {schedule.name}', diff={'is_active': schedule.is_active})
    db.commit()
    return _serialize_schedule(schedule)


def run_export_schedule(db: Session, actor: User, schedule_id: str) -> dict:
    schedule = _get_company_schedule(db, schedule_id)
    if not schedule.is_active:
        raise ValidationAppError('لا يمكن تشغيل الجداول غير النشطة')
    schedule.last_run_at = datetime.now(UTC)
    schedule.next_run_on = _advance_next_run(schedule.next_run_on, schedule.cadence)
    run_url = _build_run_url(schedule)
    record_audit(db, actor_user_id=actor.id, action='export.schedule_run', target_type='export_schedule', target_id=schedule.id, summary=f'Ran export schedule {schedule.name}', diff={'run_url': run_url, 'next_run_on': schedule.next_run_on.isoformat()})
    db.commit()
    return {'schedule': _serialize_schedule(schedule), 'run_url': run_url}


def _get_company_schedule(db: Session, schedule_id: str) -> ExportSchedule:
    company = get_company_settings(db)
    repo = ExportSchedulesRepository(db)
    schedule = repo.get_schedule(schedule_id)
    if schedule is None or schedule.company_id != company.id:
        raise NotFoundError('لم يتم العثور على جدول التصدير')
    return schedule


def _load_schedule_or_404(repo: ExportSchedulesRepository, schedule_id: str) -> dict:
    schedule = repo.get_schedule(schedule_id)
    if schedule is None:
        raise NotFoundError('لم يتم العثور على جدول التصدير')
    return _serialize_schedule(schedule)


def _serialize_schedule(schedule: ExportSchedule) -> dict:
    return {'id': schedule.id, 'name': schedule.name, 'export_type': schedule.export_type, 'cadence': schedule.cadence, 'branch_id': schedule.branch_id, 'branch_name': schedule.branch.name if schedule.branch else None, 'next_run_on': schedule.next_run_on.isoformat(), 'last_run_at': schedule.last_run_at.isoformat() if schedule.last_run_at else None, 'is_active': schedule.is_active}


def _build_run_url(schedule: ExportSchedule) -> str:
    if schedule.export_type == ExportTypeKey.CUSTOMERS_CSV.value:
        return '/api/exports/customers.csv'
    if schedule.export_type == ExportTypeKey.BOOKINGS_CSV.value:
        return f'/api/exports/bookings.csv?branch_id={schedule.branch_id}'
    if schedule.export_type == ExportTypeKey.BOOKING_LINES_CSV.value:
        return f'/api/exports/booking-lines.csv?branch_id={schedule.branch_id}'
    if schedule.export_type == ExportTypeKey.PAYMENTS_CSV.value:
        return f'/api/exports/payment-documents.csv?branch_id={schedule.branch_id}'
    if schedule.export_type == ExportTypeKey.PAYMENT_ALLOCATIONS_CSV.value:
        return f'/api/exports/payment-allocations.csv?branch_id={schedule.branch_id}'
    if schedule.export_type == ExportTypeKey.FINANCE_PRINT.value:
        return _print_url('/print/finance', schedule)
    if schedule.export_type == ExportTypeKey.REPORTS_PRINT.value:
        return _print_url('/print/reports', schedule)
    raise ValidationAppError('نوع التصدير غير مدعوم')


def _print_url(base_url: str, schedule: ExportSchedule) -> str:
    branch_name = quote(schedule.branch.name) if schedule.branch else ''
    return f'{base_url}?branchId={schedule.branch_id}&branchName={branch_name}'


def _clean_export_type(value: str) -> str:
    export_type = norm_text(value).lower()
    if export_type not in VALID_EXPORT_TYPES:
        raise ValidationAppError('نوع التصدير غير صالح')
    return export_type


def _clean_cadence(value: str) -> str:
    cadence = norm_text(value).lower()
    if cadence not in VALID_CADENCES:
        raise ValidationAppError('التكرار غير صالح')
    return cadence


def _parse_start_on(value: str | None) -> date:
    if not value:
        return date.today()
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationAppError('تاريخ بدء الجدول غير صالح') from exc


def _advance_next_run(current: date, cadence: str) -> date:
    if cadence == ExportCadenceKey.DAILY.value:
        return current + timedelta(days=1)
    return current + timedelta(days=7)
