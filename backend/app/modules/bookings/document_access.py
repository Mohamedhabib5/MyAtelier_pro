from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.repository import BookingsRepository
from app.modules.core_platform.service import record_audit
from app.modules.organization.branch_context import ensure_active_branch
from app.modules.organization.models import DocumentSequence
from app.modules.organization.service import get_company_settings

BOOKING_SEQUENCE_KEY = "booking"


def ensure_booking_sequence(db: Session, company_id: str) -> None:
    repo = BookingsRepository(db)
    if repo.get_document_sequence(company_id, BOOKING_SEQUENCE_KEY) is not None:
        return
    repo.add_document_sequence(DocumentSequence(company_id=company_id, key=BOOKING_SEQUENCE_KEY, prefix="BK", next_number=1, padding=6))
    record_audit(
        db,
        actor_user_id=None,
        action="booking.sequence_seeded",
        target_type="company",
        target_id=company_id,
        summary="Seeded booking document sequence",
    )
    db.flush()


def get_scoped_booking(db: Session, booking_id: str, session: dict) -> Booking:
    company = get_company_settings(db)
    branch = ensure_active_branch(db, session)
    booking = BookingsRepository(db).get_booking(booking_id)
    if booking is None or booking.company_id != company.id or booking.branch_id != branch.id:
        raise NotFoundError("لم يتم العثور على الحجز")
    return booking


def reload_booking_or_404(repo: BookingsRepository, booking_id: str) -> Booking:
    booking = repo.get_booking(booking_id)
    if booking is None:
        raise NotFoundError("لم يتم العثور على الحجز")
    return booking


def get_line_or_404(booking: Booking, line_id: str) -> BookingLine:
    for line in booking.lines:
        if line.id == line_id:
            return line
    raise NotFoundError("لم يتم العثور على سطر الحجز")
