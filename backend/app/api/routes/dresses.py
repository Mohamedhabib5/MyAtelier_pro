from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_dresses_manage, require_dresses_view
from app.db.session import get_db
from app.modules.dresses.schemas import DressArchiveRequest, DressCreateRequest, DressResponse, DressUpdateRequest
from app.modules.dresses.service import archive_dress, create_dress, list_dresses, restore_dress, update_dress
from app.modules.identity.models import User

router = APIRouter(prefix="/dresses", tags=["dresses"])


@router.get("", response_model=list[DressResponse])
def list_dresses_route(
    status_filter: Literal["all", "active", "inactive"] = Query(default="all", alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_dresses_view),
) -> list[DressResponse]:
    is_active = None if status_filter == "all" else status_filter == "active"
    return [DressResponse.model_validate(item) for item in list_dresses(db, is_active=is_active)]


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
