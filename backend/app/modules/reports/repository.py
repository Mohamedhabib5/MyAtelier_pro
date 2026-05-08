from __future__ import annotations

from sqlalchemy import select
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

    def get_booking_status_counts(self, company_id: str, branch_id: str | None = None) -> list[dict]:
        from app.modules.bookings.models import Booking
        from sqlalchemy import func
        stmt = (
            select(Booking.status.label('key'), func.count(Booking.id).label('count'))
            .where(Booking.company_id == company_id)
            .group_by(Booking.status)
        )
        if branch_id:
            stmt = stmt.where(Booking.branch_id == branch_id)
        results = self.db.execute(stmt).all()
        return [{'key': r.key, 'count': r.count} for r in results]

    def get_payment_type_totals(self, company_id: str, branch_id: str | None = None) -> list[dict]:
        from app.modules.payments.models import PaymentDocument, PaymentAllocation
        from sqlalchemy import func
        stmt = (
            select(PaymentDocument.document_kind.label('key'), func.sum(PaymentAllocation.allocated_amount).label('value'))
            .join(PaymentDocument.allocations)
            .where(PaymentDocument.company_id == company_id, PaymentDocument.status != 'voided')
            .group_by(PaymentDocument.document_kind)
        )
        if branch_id:
            stmt = stmt.where(PaymentDocument.branch_id == branch_id)
        results = self.db.execute(stmt).all()
        return [{'key': r.key, 'value': r.value} for r in results]

    def get_upcoming_booking_lines(self, company_id: str, branch_id: str | None = None, limit: int = 50) -> list[dict]:
        from app.modules.bookings.models import Booking, BookingLine
        from datetime import date
        stmt = (
            select(BookingLine)
            .join(BookingLine.booking)
            .where(
                Booking.company_id == company_id,
                BookingLine.status != 'cancelled',
                BookingLine.service_date >= date.today()
            )
            .order_by(BookingLine.service_date.asc())
            .limit(limit)
        )
        if branch_id:
            stmt = stmt.where(Booking.branch_id == branch_id)
        
        lines = self.db.scalars(stmt).all()
        return [
            {
                'booking_number': line.booking.booking_number,
                'customer_name': line.booking.customer.full_name,
                'service_name': line.service.name,
                'service_date': line.service_date.isoformat(),
                'status': line.status
            }
            for line in lines
        ]
