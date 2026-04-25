from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.catalog.models import Department, ServiceCatalogItem
from app.modules.catalog.repository import CatalogRepository
from app.modules.catalog.schemas import DepartmentCreateRequest, DepartmentUpdateRequest, ServiceCreateRequest, ServiceUpdateRequest
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings


PRICE_QUANT = Decimal('0.01')
RATE_QUANT = Decimal('0.01')


def list_departments(db: Session) -> list[dict]:
    company = get_company_settings(db)
    rows = CatalogRepository(db).list_departments(company.id)
    return [_serialize_department(row) for row in rows]


def create_department(db: Session, actor: User, payload: DepartmentCreateRequest) -> dict:
    company = get_company_settings(db)
    repo = CatalogRepository(db)
    code = _clean(payload.code).upper()
    if repo.get_department_by_code(company.id, code) is not None:
        raise ValidationAppError('كود القسم مستخدم بالفعل')


    department = Department(
        company_id=company.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        code=code,
        name=_clean(payload.name),
        is_active=True,
        display_order=payload.display_order,
    )
    repo.add_department(department)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action='department.created',
        target_type='department',
        target_id=department.id,
        summary=f'Created department {department.name}',
        diff={'code': department.code, 'entity_version': department.entity_version},
    )
    db.commit()
    db.refresh(department)
    return _serialize_department(department)


def update_department(db: Session, actor: User, department_id: str, payload: DepartmentUpdateRequest) -> dict:
    company = get_company_settings(db)
    repo = CatalogRepository(db)
    department = _get_department_for_company(repo, company.id, department_id)
    code = _clean(payload.code).upper()
    existing = repo.get_department_by_code(company.id, code)
    if existing is not None and existing.id != department.id:
        raise ValidationAppError('كود القسم مستخدم بالفعل')


    department.code = code
    department.name = _clean(payload.name)
    department.is_active = payload.is_active
    department.display_order = payload.display_order
    department.updated_by_user_id = actor.id
    department.entity_version += 1
    record_audit(
        db,
        actor_user_id=actor.id,
        action='department.updated',
        target_type='department',
        target_id=department.id,
        summary=f'Updated department {department.name}',
        diff={'code': department.code, 'is_active': department.is_active, 'entity_version': department.entity_version},
    )
    db.commit()
    db.refresh(department)
    return _serialize_department(department)


def set_dress_department(db: Session, actor: User, department_id: str) -> dict:
    company = get_company_settings(db)
    repo = CatalogRepository(db)
    department = _get_department_for_company(repo, company.id, department_id)

    if not department.is_active:
        raise ValidationAppError('لا يمكن اختيار قسم غير نشط كقسم للفساتين')

    if not department.is_dress_department:
        _unmark_dress_departments(db, company.id)
        department.is_dress_department = True
        department.updated_by_user_id = actor.id
        department.entity_version += 1
        db.flush()
        record_audit(
            db,
            actor_user_id=actor.id,
            action='department.set_dress_department',
            target_type='department',
            target_id=department.id,
            summary=f'Set department {department.name} as the dresses department',
            diff={'is_dress_department': True, 'entity_version': department.entity_version},
        )
        db.commit()
        db.refresh(department)

    return _serialize_department(department)


def list_services(db: Session) -> list[dict]:
    company = get_company_settings(db)
    rows = CatalogRepository(db).list_services(company.id)
    return [_serialize_service(row) for row in rows]


def create_service(db: Session, actor: User, payload: ServiceCreateRequest) -> dict:
    company = get_company_settings(db)
    repo = CatalogRepository(db)
    department = _get_department_for_company(repo, company.id, payload.department_id)
    name = _clean(payload.name)
    if repo.get_service_by_name(company.id, name) is not None:
        raise ValidationAppError('اسم الخدمة مستخدم بالفعل')

    service = ServiceCatalogItem(
        company_id=company.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        department_id=department.id,
        name=name,
        default_price=_clean_price(payload.default_price),
        tax_rate_percent=_clean_tax_rate(payload.tax_rate_percent),
        duration_minutes=payload.duration_minutes,
        notes=_clean_optional(payload.notes),
        is_active=True,
        display_order=payload.display_order,
    )
    repo.add_service(service)
    db.flush()
    db.refresh(service)
    record_audit(
        db,
        actor_user_id=actor.id,
        action='service.created',
        target_type='service',
        target_id=service.id,
        summary=f'Created service {service.name}',
        diff={
            'department_id': service.department_id,
            'default_price': float(service.default_price),
            'tax_rate_percent': float(service.tax_rate_percent),
            'entity_version': service.entity_version,
        },
    )
    db.commit()
    db.refresh(service)
    return _serialize_service(service)


