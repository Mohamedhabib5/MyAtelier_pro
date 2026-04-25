from __future__ import annotations
import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.core_platform.service import record_audit
from app.modules.customers.models import Customer
from app.modules.customers.repository import CustomersRepository
from app.modules.customers.schemas import CustomerCreateRequest, CustomerUpdateRequest
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings


def list_customers(db: Session, *, is_active: bool | None = None) -> list[dict]:
    company = get_company_settings(db)
    rows = CustomersRepository(db).list_customers(company.id, is_active=is_active)
    return [_serialize_customer(row) for row in rows]


def create_customer(db: Session, actor: User, payload: CustomerCreateRequest) -> dict:
    company = get_company_settings(db)
    repo = CustomersRepository(db)
    phone = _clean(payload.phone)
    existing = repo.get_customer_by_phone(company.id, phone)
    if existing is not None:
        raise ValidationAppError("رقم هاتف العميل مستخدم بالفعل")
    customer = Customer(
        company_id=company.id,
        created_by_user_id=actor.id,
        registration_date=datetime.date.fromisoformat(payload.registration_date) if payload.registration_date else None,
        updated_by_user_id=actor.id,
        entity_version=1,
        full_name=_clean(payload.full_name),
        groom_name=_clean_optional(payload.groom_name),
        bride_name=_clean_optional(payload.bride_name),
        phone=phone,
        phone_2=_clean_optional(payload.phone_2),
        email=_clean_optional(payload.email),
        address=_clean_optional(payload.address),
        notes=_clean_optional(payload.notes),
        is_active=True,
    )
    repo.add_customer(customer)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="customer.created",
        target_type="customer",
        target_id=customer.id,
        summary=f"Created customer {customer.full_name}",
        diff={"phone": customer.phone, "entity_version": customer.entity_version},
    )
    db.commit()
    db.refresh(customer)
    return _serialize_customer(customer)


def update_customer(db: Session, actor: User, customer_id: str, payload: CustomerUpdateRequest) -> dict:
    repo = CustomersRepository(db)
    customer = _get_company_customer_or_404(db, repo, customer_id)
    company = get_company_settings(db)

    phone = _clean(payload.phone)
    existing = repo.get_customer_by_phone(company.id, phone)
    if existing is not None and existing.id != customer.id:
        raise ValidationAppError("رقم هاتف العميل مستخدم بالفعل")

    customer.full_name = _clean(payload.full_name)
    customer.groom_name = _clean_optional(payload.groom_name)
    customer.bride_name = _clean_optional(payload.bride_name)
    customer.phone = phone
    customer.phone_2 = _clean_optional(payload.phone_2)
    customer.registration_date = datetime.date.fromisoformat(payload.registration_date) if payload.registration_date else None
    customer.email = _clean_optional(payload.email)
    customer.address = _clean_optional(payload.address)
    customer.notes = _clean_optional(payload.notes)
    customer.is_active = payload.is_active
    customer.updated_by_user_id = actor.id
    customer.entity_version += 1
    record_audit(
        db,
        actor_user_id=actor.id,
        action="customer.updated",
        target_type="customer",
        target_id=customer.id,
        summary=f"Updated customer {customer.full_name}",
        diff={"phone": customer.phone, "is_active": customer.is_active, "entity_version": customer.entity_version},
    )
    db.commit()
    db.refresh(customer)
    return _serialize_customer(customer)


def archive_customer(db: Session, actor: User, customer_id: str, reason: str | None = None) -> dict:
    repo = CustomersRepository(db)
    customer = _get_company_customer_or_404(db, repo, customer_id)
    if not customer.is_active:
        raise ValidationAppError("العميل مؤرشف بالفعل")
    customer.is_active = False
    customer.updated_by_user_id = actor.id
    customer.entity_version += 1
    normalized_reason = _clean_optional(reason)
    record_audit(
        db,
        actor_user_id=actor.id,
        action="customer.archived",
        target_type="customer",
        target_id=customer.id,
        summary=f"Archived customer {customer.full_name}",
        diff={"is_active": customer.is_active, "reason": normalized_reason, "entity_version": customer.entity_version},
    )
    db.commit()
    db.refresh(customer)
    return _serialize_customer(customer)


def restore_customer(db: Session, actor: User, customer_id: str, reason: str | None = None) -> dict:
    repo = CustomersRepository(db)
    customer = _get_company_customer_or_404(db, repo, customer_id)
    if customer.is_active:
        raise ValidationAppError("العميل نشط بالفعل")
    customer.is_active = True
    customer.updated_by_user_id = actor.id
    customer.entity_version += 1
    normalized_reason = _clean_optional(reason)
    record_audit(
        db,
        actor_user_id=actor.id,
        action="customer.restored",
        target_type="customer",
        target_id=customer.id,
        summary=f"Restored customer {customer.full_name}",
        diff={"is_active": customer.is_active, "reason": normalized_reason, "entity_version": customer.entity_version},
    )
    db.commit()
    db.refresh(customer)
    return _serialize_customer(customer)


def _serialize_customer(customer: Customer) -> dict:
    return {
        "id": customer.id,
        "company_id": customer.company_id,
        "created_by_user_id": customer.created_by_user_id,
        "updated_by_user_id": customer.updated_by_user_id,
        "entity_version": customer.entity_version,
        "registration_date": customer.registration_date.isoformat() if customer.registration_date else None,
        "full_name": customer.full_name,
        "groom_name": customer.groom_name,
        "bride_name": customer.bride_name,
        "phone": customer.phone,
        "phone_2": customer.phone_2,
        "email": customer.email,
        "address": customer.address,
        "notes": customer.notes,
        "is_active": customer.is_active,
    }


def _clean(value: str) -> str:
    text = norm_text(value)
    if not text:
        raise ValidationAppError("القيمة مطلوبة")
    return text


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    text = norm_text(value)
    return text or None


def _get_company_customer_or_404(db: Session, repo: CustomersRepository, customer_id: str) -> Customer:
    company = get_company_settings(db)
    customer = repo.get_customer(customer_id)
    if customer is None or customer.company_id != company.id:
        raise NotFoundError("لم يتم العثور على العميل")
    return customer
