from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.bookings.calculations import serialize_booking_summary
from app.modules.bookings.repository import BookingsRepository
from app.modules.bookings.rules import clean_optional, parse_date
from app.modules.organization.branch_context import resolve_branch_scope
from app.modules.organization.service import get_company_settings


def list_bookings(db: Session, session: dict, branch_id: str | None = None) -> list[dict]:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    rows = BookingsRepository(db).list_bookings(company.id, branch.id)
    return [serialize_booking_summary(row) for row in rows]


def list_booking_page(
    db: Session,
    session: dict,
    *,
    branch_id: str | None = None,
    search: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 25,
    sort_by: str = "booking_date",
    sort_dir: str = "desc",
) -> dict:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    rows, total = BookingsRepository(db).list_booking_page(
        company.id,
        branch_id=branch.id,
        search=clean_optional(search),
        status=clean_optional(status),
        date_from=parse_date(date_from) if date_from else None,
        date_to=parse_date(date_to) if date_to else None,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir="asc" if sort_dir == "asc" else "desc",
    )
    return {"items": [serialize_booking_summary(row) for row in rows], "total": total, "page": page, "page_size": page_size}


def get_calendar_events(
    db: Session,
    session: dict,
    *,
    branch_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    department_ids: list[str] | None = None,
    service_ids: list[str] | None = None,
    date_mode: str = "service",
) -> list[dict]:
    company = get_company_settings(db)
    branch = resolve_branch_scope(db, session, branch_id)
    
    lines = BookingsRepository(db).list_calendar_lines(
        company.id,
        branch_id=branch.id,
        date_from=parse_date(date_from) if date_from else None,
        date_to=parse_date(date_to) if date_to else None,
        department_ids=department_ids,
        service_ids=service_ids,
        date_mode=date_mode,
    )

    events = []
    for line in lines:
        booking = line.booking
        customer = booking.customer
        event_date = str(line.service_date if date_mode == "service" else booking.booking_date)
        
        events.append({
            "id": line.id,
            "booking_id": booking.id,
            "title": f"{customer.full_name} - {line.service.name}",
            "start": event_date,
            "end": event_date,
            "status": line.status,
            "department_name": line.department.name,
            "service_name": line.service.name,
            "customer_name": customer.full_name,
            "booking_number": booking.booking_number,
            "external_code": booking.external_code,
        })
    return events
