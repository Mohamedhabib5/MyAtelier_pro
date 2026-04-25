from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.modules.catalog.models import Department, ServiceCatalogItem
from app.modules.core_platform.destructive_preview import compute_destructive_preview
from app.modules.core_platform.period_lock import enforce_not_locked_with_override, record_period_lock_override
from app.modules.core_platform.service import record_audit
from app.modules.customers.models import Customer
from app.modules.dresses.models import DressResource
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings


def execute_destructive_delete(
    db: Session,
    *,
    actor: User,
    entity_type: str,
    entity_id: str,
    reason_code: str | None,
    reason_text: str | None = None,
    override_lock: bool = False,
    override_reason: str | None = None,
) -> dict:
    override_payload = enforce_not_locked_with_override(
        db,
        action_date=datetime.now(UTC).date(),
        action_key="destructive.delete",
        actor=actor,
        override_lock=override_lock,
        override_reason=override_reason,
    )
    preview = compute_destructive_preview(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        reason_code=reason_code,
        reason_text=reason_text,
    )
    if not preview["eligible_for_hard_delete"]:
        blocker_text = " | ".join(preview["blockers"]) if preview["blockers"] else "الحذف غير مسموح"
        raise ValidationAppError(blocker_text)

    entity = _get_entity_for_delete(db, preview["entity_type"], preview["entity_id"])
    tombstone_before = _serialize_entity_snapshot(preview["entity_type"], entity)
    entity_version_before = getattr(entity, "entity_version", None)
    db.delete(entity)
    db.flush()
    if override_payload is not None:
        record_period_lock_override(
            db,
            actor_user_id=actor.id,
            entity_type=preview["entity_type"],
            entity_id=preview["entity_id"],
            summary=f"Used period-lock override for destructive delete of {preview['entity_label']}",
            override_payload=override_payload,
        )
    record_audit(
        db,
        actor_user_id=actor.id,
        action="destructive.deleted",
        target_type=preview["entity_type"],
        target_id=preview["entity_id"],
        summary=f"Hard deleted {preview['entity_type']} {preview['entity_label']}",
        reason_code=preview["reason_code"],
        reason_text=preview["reason_text"],
        diff={
            "reason_code": preview["reason_code"],
            "reason_text": preview["reason_text"],
            "impact": preview["impact"],
            "entity_version_before": entity_version_before,
            "deleted_at": datetime.now(UTC).isoformat(),
            "tombstone_before": tombstone_before,
        },
    )
    db.commit()
    return {
        "entity_type": preview["entity_type"],
        "entity_id": preview["entity_id"],
        "entity_label": preview["entity_label"],
        "deleted": True,
        "reason_code": preview["reason_code"],
        "reason_text": preview["reason_text"],
        "impact": preview["impact"],
    }


def _get_entity_for_delete(db: Session, entity_type: str, entity_id: str):
    company = get_company_settings(db)
    if entity_type == "customer":
        entity = db.get(Customer, entity_id)
    elif entity_type == "department":
        entity = db.get(Department, entity_id)
    elif entity_type == "service":
        entity = db.get(ServiceCatalogItem, entity_id)
    elif entity_type == "dress":
        entity = db.get(DressResource, entity_id)
    else:
        raise NotFoundError("نوع الكيان غير مدعوم في الحذف التصحيحي")

    if entity is None or getattr(entity, "company_id", None) != company.id:
        raise NotFoundError("لم يتم العثور على السجل المطلوب")
    return entity


def _serialize_entity_snapshot(entity_type: str, entity) -> dict:
    if entity_type == "customer":
        return _convert_snapshot(
            {
                "id": entity.id,
                "company_id": entity.company_id,
                "full_name": entity.full_name,
                "phone": entity.phone,
                "email": entity.email,
                "address": entity.address,
                "notes": entity.notes,
                "is_active": entity.is_active,
                "entity_version": entity.entity_version,
                "created_by_user_id": entity.created_by_user_id,
                "updated_by_user_id": entity.updated_by_user_id,
            }
        )
    if entity_type == "department":
        return _convert_snapshot(
            {
                "id": entity.id,
                "company_id": entity.company_id,
                "code": entity.code,
                "name": entity.name,
                "is_active": entity.is_active,
                "entity_version": entity.entity_version,
                "created_by_user_id": entity.created_by_user_id,
                "updated_by_user_id": entity.updated_by_user_id,
            }
        )
    if entity_type == "service":
        return _convert_snapshot(
            {
                "id": entity.id,
                "company_id": entity.company_id,
                "department_id": entity.department_id,
                "name": entity.name,
                "default_price": entity.default_price,
                "tax_rate_percent": entity.tax_rate_percent,
                "duration_minutes": entity.duration_minutes,
                "notes": entity.notes,
                "is_active": entity.is_active,
                "entity_version": entity.entity_version,
                "created_by_user_id": entity.created_by_user_id,
                "updated_by_user_id": entity.updated_by_user_id,
            }
        )
    if entity_type == "dress":
        return _convert_snapshot(
            {
                "id": entity.id,
                "company_id": entity.company_id,
                "code": entity.code,
                "dress_type": entity.dress_type,
                "purchase_date": entity.purchase_date,
                "status": entity.status,
                "description": entity.description,
                "image_path": entity.image_path,
                "is_active": entity.is_active,
                "entity_version": entity.entity_version,
                "created_by_user_id": entity.created_by_user_id,
                "updated_by_user_id": entity.updated_by_user_id,
            }
        )
    return _convert_snapshot({"id": getattr(entity, "id", None), "entity_type": entity_type})


def _convert_snapshot(data: dict) -> dict:
    converted: dict = {}
    for key, value in data.items():
        if isinstance(value, Decimal):
            converted[key] = float(value)
        elif isinstance(value, (datetime, date)):
            converted[key] = value.isoformat()
        else:
            converted[key] = value
    return converted
