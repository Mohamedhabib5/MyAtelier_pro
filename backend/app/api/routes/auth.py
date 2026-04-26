from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import AuthenticationError, RateLimitError
from app.core.language import DEFAULT_LANGUAGE, LANGUAGE_SESSION_KEY, normalize_language
from app.core.rate_limiter import login_rate_limiter
from app.db.session import get_db
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.identity.schemas import AuthUserResponse, LoginRequest, SessionLanguageRequest
from app.modules.identity.service import authenticate_user, get_user_profile
from app.modules.organization.branch_context import ensure_active_branch

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=AuthUserResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> AuthUserResponse:
    client_ip = request.client.host if request.client else "unknown"
    attempted_username = payload.username.strip().lower()
    
    # Rate limit by IP + Username
    rate_limit_key = f"login:{client_ip}:{attempted_username}"
    if not login_rate_limiter.is_allowed(rate_limit_key):
        record_audit(
            db,
            actor_user_id=None,
            action="auth.rate_limit_exceeded",
            target_type="auth_session",
            target_id=None,
            summary=f"Rate limit exceeded for {attempted_username}",
            diff={"ip": client_ip, "username": attempted_username},
            success=False,
            error_code="rate_limit_exceeded",
        )
        db.commit()
        raise RateLimitError()

    try:
        user = authenticate_user(db, payload.username, payload.password)
    except AuthenticationError:
        record_audit(
            db,
            actor_user_id=None,
            action="auth.login_failed",
            target_type="auth_session",
            target_id=None,
            summary="Failed login attempt",
            diff={"username": attempted_username},
            success=False,
            error_code="invalid_credentials",
        )
        db.commit()
        raise
    request.session.clear()
    branch = ensure_active_branch(db, request.session)
    request.session.update(
        {
            'user_id': user.id,
            'active_branch_id': branch.id,
            LANGUAGE_SESSION_KEY: normalize_language(payload.language or user.preferred_language),
        }
    )
    record_audit(
        db,
        actor_user_id=user.id,
        action="auth.login_success",
        target_type="user",
        target_id=user.id,
        summary=f"User {user.username} logged in",
        diff={"username": user.username, "branch_id": branch.id},
        success=True,
    )
    db.commit()
    return AuthUserResponse(**_build_auth_payload(user, request, branch.id, branch.name))


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, db: Session = Depends(get_db)) -> Response:
    user_id = request.session.get("user_id")
    active_branch_id = request.session.get("active_branch_id")
    if user_id:
        record_audit(
            db,
            actor_user_id=user_id,
            action="auth.logout",
            target_type="user",
            target_id=user_id,
            summary="User logged out",
            diff={"branch_id": active_branch_id},
            success=True,
        )
        db.commit()
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
    previous_language = normalize_language(request.session.get(LANGUAGE_SESSION_KEY) or current_user.preferred_language)
    next_language = normalize_language(payload.language)
    request.session[LANGUAGE_SESSION_KEY] = next_language
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="auth.session_language_changed",
        target_type="user",
        target_id=current_user.id,
        summary=f"Changed session language for {current_user.username}",
        diff={"previous_language": previous_language, "next_language": next_language, "branch_id": branch.id},
        success=True,
    )
    db.commit()
    return AuthUserResponse(**_build_auth_payload(current_user, request, branch.id, branch.name))


def _build_auth_payload(user: User, request: Request, branch_id: str, branch_name: str) -> dict:
    payload = get_user_profile(user)
    payload['active_branch_id'] = branch_id
    payload['active_branch_name'] = branch_name
    session_language = request.session.get(LANGUAGE_SESSION_KEY)
    payload['session_language'] = normalize_language(session_language or payload['preferred_language'])
    payload['effective_language'] = normalize_language(session_language or payload['preferred_language'] or DEFAULT_LANGUAGE)
    return payload
