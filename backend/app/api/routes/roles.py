from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import PermissionRequired
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.identity.schemas import (
    RoleResponse, 
    CreateRoleRequest, 
    UpdateRoleRequest, 
    PermissionResponse
)
from app.modules.identity.role_service import (
    list_roles, 
    get_role_or_404, 
    create_role, 
    update_role, 
    delete_role, 
    clone_role,
    list_all_permissions
)

router = APIRouter(prefix='/roles', tags=['roles'])

@router.get('', response_model=list[RoleResponse])
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionRequired("users.manage"))
) -> list[RoleResponse]:
    return [RoleResponse.model_validate(r) for r in list_roles(db)]

@router.get('/permissions', response_model=list[PermissionResponse])
def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionRequired("users.manage"))
) -> list[PermissionResponse]:
    return [PermissionResponse.model_validate(p) for p in list_all_permissions(db)]

@router.post('', response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def add_role(
    payload: CreateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionRequired("users.manage"))
) -> RoleResponse:
    return RoleResponse.model_validate(create_role(db, current_user, payload))

@router.get('/{role_id}', response_model=RoleResponse)
def get_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionRequired("users.manage"))
) -> RoleResponse:
    return RoleResponse.model_validate(get_role_or_404(db, role_id))

@router.patch('/{role_id}', response_model=RoleResponse)
def patch_role(
    role_id: str,
    payload: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionRequired("users.manage"))
) -> RoleResponse:
    return RoleResponse.model_validate(update_role(db, current_user, role_id, payload))

@router.delete('/{role_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionRequired("users.manage"))
):
    delete_role(db, current_user, role_id)
    return None

@router.post('/{role_id}/clone', response_model=RoleResponse)
def duplicate_role(
    role_id: str,
    new_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionRequired("users.manage"))
) -> RoleResponse:
    return RoleResponse.model_validate(clone_role(db, current_user, role_id, new_name))
