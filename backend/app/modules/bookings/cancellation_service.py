from __future__ import annotations

from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.enums import PaymentDocumentKind, PaymentReceiptStatus
from app.core.exceptions import ValidationAppError
from app.modules.bookings.calculations import line_paid_total, serialize_booking_document, quantize_amount, derive_booking_status
from app.modules.bookings.document_access import get_scoped_booking_by_branch, reload_booking_or_404
from app.modules.bookings.models import Booking, BookingLine
from app.modules.bookings.repository import BookingsRepository
from app.modules.core_platform.period_lock import enforce_not_locked_with_override, record_period_lock_override
from app.modules.bookings.rules import clean_optional, parse_date
from app.modules.bookings.schemas import BookingCancellationRequest
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_by_id
from app.modules.organization.service import get_company_settings
from app.modules.payments.models import PaymentDocument, PaymentAllocation
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.payment_methods import resolve_payment_method
from app.modules.payments.accounting_bridge import auto_post_payment_document
from app.modules.bookings.revenue_bridge import reverse_booking_line_revenue_recognition
from app.modules.payments.booking_bridge import create_cancellation_refund_document

ZERO = Decimal("0.00")

def _distribute_amount(lines: list[BookingLine], total_amount: Decimal) -> list[tuple[BookingLine, Decimal]]:
    from app.modules.bookings.calculations import line_paid_total, quantize_amount
    ZERO = Decimal("0.00")
    
    total_paid = sum((line_paid_total(l) for l in lines), start=ZERO)
    if total_paid <= ZERO:
        return [(lines[0], total_amount)] if lines else []
        
    result: list[tuple[BookingLine, Decimal]] = []
    remaining = total_amount
    eligible_lines = [l for l in lines if line_paid_total(l) > ZERO]
    if not eligible_lines and lines:
        eligible_lines = [lines[0]]

    for i, line in enumerate(eligible_lines):
        line_paid = line_paid_total(line)
        if i == len(eligible_lines) - 1:
            share = remaining
        else:
            share = quantize_amount(total_amount * (line_paid / total_paid))
            if share > remaining: share = remaining
        
        result.append((line, share))
        remaining -= share
    return result


def cancel_booking_workflow(db: Session, actor: User, booking_id: str, payload: BookingCancellationRequest, branch_id: str) -> dict:
    repo = BookingsRepository(db)
    _execute_cancellation(db, actor, booking_id, payload, branch_id)
    db.commit()
    return serialize_booking_document(reload_booking_or_404(repo, booking_id))


def bulk_cancel_workflow(db: Session, actor: User, booking_id: str, payload: BulkBookingCancellationRequest, branch_id: str) -> dict:
    repo = BookingsRepository(db)
    for request in payload.requests:
        _execute_cancellation(db, actor, booking_id, request, branch_id)
    db.commit()
    return serialize_booking_document(reload_booking_or_404(repo, booking_id))


