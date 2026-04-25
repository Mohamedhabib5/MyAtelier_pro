from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings
from app.modules.payments.models import PaymentMethod
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.schemas import PaymentMethodCreateRequest, PaymentMethodUpdateRequest

DEFAULT_PAYMENT_METHOD_CODE = "cash"
DEFAULT_PAYMENT_METHOD_NAME_AR = "\u0643\u0627\u0634"
PAYMENT_METHOD_STATUS_VALUES = {"all", "active", "inactive"}


def list_payment_methods(db: Session, *, status: str = "active") -> list[dict]:
    company = get_company_settings(db)
    normalized_status = _normalize_status(status)
    repo = PaymentsRepository(db)
    changed = _ensure_active_method_available(db, company.id, actor_user_id=None)
    if changed:
        db.commit()
    if normalized_status == "active":
        rows = repo.list_payment_methods(company.id, include_inactive=False)
    elif normalized_status == "inactive":
        rows = [item for item in repo.list_payment_methods(company.id, include_inactive=True) if not item.is_active]
    else:
        rows = repo.list_payment_methods(company.id, include_inactive=True)
    return [_serialize_payment_method(item) for item in rows]


def create_payment_method(db: Session, actor: User, payload: PaymentMethodCreateRequest) -> dict:
    company = get_company_settings(db)
    repo = PaymentsRepository(db)
    code = _resolve_unique_code(repo, company.id, _normalize_code(payload.code or payload.name))
    method = PaymentMethod(
        company_id=company.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        code=code,
        name=_clean_name(payload.name),
        is_active=bool(payload.is_active),
        display_order=repo.next_payment_method_order(company.id),
    )
    repo.add_payment_method(method)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="payment_method.created",
        target_type="payment_method",
        target_id=method.id,
        summary=f"Created payment method {method.code}",
        diff={
            "code": method.code,
            "name": method.name,
            "is_active": method.is_active,
            "display_order": method.display_order,
            "entity_version": method.entity_version,
        },
    )
    db.commit()
    db.refresh(method)
    return _serialize_payment_method(method)


def update_payment_method(db: Session, actor: User, payment_method_id: str, payload: PaymentMethodUpdateRequest) -> dict:
    method = _get_scoped_payment_method_or_404(db, payment_method_id)
    previous_payload = _serialize_payment_method(method)
    has_changes = False
    if payload.name is not None:
        method.name = _clean_name(payload.name)
        has_changes = True
    if payload.is_active is not None:
        method.is_active = payload.is_active
        has_changes = True
    if payload.display_order is not None:
        method.display_order = payload.display_order
        has_changes = True
    if has_changes:
        method.updated_by_user_id = actor.id
        method.entity_version += 1
    _ensure_active_method_available(db, method.company_id, actor_user_id=actor.id)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="payment_method.updated",
        target_type="payment_method",
        target_id=method.id,
        summary=f"Updated payment method {method.code}",
        diff={
            "before": previous_payload,
            "after": _serialize_payment_method(method),
        },
    )
    db.commit()
    db.refresh(method)
    return _serialize_payment_method(method)


def ensure_default_active_payment_method(db: Session, company_id: str, *, actor_user_id: str | None) -> PaymentMethod:
    _ensure_active_method_available(db, company_id, actor_user_id=actor_user_id)
    repo = PaymentsRepository(db)
    active_rows = repo.list_payment_methods(company_id, include_inactive=False)
    if not active_rows:
        raise ValidationAppError("\u062a\u0639\u0630\u0631 \u062a\u062d\u062f\u064a\u062f \u0637\u0631\u064a\u0642\u0629 \u062f\u0641\u0639 \u0641\u0639\u0627\u0644\u0629")
    return active_rows[0]


