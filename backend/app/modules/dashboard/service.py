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
    bookings_repo = BookingsRepository(db)
    payments_repo = PaymentsRepository(db)

    # 1. Get Core Stats (Total Bookings, Total Remaining)
    booking_stats = bookings_repo.get_bookings_stats(company.id, branch_id)
    
    # 2. Get Total Income
    total_income = payments_repo.get_total_income_stats(company.id, branch_id)

    # 3. Get Charts Data
    daily_income = payments_repo.get_payment_stats_by_date(company.id, branch_id, days=7)
    department_income = payments_repo.get_payment_stats_by_department(company.id, branch_id)
    top_services = bookings_repo.get_top_services_stats(company.id, branch_id, limit=5)

    return {
        'total_income': _to_float(total_income),
        'total_remaining': _to_float(booking_stats['total_remaining']),
        'total_bookings': booking_stats['total_bookings'],
        'daily_income': [{'label': item['label'], 'value': _to_float(item['value'])} for item in daily_income],
        'department_income': [{'label': item['label'], 'value': _to_float(item['value'])} for item in department_income],
        'top_services': top_services,
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
