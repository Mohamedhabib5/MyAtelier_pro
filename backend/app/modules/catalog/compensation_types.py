from sqlalchemy.orm import Session
from app.modules.catalog.models import Department, ServiceCatalogItem
from app.modules.catalog.repository import CatalogRepository
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings
from app.modules.core_platform.service import record_audit
from decimal import Decimal
from pydantic import BaseModel, Field

SYS_COMPENSATIONS_CODE = 'SYS-COMPENSATIONS'
SYS_COMPENSATIONS_NAME = 'تعويضات وغرامات'

class CompensationTypeCreateRequest(BaseModel):
    department_id: str | None = None
    name: str = Field(min_length=2, max_length=120)
    default_price: float = Field(ge=0)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    notes: str | None = None
    display_order: int = 0

class CompensationTypeUpdateRequest(BaseModel):
    department_id: str | None = None
    name: str = Field(min_length=2, max_length=120)
    default_price: float = Field(ge=0)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    notes: str | None = None
    display_order: int = 0
    is_active: bool = True

def _ensure_sys_compensations_department(db: Session, company_id: str) -> Department:
    repo = CatalogRepository(db)
    dept = repo.get_department_by_code(company_id, SYS_COMPENSATIONS_CODE)
    if not dept:
        # Create it
        # We need an actor, but this is a system action. We can use None or a default admin.
        # But this function might be called when user views settings.
        dept = Department(
            company_id=company_id,
            code=SYS_COMPENSATIONS_CODE,
            name=SYS_COMPENSATIONS_NAME,
            is_active=True,
            is_dress_department=False,
            display_order=9999
        )
        repo.add_department(dept)
        db.flush()
    return dept

def list_compensation_types(db: Session) -> list[dict]:
    from app.modules.catalog.lifecycle import _serialize_service
    company = get_company_settings(db)
    dept = _ensure_sys_compensations_department(db, company.id)
    
    # We query services manually to include inactive ones if needed, or just active.
    # The user wants a settings page, so we return all (active and inactive) so they can edit.
    repo = CatalogRepository(db)
    # Filter only those belonging to the SYS department
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload
    stmt = (
        select(ServiceCatalogItem)
        .options(joinedload(ServiceCatalogItem.department))
        .where(
            ServiceCatalogItem.company_id == company.id,
            ServiceCatalogItem.department_id == dept.id
        )
        .order_by(ServiceCatalogItem.display_order.asc(), ServiceCatalogItem.name.asc())
    )
    items = list(db.scalars(stmt))
    return [_serialize_service(item) for item in items]

def create_compensation_type(db: Session, actor: User, payload: CompensationTypeCreateRequest) -> dict:
    from app.modules.catalog.lifecycle import _serialize_service
    company = get_company_settings(db)
    dept = _ensure_sys_compensations_department(db, company.id)
    
    service = ServiceCatalogItem(
        company_id=company.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        department_id=dept.id,
        name=payload.name.strip(),
        default_price=Decimal(str(payload.default_price)),
        tax_rate_percent=Decimal("0.00"),
        duration_minutes=payload.duration_minutes,
        notes=payload.notes,
        is_active=True,
        display_order=payload.display_order,
    )
    CatalogRepository(db).add_service(service)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="compensation_type.created",
        target_type="service",
        target_id=service.id,
        summary=f"Created compensation type {service.name}",
        diff={"name": service.name, "default_price": float(service.default_price)},
    )
    db.commit()
    db.refresh(service)
    return _serialize_service(service)

def update_compensation_type(db: Session, actor: User, service_id: str, payload: CompensationTypeUpdateRequest) -> dict:
    from app.modules.catalog.lifecycle import _get_service_for_active_company, _serialize_service
    repo = CatalogRepository(db)
    service = _get_service_for_active_company(db, repo, service_id)
    
    company = get_company_settings(db)
    dept = _ensure_sys_compensations_department(db, company.id)
    if service.department_id != dept.id:
        from app.core.exceptions import ValidationAppError
        raise ValidationAppError("هذا العنصر ليس نوع تعويض")

    service.name = payload.name.strip()
    service.default_price = Decimal(str(payload.default_price))
    service.duration_minutes = payload.duration_minutes
    service.notes = payload.notes
    service.display_order = payload.display_order
    service.is_active = payload.is_active
    service.updated_by_user_id = actor.id
    service.entity_version += 1

    record_audit(
        db,
        actor_user_id=actor.id,
        action="compensation_type.updated",
        target_type="service",
        target_id=service.id,
        summary=f"Updated compensation type {service.name}",
        diff={"name": service.name, "default_price": float(service.default_price), "entity_version": service.entity_version},
    )
    db.commit()
    db.refresh(service)
    return _serialize_service(service)
