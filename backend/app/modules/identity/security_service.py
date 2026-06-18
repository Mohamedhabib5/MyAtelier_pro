from __future__ import annotations

import pyotp
import secrets
import string

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.core.exceptions import ValidationAppError
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User, UserBackupCode
from app.modules.identity.repository import IdentityRepository
from app.core.security import encrypt_secret, decrypt_secret, SecurityNotificationService


def setup_2fa(db: Session, user: User) -> dict:
    """Generates a new TOTP secret for the user but does not enable it yet."""
    secret = pyotp.random_base32()
    user.totp_secret = encrypt_secret(secret)
    db.commit()
    
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="MyAtelier Pro")
    
    return {
        "provisioning_uri": provisioning_uri,
    }


def activate_2fa(db: Session, user: User, code: str) -> list[str]:
    """Verifies the first code and permanently enables 2FA for the user."""
    if not user.totp_secret:
        raise ValidationAppError("لم يتم إعداد التحقق الثنائي لهذا المستخدم")
    
    secret = decrypt_secret(user.totp_secret)
    totp = pyotp.TOTP(secret)
    
    if not totp.verify(code):
        SecurityNotificationService.notify_security_event("2fa_setup_failed", {"user_id": user.id, "username": user.username})
        raise ValidationAppError("رمز التحقق غير صحيح")
    
    user.is_2fa_enabled = True
    
    # Generate Backup Codes
    backup_codes = []
    repo = IdentityRepository(db)
    for _ in range(10):
        raw_code = "".join(secrets.choice(string.digits) for _ in range(8))
        backup_codes.append(raw_code)
        # We hash backup codes for security
        code_hash = hash_password(raw_code)
        repo.add_backup_code(UserBackupCode(user_id=user.id, code_hash=code_hash))
    
    record_audit(db, actor_user_id=user.id, action="auth.2fa_enabled", target_type="user", target_id=user.id, summary="Enabled 2FA")
    db.commit()
    return backup_codes


def verify_2fa_login(db: Session, user: User, code: str) -> bool:
    """Verifies a TOTP code during the login flow.
    
    Fail-closed: returns False if 2FA is not enabled or secret is missing.
    The caller is responsible for clearing the 2fa_pending session state
    and redirecting the user to re-authenticate.
    """
    if not user.is_2fa_enabled or not user.totp_secret:
        # Fail-closed: لا نسمح بالمتابعة إذا كان 2FA غير مُفعَّل.
        # لو وصلنا لهذه النقطة مع 2fa_pending=True في الجلسة، فهناك
        # عدم اتساق (race condition) — المستخدم عطَّل 2FA أثناء الجلسة.
        SecurityNotificationService.notify_security_event(
            "2fa_inconsistent_state",
            {"user_id": user.id, "username": user.username,
             "reason": "2FA disabled during pending session"}
        )
        return False
    
    secret = decrypt_secret(user.totp_secret)
    totp = pyotp.TOTP(secret)
    
    if totp.verify(code):
        return True
    
    # Notify on failure
    SecurityNotificationService.notify_security_event("2fa_login_failed", {"user_id": user.id, "username": user.username})
    return False


def verify_backup_code_login(db: Session, user: User, code: str) -> bool:
    """Verifies a backup code and marks it as used."""
    repo = IdentityRepository(db)
    valid_codes = repo.list_user_backup_codes(user.id)
    
    for bc in valid_codes:
        if verify_password(code, bc.code_hash):
            bc.is_used = True
            record_audit(db, actor_user_id=user.id, action="auth.2fa_backup_code_used", target_type="user", target_id=user.id, summary="Used backup code to login")
            db.commit()
            return True
    
    return False
