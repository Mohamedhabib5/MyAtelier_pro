from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import require_settings_manage
from app.db.session import get_db
from app.modules.core_platform.schemas import BackupRecordResponse
from app.modules.core_platform.service import create_backup, get_backup_or_404, list_backups, record_backup_download, resolve_backup_download_path
from app.modules.identity.models import User
from app.modules.organization.branch_context import ensure_active_branch, set_active_branch
from app.modules.organization.schemas import ActiveBranchResponse, BranchCreateRequest, BranchResponse, CompanyResponse, SetActiveBranchRequest, UpdateCompanyRequest
from app.modules.organization.service import create_branch, get_company_settings, update_company_settings

router = APIRouter(prefix='/settings', tags=['settings'])


@router.get('/company', response_model=CompanyResponse)
def get_company(db: Session = Depends(get_db), _: User = Depends(require_settings_manage)) -> CompanyResponse:
    return CompanyResponse.model_validate(get_company_settings(db))


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
    _: User = Depends(require_settings_manage),
) -> ActiveBranchResponse:
    branch = set_active_branch(db, request.session, payload.branch_id)
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