def resolve_payment_method(
    db: Session,
    *,
    company_id: str,
    payment_method_id: str | None,
    actor_user_id: str | None,
) -> PaymentMethod:
    repo = PaymentsRepository(db)
    if payment_method_id:
        method = repo.get_payment_method(payment_method_id)
        if method is None or method.company_id != company_id:
            raise NotFoundError("\u0644\u0645 \u064a\u062a\u0645 \u0627\u0644\u0639\u062b\u0648\u0631 \u0639\u0644\u0649 \u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639")
        if not method.is_active:
            raise ValidationAppError("\u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639 \u063a\u064a\u0631 \u0641\u0639\u0627\u0644\u0629")
        return method
    return ensure_default_active_payment_method(db, company_id, actor_user_id=actor_user_id)


def _ensure_active_method_available(db: Session, company_id: str, *, actor_user_id: str | None) -> bool:
    repo = PaymentsRepository(db)
    active_rows = repo.list_payment_methods(company_id, include_inactive=False)
    if active_rows:
        return False
    default_method = repo.get_payment_method_by_code(company_id, DEFAULT_PAYMENT_METHOD_CODE)
    if default_method is None:
        default_method = PaymentMethod(
            company_id=company_id,
            created_by_user_id=actor_user_id,
            updated_by_user_id=actor_user_id,
            entity_version=1,
            code=DEFAULT_PAYMENT_METHOD_CODE,
            name=DEFAULT_PAYMENT_METHOD_NAME_AR,
            is_active=True,
            display_order=1,
        )
        repo.add_payment_method(default_method)
        db.flush()
        return True
    default_method.is_active = True
    default_method.display_order = max(1, default_method.display_order)
    default_method.updated_by_user_id = actor_user_id
    default_method.entity_version += 1
    db.flush()
    return True


def _normalize_status(value: str) -> str:
    text = norm_text(value).lower() or "active"
    if text not in PAYMENT_METHOD_STATUS_VALUES:
        raise ValidationAppError("\u0642\u064a\u0645\u0629 \u062d\u0627\u0644\u0629 \u0637\u0631\u0642 \u0627\u0644\u062f\u0641\u0639 \u063a\u064a\u0631 \u0635\u0627\u0644\u062d\u0629")
    return text


def _clean_name(value: str) -> str:
    text = norm_text(value)
    if not text:
        raise ValidationAppError("\u0627\u0633\u0645 \u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639 \u0645\u0637\u0644\u0648\u0628")
    return text


def _normalize_code(value: str) -> str:
    normalized = norm_text(value).lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    if not normalized:
        normalized = "method"
    if len(normalized) > 40:
        normalized = normalized[:40]
    return normalized


def _resolve_unique_code(repo: PaymentsRepository, company_id: str, seed: str) -> str:
    if not repo.get_payment_method_by_code(company_id, seed):
        return seed
    for index in range(2, 5000):
        suffix = f"_{index}"
        candidate = f"{seed[: max(1, 40 - len(suffix))]}{suffix}"
        if not repo.get_payment_method_by_code(company_id, candidate):
            return candidate
    raise ValidationAppError("\u062a\u0639\u0630\u0631 \u0625\u0646\u0634\u0627\u0621 \u0631\u0645\u0632 \u0641\u0631\u064a\u062f \u0644\u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639")


def _get_scoped_payment_method_or_404(db: Session, payment_method_id: str) -> PaymentMethod:
    company = get_company_settings(db)
    method = PaymentsRepository(db).get_payment_method(payment_method_id)
    if method is None or method.company_id != company.id:
        raise NotFoundError("\u0644\u0645 \u064a\u062a\u0645 \u0627\u0644\u0639\u062b\u0648\u0631 \u0639\u0644\u0649 \u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u062f\u0641\u0639")
    return method


def _serialize_payment_method(method: PaymentMethod) -> dict:
    return {
        "id": method.id,
        "company_id": method.company_id,
        "created_by_user_id": method.created_by_user_id,
        "updated_by_user_id": method.updated_by_user_id,
        "entity_version": method.entity_version,
        "code": method.code,
        "name": method.name,
        "is_active": method.is_active,
        "display_order": method.display_order,
    }
