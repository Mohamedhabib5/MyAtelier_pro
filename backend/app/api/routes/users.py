from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_self_manage, require_users_manage
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.identity.schemas import AdminUpdateUserRequest, CreateUserRequest, SelfUpdateUserRequest, UserResponse
from app.modules.identity.service import create_user, get_user_profile, list_visible_users, update_own_profile, update_user_by_admin

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