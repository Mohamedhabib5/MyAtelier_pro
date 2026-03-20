from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modules.bookings.models import Booking, BookingLine
from app.modules.catalog.models import ServiceCatalogItem
from app.modules.organization.models import DocumentSequence
from app.modules.payments.models import PaymentAllocation, PaymentDocument


class PaymentsRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_payment_documents(self, company_id: str, branch_id: str | None = None) -> list[PaymentDocument]:
        stmt = self._document_query().where(PaymentDocument.company_id == company_id)
        if branch_id:
            stmt = stmt.where(PaymentDocument.branch_id == branch_id)
        stmt = stmt.order_by(PaymentDocument.payment_date.desc(), PaymentDocument.created_at.desc())
        return list(self.db.scalars(stmt))

    def get_payment_document(self, payment_document_id: str) -> PaymentDocument | None:
        stmt = self._document_query().where(PaymentDocument.id == payment_document_id)
        return self.db.scalars(stmt).first()

    def add_payment_document(self, payment_document: PaymentDocument) -> PaymentDocument:
        self.db.add(payment_document)
        return payment_document

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

    def _document_query(self):
        return (
            select(PaymentDocument)
            .options(
                joinedload(PaymentDocument.branch),
                joinedload(PaymentDocument.customer),
                joinedload(PaymentDocument.journal_entry),
                selectinload(PaymentDocument.allocations).joinedload(PaymentAllocation.booking).joinedload(Booking.customer),
                selectinload(PaymentDocument.allocations).joinedload(PaymentAllocation.booking_line).joinedload(BookingLine.department),
                selectinload(PaymentDocument.allocations).joinedload(PaymentAllocation.booking_line).joinedload(BookingLine.dress),
                selectinload(PaymentDocument.allocations)
                .joinedload(PaymentAllocation.booking_line)
                .joinedload(BookingLine.service)
                .joinedload(ServiceCatalogItem.department),
            )
        )
