from fastapi import APIRouter, Depends, status, Query, HTTPException, Response
from sqlalchemy.orm import Session


from app.api.deps import get_active_branch_id, require_payments_manage, require_payments_view
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.payments.schemas import (
    DisbursementVoucherCreateRequest,
    DisbursementVoucherResponse,
    DisbursementVoucherSummaryPageResponse,
    DisbursementVoucherSummaryResponse,
    DisbursementVoucherUpdateRequest,
    PaymentVoidRequest,
)
from app.modules.payments.disbursement_service import (
    create_disbursement,
    delete_disbursement,
    get_disbursement_voucher,
    list_disbursement_page,
    list_disbursements,
    update_disbursement,
    void_disbursement,
)

router = APIRouter(prefix='/disbursements', tags=['disbursements'])


@router.get('', response_model=list[DisbursementVoucherSummaryResponse])
def list_disbursements_route(
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    _: User = Depends(require_payments_view)
) -> list[DisbursementVoucherSummaryResponse]:
    return [DisbursementVoucherSummaryResponse.model_validate(item) for item in list_disbursements(db, branch_id)]


@router.get('/table', response_model=DisbursementVoucherSummaryPageResponse)
def list_disbursements_table_route(
    branch_id_param: str | None = Query(default=None, alias='branch_id'),
    search: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias='status'),
    payee_type: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sort_by: str = Query(default='voucher_date'),
    sort_dir: str = Query(default='desc'),
    active_branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    _: User = Depends(require_payments_view),
) -> DisbursementVoucherSummaryPageResponse:
    branch_id = branch_id_param or active_branch_id
    try:
        payload = list_disbursement_page(
            db,
            branch_id=branch_id,
            search=search,
            status=status_value,
            payee_type=payee_type,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DisbursementVoucherSummaryPageResponse.model_validate(payload)


@router.get('/{disbursement_voucher_id}', response_model=DisbursementVoucherResponse)
def get_disbursement_route(
    disbursement_voucher_id: str,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    _: User = Depends(require_payments_view)
) -> DisbursementVoucherResponse:
    try:
        voucher = get_disbursement_voucher(db, disbursement_voucher_id, branch_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DisbursementVoucherResponse.model_validate(voucher)


@router.post('', response_model=DisbursementVoucherResponse, status_code=status.HTTP_201_CREATED)
def create_disbursement_route(
    payload: DisbursementVoucherCreateRequest,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_payments_manage)
) -> DisbursementVoucherResponse:
    try:
        voucher = create_disbursement(db, current_user, payload, branch_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DisbursementVoucherResponse.model_validate(voucher)


@router.patch('/{disbursement_voucher_id}', response_model=DisbursementVoucherResponse)
def update_disbursement_route(
    disbursement_voucher_id: str,
    payload: DisbursementVoucherUpdateRequest,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_payments_manage)
) -> DisbursementVoucherResponse:
    try:
        voucher = update_disbursement(db, current_user, disbursement_voucher_id, payload, branch_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DisbursementVoucherResponse.model_validate(voucher)


@router.post('/{disbursement_voucher_id}/void', response_model=DisbursementVoucherResponse)
def void_disbursement_route(
    disbursement_voucher_id: str,
    payload: PaymentVoidRequest,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_payments_manage)
) -> DisbursementVoucherResponse:
    try:
        voucher = void_disbursement(db, current_user, disbursement_voucher_id, payload, branch_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DisbursementVoucherResponse.model_validate(voucher)


@router.delete('/{disbursement_voucher_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_disbursement_route(
    disbursement_voucher_id: str,
    branch_id: str = Depends(get_active_branch_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_payments_manage),
) -> Response:
    try:
        delete_disbursement(db, current_user, disbursement_voucher_id, branch_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

