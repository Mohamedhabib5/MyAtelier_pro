from __future__ import annotations

from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.api.deps import require_admin
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.ops import backup_service
from app.modules.core_platform.service import record_audit
from app.core.exceptions import ValidationAppError
from sqlalchemy.orm import Session

router = APIRouter(prefix='/ops', tags=['operations'])

class BackupInfo(BaseModel):
    id: str
    filename: str
    size_bytes: int
    created_at: str
    kind: str

@router.get('/backups', response_model=list[BackupInfo])
def list_backups_route(_: User = Depends(require_admin)) -> list[BackupInfo]:
    return [BackupInfo.model_validate(b) for b in backup_service.list_backups()]

@router.post('/backups/db', response_model=BackupInfo, status_code=status.HTTP_201_CREATED)
def create_db_backup_route(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> BackupInfo:
    backup = backup_service.create_db_backup()
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="ops.backup_db",
        target_type="backup",
        target_id=backup.id,
        summary=f"Created database backup: {backup.filename}"
    )
    return BackupInfo.model_validate(backup)

@router.post('/backups/media', response_model=BackupInfo, status_code=status.HTTP_201_CREATED)
def create_media_backup_route(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> BackupInfo:
    backup = backup_service.create_media_backup()
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="ops.backup_media",
        target_type="backup",
        target_id=backup.id,
        summary=f"Created media backup: {backup.filename}"
    )
    return BackupInfo.model_validate(backup)

@router.post('/backups/full', response_model=BackupInfo, status_code=status.HTTP_201_CREATED)
def create_full_backup_route(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> BackupInfo:
    backup = backup_service.create_full_backup()
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="ops.backup_full",
        target_type="backup",
        target_id=backup.id,
        summary=f"Created full backup: {backup.filename}"
    )
    return BackupInfo.model_validate(backup)

@router.delete('/backups/{filename}')
def delete_backup_route(
    filename: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> None:
    backup_service.delete_backup(filename)
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="ops.backup_deleted",
        target_type="backup",
        target_id=filename,
        summary=f"Deleted backup file: {filename}"
    )

@router.get('/backups/{filename}/download')
def download_backup_route(filename: str, _: User = Depends(require_admin)) -> FileResponse:
    path = backup_service.BACKUP_DIR / filename
    if not path.exists() or path.parent != backup_service.BACKUP_DIR:
        raise ValidationAppError("الملف غير موجود")
    
    return FileResponse(
        path,
        media_type='application/octet-stream',
        filename=filename
    )
