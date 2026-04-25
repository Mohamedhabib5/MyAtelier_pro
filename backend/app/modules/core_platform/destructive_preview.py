from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.bookings.models import Booking, BookingLine
from app.modules.catalog.models import Department, ServiceCatalogItem
from app.modules.core_platform.destructive_reasons import normalize_destructive_reason_code
from app.modules.core_platform.service import record_audit
from app.modules.dresses.models import DressResource
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings
from app.modules.payments.models import PaymentDocument
from app.modules.customers.models import Customer

DestructiveEntityType = str


def compute_destructive_preview(
    db: Session,
    *,
    entity_type: DestructiveEntityType,
    entity_id: str,
    reason_code: str | None,
    reason_text: str | None = None,
) -> dict:
    normalized_reason_code = normalize_destructive_reason_code(reason_code, action="hard_delete", default_code="entry_mistake")
    company = get_company_settings(db)
    normalized_entity_type = entity_type.strip().lower()

    if normalized_entity_type == "customer":
        payload = _preview_customer(db, company.id, entity_id)
    elif normalized_entity_type == "department":
        payload = _preview_department(db, company.id, entity_id)
    elif normalized_entity_type == "service":
        payload = _preview_service(db, company.id, entity_id)
    elif normalized_entity_type == "dress":
        payload = _preview_dress(db, company.id, entity_id)
    else:
        raise NotFoundError("نوع الكيان غير مدعوم في المعاينة الحالية")

    payload["reason_code"] = normalized_reason_code
    payload["reason_text"] = reason_text
    return payload


def preview_destructive_action(
    db: Session,
    *,
    actor: User,
    entity_type: DestructiveEntityType,
    entity_id: str,
    reason_code: str | None,
    reason_text: str | None = None,
) -> dict:
    payload = compute_destructive_preview(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        reason_text=reason_text,
    )
    record_audit(
        db,
        actor_user_id=actor.id,
        action="destructive.previewed",
        target_type=payload["entity_type"],
        target_id=payload["entity_id"],
        summary=f"Previewed destructive action for {payload['entity_type']}",
        diff={
            "eligible_for_hard_delete": payload["eligible_for_hard_delete"],
            "reason_code": payload["reason_code"],
            "impact": payload["impact"],
            "blockers": payload["blockers"],
        },
    )
    db.commit()
    return payload


def _preview_customer(db: Session, company_id: str, customer_id: str) -> dict:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.company_id != company_id:
        raise NotFoundError("لم يتم العثور على العميل")
    booking_count = _count(db, select(func.count()).select_from(Booking).where(Booking.company_id == company_id, Booking.customer_id == customer.id))
    payment_count = _count(db, select(func.count()).select_from(PaymentDocument).where(PaymentDocument.company_id == company_id, PaymentDocument.customer_id == customer.id))
    blockers: list[str] = []
    if booking_count > 0:
        blockers.append("لا يمكن الحذف لوجود حجوزات مرتبطة بهذا العميل")
    if payment_count > 0:
        blockers.append("لا يمكن الحذف لوجود سندات دفع مرتبطة بهذا العميل")
    return {
        "entity_type": "customer",
        "entity_id": customer.id,
        "entity_label": customer.full_name,
        "recommended_action": "archive",
        "eligible_for_hard_delete": not blockers,
        "blockers": blockers,
        "impact": {"bookings_count": booking_count, "payment_documents_count": payment_count},
    }


def _preview_department(db: Session, company_id: str, department_id: str) -> dict:
    department = db.get(Department, department_id)
    if department is None or department.company_id != company_id:
        raise NotFoundError("لم يتم العثور على القسم")
    services_count = _count(
        db,
        select(func.count()).select_from(ServiceCatalogItem).where(
            ServiceCatalogItem.company_id == company_id,
            ServiceCatalogItem.department_id == department.id,
        ),
    )
    booking_lines_count = _count(
        db,
        select(func.count()).select_from(BookingLine).join(Booking, Booking.id == BookingLine.booking_id).where(
            Booking.company_id == company_id,
            BookingLine.department_id == department.id,
        ),
    )
    blockers: list[str] = []
    if services_count > 0:
        blockers.append("لا يمكن الحذف لوجود خدمات مرتبطة بهذا القسم")
    if booking_lines_count > 0:
        blockers.append("لا يمكن الحذف لوجود بنود حجوزات مرتبطة بهذا القسم")
    return {
        "entity_type": "department",
        "entity_id": department.id,
        "entity_label": department.name,
        "recommended_action": "archive",
        "eligible_for_hard_delete": not blockers,
        "blockers": blockers,
        "impact": {"services_count": services_count, "booking_lines_count": booking_lines_count},
    }


def _preview_service(db: Session, company_id: str, service_id: str) -> dict:
    service = db.get(ServiceCatalogItem, service_id)
    if service is None or service.company_id != company_id:
        raise NotFoundError("لم يتم العثور على الخدمة")
    booking_lines_count = _count(
        db,
        select(func.count()).select_from(BookingLine).join(Booking, Booking.id == BookingLine.booking_id).where(
            Booking.company_id == company_id,
            BookingLine.service_id == service.id,
        ),
    )
    blockers = ["لا يمكن الحذف لوجود بنود حجوزات مرتبطة بهذه الخدمة"] if booking_lines_count > 0 else []
    return {
        "entity_type": "service",
        "entity_id": service.id,
        "entity_label": service.name,
        "recommended_action": "archive",
        "eligible_for_hard_delete": not blockers,
        "blockers": blockers,
        "impact": {"booking_lines_count": booking_lines_count},
    }


def _preview_dress(db: Session, company_id: str, dress_id: str) -> dict:
    dress = db.get(DressResource, dress_id)
    if dress is None or dress.company_id != company_id:
        raise NotFoundError("لم يتم العثور على الفستان")
    booking_lines_count = _count(
        db,
        select(func.count()).select_from(BookingLine).join(Booking, Booking.id == BookingLine.booking_id).where(
            Booking.company_id == company_id,
            BookingLine.dress_id == dress.id,
        ),
    )
    blockers = ["لا يمكن الحذف لوجود بنود حجوزات مرتبطة بهذا الفستان"] if booking_lines_count > 0 else []
    return {
        "entity_type": "dress",
        "entity_id": dress.id,
        "entity_label": dress.code,
        "recommended_action": "archive",
        "eligible_for_hard_delete": not blockers,
        "blockers": blockers,
        "impact": {"booking_lines_count": booking_lines_count},
    }


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)
