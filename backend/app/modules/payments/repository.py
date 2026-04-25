from __future__ import annotations

from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modules.bookings.models import Booking, BookingLine
from app.modules.catalog.models import ServiceCatalogItem
from app.modules.customers.models import Customer
from app.modules.organization.models import DocumentSequence
from app.modules.payments.models import PaymentAllocation, PaymentDocument, PaymentMethod


class PaymentsRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_payment_documents(self, company_id: str, branch_id: str | None = None) -> list[PaymentDocument]:
        stmt = self._document_query().where(PaymentDocument.company_id == company_id)
        if branch_id:
            stmt = stmt.where(PaymentDocument.branch_id == branch_id)
        stmt = stmt.order_by(PaymentDocument.payment_date.desc(), PaymentDocument.created_at.desc())
        return list(self.db.scalars(stmt))

    def list_payment_document_page(
        self,
        company_id: str,
        *,
        branch_id: str | None = None,
        search: str | None = None,
        status: str | None = None,
        document_kind: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        page_size: int = 25,
        sort_by: str = 'payment_date',
        sort_dir: str = 'desc',
    ) -> tuple[list[PaymentDocument], int]:
        stmt = (
            select(PaymentDocument.id)
            .join(PaymentDocument.customer)
            .outerjoin(PaymentDocument.allocations)
            .outerjoin(PaymentAllocation.booking)
            .where(PaymentDocument.company_id == company_id)
        )
        if branch_id:
            stmt = stmt.where(PaymentDocument.branch_id == branch_id)
        if status:
            stmt = stmt.where(PaymentDocument.status == status)
        if document_kind:
            stmt = stmt.where(PaymentDocument.document_kind == document_kind)
        if date_from:
            stmt = stmt.where(PaymentDocument.payment_date >= date_from)
        if date_to:
            stmt = stmt.where(PaymentDocument.payment_date <= date_to)
        if search:
            pattern = f'%{search.strip()}%'
            stmt = stmt.where(
                or_(
                    PaymentDocument.payment_number.ilike(pattern),
                    Customer.full_name.ilike(pattern),
                    Customer.phone.ilike(pattern),
                    PaymentDocument.notes.ilike(pattern),
                    Booking.booking_number.ilike(pattern),
                )
            )

        sort_column = {
            'payment_number': PaymentDocument.payment_number,
            'customer_name': Customer.full_name,
            'status': PaymentDocument.status,
            'document_kind': PaymentDocument.document_kind,
            'payment_date': PaymentDocument.payment_date,
        }.get(sort_by, PaymentDocument.payment_date)
        sort_expression = sort_column.asc() if sort_dir == 'asc' else sort_column.desc()
        distinct_id_stmt = stmt.distinct()
        total = self.db.scalar(select(func.count()).select_from(distinct_id_stmt.subquery())) or 0

        # PostgreSQL requires ORDER BY expressions to appear in SELECT when DISTINCT is used.
        id_page_stmt = (
            stmt.with_only_columns(
                PaymentDocument.id.label('payment_document_id'),
                sort_column.label('sort_value'),
                PaymentDocument.created_at.label('created_at'),
            )
            .distinct()
            .order_by(sort_expression, PaymentDocument.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        ids = [row.payment_document_id for row in self.db.execute(id_page_stmt).all()]
        if not ids:
            return [], total

        rows = list(self.db.scalars(self._document_query().where(PaymentDocument.id.in_(ids))))
        order_map = {document_id: index for index, document_id in enumerate(ids)}
        rows.sort(key=lambda row: order_map.get(row.id, len(order_map)))
        return rows, total

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

    def list_payment_methods(self, company_id: str, *, include_inactive: bool = True) -> list[PaymentMethod]:
        stmt = select(PaymentMethod).where(PaymentMethod.company_id == company_id)
        if not include_inactive:
            stmt = stmt.where(PaymentMethod.is_active.is_(True))
        stmt = stmt.order_by(PaymentMethod.display_order.asc(), PaymentMethod.created_at.asc())
        return list(self.db.scalars(stmt))

    def get_payment_method(self, payment_method_id: str) -> PaymentMethod | None:
        return self.db.get(PaymentMethod, payment_method_id)

    def get_payment_method_by_code(self, company_id: str, code: str) -> PaymentMethod | None:
        stmt = select(PaymentMethod).where(PaymentMethod.company_id == company_id, PaymentMethod.code == code)
        return self.db.scalars(stmt).first()

    def add_payment_method(self, payment_method: PaymentMethod) -> PaymentMethod:
        self.db.add(payment_method)
        return payment_method

    def next_payment_method_order(self, company_id: str) -> int:
        max_value = self.db.scalar(select(func.max(PaymentMethod.display_order)).where(PaymentMethod.company_id == company_id))
        return int(max_value or 0) + 1

    def _document_query(self):
        return (
            select(PaymentDocument)
            .options(
                joinedload(PaymentDocument.branch),
                joinedload(PaymentDocument.customer),
                joinedload(PaymentDocument.payment_method),
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
