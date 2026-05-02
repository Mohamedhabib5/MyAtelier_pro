"""Comprehensive report service – date-filtered KPI aggregation.

This file is intentionally separate from service.py (overview report) to
preserve backward compatibility and keep each file under 250 lines.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.repository import BookingsRepository
from app.modules.customers.models import Customer
from app.modules.organization.service import get_company_settings
from app.modules.payments.models import PaymentAllocation, PaymentDocument
from app.modules.payments.repository import PaymentsRepository

PRICE_QUANT = Decimal('0.01')
ZERO = Decimal('0.00')
TOP_CLIENTS_LIMIT = 10
TOP_SERVICES_LIMIT = 7
DAILY_INCOME_LIMIT = 60  # max days shown in chart


def get_comprehensive_report(
    db: Session,
    branch_id: str | None,
    date_from: date,
    date_to: date,
) -> dict:
    company = get_company_settings(db)

    # --- fetch data within the date range ---
    bookings = _list_bookings_in_range(db, company.id, branch_id, date_from, date_to)
    payments = _list_payments_in_range(db, company.id, branch_id, date_from, date_to)

    # --- KPI accumulators ---
    total_collected = ZERO
    total_remaining = ZERO
    daily_income: dict[str, Decimal] = defaultdict(lambda: ZERO)
    department_income: dict[str, Decimal] = defaultdict(lambda: ZERO)
    top_services: dict[str, int] = defaultdict(int)
    client_paid: dict[str, Decimal] = defaultdict(lambda: ZERO)
    client_bookings: dict[str, int] = defaultdict(int)
    client_names: dict[str, str] = {}

    for payment in payments:
        if payment.status == 'voided':
            continue
        for allocation in payment.allocations:
            amt = Decimal(str(allocation.allocated_amount)).quantize(
                PRICE_QUANT, rounding=ROUND_HALF_UP
            )
            if payment.document_kind == 'refund':
                amt = -amt
            total_collected += amt
            daily_income[payment.payment_date.isoformat()] += amt
            dept_name = allocation.booking_line.department.name if allocation.booking_line else ''
            if dept_name:
                department_income[dept_name] += amt
            cust_id = payment.customer_id
            client_paid[cust_id] += amt
            if payment.customer:
                client_names[cust_id] = payment.customer.full_name

    booking_status: dict[str, int] = defaultdict(int)
    total_bookings = len(bookings)
    cancelled_bookings = 0

    for booking in bookings:
        booking_status[booking.status] += 1
        if booking.status == 'cancelled':
            cancelled_bookings += 1
        for line in booking.lines:
            if line.status == 'cancelled':
                continue
            paid_for_line = sum(
                Decimal(str(a.allocated_amount)) for a in line.payment_allocations
            )
            remaining = Decimal(str(line.line_price)) - paid_for_line
            if remaining > ZERO:
                total_remaining += remaining.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)
            top_services[line.service.name] += 1
            cust_id = booking.customer_id
            client_bookings[cust_id] += 1
            if booking.customer:
                client_names[cust_id] = booking.customer.full_name

    # revenue recognized = same as total_collected (cash basis) for now
    total_recognized = total_collected

    cancellation_rate = (
        round(cancelled_bookings / total_bookings * 100, 1)
        if total_bookings > 0
        else 0.0
    )

    return {
        'date_from': date_from.isoformat(),
        'date_to': date_to.isoformat(),
        'total_collected': _to_float(total_collected),
        'total_recognized': _to_float(total_recognized),
        'total_remaining': _to_float(total_remaining),
        'total_bookings': total_bookings,
        'cancelled_bookings': cancelled_bookings,
        'cancellation_rate': cancellation_rate,
        'daily_income': _daily_items(daily_income),
        'department_income': _sorted_value_items(department_income),
        'top_services': _sorted_count_items(top_services),
        'top_clients': _build_top_clients(client_paid, client_bookings, client_names),
        'booking_status_counts': [
            {'key': k, 'count': v}
            for k, v in sorted(booking_status.items(), key=lambda x: x[1], reverse=True)
        ],
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _list_bookings_in_range(
    db: Session,
    company_id: str,
    branch_id: str | None,
    date_from: date,
    date_to: date,
) -> list[Booking]:
    repo = BookingsRepository(db)
    rows, _ = repo.list_booking_page(
        company_id,
        branch_id=branch_id,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10_000,  # large enough for aggregation
    )
    return rows


def _list_payments_in_range(
    db: Session,
    company_id: str,
    branch_id: str | None,
    date_from: date,
    date_to: date,
) -> list[PaymentDocument]:
    repo = PaymentsRepository(db)
    rows, _ = repo.list_payment_document_page(
        company_id,
        branch_id=branch_id,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10_000,
    )
    return rows


def _daily_items(values: dict[str, Decimal]) -> list[dict]:
    items = sorted(values.items())
    items = items[-DAILY_INCOME_LIMIT:]
    return [{'date': k, 'amount': _to_float(v)} for k, v in items]


def _sorted_value_items(values: dict[str, Decimal]) -> list[dict]:
    items = sorted(values.items(), key=lambda x: x[1], reverse=True)
    return [{'label': k, 'value': _to_float(v)} for k, v in items[:TOP_SERVICES_LIMIT]]


def _sorted_count_items(values: dict[str, int]) -> list[dict]:
    items = sorted(values.items(), key=lambda x: x[1], reverse=True)
    return [{'label': k, 'count': v} for k, v in items[:TOP_SERVICES_LIMIT]]


def _build_top_clients(
    client_paid: dict[str, Decimal],
    client_bookings: dict[str, int],
    client_names: dict[str, str],
) -> list[dict]:
    items = sorted(client_paid.items(), key=lambda x: x[1], reverse=True)
    result = []
    for cust_id, total in items[:TOP_CLIENTS_LIMIT]:
        result.append({
            'customer_name': client_names.get(cust_id, cust_id),
            'total_paid': _to_float(total),
            'booking_count': client_bookings.get(cust_id, 0),
        })
    return result


def _to_float(value: Decimal) -> float:
    return float(value.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP))
