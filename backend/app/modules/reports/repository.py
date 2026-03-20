from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.bookings.repository import BookingsRepository
from app.modules.catalog.repository import CatalogRepository
from app.modules.customers.repository import CustomersRepository
from app.modules.dresses.repository import DressesRepository
from app.modules.payments.repository import PaymentsRepository


class ReportsRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_customers(self, company_id: str):
        return CustomersRepository(self.db).list_customers(company_id)

    def list_departments(self, company_id: str):
        return CatalogRepository(self.db).list_departments(company_id)

    def list_services(self, company_id: str):
        return CatalogRepository(self.db).list_services(company_id)

    def list_dresses(self, company_id: str):
        return DressesRepository(self.db).list_dresses(company_id)

    def list_bookings(self, company_id: str, branch_id: str | None = None):
        return BookingsRepository(self.db).list_bookings(company_id, branch_id)

    def list_payment_documents(self, company_id: str, branch_id: str | None = None):
        return PaymentsRepository(self.db).list_payment_documents(company_id, branch_id)
