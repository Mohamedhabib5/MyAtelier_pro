from __future__ import annotations

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer


class CustomersRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_customers(self, company_id: str, *, is_active: bool | None = None) -> list[Customer]:
        stmt = select(Customer).where(Customer.company_id == company_id)
        if is_active is not None:
            stmt = stmt.where(Customer.is_active == is_active)
        stmt = stmt.order_by(Customer.full_name.asc())
        return list(self.db.scalars(stmt))

    def get_customer(self, customer_id: str) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_customer_by_phone(self, company_id: str, phone: str) -> Customer | None:
        stmt = select(Customer).where(Customer.company_id == company_id, Customer.phone == phone)
        return self.db.scalars(stmt).first()

    def add_customer(self, customer: Customer) -> Customer:
        self.db.add(customer)
        return customer

    def search_customers(self, company_id: str, query: str, limit: int = 20) -> list[Customer]:
        if not query:
            return []
        pattern = f"%{query.strip()}%"
        stmt = (
            select(Customer)
            .where(
                Customer.company_id == company_id,
                or_(
                    Customer.full_name.ilike(pattern),
                    Customer.phone.ilike(pattern)
                )
            )
            .order_by(Customer.full_name.asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))
