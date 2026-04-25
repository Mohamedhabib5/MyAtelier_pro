from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.catalog.models import Department, ServiceCatalogItem
from app.modules.customers.models import Customer
from app.modules.dresses.models import DressResource


def get_customer_or_404(db: Session, company_id: str, customer_id: str) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.company_id != company_id:
        raise NotFoundError('لم يتم العثور على العميل')
    return customer


def get_department_or_404(db: Session, company_id: str, department_id: str) -> Department:
    department = db.get(Department, department_id)
    if department is None or department.company_id != company_id:
        raise NotFoundError('لم يتم العثور على القسم')
    return department


def get_service_or_404(db: Session, company_id: str, service_id: str) -> ServiceCatalogItem:
    service = db.get(ServiceCatalogItem, service_id)
    if service is None or service.company_id != company_id:
        raise NotFoundError('لم يتم العثور على الخدمة')
    return service


def get_dress_or_404(db: Session, company_id: str, dress_id: str | None) -> DressResource | None:
    if not dress_id:
        return None
    dress = db.get(DressResource, dress_id)
    if dress is None or dress.company_id != company_id:
        raise NotFoundError('لم يتم العثور على الفستان')
    return dress
