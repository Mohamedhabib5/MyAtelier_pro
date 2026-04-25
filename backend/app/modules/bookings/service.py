from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.modules.bookings.calculations import derive_booking_status, line_paid_total, serialize_booking_document
from app.modules.bookings.document_access import BOOKING_SEQUENCE_KEY, ensure_booking_sequence, get_line_or_404, get_scoped_booking, reload_booking_or_404
from app.modules.bookings.line_mutations import create_initial_payment_document, materialize_line
from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.query_service import list_booking_page, list_bookings
from app.modules.bookings.reference_data import get_customer_or_404
from app.modules.bookings.repository import BookingsRepository
from app.modules.bookings.revenue_bridge import post_booking_line_revenue_recognition, reverse_booking_line_revenue_recognition
from app.modules.bookings.rules import clean_optional, parse_date
from app.modules.bookings.schemas import BookingDocumentCreateRequest, BookingDocumentUpdateRequest
from app.modules.core_platform.period_lock import enforce_not_locked_with_override, record_period_lock_override
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
    booking.updated_by_user_id = actor.id
    booking.entity_version += 1

    existing_by_id = {line.id: line for line in booking.lines}
    next_lines: list[BookingLine] = []
    line_entries: list[dict] = []
    seen_ids: set[str] = set()
    for index, payload_line in enumerate(payload.lines, start=1):
        existing_line = existing_by_id.get(payload_line.id) if payload_line.id else None
        if payload_line.id and existing_line is None:
            raise ValidationAppError("ظ„ظ… ظٹطھظ… ط§ظ„ط¹ط«ظˆط± ط¹ظ„ظ‰ ط³ط·ط± ط§ظ„ط­ط¬ط²")
        line_entry = materialize_line(db, company_id, actor.id, payload_line, existing_line, index)
        next_lines.append(line_entry["line"])
        line_entries.append(line_entry)
        if existing_line is not None:
            seen_ids.add(existing_line.id)

    for line in booking.lines:
        if line.id in seen_ids:
            continue
        if line.revenue_journal_entry_id:
            raise ValidationAppError("ظ„ط§ ظٹظ…ظƒظ† ط­ط°ظپ ط§ظ„ط³ط·ظˆط± ط§ظ„ظ…ظƒطھظ…ظ„ط© ط¨ط¹ط¯ ط§ظ„ط§ط¹طھط±ط§ظپ ط¨ط§ظ„ط¥ظٹط±ط§ط¯")
        if line_paid_total(line) > ZERO:
            raise ValidationAppError("ظ„ط§ ظٹظ…ظƒظ† ط­ط°ظپ ط§ظ„ط³ط·ظˆط± ط§ظ„طھظٹ ظ„ظ‡ط§ ظ…ط¯ظپظˆط¹ط§طھ ظ…ط­طµظ„ط©")

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


def complete_booking_line(db: Session, actor: User, booking_id: str, line_id: str, session: dict) -> dict:
    booking = get_scoped_booking(db, booking_id, session)
    line = get_line_or_404(booking, line_id)
    if line.status == "cancelled":
        raise ValidationAppError("ظ„ط§ ظٹظ…ظƒظ† ط¥ظƒظ…ط§ظ„ ط§ظ„ط³ط·ظˆط± ط§ظ„ظ…ظ„ط؛ط§ط©")
    if line.revenue_journal_entry_id:
        raise ValidationAppError("تم الاعتراف بالإيراد لهذا السطر مسبقًا")

    journal_entry = post_booking_line_revenue_recognition(db, actor, line, date.today())
    line.status = "completed"
    line.revenue_journal_entry_id = journal_entry.id
    line.revenue_journal_entry = journal_entry
    line.revenue_recognized_at = datetime.now(UTC)
    line.updated_by_user_id = actor.id
    line.entity_version += 1
    booking.status = derive_booking_status(booking.lines)
    booking.updated_by_user_id = actor.id
    booking.entity_version += 1
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="booking.line_completed",
        target_type="booking_line",
        target_id=line.id,
        summary=f"Completed booking line {booking.booking_number} / {line.line_number}",
        diff={
            "journal_entry_number": journal_entry.entry_number,
            "line_price": float(line.line_price),
            "recognized_at": line.revenue_recognized_at.isoformat(),
            "entity_version": line.entity_version,
        },
    )
    db.commit()
    return serialize_booking_document(reload_booking_or_404(BookingsRepository(db), booking.id))


