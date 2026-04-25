from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_customers_manage, require_customers_view
from app.db.session import get_db
from app.modules.customers.schemas import CustomerArchiveRequest, CustomerCreateRequest, CustomerResponse, CustomerUpdateRequest
from app.modules.customers.service import archive_customer, create_customer, list_customers, restore_customer, update_customer
from app.modules.identity.models import User

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerResponse])
def list_customers_route(
    status_filter: Literal["all", "active", "inactive"] = Query(default="all", alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_customers_view),
) -> list[CustomerResponse]:
    is_active = None if status_filter == "all" else status_filter == "active"
    return [CustomerResponse.model_validate(item) for item in list_customers(db, is_active=is_active)]


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer_route(
    payload: CustomerCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customers_manage),
) -> CustomerResponse:
    return CustomerResponse.model_validate(create_customer(db, current_user, payload))


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer_route(
    customer_id: str,
    payload: CustomerUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customers_manage),
) -> CustomerResponse:
    return CustomerResponse.model_validate(update_customer(db, current_user, customer_id, payload))


@router.post("/{customer_id}/archive", response_model=CustomerResponse)
def archive_customer_route(
    customer_id: str,
    payload: CustomerArchiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customers_manage),
) -> CustomerResponse:
    return CustomerResponse.model_validate(archive_customer(db, current_user, customer_id, payload.reason))


@router.post("/{customer_id}/restore", response_model=CustomerResponse)
def restore_customer_route(
    customer_id: str,
    payload: CustomerArchiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customers_manage),
) -> CustomerResponse:
    return CustomerResponse.model_validate(restore_customer(db, current_user, customer_id, payload.reason))
