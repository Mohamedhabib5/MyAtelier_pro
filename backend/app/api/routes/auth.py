from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.language import DEFAULT_LANGUAGE, LANGUAGE_SESSION_KEY, normalize_language
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.identity.schemas import AuthUserResponse, LoginRequest, SessionLanguageRequest
from app.modules.identity.service import authenticate_user, get_user_profile
from app.modules.organization.branch_context import ensure_active_branch

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=AuthUserResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> AuthUserResponse:
    user = authenticate_user(db, payload.username, payload.password)
    request.session.clear()
    branch = ensure_active_branch(db, request.session)
    request.session.update(
        {
            'user_id': user.id,
            'active_branch_id': branch.id,
            LANGUAGE_SESSION_KEY: normalize_language(payload.language or user.preferred_language),
        }
    )
    return AuthUserResponse(**_build_auth_payload(user, request, branch.id, branch.name))


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request) -> Response:
    request.session.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/me', response_model=AuthUserResponse)
def get_me(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AuthUserResponse:
    branch = ensure_active_branch(db, request.session)
    return AuthUserResponse(**_build_auth_payload(current_user, request, branch.id, branch.name))


@router.post('/language', response_model=AuthUserResponse)
def set_session_language(
    payload: SessionLanguageRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AuthUserResponse:
    branch = ensure_active_branch(db, request.session)
    request.session[LANGUAGE_SESSION_KEY] = normalize_language(payload.language)
    return AuthUserResponse(**_build_auth_payload(current_user, request, branch.id, branch.name))


def _build_auth_payload(user: User, request: Request, branch_id: str, branch_name: str) -> dict:
    payload = get_user_profile(user)
    payload['active_branch_id'] = branch_id
    payload['active_branch_name'] = branch_name
    session_language = request.session.get(LANGUAGE_SESSION_KEY)
    payload['session_language'] = normalize_language(session_language or payload['preferred_language'])
    payload['effective_language'] = normalize_language(session_language or payload['preferred_language'] or DEFAULT_LANGUAGE)
    return payload
