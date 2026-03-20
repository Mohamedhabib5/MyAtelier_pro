from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from app.modules.bookings.models import Booking, BookingLine

PRICE_QUANT = Decimal('0.01')
ZERO = Decimal('0.00')


def quantize_amount(value: Decimal | float | int | str) -> Decimal:
    return Decimal(str(value)).quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)


def line_paid_total(line: BookingLine, *, ignore_payment_document_id: str | None = None) -> Decimal:
    total = ZERO
    for allocation in line.payment_allocations:
        document = allocation.payment_document
        if document.status == 'voided':
            continue
        if ignore_payment_document_id and document.id == ignore_payment_document_id:
            continue
        total += quantize_amount(allocation.allocated_amount)
    return quantize_amount(total)


def line_remaining_amount(line: BookingLine, *, ignore_payment_document_id: str | None = None) -> Decimal:
    return quantize_amount(quantize_amount(line.line_price) - line_paid_total(line, ignore_payment_document_id=ignore_payment_document_id))


def line_payment_state(line: BookingLine, *, ignore_payment_document_id: str | None = None) -> str:
    paid_total = line_paid_total(line, ignore_payment_document_id=ignore_payment_document_id)
    remaining = line_remaining_amount(line, ignore_payment_document_id=ignore_payment_document_id)
    if paid_total <= ZERO:
        return 'unpaid'
    if remaining <= ZERO:
        return 'paid'
    return 'partial'


def derive_booking_status(lines: list[BookingLine]) -> str:
    if not lines:
        return 'draft'
    statuses = [line.status for line in lines]
    active_statuses = [status for status in statuses if status != 'cancelled']
    if not active_statuses:
        return 'cancelled'
    if all(status == 'draft' for status in active_statuses):
        return 'draft'
    if all(status == 'completed' for status in active_statuses):
        return 'completed'
    if any(status == 'completed' for status in active_statuses):
        return 'partially_completed'
    if any(status == 'confirmed' for status in active_statuses):
        return 'confirmed'
    return 'draft'


def booking_total_amount(booking: Booking) -> Decimal:
    return quantize_amount(sum((quantize_amount(line.line_price) for line in booking.lines if line.status != 'cancelled'), start=ZERO))


def booking_paid_total(booking: Booking) -> Decimal:
    return quantize_amount(sum((line_paid_total(line) for line in booking.lines if line.status != 'cancelled'), start=ZERO))


def booking_remaining_amount(booking: Booking) -> Decimal:
    return quantize_amount(sum((line_remaining_amount(line) for line in booking.lines if line.status != 'cancelled'), start=ZERO))


def serialize_booking_line(line: BookingLine) -> dict:
    paid_total = line_paid_total(line)
    remaining = line_remaining_amount(line)
    return {
        'id': line.id,
        'booking_id': line.booking_id,
        'line_number': line.line_number,
        'department_id': line.department_id,
        'department_name': line.department.name,
        'service_id': line.service_id,
        'service_name': line.service.name,
        'dress_id': line.dress_id,
        'dress_code': line.dress.code if line.dress else None,
        'service_date': line.service_date.isoformat(),
        'suggested_price': float(quantize_amount(line.suggested_price)),
        'line_price': float(quantize_amount(line.line_price)),
        'paid_total': float(paid_total),
        'remaining_amount': float(remaining),
        'payment_state': line_payment_state(line),
        'status': line.status,
        'revenue_journal_entry_id': line.revenue_journal_entry_id,
        'revenue_journal_entry_number': line.revenue_journal_entry.entry_number if line.revenue_journal_entry else None,
        'revenue_journal_entry_status': line.revenue_journal_entry.status if line.revenue_journal_entry else None,
        'revenue_recognized_at': line.revenue_recognized_at.isoformat() if line.revenue_recognized_at else None,
        'notes': line.notes,
        'is_locked': bool(line.revenue_journal_entry_id),
    }


def serialize_booking_summary(booking: Booking) -> dict:
    lines = [serialize_booking_line(line) for line in booking.lines]
    ordered_dates = sorted((line['service_date'] for line in lines if line['status'] != 'cancelled'))
    service_summary = '، '.join(line['service_name'] for line in lines[:3])
    if len(lines) > 3:
        service_summary = f'{service_summary} +{len(lines) - 3}'
    return {
        'id': booking.id,
        'company_id': booking.company_id,
        'branch_id': booking.branch_id,
        'branch_name': booking.branch.name,
        'booking_number': booking.booking_number,
        'customer_id': booking.customer_id,
        'customer_name': booking.customer.full_name,
        'booking_date': booking.booking_date.isoformat(),
        'status': booking.status,
        'line_count': len(lines),
        'service_summary': service_summary,
        'next_service_date': ordered_dates[0] if ordered_dates else None,
        'total_amount': float(booking_total_amount(booking)),
        'paid_total': float(booking_paid_total(booking)),
        'remaining_amount': float(booking_remaining_amount(booking)),
        'notes': booking.notes,
    }


def serialize_booking_document(booking: Booking) -> dict:
    payload = serialize_booking_summary(booking)
    payload['lines'] = [serialize_booking_line(line) for line in booking.lines]
    return payload
