from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_settings_manage
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.payments.payment_methods import create_payment_method, list_payment_methods, update_payment_method
from app.modules.payments.schemas import PaymentMethodCreateRequest, PaymentMethodResponse, PaymentMethodUpdateRequest

router = APIRouter(prefix="/payment-methods", tags=["payment-methods"])


@router.get("", response_model=list[PaymentMethodResponse])
def list_payment_methods_route(
    status_filter: str = Query(default="active", alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PaymentMethodResponse]:
    return [
        PaymentMethodResponse.model_validate(item)
        for item in list_payment_methods(db, status=status_filter)
    ]


@router.post("", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
def create_payment_method_route(
    payload: PaymentMethodCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_settings_manage),
) -> PaymentMethodResponse:
    return PaymentMethodResponse.model_validate(create_payment_method(db, current_user, payload))


@router.patch("/{payment_method_id}", response_model=PaymentMethodResponse)
def update_payment_method_route(
    payment_method_id: str,
    payload: PaymentMethodUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_settings_manage),
) -> PaymentMethodResponse:
    return PaymentMethodResponse.model_validate(update_payment_method(db, current_user, payment_method_id, payload))
