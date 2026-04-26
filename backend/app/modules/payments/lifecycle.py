from __future__ import annotations

from datetime import UTC, datetime
from sqlalchemy.orm import Session

from app.core.enums import PaymentReceiptStatus
from app.modules.core_platform.destructive_reasons import normalize_destructive_reason_code
from app.modules.core_platform.period_lock import enforce_not_locked_with_override, record_period_lock_override
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.payments.accounting_bridge import reverse_linked_payment_document_entry
from app.modules.payments.document_access import (
    ensure_payment_document_is_editable,
    get_scoped_payment_document,
    load_document_or_404,
)
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.rules import clean_required_text, parse_payment_date
from app.modules.payments.schemas import PaymentVoidRequest


def void_payment(db: Session, actor: User, payment_document_id: str, payload: PaymentVoidRequest, session: dict) -> dict:
    payment_document = get_scoped_payment_document(db, payment_document_id, session)
    ensure_payment_document_is_editable(payment_document)
    void_date = parse_payment_date(payload.void_date)
    override_payload = enforce_not_locked_with_override(
        db,
        action_date=void_date,
        action_key="payment.void",
        actor=actor,
        override_lock=payload.override_lock,
        override_reason=payload.override_reason,
    )
    reversal = (
        reverse_linked_payment_document_entry(db, actor, payment_document, void_date)
        if payment_document.journal_entry_id
        else None
    )
    payment_document.status = PaymentReceiptStatus.VOIDED.value
    payment_document.voided_at = datetime.now(UTC)
    payment_document.voided_by_user_id = actor.id
    payment_document.updated_by_user_id = actor.id
    payment_document.entity_version += 1
    reason_code = normalize_destructive_reason_code(payload.reason_code, action="void", default_code="financial_correction")
    payment_document.void_reason = clean_required_text(payload.reason, "سبب الإبطال مطلوب")
    db.flush()
    if override_payload is not None:
        record_period_lock_override(
            db,
            actor_user_id=actor.id,
            entity_type="payment_document",
            entity_id=payment_document.id,
            summary=f"Used period-lock override for payment void {payment_document.payment_number}",
            override_payload=override_payload,
        )
    record_audit(
        db,
        actor_user_id=actor.id,
        action="payment_document.voided",
        target_type="payment_document",
        target_id=payment_document.id,
        summary=f"Voided payment document {payment_document.payment_number}",
        diff={
            "reason_code": reason_code,
            "reason": payment_document.void_reason,
            "journal_entry_id": payment_document.journal_entry_id,
            "reversal_entry_number": reversal.entry_number if reversal else None,
            "entity_version": payment_document.entity_version,
        },
    )
    db.commit()
    return load_document_or_404(PaymentsRepository(db), payment_document.id, include_allocations=True)
