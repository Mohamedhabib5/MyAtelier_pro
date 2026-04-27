from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.modules.bookings.calculations import derive_booking_status, line_paid_total, serialize_booking_document
from app.modules.bookings.document_access import BOOKING_SEQUENCE_KEY, ensure_booking_sequence, get_scoped_booking, reload_booking_or_404
from app.modules.bookings.line_mutations import create_initial_payment_document, materialize_line
from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.query_service import list_booking_page, list_bookings
from app.modules.bookings.reference_data import get_customer_or_404
from app.modules.bookings.repository import BookingsRepository
from app.modules.bookings.rules import clean_optional, parse_date
from app.modules.bookings.schemas import BookingDocumentCreateRequest, BookingDocumentUpdateRequest
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.branch_context import ensure_active_branch
from app.modules.organization.service import get_company_settings

ZERO = Decimal("0.00")

def get_booking_document(db: Session, booking_id: str, session: dict) -> dict:
    return serialize_booking_document(get_scoped_booking(db, booking_id, session))


def create_booking(db: Session, actor: User, payload: BookingDocumentCreateRequest, session: dict) -> dict:
    company = get_company_settings(db)
    branch = ensure_active_branch(db, session)
    repo = BookingsRepository(db)
    ensure_booking_sequence(db, company.id)
    booking = Booking(
        company_id=company.id,
        branch_id=branch.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        booking_number=repo.reserve_sequence_number(company.id, BOOKING_SEQUENCE_KEY),
        customer_id=get_customer_or_404(db, company.id, payload.customer_id).id,
        booking_date=parse_date(payload.booking_date, default_today=True),
        status="draft",
        notes=clean_optional(payload.notes),
        external_code=clean_optional(payload.external_code),
    )
    line_entries = [
        materialize_line(db, company.id, actor.id, payload_line, None, index)
        for index, payload_line in enumerate(payload.lines, start=1)
    ]
    booking.lines = [entry["line"] for entry in line_entries]
    booking.status = derive_booking_status(booking.lines)
    repo.add_booking(booking)
    db.flush()
    create_initial_payment_document(
        db,
        actor,
        booking,
        line_entries,
        payment_method_id=payload.initial_payment_method_id,
    )
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="booking.created",
        target_type="booking",
        target_id=booking.id,
        summary=f"Created booking {booking.booking_number}",
        diff={
            "status": booking.status,
            "branch_id": booking.branch_id,
            "line_count": len(booking.lines),
            "entity_version": booking.entity_version,
        },
    )
    db.commit()
    return serialize_booking_document(reload_booking_or_404(repo, booking.id))


def update_booking(db: Session, actor: User, booking_id: str, payload: BookingDocumentUpdateRequest, session: dict) -> dict:
    booking = get_scoped_booking(db, booking_id, session)
    company_id = booking.company_id
    booking.customer_id = get_customer_or_404(db, company_id, payload.customer_id).id
    booking.booking_date = parse_date(payload.booking_date, default_today=False, current_value=booking.booking_date)
    booking.notes = clean_optional(payload.notes)
    booking.external_code = clean_optional(payload.external_code)
    booking.updated_by_user_id = actor.id
    booking.entity_version += 1

    existing_by_id = {line.id: line for line in booking.lines}
    next_lines: list[BookingLine] = []
    line_entries: list[dict] = []
    seen_ids: set[str] = set()
    for index, payload_line in enumerate(payload.lines, start=1):
        existing_line = existing_by_id.get(payload_line.id) if payload_line.id else None
        if payload_line.id and existing_line is None:
            raise ValidationAppError("لم يتم العثور على سطر الحجز")
        line_entry = materialize_line(db, company_id, actor.id, payload_line, existing_line, index)
        next_lines.append(line_entry["line"])
        line_entries.append(line_entry)
        if existing_line is not None:
            seen_ids.add(existing_line.id)

    for line in booking.lines:
        if line.id in seen_ids:
            continue
        if line.revenue_journal_entry_id:
            raise ValidationAppError("لا يمكن حذف السطور المكتملة بعد الاعتراف بالإيراد")
        if line_paid_total(line) > ZERO:
            raise ValidationAppError("لا يمكن حذف السطور التي لها مدفوعات محصلة")

    booking.lines = next_lines
    booking.status = derive_booking_status(booking.lines)
    db.flush()
    create_initial_payment_document(
        db,
        actor,
        booking,
        line_entries,
        payment_method_id=payload.initial_payment_method_id,
    )
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="booking.updated",
        target_type="booking",
        target_id=booking.id,
        summary=f"Updated booking {booking.booking_number}",
        diff={
            "status": booking.status,
            "line_count": len(booking.lines),
            "entity_version": booking.entity_version,
        },
    )
    db.commit()
    return serialize_booking_document(reload_booking_or_404(BookingsRepository(db), booking.id))
