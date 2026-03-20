from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.modules.bookings.calculations import line_remaining_amount
from app.modules.bookings.repository import BookingsRepository
from app.modules.organization.service import get_company_settings
from app.modules.payments.repository import PaymentsRepository

PRICE_QUANT = Decimal('0.01')
ZERO = Decimal('0.00')


def get_finance_dashboard(db: Session, branch_id: str | None = None) -> dict:
    company = get_company_settings(db)
    bookings = BookingsRepository(db).list_bookings(company.id, branch_id)
    payment_documents = PaymentsRepository(db).list_payment_documents(company.id, branch_id)

    daily_income: dict[str, Decimal] = defaultdict(lambda: ZERO)
    department_income: dict[str, Decimal] = defaultdict(lambda: ZERO)
    total_income = ZERO
    top_services: dict[str, int] = defaultdict(int)
    total_remaining = ZERO

    for payment_document in payment_documents:
        if payment_document.status == 'voided':
            continue
        for allocation in payment_document.allocations:
            amount = Decimal(str(allocation.allocated_amount)).quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)
            total_income += amount
            daily_income[payment_document.payment_date.isoformat()] += amount
            department_income[allocation.booking_line.department.name] += amount

    for booking in bookings:
        for line in booking.lines:
            if line.status == 'cancelled':
                continue
            total_remaining += line_remaining_amount(line)
            top_services[line.service.name] += 1

    return {
        'total_income': _to_float(total_income),
        'total_remaining': _to_float(total_remaining),
        'total_bookings': len(bookings),
        'daily_income': _sorted_daily_items(daily_income),
        'department_income': _sorted_metric_items(department_income),
        'top_services': _sorted_count_items(top_services),
    }


def _sorted_daily_items(values: dict[str, Decimal]) -> list[dict]:
    items = [{'label': key, 'value': _to_float(value)} for key, value in sorted(values.items())]
    return items[-7:]


def _sorted_metric_items(values: dict[str, Decimal]) -> list[dict]:
    items = [{'label': key, 'value': _to_float(value)} for key, value in sorted(values.items(), key=lambda item: item[1], reverse=True)]
    return items[:7]


def _sorted_count_items(values: dict[str, int]) -> list[dict]:
    items = [{'label': key, 'count': value} for key, value in sorted(values.items(), key=lambda item: item[1], reverse=True)]
    return items[:5]


def _to_float(value: Decimal) -> float:
    return float(value.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP))
