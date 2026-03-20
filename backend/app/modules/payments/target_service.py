from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.security import norm_text
from app.modules.bookings.calculations import booking_paid_total, booking_total_amount, line_paid_total, line_payment_state, line_remaining_amount
from app.modules.bookings.repository import BookingsRepository
from app.modules.customers.repository import CustomersRepository
from app.modules.organization.branch_context import resolve_branch_scope
from app.modules.organization.service import get_company_settings


def search_payment_targets(db: Session, session: dict, query: str, branch_id: str | None = None) -> list[dict]:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    token = norm_text(query).lower()
    if len(token) < 2:
        return []
    customers = CustomersRepository(db).list_customers(company.id)
    bookings = BookingsRepository(db).list_bookings(company.id, branch.id)
    results: list[dict] = []
    for customer in customers:
        haystack = f"{customer.full_name} {customer.phone}".lower()
        if token in haystack:
            results.append({'kind': 'customer', 'id': customer.id, 'label': f'{customer.full_name} • {customer.phone}', 'customer_id': customer.id, 'customer_name': customer.full_name, 'booking_id': None, 'booking_number': None})
    for booking in bookings:
        if token in booking.booking_number.lower() or token in booking.customer.full_name.lower():
            results.append({'kind': 'booking', 'id': booking.id, 'label': f'{booking.booking_number} • {booking.customer.full_name}', 'customer_id': booking.customer_id, 'customer_name': booking.customer.full_name, 'booking_id': booking.id, 'booking_number': booking.booking_number})
    return results[:12]


def get_customer_payment_target(db: Session, session: dict, customer_id: str, branch_id: str | None = None, ignore_payment_document_id: str | None = None) -> dict:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    bookings = BookingsRepository(db).list_bookings(company.id, branch.id, customer_id)
    if not bookings:
        customer = CustomersRepository(db).get_customer(customer_id)
        if customer is None or customer.company_id != company.id:
            raise NotFoundError('لم يتم العثور على العميل')
        return _serialize_target('customer', customer.id, customer.full_name, branch.id, branch.name, [], ignore_payment_document_id)
    customer_name = bookings[0].customer.full_name
    return _serialize_target('customer', customer_id, customer_name, branch.id, branch.name, bookings, ignore_payment_document_id)


def get_booking_payment_target(db: Session, session: dict, booking_id: str, branch_id: str | None = None, ignore_payment_document_id: str | None = None) -> dict:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    booking = BookingsRepository(db).get_booking(booking_id)
    if booking is None or booking.company_id != company.id or booking.branch_id != branch.id:
        raise NotFoundError('لم يتم العثور على الحجز')
    return _serialize_target('booking', booking.id, booking.customer.full_name, branch.id, branch.name, [booking], ignore_payment_document_id)


def _serialize_target(scope_kind: str, scope_id: str, customer_name: str, branch_id: str, branch_name: str, bookings: list, ignore_payment_document_id: str | None) -> dict:
    booking_items = []
    total_remaining = 0.0
    customer_id = bookings[0].customer_id if bookings else scope_id
    for booking in bookings:
        lines = []
        for line in booking.lines:
            if line.status == 'cancelled':
                continue
            remaining = float(line_remaining_amount(line, ignore_payment_document_id=ignore_payment_document_id))
            if remaining <= 0:
                continue
            lines.append({'line_id': line.id, 'line_number': line.line_number, 'service_name': line.service.name, 'department_name': line.department.name, 'dress_code': line.dress.code if line.dress else None, 'service_date': line.service_date.isoformat(), 'line_status': line.status, 'line_price': float(line.line_price), 'paid_total': float(line_paid_total(line, ignore_payment_document_id=ignore_payment_document_id)), 'remaining_amount': remaining, 'payment_state': line_payment_state(line, ignore_payment_document_id=ignore_payment_document_id)})
        if not lines:
            continue
        booking_remaining = sum(line['remaining_amount'] for line in lines)
        total_remaining += booking_remaining
        booking_items.append({'booking_id': booking.id, 'booking_number': booking.booking_number, 'booking_date': booking.booking_date.isoformat(), 'booking_status': booking.status, 'total_amount': float(booking_total_amount(booking)), 'paid_total': float(booking_paid_total(booking)), 'remaining_amount': booking_remaining, 'lines': lines})
    return {'scope_kind': scope_kind, 'scope_id': scope_id, 'customer_id': customer_id, 'customer_name': customer_name, 'branch_id': branch_id, 'branch_name': branch_name, 'total_remaining': total_remaining, 'bookings': booking_items}
