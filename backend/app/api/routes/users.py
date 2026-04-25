from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_self_manage, require_users_manage
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.identity.schemas import AdminUpdateUserRequest, CreateUserRequest, SelfUpdateUserRequest, UserGridPreferenceResponse, UserGridPreferenceUpdateRequest, UserResponse
from app.modules.identity.service import create_user, get_user_grid_preference, get_user_profile, list_visible_users, set_user_grid_preference, update_own_profile, update_user_by_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(current_user: User = Depends(require_self_manage), db: Session = Depends(get_db)) -> list[UserResponse]:
    return [UserResponse(**item) for item in list_visible_users(db, current_user)]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_route(
    payload: CreateUserRequest,
    manager_user: User = Depends(require_users_manage),
    db: Session = Depends(get_db),
) -> UserResponse:
    return UserResponse(**create_user(db, manager_user, payload))


@router.get("/me", response_model=UserResponse)
def get_my_user(current_user: User = Depends(require_self_manage)) -> UserResponse:
    return UserResponse(**get_user_profile(current_user))


@router.patch("/me", response_model=UserResponse)
def update_my_user(
    payload: SelfUpdateUserRequest,
    current_user: User = Depends(require_self_manage),
    db: Session = Depends(get_db),
) -> UserResponse:
    return UserResponse(**update_own_profile(db, current_user, payload))


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_route(
    user_id: str,
    payload: AdminUpdateUserRequest,
    manager_user: User = Depends(require_users_manage),
    db: Session = Depends(get_db),
) -> UserResponse:
    return UserResponse(**update_user_by_admin(db, manager_user, user_id, payload))


@router.get("/me/grid-preferences/{table_key}", response_model=UserGridPreferenceResponse)
def get_my_grid_preference(
    table_key: str,
    current_user: User = Depends(require_self_manage),
    db: Session = Depends(get_db),
) -> UserGridPreferenceResponse:
    return UserGridPreferenceResponse.model_validate(get_user_grid_preference(db, current_user, table_key))


@router.put("/me/grid-preferences/{table_key}", response_model=UserGridPreferenceResponse)
def update_my_grid_preference(
    table_key: str,
    payload: UserGridPreferenceUpdateRequest,
    current_user: User = Depends(require_self_manage),
    db: Session = Depends(get_db),
) -> UserGridPreferenceResponse:
    return UserGridPreferenceResponse.model_validate(set_user_grid_preference(db, current_user, table_key, payload.state))
