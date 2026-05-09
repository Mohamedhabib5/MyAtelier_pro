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

    def count_active_customers(self, company_id: str) -> int:
        return CustomersRepository(self.db).count_customers(company_id, is_active=True)

    def count_active_services(self, company_id: str) -> int:
        return CatalogRepository(self.db).count_services(company_id, is_active=True)

    def get_dress_status_summary(self, company_id: str) -> list[dict]:
        return DressesRepository(self.db).get_dress_status_counts(company_id)

    def get_department_service_counts(self, company_id: str) -> dict[str, int]:
        return CatalogRepository(self.db).get_department_service_counts(company_id)

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

    def get_comprehensive_payment_stats(self, company_id: str, branch_id: str | None, date_from: date, date_to: date) -> dict:
        from app.modules.payments.models import PaymentDocument, PaymentAllocation
        from app.modules.bookings.models import BookingLine
        from app.modules.catalog.models import Department
        from app.modules.customers.models import Customer
        from sqlalchemy import func, case
        from decimal import Decimal

        # Base filter for all payment queries in this range
        base_where = [
            PaymentDocument.company_id == company_id,
            PaymentDocument.status != 'voided',
            PaymentDocument.payment_date >= date_from,
            PaymentDocument.payment_date <= date_to
        ]
        if branch_id:
            base_where.append(PaymentDocument.branch_id == branch_id)

        # Net amount expression (collection is positive, refund is negative)
        net_amount_expr = case(
            (PaymentDocument.document_kind == 'refund', -PaymentAllocation.allocated_amount),
            else_=PaymentAllocation.allocated_amount
        )

        # 1. Total Collected
        total_collected = self.db.scalar(
            select(func.sum(net_amount_expr))
            .join(PaymentDocument.allocations)
            .where(*base_where)
        ) or Decimal('0.00')

        # 2. Daily Income
        daily_income_results = self.db.execute(
            select(PaymentDocument.payment_date, func.sum(net_amount_expr))
            .join(PaymentDocument.allocations)
            .where(*base_where)
            .group_by(PaymentDocument.payment_date)
        ).all()
        daily_income = {r[0].isoformat(): r[1] for r in daily_income_results}

        # 3. Department Income
        dept_income_results = self.db.execute(
            select(Department.name, func.sum(net_amount_expr))
            .join(PaymentAllocation.payment_document)
            .join(PaymentAllocation.booking_line)
            .join(BookingLine.department)
            .where(*base_where)
            .group_by(Department.name)
        ).all()
        department_income = {r[0]: r[1] for r in dept_income_results}

        # 4. Client Paid
        client_paid_results = self.db.execute(
            select(Customer.id, Customer.full_name, func.sum(net_amount_expr))
            .join(PaymentDocument.customer)
            .join(PaymentDocument.allocations)
            .where(*base_where)
            .group_by(Customer.id, Customer.full_name)
        ).all()
        client_paid = {r[0]: r[2] for r in client_paid_results}
        client_names = {r[0]: r[1] for r in client_paid_results}

        return {
            "total_collected": total_collected,
            "daily_income": daily_income,
            "department_income": department_income,
            "client_paid": client_paid,
            "client_names": client_names
        }

    def get_comprehensive_booking_stats(self, company_id: str, branch_id: str | None, date_from: date, date_to: date) -> dict:
        from app.modules.bookings.models import Booking, BookingLine
        from app.modules.catalog.models import ServiceCatalogItem
        from app.modules.customers.models import Customer
        from app.modules.payments.models import PaymentAllocation, PaymentDocument
        from sqlalchemy import func
        from decimal import Decimal

        base_where = [
            Booking.company_id == company_id,
            Booking.booking_date >= date_from,
            Booking.booking_date <= date_to
        ]
        if branch_id:
            base_where.append(Booking.branch_id == branch_id)

        # 1. Total and Cancelled Bookings, Booking Status Counts
        status_results = self.db.execute(
            select(Booking.status, func.count(Booking.id))
            .where(*base_where)
            .group_by(Booking.status)
        ).all()
        booking_status = {r[0]: r[1] for r in status_results}
        total_bookings = sum(booking_status.values())
        cancelled_bookings = booking_status.get('cancelled', 0)

        # 2. Client Bookings
        client_bookings_results = self.db.execute(
            select(Customer.id, Customer.full_name, func.count(Booking.id))
            .join(Booking.customer)
            .where(*base_where)
            .group_by(Customer.id, Customer.full_name)
        ).all()
        client_bookings = {r[0]: r[2] for r in client_bookings_results}
        client_names = {r[0]: r[1] for r in client_bookings_results}

        # 3. Top Services (from non-cancelled lines of bookings in range)
        top_services_results = self.db.execute(
            select(ServiceCatalogItem.name, func.count(BookingLine.id))
            .join(BookingLine.booking)
            .join(BookingLine.service)
            .where(*base_where, BookingLine.status != 'cancelled')
            .group_by(ServiceCatalogItem.name)
        ).all()
        top_services = {r[0]: r[1] for r in top_services_results}

        # 4. Total Remaining
        # Sum of line_price for non-cancelled lines
        total_line_price = self.db.scalar(
            select(func.sum(BookingLine.line_price))
            .join(BookingLine.booking)
            .where(*base_where, BookingLine.status != 'cancelled')
        ) or Decimal('0.00')

        # Sum of all allocations for those lines (regardless of payment date)
        total_allocated = self.db.scalar(
            select(func.sum(PaymentAllocation.allocated_amount))
            .join(PaymentAllocation.booking_line)
            .join(BookingLine.booking)
            .join(PaymentAllocation.payment_document)
            .where(*base_where, BookingLine.status != 'cancelled', PaymentDocument.status != 'voided')
        ) or Decimal('0.00')

        total_remaining = total_line_price - total_allocated

        return {
            "total_bookings": total_bookings,
            "cancelled_bookings": cancelled_bookings,
            "booking_status": booking_status,
            "client_bookings": client_bookings,
            "client_names": client_names,
            "top_services": top_services,
            "total_remaining": total_remaining
        }
