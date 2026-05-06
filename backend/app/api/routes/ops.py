from __future__ import annotations

from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.api.deps import require_admin
from app.modules.identity.models import User
from app.modules.ops import backup_service
from app.core.exceptions import ValidationAppError

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
def create_db_backup_route(_: User = Depends(require_admin)) -> BackupInfo:
    return BackupInfo.model_validate(backup_service.create_db_backup())

@router.post('/backups/media', response_model=BackupInfo, status_code=status.HTTP_201_CREATED)
def create_media_backup_route(_: User = Depends(require_admin)) -> BackupInfo:
    return BackupInfo.model_validate(backup_service.create_media_backup())

@router.post('/backups/full', response_model=BackupInfo, status_code=status.HTTP_201_CREATED)
def create_full_backup_route(_: User = Depends(require_admin)) -> BackupInfo:
    return BackupInfo.model_validate(backup_service.create_full_backup())

@router.delete('/backups/{filename}')
def delete_backup_route(filename: str, _: User = Depends(require_admin)) -> None:
    backup_service.delete_backup(filename)

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
