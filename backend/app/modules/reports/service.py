from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.modules.organization.service import get_company_settings
from app.modules.reports.repository import ReportsRepository

PRICE_QUANT = Decimal('0.01')
ZERO = Decimal('0.00')


def get_reports_overview(db: Session, branch_id: str | None = None) -> dict:
    company = get_company_settings(db)
    repository = ReportsRepository(db)
    
    # 1. Aggregated Metrics (SQL-side counting)
    active_customers_count = repository.count_active_customers(company.id)
    active_services_count = repository.count_active_services(company.id)
    dress_status_counts = repository.get_dress_status_summary(company.id)
    department_service_counts = repository.get_department_service_counts(company.id)
    
    # 2. Fetch small lists needed for UI structure
    departments = repository.list_departments(company.id)

    # 3. Domain Aggregations (SQL GROUP BY)
    booking_status_counts = repository.get_booking_status_counts(company.id, branch_id)
    payment_type_totals = repository.get_payment_type_totals(company.id, branch_id)
    
    # 4. Upcoming Bookings (SQL Filtered & Limited)
    upcoming_booking_items = repository.get_upcoming_booking_lines(company.id, branch_id, limit=5)

    return {
        'active_customers': active_customers_count,
        'active_services': active_services_count,
        'available_dresses': next((item['count'] for item in dress_status_counts if item['key'] == 'available'), 0),
        'upcoming_bookings': len(upcoming_booking_items), 
        'booking_status_counts': sorted(booking_status_counts, key=lambda x: x['count'], reverse=True),
        'payment_type_totals': [{'key': item['key'], 'value': _to_float(item['value'])} for item in sorted(payment_type_totals, key=lambda x: x['value'], reverse=True)],
        'dress_status_counts': dress_status_counts,
        'department_service_counts': _sorted_department_counts(department_service_counts, departments),
        'upcoming_booking_items': upcoming_booking_items,
    }


def _sorted_count_metrics(values: dict[str, int]) -> list[dict]:
    return [{'key': key, 'count': count} for key, count in sorted(values.items(), key=lambda item: item[1], reverse=True)]


def _sorted_value_metrics(values: dict[str, Decimal]) -> list[dict]:
    return [{'key': key, 'value': _to_float(value)} for key, value in sorted(values.items(), key=lambda item: item[1], reverse=True)]


def _sorted_department_counts(values: dict[str, int], departments: list) -> list[dict]:
    ordered = []
    seen: set[str] = set()
    for department in departments:
        ordered.append({'label': department.name, 'count': values.get(department.name, 0)})
        seen.add(department.name)
    for label, count in values.items():
        if label not in seen:
            ordered.append({'label': label, 'count': count})
    return ordered


def _to_float(value: Decimal) -> float:
    return float(value.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP))
