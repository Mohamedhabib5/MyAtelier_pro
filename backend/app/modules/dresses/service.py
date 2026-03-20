from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.core_platform.service import record_audit
from app.modules.dresses.models import DressResource
from app.modules.dresses.repository import DressesRepository
from app.modules.dresses.schemas import DressCreateRequest, DressUpdateRequest
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings

VALID_STATUSES = {'available', 'reserved', 'maintenance'}


def list_dresses(db: Session) -> list[dict]:
    company = get_company_settings(db)
    rows = DressesRepository(db).list_dresses(company.id)
    return [_serialize_dress(row) for row in rows]


def create_dress(db: Session, actor: User, payload: DressCreateRequest) -> dict:
    company = get_company_settings(db)
    repo = DressesRepository(db)
    code = _clean(payload.code).upper()
    if repo.get_dress_by_code(company.id, code) is not None:
        raise ValidationAppError('كود الفستان مستخدم بالفعل')

    dress = DressResource(
        company_id=company.id,
        code=code,
        dress_type=_clean(payload.dress_type),
        purchase_date=_parse_date(payload.purchase_date),
        status=_clean_status(payload.status),
        description=_clean(payload.description),
        image_path=_clean_optional(payload.image_path),
        is_active=True,
    )
    repo.add_dress(dress)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action='dress.created',
        target_type='dress',
        target_id=dress.id,
        summary=f'Created dress {dress.code}',
        diff={'status': dress.status},
    )
    db.commit()
    db.refresh(dress)
    return _serialize_dress(dress)


def update_dress(db: Session, actor: User, dress_id: str, payload: DressUpdateRequest) -> dict:
    company = get_company_settings(db)
    repo = DressesRepository(db)
    dress = repo.get_dress(dress_id)
    if dress is None or dress.company_id != company.id:
        raise NotFoundError('لم يتم العثور على الفستان')

    code = _clean(payload.code).upper()
    existing = repo.get_dress_by_code(company.id, code)
    if existing is not None and existing.id != dress.id:
        raise ValidationAppError('كود الفستان مستخدم بالفعل')

    dress.code = code
    dress.dress_type = _clean(payload.dress_type)
    dress.purchase_date = _parse_date(payload.purchase_date)
    dress.status = _clean_status(payload.status)
    dress.description = _clean(payload.description)
    dress.image_path = _clean_optional(payload.image_path)
    dress.is_active = payload.is_active
    record_audit(
        db,
        actor_user_id=actor.id,
        action='dress.updated',
        target_type='dress',
        target_id=dress.id,
        summary=f'Updated dress {dress.code}',
        diff={'status': dress.status, 'is_active': dress.is_active},
    )
    db.commit()
    db.refresh(dress)
    return _serialize_dress(dress)


def _serialize_dress(dress: DressResource) -> dict:
    return {
        'id': dress.id,
        'company_id': dress.company_id,
        'code': dress.code,
        'dress_type': dress.dress_type,
        'purchase_date': dress.purchase_date.isoformat() if dress.purchase_date else None,
        'status': dress.status,
        'description': dress.description,
        'image_path': dress.image_path,
        'is_active': dress.is_active,
    }


def _clean(value: str) -> str:
    text = norm_text(value)
    if not text:
        raise ValidationAppError('القيمة مطلوبة')
    return text


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    text = norm_text(value)
    return text or None


def _clean_status(value: str) -> str:
    status = _clean(value).lower()
    if status not in VALID_STATUSES:
        raise ValidationAppError('حالة الفستان غير صالحة')
    return status


def _parse_date(value: str | None) -> date | None:
    text = _clean_optional(value)
    if text is None:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValidationAppError('تاريخ الشراء غير صالح') from exc
