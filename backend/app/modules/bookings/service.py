from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError, ConflictError
from app.core.messages import BOOKING_CANCELLED_NO_EDIT, BOOKING_LINE_NOT_FOUND, BOOKING_LINE_RECOGNIZED_DELETE_ERROR, BOOKING_LINE_PAID_DELETE_ERROR
from app.modules.bookings.calculations import derive_booking_status, line_paid_total, serialize_booking_document
from app.modules.bookings.document_access import BOOKING_SEQUENCE_KEY, ensure_booking_sequence, get_scoped_booking_by_branch, reload_booking_or_404
from app.modules.bookings.line_mutations import create_initial_payment_document, materialize_line
from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.query_service import get_calendar_events, list_booking_page, list_bookings
from app.modules.bookings.reference_data import get_customer_or_404
from app.modules.bookings.repository import BookingsRepository
from app.modules.bookings.rules import clean_optional, parse_date
from app.modules.bookings.schemas import BookingDocumentCreateRequest, BookingDocumentUpdateRequest
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_by_id
from app.modules.organization.service import get_company_settings

ZERO = Decimal("0.00")

def get_booking_document(db: Session, booking_id: str, branch_id: str) -> dict:
    return serialize_booking_document(get_scoped_booking_by_branch(db, booking_id, branch_id))


def create_booking(db: Session, actor: User, payload: BookingDocumentCreateRequest, branch_id: str) -> dict:
    company = get_company_settings(db)
    branch = resolve_branch_by_id(db, branch_id)
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


def update_booking(db: Session, actor: User, booking_id: str, payload: BookingDocumentUpdateRequest, branch_id: str) -> dict:
    booking = get_scoped_booking_by_branch(db, booking_id, branch_id)
    
    if booking.status == "cancelled":
        raise ValidationAppError(BOOKING_CANCELLED_NO_EDIT)

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
            raise ValidationAppError(BOOKING_LINE_NOT_FOUND)
        line_entry = materialize_line(db, company_id, actor.id, payload_line, existing_line, index)
        next_lines.append(line_entry["line"])
        line_entries.append(line_entry)
        if existing_line is not None:
            seen_ids.add(existing_line.id)

    for line in booking.lines:
        if line.id in seen_ids:
            continue
        if line.revenue_journal_entry_id:
            raise ValidationAppError(BOOKING_LINE_RECOGNIZED_DELETE_ERROR)
        if line_paid_total(line) > ZERO:
            raise ValidationAppError(BOOKING_LINE_PAID_DELETE_ERROR)

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


def create_compensation_booking(db: Session, actor: User, original_booking_id: str, payload: BookingCompensationCreateRequest, branch_id: str) -> dict:
    original = get_scoped_booking_by_branch(db, original_booking_id, branch_id)
    company = get_company_settings(db)
    branch = resolve_branch_by_id(db, branch_id)
    repo = BookingsRepository(db)
    
    compensation_number = f"{original.booking_number}-C"
    
    # Check if already exists (unlikely but safe)
    existing = db.query(Booking).filter_by(company_id=company.id, booking_number=compensation_number).first()
    if existing:
        # If multiple compensations, add index
        count = db.query(Booking).filter(Booking.booking_number.like(f"{compensation_number}%")).count()
        compensation_number = f"{compensation_number}{count + 1}"

    booking = Booking(
        company_id=company.id,
        branch_id=branch.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        booking_number=compensation_number,
        customer_id=original.customer_id,
        booking_date=parse_date(None, default_today=True),
        status="active",
        parent_booking_id=original.id,
        notes=f"سند تعويض مرتبط بالحجز {original.booking_number}. {clean_optional(payload.notes) or ''}",
    )
    
    line = BookingLine(
        booking=booking,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        department_id=payload.department_id,
        service_id=payload.service_id,
        line_number=1,
        service_date=booking.booking_date,
        suggested_price=Decimal(str(payload.amount)),
        line_price=Decimal(str(payload.amount)),
        status="active"
    )
    booking.lines = [line]
    
    repo.add_booking(booking)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="booking.compensation_created",
        target_type="booking",
        target_id=booking.id,
        summary=f"Created compensation booking {booking.booking_number} from {original.booking_number}",
        diff={
            "parent_id": original.id,
            "amount": float(line.line_price)
        },
    )
    db.commit()
    return serialize_booking_document(reload_booking_or_404(repo, booking.id))

def delete_booking(db: Session, actor: User, booking_id: str, branch_id: str) -> None:
    booking = get_scoped_booking_by_branch(db, booking_id, branch_id)
    
    # Financial Integrity Check
    for line in booking.lines:
        if line_paid_total(line) > ZERO:
            raise ConflictError(f"لا يمكن حذف الحجز {booking.booking_number} لوجود مبالغ مدفوعة. يجب حذف سندات القبض المرتبطة أولاً.")
        if line.revenue_journal_entry_id:
            raise ConflictError(f"لا يمكن حذف الحجز {booking.booking_number} لوجود قيود إيرادات معترف بها.")

    record_audit(
        db,
        actor_user_id=actor.id,
        action="booking.deleted",
        target_type="booking",
        target_id=booking.id,
        summary=f"Permanently deleted booking {booking.booking_number}",
        diff={
            "booking_number": booking.booking_number,
            "customer_id": booking.customer_id,
            "line_count": len(booking.lines)
        },
    )
    db.delete(booking)
    db.commit()


def delete_booking_line(db: Session, actor: User, booking_id: str, line_id: str, branch_id: str) -> dict:
    booking = get_scoped_booking_by_branch(db, booking_id, branch_id)
    line = next((l for l in booking.lines if l.id == line_id), None)
    if not line:
        raise ValidationAppError(BOOKING_LINE_NOT_FOUND)

    # Financial Integrity Check
    if line_paid_total(line) > ZERO:
        raise ConflictError("لا يمكن حذف السطر لوجود مبالغ مدفوعة مرتبطة به.")
    if line.revenue_journal_entry_id:
        raise ConflictError("لا يمكن حذف السطر لوجود قيد إيراد معترف به.")

    record_audit(
        db,
        actor_user_id=actor.id,
        action="booking_line.deleted",
        target_type="booking_line",
        target_id=line.id,
        summary=f"Permanently deleted line {line.line_number} from booking {booking.booking_number}",
        diff={
            "booking_id": booking.id,
            "line_number": line.line_number,
            "service_name": line.service.name
        },
    )
    db.delete(line)
    db.flush()
    
    # Re-index remaining lines to prevent gaps if needed, or just keep them
    # For now, we'll just derive the status again
    booking.status = derive_booking_status(booking.lines)
    db.commit()
    return serialize_booking_document(reload_booking_or_404(BookingsRepository(db), booking.id))
 
 