def update_service(db: Session, actor: User, service_id: str, payload: ServiceUpdateRequest) -> dict:
    company = get_company_settings(db)
    repo = CatalogRepository(db)
    service = _get_service_for_company(repo, company.id, service_id)
    department = _get_department_for_company(repo, company.id, payload.department_id)
    name = _clean(payload.name)
    existing = repo.get_service_by_name(company.id, name)
    if existing is not None and existing.id != service.id:
        raise ValidationAppError('اسم الخدمة مستخدم بالفعل')

    service.department_id = department.id
    service.name = name
    service.default_price = _clean_price(payload.default_price)
    service.tax_rate_percent = _clean_tax_rate(payload.tax_rate_percent)
    service.duration_minutes = payload.duration_minutes
    service.notes = _clean_optional(payload.notes)
    service.is_active = payload.is_active
    service.display_order = payload.display_order
    service.updated_by_user_id = actor.id
    service.entity_version += 1
    db.flush()
    db.refresh(service)
    record_audit(
        db,
        actor_user_id=actor.id,
        action='service.updated',
        target_type='service',
        target_id=service.id,
        summary=f'Updated service {service.name}',
        diff={
            'department_id': service.department_id,
            'default_price': float(service.default_price),
            'tax_rate_percent': float(service.tax_rate_percent),
            'is_active': service.is_active,
            'entity_version': service.entity_version,
        },
    )
    db.commit()
    db.refresh(service)
    return _serialize_service(service)


def _get_department_for_company(repo: CatalogRepository, company_id: str, department_id: str) -> Department:
    department = repo.get_department(department_id)
    if department is None or department.company_id != company_id:
        raise NotFoundError('لم يتم العثور على القسم')
    return department


def _get_service_for_company(repo: CatalogRepository, company_id: str, service_id: str) -> ServiceCatalogItem:
    service = repo.get_service(service_id)
    if service is None or service.company_id != company_id:
        raise NotFoundError('لم يتم العثور على الخدمة')
    return service


def _serialize_department(department: Department) -> dict:
    return {
        'id': department.id,
        'company_id': department.company_id,
        'created_by_user_id': department.created_by_user_id,
        'updated_by_user_id': department.updated_by_user_id,
        'entity_version': department.entity_version,
        'code': department.code,
        'name': department.name,
        'is_active': department.is_active,
        'is_dress_department': department.is_dress_department,
        'display_order': department.display_order,
    }

def _unmark_dress_departments(db: Session, company_id: str):
    repo = CatalogRepository(db)
    current = repo.get_dress_department(company_id)
    if current:
        current.is_dress_department = False
        db.flush()


def _serialize_service(service: ServiceCatalogItem) -> dict:
    return {
        'id': service.id,
        'company_id': service.company_id,
        'created_by_user_id': service.created_by_user_id,
        'updated_by_user_id': service.updated_by_user_id,
        'entity_version': service.entity_version,
        'department_id': service.department_id,
        'department_name': service.department.name,
        'name': service.name,
        'default_price': float(service.default_price),
        'tax_rate_percent': float(service.tax_rate_percent),
        'duration_minutes': service.duration_minutes,
        'notes': service.notes,
        'is_active': service.is_active,
        'display_order': service.display_order,
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


def _clean_price(value: float) -> Decimal:
    amount = Decimal(str(value)).quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)
    if amount < Decimal('0'):
        raise ValidationAppError('لا يمكن أن يكون السعر سالبًا')
    return amount


def _clean_tax_rate(value: float) -> Decimal:
    rate = Decimal(str(value)).quantize(RATE_QUANT, rounding=ROUND_HALF_UP)
    if rate < Decimal('0') or rate > Decimal('100'):
        raise ValidationAppError('نسبة الضريبة يجب أن تكون بين 0 و 100')
    return rate
