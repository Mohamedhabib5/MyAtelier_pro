from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_catalog_manage, require_catalog_view
from app.db.session import get_db
from app.modules.catalog.schemas import DepartmentCreateRequest, DepartmentResponse, DepartmentUpdateRequest, ServiceCreateRequest, ServiceResponse, ServiceUpdateRequest
from app.modules.catalog.service import create_department, create_service, list_departments, list_services, update_department, update_service
from app.modules.identity.models import User

router = APIRouter(prefix='/catalog', tags=['catalog'])


@router.get('/departments', response_model=list[DepartmentResponse])
def list_departments_route(db: Session = Depends(get_db), _: User = Depends(require_catalog_view)) -> list[DepartmentResponse]:
    return [DepartmentResponse.model_validate(item) for item in list_departments(db)]


@router.post('/departments', response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department_route(payload: DepartmentCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_catalog_manage)) -> DepartmentResponse:
    return DepartmentResponse.model_validate(create_department(db, current_user, payload))


@router.patch('/departments/{department_id}', response_model=DepartmentResponse)
def update_department_route(
    department_id: str,
    payload: DepartmentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> DepartmentResponse:
    return DepartmentResponse.model_validate(update_department(db, current_user, department_id, payload))


@router.get('/services', response_model=list[ServiceResponse])
def list_services_route(db: Session = Depends(get_db), _: User = Depends(require_catalog_view)) -> list[ServiceResponse]:
    return [ServiceResponse.model_validate(item) for item in list_services(db)]


@router.post('/services', response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service_route(payload: ServiceCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_catalog_manage)) -> ServiceResponse:
    return ServiceResponse.model_validate(create_service(db, current_user, payload))


@router.patch('/services/{service_id}', response_model=ServiceResponse)
def update_service_route(
    service_id: str,
    payload: ServiceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> ServiceResponse:
    return ServiceResponse.model_validate(update_service(db, current_user, service_id, payload))
