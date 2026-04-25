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
