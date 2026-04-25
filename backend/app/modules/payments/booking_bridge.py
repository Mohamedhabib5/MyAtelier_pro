from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import PaymentReceiptStatus
from app.core.exceptions import ValidationAppError
from app.modules.bookings.calculations import quantize_amount
from app.modules.bookings.models import Booking, BookingLine
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings
from app.modules.payments.accounting_bridge import auto_post_payment_document
from app.modules.payments.document_access import PAYMENT_SEQUENCE_KEY, ensure_payment_sequence
from app.modules.payments.models import PaymentAllocation, PaymentDocument
from app.modules.payments.payment_methods import resolve_payment_method
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.serializers import document_total

ZERO = Decimal("0.00")


def create_payment_document_from_lines(
    db: Session,
    actor: User,
    booking: Booking,
    line_amounts: list[tuple[BookingLine, Decimal]],
    payment_date: date,
    payment_method_id: str | None = None,
) -> PaymentDocument:
    company = get_company_settings(db)
    if booking.company_id != company.id:
        raise ValidationAppError("الحجز خارج نطاق إنشاء سند الدفع")
    repo = PaymentsRepository(db)
    ensure_payment_sequence(db, company.id)
    payment_method = resolve_payment_method(
        db,
        company_id=company.id,
        payment_method_id=payment_method_id,
        actor_user_id=actor.id,
    )
    document = PaymentDocument(
        company_id=company.id,
        branch_id=booking.branch_id,
        customer_id=booking.customer_id,
        payment_method_id=payment_method.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        payment_number=repo.reserve_sequence_number(company.id, PAYMENT_SEQUENCE_KEY),
        payment_date=payment_date,
        document_kind="collection",
        status=PaymentReceiptStatus.ACTIVE.value,
        notes=f"دفعة أولية من وثيقة الحجز {booking.booking_number}",
    )
    allocations: list[PaymentAllocation] = []
    for index, (line, amount) in enumerate(line_amounts, start=1):
        normalized = quantize_amount(amount)
        if normalized <= ZERO:
            continue
        allocations.append(
            PaymentAllocation(
                payment_document=document,
                created_by_user_id=actor.id,
                updated_by_user_id=actor.id,
                entity_version=1,
                booking_id=booking.id,
                booking_line_id=line.id,
                line_number=index,
                allocated_amount=normalized,
            )
        )
    if not allocations:
        return document
    document.allocations = allocations
    repo.add_payment_document(document)
    db.flush()
    journal_entry = auto_post_payment_document(db, actor, document)
    document.journal_entry_id = journal_entry.id
    document.journal_entry = journal_entry
    record_audit(
        db,
        actor_user_id=actor.id,
        action="payment_document.created_from_booking",
        target_type="payment_document",
        target_id=document.id,
        summary=f"Created payment document {document.payment_number} from booking {booking.booking_number}",
        diff={
            "booking_id": booking.id,
            "allocation_count": len(allocations),
            "total_amount": float(document_total(document)),
            "entity_version": document.entity_version,
        },
    )
    return document
