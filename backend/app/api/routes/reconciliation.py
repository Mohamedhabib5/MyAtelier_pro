from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_active_branch_id, require_reconcile_cash
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.finance.service import reconciliation_service

router = APIRouter(prefix="/reconciliations", tags=["reconciliations"])


class ReconciliationItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    payment_document_id: str
    payment_number: str | None = None
    expected_amount: float
    actual_amount: float
    is_reconciled: bool

    @classmethod
    def model_validate(cls, obj, **kwargs):
        res = super().model_validate(obj, **kwargs)
        if hasattr(obj, 'payment_document') and obj.payment_document:
            res.payment_number = obj.payment_document.payment_number
        return res


class ReconciliationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    branch_id: str
    reconciliation_date: date
    start_date: date | None = None
    end_date: date | None = None
    payment_method_id: str
    payment_method_name: str | None = None
    receiver_name: str | None
    total_expected_amount: float
    total_actual_amount: float
    difference_amount: float
    status: str
    notes: str | None
    created_at: datetime
    is_latest: bool = False
    items: list[ReconciliationItemResponse]

    @classmethod
    def model_validate(cls, obj, **kwargs):
        res = super().model_validate(obj, **kwargs)
        if hasattr(obj, 'payment_method') and obj.payment_method:
            res.payment_method_name = obj.payment_method.name
        return res


class ReconciliationItemInput(BaseModel):
    payment_document_id: str
    actual_amount: float


class ReconciliationCreateRequest(BaseModel):
    payment_method_id: str
    start_date: str
    end_date: str
    receiver_name: str | None = None
    notes: str | None = None
    items: list[ReconciliationItemInput]


class ReconciliationUpdateRequest(BaseModel):
    receiver_name: str | None = None
    notes: str | None = None


class PendingPaymentResponse(BaseModel):
    id: str
    payment_number: str
    payment_date: str
    customer_name: str
    direct_amount: float
    notes: str | None


@router.get("/pending", response_model=list[PendingPaymentResponse])
def get_pending_payments(
    payment_method_id: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db),
    branch_id: str = Depends(get_active_branch_id),
    _: User = Depends(require_reconcile_cash),
):
    try:
        s_date = date.fromisoformat(start_date)
        e_date = date.fromisoformat(end_date)
    except Exception:
        raise HTTPException(status_code=400, detail="صيغة التاريخ غير صالحة")
        
    payments = reconciliation_service.get_pending_payments(
        db, branch_id, payment_method_id, s_date, e_date
    )
    
    from app.modules.payments.serializers import document_total

    return [
        PendingPaymentResponse(
            id=p.id,
            payment_number=p.payment_number,
            payment_date=str(p.payment_date),
            customer_name=p.customer.full_name if p.customer else "",
            direct_amount=float(document_total(p)),
            notes=p.notes
        )
        for p in payments
    ]


@router.get("", response_model=list[ReconciliationResponse])
def list_reconciliations(
    db: Session = Depends(get_db),
    branch_id: str = Depends(get_active_branch_id),
    _: User = Depends(require_reconcile_cash),
):
    recons = reconciliation_service.list_reconciliations(db, branch_id)
    latest_ids = reconciliation_service.get_latest_reconciliation_ids(db, branch_id)
    
    responses = []
    for r in recons:
        resp = ReconciliationResponse.model_validate(r)
        resp.is_latest = r.id in latest_ids
        responses.append(resp)
    return responses


@router.post("", response_model=ReconciliationResponse, status_code=status.HTTP_201_CREATED)
def create_reconciliation(
    payload: ReconciliationCreateRequest,
    db: Session = Depends(get_db),
    branch_id: str = Depends(get_active_branch_id),
    current_user: User = Depends(require_reconcile_cash),
):
    payload_dict = payload.model_dump()
    try:
        recon = reconciliation_service.create_reconciliation(
            db, current_user, branch_id, payload_dict
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    latest_ids = reconciliation_service.get_latest_reconciliation_ids(db, branch_id)
    resp = ReconciliationResponse.model_validate(recon)
    resp.is_latest = recon.id in latest_ids
    return resp


@router.put("/{reconciliation_id}", response_model=ReconciliationResponse)
def update_reconciliation(
    reconciliation_id: str,
    payload: ReconciliationUpdateRequest,
    db: Session = Depends(get_db),
    branch_id: str = Depends(get_active_branch_id),
    current_user: User = Depends(require_reconcile_cash),
):
    try:
        recon = reconciliation_service.update_reconciliation(
            db, current_user, reconciliation_id, branch_id, payload.model_dump(exclude_unset=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    latest_ids = reconciliation_service.get_latest_reconciliation_ids(db, branch_id)
    resp = ReconciliationResponse.model_validate(recon)
    resp.is_latest = recon.id in latest_ids
    return resp


@router.delete("/{reconciliation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reconciliation(
    reconciliation_id: str,
    db: Session = Depends(get_db),
    branch_id: str = Depends(get_active_branch_id),
    current_user: User = Depends(require_reconcile_cash),
):
    try:
        reconciliation_service.delete_reconciliation(db, current_user, reconciliation_id, branch_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return
