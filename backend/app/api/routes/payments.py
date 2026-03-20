from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_payments_manage, require_payments_view
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.payments.schemas import PaymentDocumentCreateRequest, PaymentDocumentResponse, PaymentDocumentSummaryResponse, PaymentDocumentUpdateRequest, PaymentVoidRequest
from app.modules.payments.service import create_payment, get_payment_document, list_payments, update_payment, void_payment

router = APIRouter(prefix='/payments', tags=['payments'])


@router.get('', response_model=list[PaymentDocumentSummaryResponse])
def list_payments_route(request: Request, db: Session = Depends(get_db), _: User = Depends(require_payments_view)) -> list[PaymentDocumentSummaryResponse]:
    return [PaymentDocumentSummaryResponse.model_validate(item) for item in list_payments(db, request.session)]


@router.get('/{payment_document_id}', response_model=PaymentDocumentResponse)
def get_payment_route(payment_document_id: str, request: Request, db: Session = Depends(get_db), _: User = Depends(require_payments_view)) -> PaymentDocumentResponse:
    return PaymentDocumentResponse.model_validate(get_payment_document(db, payment_document_id, request.session))


@router.post('', response_model=PaymentDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_payment_route(payload: PaymentDocumentCreateRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_payments_manage)) -> PaymentDocumentResponse:
    return PaymentDocumentResponse.model_validate(create_payment(db, current_user, payload, request.session))


@router.patch('/{payment_document_id}', response_model=PaymentDocumentResponse)
def update_payment_route(payment_document_id: str, payload: PaymentDocumentUpdateRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_payments_manage)) -> PaymentDocumentResponse:
    return PaymentDocumentResponse.model_validate(update_payment(db, current_user, payment_document_id, payload, request.session))


@router.post('/{payment_document_id}/void', response_model=PaymentDocumentResponse)
def void_payment_route(payment_document_id: str, payload: PaymentVoidRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_payments_manage)) -> PaymentDocumentResponse:
    return PaymentDocumentResponse.model_validate(void_payment(db, current_user, payment_document_id, payload, request.session))
