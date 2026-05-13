from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import AuthorizationError, RateLimitError, ValidationAppError
from app.core.rate_limiter import two_fa_rate_limiter
from app.db.session import get_db
from app.modules.identity.models import User
from app.modules.identity.schemas import (
    Verify2FARequest, 
    TwoFASetupResponse, 
    TwoFAActivationResponse, 
    AuthUserResponse
)
from app.modules.identity.service import (
    setup_2fa, 
    activate_2fa, 
    verify_2fa_login, 
    verify_backup_code_login,
    get_user_profile
)
from app.modules.organization.branch_context import ensure_active_branch

router = APIRouter(prefix='/auth/2fa', tags=['auth-2fa'])

@router.post('/setup', response_model=TwoFASetupResponse)
def init_2fa_setup(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
) -> TwoFASetupResponse:
    """Step 1: Generate TOTP secret and QR URI."""
    if current_user.is_2fa_enabled:
        raise ValidationAppError("التحقق الثنائي مفعل بالفعل لهذا الحساب")
    
    result = setup_2fa(db, current_user)
    return TwoFASetupResponse(**result)

@router.post('/activate', response_model=TwoFAActivationResponse)
def complete_2fa_setup(
    payload: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TwoFAActivationResponse:
    """Step 2: Verify first code and activate 2FA + generate backup codes."""
    if current_user.is_2fa_enabled:
        raise ValidationAppError("التحقق الثنائي مفعل بالفعل")
        
    backup_codes = activate_2fa(db, current_user, payload.code)
    request.session["2fa_pending"] = False
    return TwoFAActivationResponse(backup_codes=backup_codes)

@router.post('/verify', response_model=AuthUserResponse)
def verify_login_2fa(
    payload: Verify2FARequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AuthUserResponse:
    """Verify TOTP code during login."""
    if not request.session.get("2fa_pending"):
        raise AuthorizationError("لا يوجد طلب تحقق ثنائي معلق")

    client_ip = request.client.host if request.client else "unknown"
    rate_limit_key = f"2fa:{client_ip}:{current_user.id}"
    if not two_fa_rate_limiter.is_allowed(rate_limit_key):
        raise RateLimitError("محاولات كثيرة جداً. يرجى المحاولة لاحقاً")

    if verify_2fa_login(db, current_user, payload.code):
        request.session["2fa_pending"] = False
        branch = ensure_active_branch(db, request.session)
        profile = get_user_profile(current_user)
        profile.update({
            "active_branch_id": branch.id,
            "active_branch_name": branch.name,
            "session_language": request.session.get("language", current_user.preferred_language),
            "effective_language": request.session.get("language", current_user.preferred_language),
            "is_2fa_required": False
        })
        return AuthUserResponse(**profile)
    
    raise ValidationAppError("رمز التحقق غير صحيح")

@router.post('/verify-backup', response_model=AuthUserResponse)
def verify_login_backup(
    payload: Verify2FARequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AuthUserResponse:
    """Verify backup code during login."""
    if not request.session.get("2fa_pending"):
        raise AuthorizationError("لا يوجد طلب تحقق ثنائي معلق")

    if verify_backup_code_login(db, current_user, payload.code):
        request.session["2fa_pending"] = False
        branch = ensure_active_branch(db, request.session)
        profile = get_user_profile(current_user)
        profile.update({
            "active_branch_id": branch.id,
            "active_branch_name": branch.name,
            "session_language": request.session.get("language", current_user.preferred_language),
            "effective_language": request.session.get("language", current_user.preferred_language),
            "is_2fa_required": False
        })
        return AuthUserResponse(**profile)
    
    raise ValidationAppError("رمز النسخ الاحتياطي غير صحيح")
