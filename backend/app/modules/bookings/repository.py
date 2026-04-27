from __future__ import annotations

from datetime import date

from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modules.bookings.models import Booking, BookingLine
from app.modules.catalog.models import ServiceCatalogItem
from app.modules.customers.models import Customer
from app.modules.organization.models import DocumentSequence
from app.modules.payments.models import PaymentAllocation, PaymentDocument


class BookingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_bookings(self, company_id: str, branch_id: str | None = None, customer_id: str | None = None) -> list[Booking]:
        stmt = self._booking_query().where(Booking.company_id == company_id)
        if branch_id:
            stmt = stmt.where(Booking.branch_id == branch_id)
        if customer_id:
            stmt = stmt.where(Booking.customer_id == customer_id)
        stmt = stmt.order_by(Booking.booking_date.desc(), Booking.created_at.desc())
        return list(self.db.scalars(stmt))

    def list_booking_page(
        self,
        company_id: str,
        *,
        branch_id: str | None = None,
        customer_id: str | None = None,
        search: str | None = None,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        page_size: int = 25,
        sort_by: str = 'booking_date',
        sort_dir: str = 'desc',
    ) -> tuple[list[Booking], int]:
        stmt = select(Booking.id).join(Booking.customer).outerjoin(Booking.lines).outerjoin(BookingLine.service).where(Booking.company_id == company_id)
        if branch_id:
            stmt = stmt.where(Booking.branch_id == branch_id)
        if customer_id:
            stmt = stmt.where(Booking.customer_id == customer_id)
        if status:
            stmt = stmt.where(Booking.status == status)
        if date_from:
            stmt = stmt.where(Booking.booking_date >= date_from)
        if date_to:
            stmt = stmt.where(Booking.booking_date <= date_to)
        if search:
            pattern = f'%{search.strip()}%'
            stmt = stmt.where(
                or_(
                    Booking.booking_number.ilike(pattern),
                    Customer.full_name.ilike(pattern),
                    Customer.phone.ilike(pattern),
                    Booking.notes.ilike(pattern),
                    Booking.external_code.ilike(pattern),
                    ServiceCatalogItem.name.ilike(pattern),
                )
            )

        sort_column = {
            'booking_number': Booking.booking_number,
            'customer_name': Customer.full_name,
            'status': Booking.status,
            'next_service_date': Booking.booking_date,
            'booking_date': Booking.booking_date,
        }.get(sort_by, Booking.booking_date)
        sort_expression = sort_column.asc() if sort_dir == 'asc' else sort_column.desc()
        id_stmt = stmt.with_only_columns(Booking.id).distinct()
        total = self.db.scalar(select(func.count()).select_from(id_stmt.subquery())) or 0

        ordered_id_rows = self.db.execute(
            stmt.with_only_columns(
                Booking.id,
                sort_column.label('_sort_value'),
                Booking.created_at.label('_created_at'),
            )
            .group_by(Booking.id, sort_column, Booking.created_at)
            .order_by(sort_expression, Booking.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        ids = [row[0] for row in ordered_id_rows]
        if not ids:
            return [], total

        rows = list(self.db.scalars(self._booking_query().where(Booking.id.in_(ids))))
        order_map = {booking_id: index for index, booking_id in enumerate(ids)}
        rows.sort(key=lambda row: order_map.get(row.id, len(order_map)))
        return rows, total

    def list_calendar_lines(
        self,
        company_id: str,
        *,
        branch_id: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        department_ids: list[str] | None = None,
        service_ids: list[str] | None = None,
        date_mode: str = "service",
    ) -> list[BookingLine]:
        stmt = (
            select(BookingLine)
            .join(BookingLine.booking)
            .join(BookingLine.department)
            .join(BookingLine.service)
            .join(Booking.customer)
            .where(Booking.company_id == company_id)
        )
        if branch_id:
            stmt = stmt.where(Booking.branch_id == branch_id)
        if department_ids:
            stmt = stmt.where(BookingLine.department_id.in_(department_ids))
        if service_ids:
            stmt = stmt.where(BookingLine.service_id.in_(service_ids))
        
        date_col = BookingLine.service_date if date_mode == "service" else Booking.booking_date
        if date_from:
            stmt = stmt.where(date_col >= date_from)
        if date_to:
            stmt = stmt.where(date_col <= date_to)

        stmt = stmt.options(
            joinedload(BookingLine.booking).joinedload(Booking.customer),
            joinedload(BookingLine.department),
            joinedload(BookingLine.service),
        )
        return list(self.db.scalars(stmt))

    def get_booking(self, booking_id: str) -> Booking | None:
        stmt = self._booking_query().where(Booking.id == booking_id)
        return self.db.scalars(stmt).first()

    def add_booking(self, booking: Booking) -> Booking:
        self.db.add(booking)
        return booking

    def get_document_sequence(self, company_id: str, key: str) -> DocumentSequence | None:
        stmt = select(DocumentSequence).where(DocumentSequence.company_id == company_id, DocumentSequence.key == key)
        return self.db.scalars(stmt).first()

    def add_document_sequence(self, sequence: DocumentSequence) -> DocumentSequence:
        self.db.add(sequence)
        return sequence

    def reserve_sequence_number(self, company_id: str, key: str) -> str:
        sequence = self.get_document_sequence(company_id, key)
        if sequence is None:
            raise ValueError(f'Missing document sequence: {key}')
        value = sequence.next_number
        sequence.next_number += 1
        return f"{sequence.prefix}{value:0{sequence.padding}d}"

    def find_dress_conflict(self, company_id: str, dress_id: str, service_date: date, ignore_line_id: str | None = None) -> BookingLine | None:
        stmt = (
            select(BookingLine)
            .join(BookingLine.booking)
            .where(
                Booking.company_id == company_id,
                BookingLine.dress_id == dress_id,
                BookingLine.service_date == service_date,
                BookingLine.status != 'cancelled',
            )
        )
        if ignore_line_id:
            stmt = stmt.where(BookingLine.id != ignore_line_id)
        return self.db.scalars(stmt).first()

    def _booking_query(self):
        return (
            select(Booking)
            .options(
                joinedload(Booking.branch),
                joinedload(Booking.customer),
                selectinload(Booking.lines).joinedload(BookingLine.department),
                selectinload(Booking.lines).joinedload(BookingLine.service).joinedload(ServiceCatalogItem.department),
                selectinload(Booking.lines).joinedload(BookingLine.dress),
                selectinload(Booking.lines).joinedload(BookingLine.revenue_journal_entry),
                selectinload(Booking.lines)
                .selectinload(BookingLine.payment_allocations)
                .joinedload(PaymentAllocation.payment_document)
                .joinedload(PaymentDocument.journal_entry),
            )
        )