def _execute_cancellation(db: Session, actor: User, booking_id: str, payload: BookingCancellationRequest, branch_id: str) -> None:
    from app.modules.payments.models import PaymentMethod
    from app.modules.payments.payment_methods import SYSTEM_INTERNAL_METHOD_CODE, _ensure_active_method_available
    from app.modules.payments.booking_bridge import create_payment_document_from_lines

    booking = get_scoped_booking_by_branch(db, booking_id, branch_id)
    
    company = get_company_settings(db)
    branch = resolve_branch_by_id(db, branch_id)
    
    cancel_date = parse_date(payload.cancellation_date, default_today=True)
    reason = clean_optional(payload.reason)
    
    # Determine Scope
    target_lines: list[BookingLine] = []
    if payload.line_ids:
        # Partial Cancellation
        line_id_set = set(payload.line_ids)
        target_lines = [line for line in booking.lines if line.id in line_id_set]
        if not target_lines:
            raise ValidationAppError("لم يتم العثور على أسطر الخدمة المحددة")
    else:
        # Full Cancellation
        if booking.status == "cancelled":
            raise ValidationAppError("الحجز ملغي بالفعل")
        target_lines = booking.lines

    # Calculate Totals
    total_paid_in_scope = sum(line_paid_total(line) for line in target_lines)
    max_refundable = quantize_amount(total_paid_in_scope)
    
    refund_amount = quantize_amount(Decimal(str(payload.refund_amount)))
    transfer_amount = quantize_amount(Decimal(str(payload.transfer_amount)))
    
    if (refund_amount + transfer_amount) > max_refundable:
        raise ValidationAppError(f"مجموع الرد والتحويل ({refund_amount + transfer_amount}) يتجاوز إجمالي المقبوض في النطاق المختار ({max_refundable})")
    
    forfeit_amount = quantize_amount(max_refundable - refund_amount - transfer_amount)

    # --- Enforce Period Lock ---
    override_payload = enforce_not_locked_with_override(
        db,
        action_date=cancel_date,
        action_key="booking.cancelled",
        actor=actor,
        override_lock=getattr(payload, "override_lock", False),
        override_reason=getattr(payload, "override_reason", None),
    )

    # Update status for target lines
    cancellation_time = datetime.now()
    for line in target_lines:
        if line.status == "cancelled":
            continue
        if line.revenue_journal_entry_id:
            reverse_booking_line_revenue_recognition(db, actor, line, cancel_date)
            
        line.status = "cancelled"
        line.cancelled_at = cancellation_time
        line.cancellation_reason = reason
        line.cancelled_by_user_id = actor.id

    # If full cancellation, update booking status
    if not payload.line_ids:
        booking.status = "cancelled"
        booking.cancelled_at = cancellation_time
        booking.cancellation_reason = reason
        booking.cancelled_by_user_id = actor.id
    else:
        booking.status = derive_booking_status(booking.lines)
    
    booking.updated_by_user_id = actor.id
    booking.entity_version += 1
    db.flush()
    
    # --- Handle Override Logging ---
    if override_payload:
        record_period_lock_override(
            db,
            actor_user_id=actor.id,
            entity_type="booking",
            entity_id=booking.id,
            summary=f"Cancelled booking {booking.booking_number} in locked period",
            override_payload=override_payload,
        )

    # --- PROCESS PAYMENTS (Wash Transaction Logic) ---
    
    # Get internal payment method
    internal_method = db.query(PaymentMethod).filter_by(company_id=company.id, code=SYSTEM_INTERNAL_METHOD_CODE).first()
    if not internal_method:
        _ensure_active_method_available(db, company.id, actor_user_id=actor.id)
        internal_method = db.query(PaymentMethod).filter_by(company_id=company.id, code=SYSTEM_INTERNAL_METHOD_CODE).first()

    # 1. Actual Refund (Money returning to customer)
    if refund_amount > ZERO:
        line_refunds = _distribute_amount(target_lines, refund_amount)
        create_cancellation_refund_document(
            db, actor, booking, line_refunds,
            cancel_date, reason,
            payment_method_id=payload.payment_method_id,
            notes=f"سند رد نقدي لإلغاء في الحجز {booking.booking_number}. السبب: {reason}"
        )

    # 2. Internal Movement (Transfer + Forfeit)
    internal_movement_total = transfer_amount + forfeit_amount
    if internal_movement_total > ZERO:
        # a) Internal Refund (Reversal)
        line_internal_reversals = _distribute_amount(target_lines, internal_movement_total)
        create_cancellation_refund_document(
            db, actor, booking, line_internal_reversals,
            cancel_date, reason,
            payment_method_id=internal_method.id,
            notes=f"تسوية نظام (عكس رصيد) لإلغاء/تحويل في الحجز {booking.booking_number}"
        )
        
        # b) Internal Collection (Settlement)
        collection_allocations: list[tuple[BookingLine, Decimal]] = []
        
        # Add forfeit portion back to cancelled lines
        if forfeit_amount > ZERO:
            forfeit_shares = _distribute_amount(target_lines, forfeit_amount)
            collection_allocations.extend(forfeit_shares)
            
        # Add transfer portion to destination line
        if transfer_amount > ZERO:
            dest_line = next((l for l in booking.lines if l.id == payload.transfer_to_line_id), None)
            if not dest_line:
                raise ValidationAppError("سطر التحويل غير موجود")
            collection_allocations.append((dest_line, transfer_amount))
            
        create_payment_document_from_lines(
            db, actor, booking, collection_allocations,
            cancel_date,
            payment_method_id=internal_method.id,
            notes=f"تسوية نظام (إعادة تخصيص غرامة/تحويل) للحجز {booking.booking_number}"
        )

    # Finalize line prices for target lines (Forfeiture Revenue)
    for line in target_lines:
        db.refresh(line)
        final_paid = line_paid_total(line)
        line.line_price = final_paid
        
        # Recalculate tax based on the forfeited (final paid) amount
        if line.tax_rate_percent > ZERO and final_paid > ZERO:
            rate = line.tax_rate_percent / Decimal("100")
            base_price = final_paid / (Decimal("1") + rate)
            line.tax_amount = quantize_amount(final_paid - base_price)
        else:
            line.tax_amount = ZERO
            
        # Recognized forfeited amount as realized revenue
        if line.line_price > ZERO:
            from app.modules.bookings.revenue_bridge import post_booking_line_revenue_recognition
            try:
                recognition_entry = post_booking_line_revenue_recognition(db, actor, line, cancel_date)
                line.revenue_journal_entry_id = recognition_entry.id
                line.revenue_recognized_at = datetime.now()
            except Exception as e:
                from app.modules.core_platform.service import record_audit
                record_audit(
                    db,
                    actor_user_id=actor.id,
                    action="booking.revenue_recognition_failed",
                    target_type="booking_line",
                    target_id=line.id,
                    summary=f"Failed to recognize revenue for line {line.id}",
                    diff={"error": str(e)},
                    success=False,
                    error_code="revenue_reversal_failed",
                )
                raise
    
    if not payload.line_ids:
        record_audit(
            db,
            actor_user_id=actor.id,
            action="booking.cancelled",
            target_type="booking",
            target_id=booking.id,
            summary=f"Cancelled booking for {booking.booking_number}. Refund: {refund_amount}, Transfer: {transfer_amount}",
            diff={
                "refund_amount": float(refund_amount),
                "transfer_amount": float(transfer_amount),
                "forfeit_amount": float(forfeit_amount),
                "reason": reason,
                "partial": False
            },
        )
    else:
        record_audit(
            db,
            actor_user_id=actor.id,
            action="booking.line_cancelled",
            target_type="booking",
            target_id=booking.id,
            summary=f"Cancelled lines for {booking.booking_number}. Refund: {refund_amount}, Transfer: {transfer_amount}",
            diff={
                "refund_amount": float(refund_amount),
                "transfer_amount": float(transfer_amount),
                "forfeit_amount": float(forfeit_amount),
                "reason": reason,
                "partial": True
            },
        )


