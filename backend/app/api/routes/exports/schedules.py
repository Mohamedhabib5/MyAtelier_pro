from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import require_exports_manage, require_exports_view
from app.db.session import get_db
from app.modules.exports.schemas import (
    ExportScheduleCreateRequest,
    ExportScheduleResponse,
    ExportScheduleRunDueRequest,
    ExportScheduleRunDueResponse,
    ExportScheduleRunResponse,
    ExportScheduleToggleResponse,
    DailyEmailReportConfigResponse,
    DailyEmailReportConfigCreateRequest,
    DailyEmailReportConfigUpdateRequest,
)
from app.modules.exports.schedule_service import (
    create_export_schedule,
    list_export_schedules,
    run_due_export_schedules,
    run_export_schedule,
    toggle_export_schedule,
)
from app.modules.identity.models import User

router = APIRouter()

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


@router.post('/schedules/run-due-reports')
def run_due_reports_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_manage),
) -> dict:
    from app.modules.exports.daily_report_service import check_and_run_due_reports
    from app.modules.core_platform.automation_audit import record_automation_job_run
    
    res = check_and_run_due_reports(db)
    
    record_automation_job_run(
        db,
        actor_user_id=current_user.id,
        job_key="exports.daily_email_reports_dispatch",
        summary="Dispatched daily email reports to active configs",
        trigger_source="manual",
        success=bool(res.get("failed_date") is None),
        diff=res
    )
    return res


def _mask_config_password(config) -> DailyEmailReportConfigResponse:
    from app.modules.exports.schemas import DailyEmailReportConfigResponse
    c_dict = {
        "id": config.id,
        "company_id": config.company_id,
        "name": config.name,
        "sender_email": config.sender_email,
        "sender_password": "********",
        "smtp_server": config.smtp_server,
        "smtp_port": config.smtp_port,
        "recipient_email": config.recipient_email,
        "send_hour": config.send_hour,
        "is_active": config.is_active,
        "send_daily_summary": config.send_daily_summary,
        "notify_booking_created": config.notify_booking_created,
        "notify_booking_modified": config.notify_booking_modified,
        "notify_payment_captured": config.notify_payment_captured,
        "notify_payment_refunded": config.notify_payment_refunded,
        "notify_entity_deleted": config.notify_entity_deleted,
        "notify_operations_daily": config.notify_operations_daily,
        "notify_financial_critical": config.notify_financial_critical,
        "notify_backup_warnings": config.notify_backup_warnings,
        "booking_email_template": config.booking_email_template,
        "payment_email_template": config.payment_email_template,
    }
    return DailyEmailReportConfigResponse(**c_dict)


@router.get('/daily-reports', response_model=list[DailyEmailReportConfigResponse])
def list_daily_report_configs_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_view)
) -> list[DailyEmailReportConfigResponse]:
    from app.modules.exports.models import DailyEmailReportConfig
    from app.modules.organization.service import get_company_settings
    company = get_company_settings(db)
    configs = db.query(DailyEmailReportConfig).filter(DailyEmailReportConfig.company_id == company.id).all()
    return [_mask_config_password(c) for c in configs]


@router.post('/daily-reports', response_model=DailyEmailReportConfigResponse)
def create_daily_report_config_route(
    payload: DailyEmailReportConfigCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_manage)
) -> DailyEmailReportConfigResponse:
    from app.modules.exports.models import DailyEmailReportConfig
    from app.modules.organization.service import get_company_settings
    from app.core.security import encrypt_secret
    
    company = get_company_settings(db)
    encrypted_password = encrypt_secret(payload.sender_password)
    
    config = DailyEmailReportConfig(
        company_id=company.id,
        name=payload.name,
        sender_email=payload.sender_email,
        sender_password=encrypted_password,
        smtp_server=payload.smtp_server,
        smtp_port=payload.smtp_port,
        recipient_email=payload.recipient_email,
        send_hour=payload.send_hour,
        is_active=payload.is_active,
        send_daily_summary=payload.send_daily_summary,
        notify_booking_created=payload.notify_booking_created,
        notify_booking_modified=payload.notify_booking_modified,
        notify_payment_captured=payload.notify_payment_captured,
        notify_payment_refunded=payload.notify_payment_refunded,
        notify_entity_deleted=payload.notify_entity_deleted,
        notify_operations_daily=payload.notify_operations_daily,
        notify_financial_critical=payload.notify_financial_critical,
        notify_backup_warnings=payload.notify_backup_warnings,
        booking_email_template=payload.booking_email_template,
        payment_email_template=payload.payment_email_template,
    )
    db.add(config)
    db.flush()
    
    from app.modules.core_platform.audit import record_audit
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="export.daily_report_config_created",
        target_type="daily_email_report_config",
        target_id=config.id,
        summary=f"Created daily email report configuration: {config.name}",
    )
    db.commit()
    db.refresh(config)
    return _mask_config_password(config)


