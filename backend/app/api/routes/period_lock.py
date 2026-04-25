from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_period_lock_manage, require_settings_manage
from app.db.session import get_db
from app.modules.core_platform.period_lock import get_period_lock_state, list_period_lock_exceptions, update_period_lock_state
from app.modules.core_platform.schemas import PeriodLockExceptionResponse, PeriodLockResponse, PeriodLockUpdateRequest
from app.modules.identity.models import User

router = APIRouter(prefix="/settings/period-lock", tags=["settings"])


@router.get("", response_model=PeriodLockResponse)
def get_period_lock_route(
    _: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> PeriodLockResponse:
    return PeriodLockResponse.model_validate(get_period_lock_state(db))


@router.put("", response_model=PeriodLockResponse)
def update_period_lock_route(
    payload: PeriodLockUpdateRequest,
    current_user: User = Depends(require_period_lock_manage),
    db: Session = Depends(get_db),
) -> PeriodLockResponse:
    return PeriodLockResponse.model_validate(
        update_period_lock_state(
            db,
            actor=current_user,
            locked_through=payload.locked_through,
            note=payload.note,
        )
    )


@router.get("/exceptions", response_model=list[PeriodLockExceptionResponse])
def list_period_lock_exceptions_route(
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_period_lock_manage),
    db: Session = Depends(get_db),
) -> list[PeriodLockExceptionResponse]:
    rows = list_period_lock_exceptions(db, limit=limit)
    return [PeriodLockExceptionResponse.model_validate(item) for item in rows]
