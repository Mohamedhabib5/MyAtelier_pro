from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.catalog.models import Department, ServiceCatalogItem
from app.modules.catalog.repository import CatalogRepository
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings


def list_departments(db: Session, *, is_active: bool | None = None) -> list[dict]:
    company = get_company_settings(db)
    rows = CatalogRepository(db).list_departments(company.id, is_active=is_active)
    return [_serialize_department(row) for row in rows]


def list_services(db: Session, *, is_active: bool | None = None) -> list[dict]:
    company = get_company_settings(db)
    rows = CatalogRepository(db).list_services(company.id, is_active=is_active)
    return [_serialize_service(row) for row in rows]


def archive_department(db: Session, actor: User, department_id: str, reason: str | None = None) -> dict:
    repo = CatalogRepository(db)
    department = _get_department_for_active_company(db, repo, department_id)
    if not department.is_active:
        raise ValidationAppError("القسم مؤرشف بالفعل")
    department.is_active = False
    department.updated_by_user_id = actor.id
    department.entity_version += 1
    normalized_reason = _clean_optional(reason)
    record_audit(
        db,
        actor_user_id=actor.id,
        action="department.archived",
        target_type="department",
        target_id=department.id,
        summary=f"Archived department {department.name}",
        diff={"is_active": department.is_active, "reason": normalized_reason, "entity_version": department.entity_version},
    )
    db.commit()
    db.refresh(department)
    return _serialize_department(department)


def restore_department(db: Session, actor: User, department_id: str, reason: str | None = None) -> dict:
    repo = CatalogRepository(db)
    department = _get_department_for_active_company(db, repo, department_id)
    if department.is_active:
        raise ValidationAppError("القسم نشط بالفعل")
    department.is_active = True
    department.updated_by_user_id = actor.id
    department.entity_version += 1
    normalized_reason = _clean_optional(reason)
    record_audit(
        db,
        actor_user_id=actor.id,
        action="department.restored",
        target_type="department",
        target_id=department.id,
        summary=f"Restored department {department.name}",
        diff={"is_active": department.is_active, "reason": normalized_reason, "entity_version": department.entity_version},
    )
    db.commit()
    db.refresh(department)
    return _serialize_department(department)


def archive_service(db: Session, actor: User, service_id: str, reason: str | None = None) -> dict:
    repo = CatalogRepository(db)
    service = _get_service_for_active_company(db, repo, service_id)
    if not service.is_active:
        raise ValidationAppError("الخدمة مؤرشفة بالفعل")
    service.is_active = False
    service.updated_by_user_id = actor.id
    service.entity_version += 1
    normalized_reason = _clean_optional(reason)
    db.flush()
    db.refresh(service)
    record_audit(
        db,
        actor_user_id=actor.id,
        action="service.archived",
        target_type="service",
        target_id=service.id,
        summary=f"Archived service {service.name}",
        diff={"is_active": service.is_active, "reason": normalized_reason, "entity_version": service.entity_version},
    )
    db.commit()
    db.refresh(service)
    return _serialize_service(service)


def restore_service(db: Session, actor: User, service_id: str, reason: str | None = None) -> dict:
    repo = CatalogRepository(db)
    service = _get_service_for_active_company(db, repo, service_id)
    if service.is_active:
        raise ValidationAppError("الخدمة نشطة بالفعل")
    service.is_active = True
    service.updated_by_user_id = actor.id
    service.entity_version += 1
    normalized_reason = _clean_optional(reason)
    db.flush()
    db.refresh(service)
    record_audit(
        db,
        actor_user_id=actor.id,
        action="service.restored",
        target_type="service",
        target_id=service.id,
        summary=f"Restored service {service.name}",
        diff={"is_active": service.is_active, "reason": normalized_reason, "entity_version": service.entity_version},
    )
    db.commit()
    db.refresh(service)
    return _serialize_service(service)


def _get_department_for_active_company(db: Session, repo: CatalogRepository, department_id: str) -> Department:
    company = get_company_settings(db)
    department = repo.get_department(department_id)
    if department is None or department.company_id != company.id:
        raise NotFoundError("لم يتم العثور على القسم")
    return department


def _get_service_for_active_company(db: Session, repo: CatalogRepository, service_id: str) -> ServiceCatalogItem:
    company = get_company_settings(db)
    service = repo.get_service(service_id)
    if service is None or service.company_id != company.id:
        raise NotFoundError("لم يتم العثور على الخدمة")
    return service


def _serialize_department(department: Department) -> dict:
    return {
        "id": department.id,
        "company_id": department.company_id,
        "created_by_user_id": department.created_by_user_id,
        "updated_by_user_id": department.updated_by_user_id,
        "entity_version": department.entity_version,
        "code": department.code,
        "name": department.name,
        "is_active": department.is_active,
    }


def _serialize_service(service: ServiceCatalogItem) -> dict:
    return {
        "id": service.id,
        "company_id": service.company_id,
        "created_by_user_id": service.created_by_user_id,
        "updated_by_user_id": service.updated_by_user_id,
        "entity_version": service.entity_version,
        "department_id": service.department_id,
        "department_name": service.department.name,
        "name": service.name,
        "default_price": float(service.default_price),
        "tax_rate_percent": float(service.tax_rate_percent),
        "duration_minutes": service.duration_minutes,
        "notes": service.notes,
        "is_active": service.is_active,
    }


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    text = norm_text(value)
    return text or None
