from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.catalog.models import Department, ServiceCatalogItem


class CatalogRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_departments(self, company_id: str, *, is_active: bool | None = None) -> list[Department]:
        stmt = select(Department).where(Department.company_id == company_id)
        if is_active is not None:
            stmt = stmt.where(Department.is_active == is_active)
        stmt = stmt.order_by(Department.display_order.asc(), Department.name.asc())
        return list(self.db.scalars(stmt))

    def get_department(self, department_id: str) -> Department | None:
        return self.db.get(Department, department_id)

    def get_department_by_code(self, company_id: str, code: str) -> Department | None:
        stmt = select(Department).where(Department.company_id == company_id, Department.code == code)
        return self.db.scalars(stmt).first()

    def get_dress_department(self, company_id: str) -> Department | None:
        stmt = select(Department).where(Department.company_id == company_id, Department.is_dress_department == True)
        return self.db.scalars(stmt).first()

    def add_department(self, department: Department) -> Department:
        self.db.add(department)
        return department

    def list_services(self, company_id: str, *, is_active: bool | None = None) -> list[ServiceCatalogItem]:
        stmt = (
            select(ServiceCatalogItem)
            .options(joinedload(ServiceCatalogItem.department))
            .where(ServiceCatalogItem.company_id == company_id)
        )
        if is_active is not None:
            stmt = stmt.where(ServiceCatalogItem.is_active == is_active)
        stmt = stmt.order_by(ServiceCatalogItem.display_order.asc(), ServiceCatalogItem.name.asc())
        return list(self.db.scalars(stmt))

    def get_service(self, service_id: str) -> ServiceCatalogItem | None:
        return self.db.get(ServiceCatalogItem, service_id)

    def get_service_by_name(self, company_id: str, name: str) -> ServiceCatalogItem | None:
        stmt = select(ServiceCatalogItem).where(ServiceCatalogItem.company_id == company_id, ServiceCatalogItem.name == name)
        return self.db.scalars(stmt).first()

    def add_service(self, service: ServiceCatalogItem) -> ServiceCatalogItem:
        self.db.add(service)
        return service
