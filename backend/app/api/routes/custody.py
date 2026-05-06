from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_custody_manage, require_custody_view, require_payments_manage
from app.db.session import get_db
from app.modules.organization.branch_context import resolve_branch_scope
from app.modules.custody.schemas import CustodyCaseActionRequest, CustodyCaseCreateRequest, CustodyCaseResponse, CustodyCompensationCollectRequest
from app.modules.custody.lifecycle import apply_custody_action, collect_custody_compensation
from app.modules.custody.service import create_custody_case, get_custody_case, list_custody_cases
from app.modules.identity.models import User

router = APIRouter(prefix="/custody", tags=["custody"])



@router.get("")
def list_custody_cases_route(
    request: Request,
    view: str = "open",
    branch_id: str | None = Query(default=None),
    page: int | None = Query(default=None),
    page_size: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_custody_view),
) -> dict | list[CustodyCaseResponse]:
    branch = resolve_branch_scope(db, request.session, branch_id)
    result = list_custody_cases(db, branch.id, view=view, page=page, page_size=page_size)
    if isinstance(result, dict):
        return {
            "items": [CustodyCaseResponse.model_validate(item) for item in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        }
    return [CustodyCaseResponse.model_validate(item) for item in result]


@router.post("", response_model=CustodyCaseResponse, status_code=status.HTTP_201_CREATED)
def create_custody_case_route(
    payload: CustodyCaseCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_custody_manage),
) -> CustodyCaseResponse:
    return CustodyCaseResponse.model_validate(create_custody_case(db, current_user, request.session, payload))


@router.get("/{case_id}", response_model=CustodyCaseResponse)
def get_custody_case_route(
    case_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_custody_view),
) -> CustodyCaseResponse:
    return CustodyCaseResponse.model_validate(get_custody_case(db, request.session, case_id))


@router.post("/{case_id}/actions", response_model=CustodyCaseResponse)
def apply_custody_action_route(
    case_id: str,
    payload: CustodyCaseActionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_custody_manage),
) -> CustodyCaseResponse:
    return CustodyCaseResponse.model_validate(
        apply_custody_action(
            db,
            current_user,
            request.session,
            case_id,
            action=payload.action,
            action_date=payload.action_date,
            note=payload.note,
            product_condition=payload.product_condition,
            return_outcome=payload.return_outcome,
            compensation_amount=payload.compensation_amount,
            payment_method_id=payload.payment_method_id,
        )
    )


@router.post("/{case_id}/compensation", response_model=CustodyCaseResponse)
def collect_custody_compensation_route(
    case_id: str,
    payload: CustodyCompensationCollectRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_custody_manage),
    _: User = Depends(require_payments_manage),
) -> CustodyCaseResponse:
    return CustodyCaseResponse.model_validate(
        collect_custody_compensation(
            db,
            current_user,
            request.session,
            case_id,
            compensation_type_id=payload.compensation_type_id,
            amount=payload.amount,
            payment_date=payload.payment_date,
            note=payload.note,
            payment_method_id=payload.payment_method_id,
            override_lock=payload.override_lock,
            override_reason=payload.override_reason,
        )
    )
