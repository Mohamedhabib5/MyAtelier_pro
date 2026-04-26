from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.modules.bookings.calculations import derive_booking_status, line_paid_total, serialize_booking_document
from app.modules.bookings.document_access import get_line_or_404, get_scoped_booking, reload_booking_or_404
from app.modules.bookings.repository import BookingsRepository
from app.modules.bookings.revenue_bridge import post_booking_line_revenue_recognition, reverse_booking_line_revenue_recognition
from app.modules.core_platform.period_lock import enforce_not_locked_with_override, record_period_lock_override
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User

ZERO = Decimal("0.00")

def complete_booking_line(db: Session, actor: User, booking_id: str, line_id: str, session: dict) -> dict:
    booking = get_scoped_booking(db, booking_id, session)
    line = get_line_or_404(booking, line_id)
    if line.status == "cancelled":
        raise ValidationAppError("لا يمكن إكمال السطور الملغاة")
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
        raise ValidationAppError("لا يمكن إلغاء السطور المكتملة")
    if line_paid_total(line) > ZERO:
        raise ValidationAppError("لا يمكن إلغاء سطر له مدفوعات محصلة قبل معالجة الدفع")
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
        raise ValidationAppError("يمكن عكس الإيراد فقط لسطر مكتمل")

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
