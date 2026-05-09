"""Comprehensive report service – date-filtered KPI aggregation.

This file is intentionally separate from service.py (overview report) to
preserve backward compatibility and keep each file under 250 lines.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.modules.bookings.calculations import line_paid_total
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
    from app.modules.reports.repository import ReportsRepository
    repo = ReportsRepository(db)

    # --- Fetch Aggregated Stats via SQL ---
    payment_stats = repo.get_comprehensive_payment_stats(company.id, branch_id, date_from, date_to)
    booking_stats = repo.get_comprehensive_booking_stats(company.id, branch_id, date_from, date_to)

    # Merge client names from both sources
    client_names = payment_stats['client_names']
    client_names.update(booking_stats['client_names'])

    total_collected = payment_stats['total_collected']
    total_recognized = total_collected

    total_bookings = booking_stats['total_bookings']
    cancelled_bookings = booking_stats['cancelled_bookings']

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
        'total_remaining': _to_float(booking_stats['total_remaining']),
        'total_bookings': total_bookings,
        'cancelled_bookings': cancelled_bookings,
        'cancellation_rate': cancellation_rate,
        'daily_income': _daily_items(payment_stats['daily_income']),
        'department_income': _sorted_value_items(payment_stats['department_income']),
        'top_services': _sorted_count_items(booking_stats['top_services']),
        'top_clients': _build_top_clients(payment_stats['client_paid'], booking_stats['client_bookings'], client_names),
        'booking_status_counts': [
            {'key': k, 'count': v}
            for k, v in sorted(booking_stats['booking_status'].items(), key=lambda x: x[1], reverse=True)
        ],
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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
