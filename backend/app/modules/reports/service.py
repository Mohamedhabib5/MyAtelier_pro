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
    customers = repository.list_customers(company.id)
    departments = repository.list_departments(company.id)
    services = repository.list_services(company.id)
    dresses = repository.list_dresses(company.id)
    bookings = repository.list_bookings(company.id, branch_id)
    payment_documents = repository.list_payment_documents(company.id, branch_id)

    booking_status_counts: dict[str, int] = defaultdict(int)
    dress_status_counts: dict[str, int] = defaultdict(int)
    payment_type_totals: dict[str, Decimal] = defaultdict(lambda: ZERO)
    department_service_counts: dict[str, int] = defaultdict(int)

    for booking in bookings:
        booking_status_counts[booking.status] += 1
    for dress in dresses:
        dress_status_counts[dress.status] += 1
    for payment_document in payment_documents:
        if payment_document.status == 'voided':
            continue
        total = ZERO
        for allocation in payment_document.allocations:
            total += Decimal(str(allocation.allocated_amount))
        payment_type_totals[payment_document.document_kind] += total
    for service in services:
        department_service_counts[service.department.name] += 1

    upcoming_booking_items = _upcoming_bookings(bookings)
    return {
        'active_customers': sum(1 for customer in customers if customer.is_active),
        'active_services': sum(1 for service in services if service.is_active),
        'available_dresses': sum(1 for dress in dresses if dress.is_active and dress.status == 'available'),
        'upcoming_bookings': len(upcoming_booking_items),
        'booking_status_counts': _sorted_count_metrics(booking_status_counts),
        'payment_type_totals': _sorted_value_metrics(payment_type_totals),
        'dress_status_counts': _sorted_count_metrics(dress_status_counts),
        'department_service_counts': _sorted_department_counts(department_service_counts, departments),
        'upcoming_booking_items': upcoming_booking_items[:5],
    }


def _upcoming_bookings(bookings: list) -> list[dict]:
    today_value = date.today()
    items = []
    for booking in bookings:
        for line in booking.lines:
            if line.status == 'cancelled' or line.service_date < today_value:
                continue
            items.append({'booking_number': booking.booking_number, 'customer_name': booking.customer.full_name, 'service_name': line.service.name, 'service_date': line.service_date.isoformat(), 'status': line.status})
    items.sort(key=lambda item: item['service_date'])
    return items


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
