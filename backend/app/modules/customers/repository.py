from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer


class CustomersRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_customers(self, company_id: str) -> list[Customer]:
        stmt = select(Customer).where(Customer.company_id == company_id).order_by(Customer.full_name.asc())
        return list(self.db.scalars(stmt))

    def get_customer(self, customer_id: str) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_customer_by_phone(self, company_id: str, phone: str) -> Customer | None:
        stmt = select(Customer).where(Customer.company_id == company_id, Customer.phone == phone)
        return self.db.scalars(stmt).first()

    def add_customer(self, customer: Customer) -> Customer:
        self.db.add(customer)
        return customer