@router.patch('/daily-reports/{config_id}', response_model=DailyEmailReportConfigResponse)
def update_daily_report_config_route(
    config_id: str,
    payload: DailyEmailReportConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_manage)
) -> DailyEmailReportConfigResponse:
    from app.modules.exports.models import DailyEmailReportConfig
    from app.core.security import encrypt_secret
    from app.core.exceptions import NotFoundError
    
    config = db.query(DailyEmailReportConfig).filter(DailyEmailReportConfig.id == config_id).first()
    if not config:
        raise NotFoundError("لم يتم العثور على التكوين البريدي")
        
    if payload.name is not None:
        config.name = payload.name
    if payload.sender_email is not None:
        config.sender_email = payload.sender_email
    if payload.sender_password is not None and payload.sender_password != "********":
        config.sender_password = encrypt_secret(payload.sender_password)
    if payload.smtp_server is not None:
        config.smtp_server = payload.smtp_server
    if payload.smtp_port is not None:
        config.smtp_port = payload.smtp_port
    if payload.recipient_email is not None:
        config.recipient_email = payload.recipient_email
    if payload.send_hour is not None:
        config.send_hour = payload.send_hour
    if payload.is_active is not None:
        config.is_active = payload.is_active
    if payload.send_daily_summary is not None:
        config.send_daily_summary = payload.send_daily_summary
    if payload.notify_booking_created is not None:
        config.notify_booking_created = payload.notify_booking_created
    if payload.notify_booking_modified is not None:
        config.notify_booking_modified = payload.notify_booking_modified
    if payload.notify_payment_captured is not None:
        config.notify_payment_captured = payload.notify_payment_captured
    if payload.notify_payment_refunded is not None:
        config.notify_payment_refunded = payload.notify_payment_refunded
    if payload.notify_entity_deleted is not None:
        config.notify_entity_deleted = payload.notify_entity_deleted
    if payload.notify_operations_daily is not None:
        config.notify_operations_daily = payload.notify_operations_daily
    if payload.notify_financial_critical is not None:
        config.notify_financial_critical = payload.notify_financial_critical
    if payload.notify_backup_warnings is not None:
        config.notify_backup_warnings = payload.notify_backup_warnings
    if payload.booking_email_template is not None:
        config.booking_email_template = payload.booking_email_template
    if payload.payment_email_template is not None:
        config.payment_email_template = payload.payment_email_template
        
    db.flush()
    from app.modules.core_platform.audit import record_audit
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="export.daily_report_config_updated",
        target_type="daily_email_report_config",
        target_id=config.id,
        summary=f"Updated daily email report configuration: {config.name}",
    )
    db.commit()
    db.refresh(config)
    return _mask_config_password(config)


@router.delete('/daily-reports/{config_id}')
def delete_daily_report_config_route(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_manage)
) -> dict:
    from app.modules.exports.models import DailyEmailReportConfig
    from app.core.exceptions import NotFoundError
    
    config = db.query(DailyEmailReportConfig).filter(DailyEmailReportConfig.id == config_id).first()
    if not config:
        raise NotFoundError("لم يتم العثور على التكوين البريدي")
        
    db.delete(config)
    
    from app.modules.core_platform.audit import record_audit
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="export.daily_report_config_deleted",
        target_type="daily_email_report_config",
        target_id=config_id,
        summary=f"Deleted daily email report configuration: {config.name}",
    )
    db.commit()
    return {"success": True}


@router.post('/daily-reports/{config_id}/test')
def test_daily_report_config_route(
    config_id: str,
    report_date: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_exports_manage)
) -> dict:
    from app.modules.organization.service import get_company_settings
    from app.core.exceptions import ValidationAppError
    from datetime import datetime
    
    company = get_company_settings(db)
    
    parsed_date = None
    if report_date:
        try:
            parsed_date = datetime.strptime(report_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationAppError("تنسيق التاريخ غير صحيح، يجب أن يكون YYYY-MM-DD")
            
    from app.modules.core_platform.audit import record_audit
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="export.daily_report_config_test_run",
        target_type="daily_email_report_config",
        target_id=config_id,
        summary="Triggered manual test run of daily email report config",
    )
    from app.modules.exports.daily_report_service import run_test_report_for_config
    return run_test_report_for_config(db, config_id, company.id, parsed_date)
