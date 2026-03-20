from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.core_platform.service import record_audit
from app.modules.customers.models import Customer
from app.modules.customers.repository import CustomersRepository
from app.modules.customers.schemas import CustomerCreateRequest, CustomerUpdateRequest
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings


def list_customers(db: Session) -> list[dict]:
    company = get_company_settings(db)
    rows = CustomersRepository(db).list_customers(company.id)
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
        full_name=_clean(payload.full_name),
        phone=phone,
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
        diff={"phone": customer.phone},
    )
    db.commit()
    db.refresh(customer)
    return _serialize_customer(customer)


def update_customer(db: Session, actor: User, customer_id: str, payload: CustomerUpdateRequest) -> dict:
    company = get_company_settings(db)
    repo = CustomersRepository(db)
    customer = repo.get_customer(customer_id)
    if customer is None or customer.company_id != company.id:
        raise NotFoundError("لم يتم العثور على العميل")

    phone = _clean(payload.phone)
    existing = repo.get_customer_by_phone(company.id, phone)
    if existing is not None and existing.id != customer.id:
        raise ValidationAppError("رقم هاتف العميل مستخدم بالفعل")

    customer.full_name = _clean(payload.full_name)
    customer.phone = phone
    customer.email = _clean_optional(payload.email)
    customer.address = _clean_optional(payload.address)
    customer.notes = _clean_optional(payload.notes)
    customer.is_active = payload.is_active
    record_audit(
        db,
        actor_user_id=actor.id,
        action="customer.updated",
        target_type="customer",
        target_id=customer.id,
        summary=f"Updated customer {customer.full_name}",
        diff={"phone": customer.phone, "is_active": customer.is_active},
    )
    db.commit()
    db.refresh(customer)
    return _serialize_customer(customer)


def _serialize_customer(customer: Customer) -> dict:
    return {
        "id": customer.id,
        "company_id": customer.company_id,
        "full_name": customer.full_name,
        "phone": customer.phone,
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