def undo_cancellation_workflow(db: Session, actor: User, booking_id: str, line_ids: list[str] | None, branch_id: str) -> dict:
    booking = get_scoped_booking_by_branch(db, booking_id, branch_id)
    repo = BookingsRepository(db)

    # Determine Scope
    target_lines: list[BookingLine] = []
    if line_ids:
        line_id_set = set(line_ids)
        target_lines = [line for line in booking.lines if line.id in line_id_set]
    else:
        target_lines = [line for line in booking.lines if line.status == "cancelled"]

    if not target_lines:
        raise ValidationAppError("لا توجد أسطر ملغاة للتراجع عنها")

    # Restore Status
    for line in target_lines:
        if line.status != "cancelled":
            continue
        line.status = "confirmed" # Default restoration state
        line.cancelled_at = None
        line.cancellation_reason = None
        line.cancelled_by_user_id = None

    # Restore Booking Status
    booking.status = derive_booking_status(booking.lines)
    if not line_ids:
        if booking.status == "cancelled":
            booking.status = "confirmed"
        booking.cancelled_at = None
        booking.cancellation_reason = None
        booking.cancelled_by_user_id = None

    # Cleanup Linked Documents (Refunds and Internal Settlements)
    from app.modules.payments.service import delete_payment
    from app.modules.payments.payment_methods import SYSTEM_INTERNAL_METHOD_CODE
    
    docs_to_delete: set[str] = set()
    for line in target_lines:
        for alloc in line.payment_allocations:
            doc = alloc.payment_document
            # Delete if it's a refund (actual or internal reversal)
            if doc.document_kind == PaymentDocumentKind.REFUND.value:
                docs_to_delete.add(doc.id)
            # Delete if it's an internal settlement (collection with system_internal method)
            elif doc.document_kind == PaymentDocumentKind.COLLECTION.value and doc.payment_method.code == SYSTEM_INTERNAL_METHOD_CODE:
                docs_to_delete.add(doc.id)

    for doc_id in docs_to_delete:
        try:
            delete_payment(db, actor, doc_id, branch_id)
        except Exception as e:
            raise ValidationAppError(f"فشل حذف السند المرتبط {doc_id}: {str(e)}")

    record_audit(
        db,
        actor_user_id=actor.id,
        action="booking.cancellation_undone",
        target_type="booking",
        target_id=booking.id,
        summary=f"Undid cancellation for {booking.booking_number}",
        diff={
            "line_ids": line_ids,
            "docs_deleted": list(docs_to_delete)
        },
    )

    db.commit()
    return serialize_booking_document(reload_booking_or_404(repo, booking.id))
