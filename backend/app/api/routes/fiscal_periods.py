from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import require_settings_manage
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.organization.schemas import (
    FiscalPeriodCreateRequest,
    FiscalPeriodResponse,
    FiscalPeriodUpdateRequest,
)
from app.modules.organization.service import (
    create_fiscal_period,
    delete_fiscal_period,
    list_fiscal_periods,
    update_fiscal_period,
)

router = APIRouter(prefix='/settings/fiscal-periods', tags=['settings'])


@router.get('', response_model=list[FiscalPeriodResponse])
def list_fiscal_periods_route(
    db: Session = Depends(get_db),
    _: User = Depends(require_settings_manage),
) -> list[FiscalPeriodResponse]:
    return [FiscalPeriodResponse.model_validate(item) for item in list_fiscal_periods(db)]


@router.post('', response_model=FiscalPeriodResponse)
def create_fiscal_period_route(
    payload: FiscalPeriodCreateRequest,
    current_user: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> FiscalPeriodResponse:
    period = create_fiscal_period(db, payload, current_user.id)
    return FiscalPeriodResponse.model_validate(period)


@router.patch('/{period_id}', response_model=FiscalPeriodResponse)
def update_fiscal_period_route(
    period_id: str,
    payload: FiscalPeriodUpdateRequest,
    current_user: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> FiscalPeriodResponse:
    period = update_fiscal_period(db, period_id, payload, current_user.id)
    return FiscalPeriodResponse.model_validate(period)


@router.delete('/{period_id}')
def delete_fiscal_period_route(
    period_id: str,
    current_user: User = Depends(require_settings_manage),
    db: Session = Depends(get_db),
) -> Response:
    delete_fiscal_period(db, period_id, current_user.id)
    return Response(status_code=204)
