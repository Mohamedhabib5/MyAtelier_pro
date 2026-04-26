from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import require_destructive_manage, require_settings_manage
from app.db.session import get_db
from app.modules.core_platform.schemas import BackupRecordResponse, DestructiveDeleteRequest, DestructiveDeleteResponse, DestructivePreviewRequest, DestructivePreviewResponse, DestructiveReasonResponse, OpsAlertResponse, OpsAlertTestRequest, OpsBackupAlertRunRequest, OpsBackupAlertRunResponse, OpsMetricsResponse
from app.modules.core_platform.automation_audit import record_automation_job_run
from app.modules.core_platform.destructive_delete import execute_destructive_delete
from app.modules.core_platform.destructive_preview import preview_destructive_action
from app.modules.core_platform.service import collect_ops_metrics, create_backup, get_backup_or_404, list_backups, list_destructive_reasons, record_audit, record_backup_download, resolve_backup_download_path, run_backup_stale_alert_check, send_ops_webhook_alert
from app.modules.identity.models import User
from app.modules.organization.branch_context import ensure_active_branch, set_active_branch
from app.modules.organization.schemas import (
    ActiveBranchResponse,
    BranchCreateRequest,
    BranchResponse,
    CompanyResponse,
    SetActiveBranchRequest,
    UpdateCompanyRequest,
)
from app.modules.organization.service import (
    create_branch,
    get_company_settings,
    update_company_settings,
)

router = APIRouter(prefix='/settings', tags=['settings'])


@router.get('/company', response_model=CompanyResponse)
def get_company(db: Session = Depends(get_db), _: User = Depends(require_settings_manage)) -> CompanyResponse:
    return CompanyResponse.model_validate(get_company_settings(db))


@router.get('/destructive-reasons', response_model=list[DestructiveReasonResponse])
def list_destructive_reasons_route(
    action: str | None = Query(default=None),
    _: User = Depends(require_destructive_manage),
) -> list[DestructiveReasonResponse]:
    return [DestructiveReasonResponse.model_validate(item) for item in list_destructive_reasons(action)]


@router.post('/destructive-preview', response_model=DestructivePreviewResponse)
def destructive_preview_route(
    payload: DestructivePreviewRequest,
    current_user: User = Depends(require_destructive_manage),
    db: Session = Depends(get_db),
) -> DestructivePreviewResponse:
    preview = preview_destructive_action(
        db,
        actor=current_user,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        reason_code=payload.reason_code,
        reason_text=payload.reason_text,
    )
    return DestructivePreviewResponse.model_validate(preview)


@router.post('/destructive-delete', response_model=DestructiveDeleteResponse)
def destructive_delete_route(
    payload: DestructiveDeleteRequest,
    current_user: User = Depends(require_destructive_manage),
    db: Session = Depends(get_db),
) -> DestructiveDeleteResponse:
    deleted = execute_destructive_delete(
        db,
        actor=current_user,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        reason_code=payload.reason_code,
        reason_text=payload.reason_text,
        override_lock=payload.override_lock,
        override_reason=payload.override_reason,
    )
    return DestructiveDeleteResponse.model_validate(deleted)


@router.patch('/company', response_model=CompanyResponse)
def update_company(
    payload: UpdateCompanyRequest,
    current_user: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> CompanyResponse:
    company = update_company_settings(db, payload, current_user.id)
    return CompanyResponse.model_validate(company)


@router.post('/branches', response_model=BranchResponse)
def create_branch_route(
    payload: BranchCreateRequest,
    current_user: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> BranchResponse:
    branch = create_branch(db, payload, current_user.id)
    return BranchResponse.model_validate(branch)


@router.get('/branches/active', response_model=ActiveBranchResponse)
def get_active_branch_route(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_settings_manage),
) -> ActiveBranchResponse:
    branch = ensure_active_branch(db, request.session)
    return ActiveBranchResponse.model_validate(branch)


@router.post('/branches/active', response_model=ActiveBranchResponse)
def set_active_branch_route(
    payload: SetActiveBranchRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_settings_manage),
) -> ActiveBranchResponse:
    previous_branch_id = request.session.get('active_branch_id')
    branch = set_active_branch(db, request.session, payload.branch_id)
    record_audit(
        db,
        actor_user_id=current_user.id,
        action='branch.active_switched',
        target_type='branch',
        target_id=branch.id,
        summary=f'Switched active branch to {branch.name}',
        diff={'previous_branch_id': previous_branch_id, 'next_branch_id': branch.id},
    )
    db.commit()
    return ActiveBranchResponse.model_validate(branch)


