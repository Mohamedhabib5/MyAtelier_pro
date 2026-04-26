from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Request
from sqlalchemy.orm import Session

from app.api.deps import require_dresses_manage, require_dresses_view
from app.db.session import get_db
from app.modules.dresses.schemas import DressArchiveRequest, DressCreateRequest, DressResponse, DressUpdateRequest
from app.modules.dresses.service import archive_dress, create_dress, list_dresses, restore_dress, update_dress
from app.modules.identity.models import User
import shutil
import os
from pathlib import Path
from app.modules.core_platform.service import record_audit
from app.core.exceptions import ValidationAppError

router = APIRouter(prefix="/dresses", tags=["dresses"])


@router.get("", response_model=list[DressResponse])
def list_dresses_route(
    status_filter: Literal["all", "active", "inactive"] = Query(default="all", alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_dresses_view),
) -> list[DressResponse]:
    is_active = None if status_filter == "all" else status_filter == "active"
    return [DressResponse.model_validate(item) for item in list_dresses(db, is_active=is_active)]


@router.get("/{dress_id}", response_model=DressResponse)
def get_dress_route(
    dress_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_dresses_view),
) -> DressResponse:
    from app.modules.dresses.service import _get_company_dress_or_404, _serialize_dress, DressesRepository
    repo = DressesRepository(db)
    dress = _get_company_dress_or_404(db, repo, dress_id)
    return DressResponse.model_validate(_serialize_dress(dress))


@router.post("", response_model=DressResponse, status_code=status.HTTP_201_CREATED)
def create_dress_route(
    payload: DressCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dresses_manage),
) -> DressResponse:
    return DressResponse.model_validate(create_dress(db, current_user, payload))


@router.patch("/{dress_id}", response_model=DressResponse)
def update_dress_route(
    dress_id: str,
    payload: DressUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dresses_manage),
) -> DressResponse:
    return DressResponse.model_validate(update_dress(db, current_user, dress_id, payload))


@router.post("/{dress_id}/archive", response_model=DressResponse)
def archive_dress_route(
    dress_id: str,
    payload: DressArchiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dresses_manage),
) -> DressResponse:
    return DressResponse.model_validate(archive_dress(db, current_user, dress_id, payload.reason))


@router.post("/{dress_id}/restore", response_model=DressResponse)
def restore_dress_route(
    dress_id: str,
    payload: DressArchiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dresses_manage),
) -> DressResponse:
    return DressResponse.model_validate(restore_dress(db, current_user, dress_id, payload.reason))


@router.post("/upload")
async def upload_dress_image_route(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dresses_manage),
) -> dict:
    settings = request.app.state.settings
    
    # Validate file size
    file_size = 0
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.max_image_size_bytes:
        raise ValidationAppError(f"حجم الملف كبير جداً. الحد الأقصى هو {settings.max_image_size_bytes // 1024} كيلوبايت")
    
    # Validate file type using magic bytes
    header = file.file.read(8)
    file.file.seek(0)
    
    is_valid_image = False
    if header.startswith(b'\xff\xd8\xff'):  # JPEG
        is_valid_image = True
    elif header.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
        is_valid_image = True
    elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):  # GIF
        is_valid_image = True
    elif header.startswith(b'RIFF') and header[8:12] == b'WEBP':  # WEBP
        is_valid_image = True
        
    if not is_valid_image:
        raise ValidationAppError("الملف المرفوع ليس صورة صالحة (JPEG, PNG, GIF, WEBP فقط)")
        
    # Ensure directory exists
    upload_dir = Path(settings.attachment_storage_dir) / "dresses"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename with sanitized extension
    import uuid
    import re
    original_ext = Path(file.filename).suffix.lower()
    if original_ext not in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
        raise ValidationAppError("امتداد الملف غير مسموح به")
        
    filename = f"{uuid.uuid4()}{original_ext}"
    file_path = upload_dir / filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="dress.image_uploaded",
        target_type="attachment",
        target_id=filename,
        summary=f"Uploaded dress image {file.filename}",
        diff={"content_type": file.content_type, "size_bytes": file_size, "path": f"dresses/{filename}"}
    )
    
    return {"image_path": f"dresses/{filename}"}
