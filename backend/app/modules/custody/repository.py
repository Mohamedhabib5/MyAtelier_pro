from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.bookings.models import Booking
from app.modules.custody.models import CustodyCase
from app.modules.customers.models import Customer
from app.modules.dresses.models import DressResource


class CustodyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_cases_detailed(self, company_id: str, branch_id: str, *, view: str = "all"):
        stmt = (
            select(CustodyCase, Customer.full_name, Booking.booking_number, DressResource.code)
            .join(Customer, CustodyCase.customer_id == Customer.id, isouter=True)
            .join(Booking, CustodyCase.booking_id == Booking.id, isouter=True)
            .join(DressResource, CustodyCase.dress_id == DressResource.id, isouter=True)
            .where(CustodyCase.company_id == company_id, CustodyCase.branch_id == branch_id)
        )
        if view == "settled":
            stmt = stmt.where(CustodyCase.status == "settled")
        elif view == "open":
            stmt = stmt.where(CustodyCase.status != "settled")
        stmt = stmt.order_by(CustodyCase.custody_date.desc(), CustodyCase.created_at.desc())
        return self.db.execute(stmt).all()

    def get_case(self, case_id: str) -> CustodyCase | None:
        return self.db.get(CustodyCase, case_id)

    def get_case_by_booking_line(self, company_id: str, branch_id: str, booking_line_id: str) -> CustodyCase | None:
        stmt = select(CustodyCase).where(
            CustodyCase.company_id == company_id,
            CustodyCase.branch_id == branch_id,
            CustodyCase.booking_line_id == booking_line_id,
        )
        return self.db.scalars(stmt).first()

    def add_case(self, custody_case: CustodyCase) -> CustodyCase:
        self.db.add(custody_case)
        return custody_case

    def next_case_number(self, company_id: str, branch_id: str) -> str:
        count_stmt = select(func.count()).select_from(CustodyCase).where(
            CustodyCase.company_id == company_id,
            CustodyCase.branch_id == branch_id,
        )
        next_number = int(self.db.scalar(count_stmt) or 0) + 1
        return f"CUS-{next_number:06d}"
