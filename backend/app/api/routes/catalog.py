from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_catalog_manage, require_catalog_view
from app.db.session import get_db
from app.modules.catalog.lifecycle import (
    archive_department,
    archive_service,
    list_departments,
    list_services,
    restore_department,
    restore_service,
)
from app.modules.catalog.schemas import (
    CatalogArchiveRequest,
    DepartmentCreateRequest,
    DepartmentResponse,
    DepartmentUpdateRequest,
    ServiceCreateRequest,
    ServiceResponse,
    ServiceUpdateRequest,
    SetDressDepartmentRequest,
)
from app.modules.catalog.service import create_department, create_service, set_dress_department, update_department, update_service
from app.modules.identity.models import User

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments_route(
    status_filter: Literal["all", "active", "inactive"] = Query(default="all", alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_catalog_view),
) -> list[DepartmentResponse]:
    is_active = None if status_filter == "all" else status_filter == "active"
    return [DepartmentResponse.model_validate(item) for item in list_departments(db, is_active=is_active)]


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department_route(
    payload: DepartmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> DepartmentResponse:
    return DepartmentResponse.model_validate(create_department(db, current_user, payload))


@router.patch("/departments/{department_id}", response_model=DepartmentResponse)
def update_department_route(
    department_id: str,
    payload: DepartmentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> DepartmentResponse:
    return DepartmentResponse.model_validate(update_department(db, current_user, department_id, payload))


@router.post("/departments/{department_id}/archive", response_model=DepartmentResponse)
def archive_department_route(
    department_id: str,
    payload: CatalogArchiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> DepartmentResponse:
    return DepartmentResponse.model_validate(archive_department(db, current_user, department_id, payload.reason))


@router.post("/departments/{department_id}/restore", response_model=DepartmentResponse)
def restore_department_route(
    department_id: str,
    payload: CatalogArchiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> DepartmentResponse:
    return DepartmentResponse.model_validate(restore_department(db, current_user, department_id, payload.reason))


@router.post("/operational/dresses-department", response_model=DepartmentResponse)
def make_dress_department_route(
    payload: SetDressDepartmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> DepartmentResponse:
    return DepartmentResponse.model_validate(set_dress_department(db, current_user, payload.department_id))


@router.get("/services", response_model=list[ServiceResponse])
def list_services_route(
    status_filter: Literal["all", "active", "inactive"] = Query(default="all", alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_catalog_view),
) -> list[ServiceResponse]:
    is_active = None if status_filter == "all" else status_filter == "active"
    return [ServiceResponse.model_validate(item) for item in list_services(db, is_active=is_active)]


@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service_route(
    payload: ServiceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> ServiceResponse:
    return ServiceResponse.model_validate(create_service(db, current_user, payload))


@router.patch("/services/{service_id}", response_model=ServiceResponse)
def update_service_route(
    service_id: str,
    payload: ServiceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> ServiceResponse:
    return ServiceResponse.model_validate(update_service(db, current_user, service_id, payload))


@router.post("/services/{service_id}/archive", response_model=ServiceResponse)
def archive_service_route(
    service_id: str,
    payload: CatalogArchiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> ServiceResponse:
    return ServiceResponse.model_validate(archive_service(db, current_user, service_id, payload.reason))


@router.post("/services/{service_id}/restore", response_model=ServiceResponse)
def restore_service_route(
    service_id: str,
    payload: CatalogArchiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_catalog_manage),
) -> ServiceResponse:
    return ServiceResponse.model_validate(restore_service(db, current_user, service_id, payload.reason))
