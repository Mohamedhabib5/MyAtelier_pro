from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.modules.bookings.calculations import line_remaining_amount, quantize_amount
from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.repository import BookingsRepository
from app.modules.payments.models import PaymentAllocation
from app.modules.payments.schemas import PaymentAllocationInput


def build_allocations(
    db: Session,
    company_id: str,
    branch_id: str,
    customer_id: str,
    items: list[PaymentAllocationInput],
    *,
    ignore_payment_document_id: str | None = None,
    actor_user_id: str,
) -> list[PaymentAllocation]:
    if not items:
        raise ValidationAppError("يجب إدخال سطر تخصيص واحد على الأقل")
    allocations: list[PaymentAllocation] = []
    seen_lines: set[str] = set()
    for index, item in enumerate(items, start=1):
        booking, line = get_booking_line_scope(
            db,
            company_id,
            branch_id,
            customer_id,
            item.booking_id,
            item.booking_line_id,
        )
        if line.id in seen_lines:
            raise ValidationAppError("لا يمكن تكرار سطر الحجز نفسه داخل سند الدفع الواحد")
        remaining_amount = line_remaining_amount(
            line,
            ignore_payment_document_id=ignore_payment_document_id,
        )
        amount = quantize_amount(item.allocated_amount)
        if amount > remaining_amount:
            raise ValidationAppError("لا يمكن أن يتجاوز مبلغ التخصيص المتبقي على السطر")
        allocations.append(
            PaymentAllocation(
                created_by_user_id=actor_user_id,
                updated_by_user_id=actor_user_id,
                entity_version=1,
                booking_id=booking.id,
                booking_line_id=line.id,
                line_number=index,
                allocated_amount=amount,
            )
        )
        seen_lines.add(line.id)
    return allocations


def get_booking_line_scope(
    db: Session,
    company_id: str,
    branch_id: str,
    customer_id: str,
    booking_id: str,
    line_id: str,
) -> tuple[Booking, BookingLine]:
    booking = BookingsRepository(db).get_booking(booking_id)
    if (
        booking is None
        or booking.company_id != company_id
        or booking.branch_id != branch_id
        or booking.customer_id != customer_id
    ):
        raise NotFoundError("لم يتم العثور على الحجز في سياق سند الدفع الحالي")
    for line in booking.lines:
        if line.id != line_id:
            continue
        if line.status == "cancelled":
            raise ValidationAppError("لا يمكن تسجيل دفعات على السطور الملغاة")
        return booking, line
    raise NotFoundError("لم يتم العثور على سطر الحجز في سياق سند الدفع الحالي")
