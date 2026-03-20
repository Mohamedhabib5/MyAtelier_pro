from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modules.bookings.models import Booking, BookingLine
from app.modules.catalog.models import ServiceCatalogItem
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