@router.post('/backups', response_model=BackupRecordResponse)
def create_backup_route(
    request: Request,
    current_user: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> BackupRecordResponse:
    settings_obj = request.app.state.settings
    company = get_company_settings(db)
    backup_record = create_backup(
        db,
        backup_dir=Path(settings_obj.backup_storage_dir),
        attachment_dir=Path(settings_obj.attachment_storage_dir),
        database_url=settings_obj.database_url,
        created_by_user_id=current_user.id,
        company_name=company.name,
    )
    return BackupRecordResponse.model_validate(backup_record)


@router.get('/backups', response_model=list[BackupRecordResponse])
def list_backups_route(
    db: Session = Depends(get_db),
    _: User = Depends(require_settings_manage),
) -> list[BackupRecordResponse]:
    return [BackupRecordResponse.model_validate(item) for item in list_backups(db)]


@router.get('/backups/{backup_id}/download')
def download_backup(
    backup_id: str,
    request: Request,
    current_user: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> FileResponse:
    backup_record = get_backup_or_404(db, backup_id)
    settings_obj = request.app.state.settings
    resolved_path = resolve_backup_download_path(Path(settings_obj.backup_storage_dir), backup_record)
    record_backup_download(db, actor_user_id=current_user.id, backup_record=backup_record)
    return FileResponse(path=resolved_path, filename=backup_record.filename, media_type='application/zip')


@router.get('/ops/metrics', response_model=OpsMetricsResponse)
def get_ops_metrics(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_settings_manage),
) -> OpsMetricsResponse:
    settings_obj = request.app.state.settings
    payload = collect_ops_metrics(db, backup_stale_threshold_hours=settings_obj.ops_backup_stale_threshold_hours)
    return OpsMetricsResponse.model_validate(payload)


@router.post('/ops/alerts/test', response_model=OpsAlertResponse)
def send_test_ops_alert(
    payload: OpsAlertTestRequest,
    request: Request,
    current_user: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> OpsAlertResponse:
    settings_obj = request.app.state.settings
    sent, detail = send_ops_webhook_alert(
        webhook_url=settings_obj.ops_alert_webhook_url,
        severity=payload.severity.upper(),
        message=payload.message,
        dry_run=payload.dry_run,
    )
    record_audit(
        db,
        actor_user_id=current_user.id,
        action='ops.alert_test',
        target_type='ops_alert',
        target_id=None,
        summary='Triggered operations alert test',
        diff={'severity': payload.severity.upper(), 'dry_run': payload.dry_run, 'sent': sent, 'detail': detail},
    )
    db.commit()
    return OpsAlertResponse(sent=sent, channel='webhook', detail=detail)


@router.post('/ops/alerts/run-backup-check', response_model=OpsBackupAlertRunResponse)
def run_backup_stale_check_alert(
    payload: OpsBackupAlertRunRequest,
    request: Request,
    current_user: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> OpsBackupAlertRunResponse:
    settings_obj = request.app.state.settings
    result = run_backup_stale_alert_check(
        db,
        backup_stale_threshold_hours=settings_obj.ops_backup_stale_threshold_hours,
        webhook_url=settings_obj.ops_alert_webhook_url,
        dry_run=payload.dry_run,
        force=payload.force,
    )
    run_success = (not result["stale"]) or result["sent"] or payload.dry_run
    record_automation_job_run(
        db,
        actor_user_id=current_user.id,
        job_key="ops.backup_stale_check",
        summary="Ran backup stale alert check",
        trigger_source=payload.trigger_source,
        success=run_success,
        diff={
            'dry_run': payload.dry_run,
            'force': payload.force,
            'stale': result['stale'],
            'sent': result['sent'],
            'severity': result['severity'],
            'detail': result['detail'],
            'backup_age_hours': result['backup_age_hours'],
        },
    )
    db.commit()
    return OpsBackupAlertRunResponse.model_validate(result)
