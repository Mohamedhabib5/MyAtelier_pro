from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import require_payments_view
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.payments.schemas import PaymentTargetDetailResponse, PaymentTargetSearchResult
from app.modules.payments.target_service import get_booking_payment_target, get_customer_payment_target, search_payment_targets

router = APIRouter(prefix='/payment-targets', tags=['payment-targets'])


@router.get('/search', response_model=list[PaymentTargetSearchResult])
def search_payment_targets_route(
    request: Request,
    q: str = Query(default=''),
    db: Session = Depends(get_db),
    _: User = Depends(require_payments_view),
) -> list[PaymentTargetSearchResult]:
    return [PaymentTargetSearchResult.model_validate(item) for item in search_payment_targets(db, request.session, q)]


@router.get('/customer/{customer_id}', response_model=PaymentTargetDetailResponse)
def get_customer_payment_target_route(
    customer_id: str,
    request: Request,
    ignore_payment_document_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_payments_view),
) -> PaymentTargetDetailResponse:
    return PaymentTargetDetailResponse.model_validate(
        get_customer_payment_target(db, request.session, customer_id, ignore_payment_document_id=ignore_payment_document_id),
    )


@router.get('/booking/{booking_id}', response_model=PaymentTargetDetailResponse)
def get_booking_payment_target_route(
    booking_id: str,
    request: Request,
    ignore_payment_document_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_payments_view),
) -> PaymentTargetDetailResponse:
    return PaymentTargetDetailResponse.model_validate(
        get_booking_payment_target(db, request.session, booking_id, ignore_payment_document_id=ignore_payment_document_id),
    )