def cancel_booking_line(db: Session, actor: User, booking_id: str, line_id: str, session: dict) -> dict:
    booking = get_scoped_booking(db, booking_id, session)
    line = get_line_or_404(booking, line_id)
    if line.revenue_journal_entry_id:
        raise ValidationAppError("ظ„ط§ ظٹظ…ظƒظ† ط¥ظ„ط؛ط§ط، ط§ظ„ط³ط·ظˆط± ط§ظ„ظ…ظƒطھظ…ظ„ط©")
    if line_paid_total(line) > ZERO:
        raise ValidationAppError("ظ„ط§ ظٹظ…ظƒظ† ط¥ظ„ط؛ط§ط، ط³ط·ط± ظ„ظ‡ ظ…ط¯ظپظˆط¹ط§طھ ظ…ط­طµظ„ط© ظ‚ط¨ظ„ ظ…ط¹ط§ظ„ط¬ط© ط§ظ„ط¯ظپط¹")
    line.status = "cancelled"
    line.updated_by_user_id = actor.id
    line.entity_version += 1
    booking.status = derive_booking_status(booking.lines)
    booking.updated_by_user_id = actor.id
    booking.entity_version += 1
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="booking.line_cancelled",
        target_type="booking_line",
        target_id=line.id,
        summary=f"Cancelled booking line {booking.booking_number} / {line.line_number}",
        diff={"booking_status": booking.status, "entity_version": line.entity_version},
    )
    db.commit()
    return serialize_booking_document(reload_booking_or_404(BookingsRepository(db), booking.id))


def reverse_completed_booking_line(
    db: Session,
    actor: User,
    booking_id: str,
    line_id: str,
    session: dict,
    *,
    override_lock: bool = False,
    override_reason: str | None = None,
) -> dict:
    override_payload = enforce_not_locked_with_override(
        db,
        action_date=date.today(),
        action_key="booking.line_revenue_reversed",
        actor=actor,
        override_lock=override_lock,
        override_reason=override_reason,
    )
    booking = get_scoped_booking(db, booking_id, session)
    line = get_line_or_404(booking, line_id)
    if line.status != "completed" or not line.revenue_journal_entry_id:
        raise ValidationAppError("ظٹظ…ظƒظ† ط¹ظƒط³ ط§ظ„ط¥ظٹط±ط§ط¯ ظپظ‚ط· ظ„ط³ط·ط± ظ…ظƒطھظ…ظ„")

    reversal = reverse_booking_line_revenue_recognition(db, actor, line, date.today())
    line.status = "confirmed"
    line.revenue_journal_entry_id = None
    line.revenue_journal_entry = None
    line.revenue_recognized_at = None
    line.updated_by_user_id = actor.id
    line.entity_version += 1
    booking.status = derive_booking_status(booking.lines)
    booking.updated_by_user_id = actor.id
    booking.entity_version += 1
    db.flush()
    if override_payload is not None:
        record_period_lock_override(
            db,
            actor_user_id=actor.id,
            entity_type="booking_line",
            entity_id=line.id,
            summary=f"Used period-lock override for revenue reversal on booking {booking.booking_number}",
            override_payload=override_payload,
        )
    record_audit(
        db,
        actor_user_id=actor.id,
        action="booking.line_revenue_reversed",
        target_type="booking_line",
        target_id=line.id,
        summary=f"Reversed revenue recognition for booking line {booking.booking_number} / {line.line_number}",
        diff={
            "reversal_entry_number": reversal.entry_number,
            "booking_status": booking.status,
            "entity_version": line.entity_version,
        },
    )
    db.commit()
    return serialize_booking_document(reload_booking_or_404(BookingsRepository(db), booking.id))
