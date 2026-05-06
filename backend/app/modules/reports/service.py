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
    
    # 1. Basic Counts (Optimized via direct repository calls)
    customers = repository.list_customers(company.id)
    departments = repository.list_departments(company.id)
    services = repository.list_services(company.id)
    dresses = repository.list_dresses(company.id)

    # 2. Aggregated Metrics (SQL GROUP BY)
    booking_status_counts = repository.get_booking_status_counts(company.id, branch_id)
    payment_type_totals = repository.get_payment_type_totals(company.id, branch_id)
    
    # 3. Upcoming Bookings (SQL Filtered & Limited)
    upcoming_booking_items = repository.get_upcoming_booking_lines(company.id, branch_id, limit=5)

    # 4. Department Counts (Calculated from in-memory service list - usually small)
    department_service_counts: dict[str, int] = defaultdict(int)
    for service in services:
        department_service_counts[service.department.name] += 1

    return {
        'active_customers': sum(1 for customer in customers if customer.is_active),
        'active_services': sum(1 for service in services if service.is_active),
        'available_dresses': sum(1 for dress in dresses if dress.is_active and dress.status == 'available'),
        'upcoming_bookings': len(upcoming_booking_items), # Note: This is now just the top 5 for overview
        'booking_status_counts': sorted(booking_status_counts, key=lambda x: x['count'], reverse=True),
        'payment_type_totals': [{'key': item['key'], 'value': _to_float(item['value'])} for item in sorted(payment_type_totals, key=lambda x: x['value'], reverse=True)],
        'dress_status_counts': _get_dress_status_summary(dresses),
        'department_service_counts': _sorted_department_counts(department_service_counts, departments),
        'upcoming_booking_items': upcoming_booking_items,
    }


def _get_dress_status_summary(dresses: list) -> list[dict]:
    counts: dict[str, int] = defaultdict(int)
    for dress in dresses:
        counts[dress.status] += 1
    return [{'key': key, 'count': count} for key, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)]


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
