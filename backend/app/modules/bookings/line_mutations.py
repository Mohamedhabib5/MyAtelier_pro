from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.modules.bookings.calculations import line_paid_total, quantize_amount
from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.reference_data import (
    get_department_or_404,
    get_dress_or_404,
    get_service_or_404,
)
from app.modules.bookings.repository import BookingsRepository
from app.modules.bookings.rules import (
    calculate_tax_amount,
    clean_line_status,
    clean_optional,
    department_uses_dress,
    ensure_locked_line_unchanged,
    parse_date,
)
from app.modules.bookings.schemas import BookingLineInput
from app.modules.identity.models import User
from app.modules.payments.booking_bridge import create_payment_document_from_lines

ZERO = Decimal("0.00")


def materialize_line(
    db: Session,
    company_id: str,
    actor_user_id: str,
    payload: BookingLineInput,
    existing_line: BookingLine | None,
    line_number: int,
) -> dict:
    department = get_department_or_404(db, company_id, payload.department_id)
    service = get_service_or_404(db, company_id, payload.service_id)
    if service.department_id != department.id:
        raise ValidationAppError("الخدمة المختارة لا تنتمي إلى القسم المحدد")
    dress = get_dress_or_404(db, company_id, payload.dress_id)
    if dress and not department_uses_dress(department):
        raise ValidationAppError("اختيار الفستان متاح فقط للأقسام الخاصة بالفستان")
    service_date = parse_date(payload.service_date)
    status = clean_line_status(payload.status)
    suggested_price = quantize_amount(
        payload.suggested_price if payload.suggested_price is not None else service.default_price
    )
    line_price = quantize_amount(payload.line_price)
    tax_rate_percent = quantize_amount(service.tax_rate_percent)
    tax_amount = calculate_tax_amount(line_price, tax_rate_percent)

    repo = BookingsRepository(db)
    ignore_line_id = existing_line.id if existing_line else None
    if dress and repo.find_dress_conflict(company_id, dress.id, service_date, ignore_line_id=ignore_line_id):
        raise ValidationAppError("الفستان محجوز بالفعل في تاريخ الخدمة المحدد")
    initial_payment_amount = quantize_amount(payload.initial_payment_amount or ZERO)
    if initial_payment_amount < ZERO:
        raise ValidationAppError("لا يمكن أن تكون الدفعة الأولى سالبة")

    current_paid_total = line_paid_total(existing_line) if existing_line is not None else ZERO
    if line_price < current_paid_total:
        raise ValidationAppError("لا يمكن أن يكون سعر السطر أقل من المدفوع المحصل")
    if status == "cancelled" and current_paid_total > ZERO:
        raise ValidationAppError("لا يمكن إلغاء السطور ذات المدفوعات المحصلة من محرر الحجز")
    if status == "cancelled" and initial_payment_amount > ZERO:
        raise ValidationAppError("لا يمكن للسطور الملغاة استقبال دفعة أولى")
    if existing_line is None and initial_payment_amount > line_price:
        raise ValidationAppError("لا يمكن أن تتجاوز الدفعة الأولى سعر السطر")
    if existing_line is not None and initial_payment_amount > quantize_amount(line_price - current_paid_total):
        raise ValidationAppError("لا يمكن أن تتجاوز الدفعة الأولى المتبقي على السطر")

    if existing_line is not None:
        if existing_line.revenue_journal_entry_id:
            ensure_locked_line_unchanged(
                existing_line,
                department.id,
                service.id,
                dress.id if dress else None,
                service_date,
                suggested_price,
                line_price,
                status,
                payload.notes,
                tax_rate_percent,
                tax_amount,
            )
            if initial_payment_amount > ZERO:
                raise ValidationAppError("لا يمكن إضافة دفعة أولى لسطر مكتمل من شاشة الحجز")
            return {"line": existing_line, "initial_payment_amount": ZERO}
        existing_line.department_id = department.id
        existing_line.service_id = service.id
        existing_line.dress_id = dress.id if dress else None
        existing_line.line_number = line_number
        existing_line.service_date = service_date
        existing_line.suggested_price = suggested_price
        existing_line.line_price = line_price
        existing_line.tax_rate_percent = tax_rate_percent
        existing_line.tax_amount = tax_amount
        existing_line.status = status
        existing_line.notes = clean_optional(payload.notes)
        existing_line.updated_by_user_id = actor_user_id
        existing_line.entity_version += 1
        return {"line": existing_line, "initial_payment_amount": initial_payment_amount}

    line = BookingLine(
        created_by_user_id=actor_user_id,
        updated_by_user_id=actor_user_id,
        entity_version=1,
        department_id=department.id,
        service_id=service.id,
        dress_id=dress.id if dress else None,
        line_number=line_number,
        service_date=service_date,
        suggested_price=suggested_price,
        line_price=line_price,
        tax_rate_percent=tax_rate_percent,
        tax_amount=tax_amount,
        status=status,
        notes=clean_optional(payload.notes),
    )
    return {"line": line, "initial_payment_amount": initial_payment_amount}


def create_initial_payment_document(
    db: Session,
    actor: User,
    booking: Booking,
    line_entries: list[dict],
    payment_method_id: str | None = None,
) -> None:
    initial_allocations = []
    for entry in line_entries:
        amount = entry["initial_payment_amount"]
        if amount <= ZERO:
            continue
        line = entry["line"]
        initial_allocations.append((line, amount))
    if initial_allocations:
        create_payment_document_from_lines(
            db,
            actor,
            booking,
            initial_allocations,
            booking.booking_date,
            payment_method_id=payment_method_id,
        )
