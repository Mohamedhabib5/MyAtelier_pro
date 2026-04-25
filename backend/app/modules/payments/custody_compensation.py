from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import PaymentReceiptStatus
from app.modules.core_platform.period_lock import enforce_not_locked_with_override, record_period_lock_override
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.branch_context import ensure_active_branch
from app.modules.organization.service import get_company_settings
from app.modules.payments.accounting_bridge import auto_post_payment_document
from app.modules.payments.document_access import PAYMENT_SEQUENCE_KEY, ensure_payment_sequence
from app.modules.payments.models import PaymentDocument
from app.modules.payments.payment_methods import resolve_payment_method
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.rules import clean_optional_text, parse_payment_date


def create_custody_compensation_payment(
    db: Session,
    actor: User,
    session: dict,
    *,
    customer_id: str,
    payment_date: str,
    amount: float,
    source_case_id: str,
    note: str | None,
    payment_method_id: str | None = None,
    override_lock: bool = False,
    override_reason: str | None = None,
) -> PaymentDocument:
    return _create_custody_direct_payment(
        db,
        actor,
        session,
        customer_id=customer_id,
        payment_date=payment_date,
        amount=amount,
        source_case_id=source_case_id,
        note=note,
        payment_method_id=payment_method_id,
        document_kind="custody_compensation",
        period_action_key="custody.compensation_collection",
        audit_action="payment_document.custody_compensation_created",
        audit_summary_prefix="Created custody compensation payment",
        override_lock=override_lock,
        override_reason=override_reason,
    )


def create_custody_deposit_collection_payment(
    db: Session,
    actor: User,
    session: dict,
    *,
    customer_id: str,
    payment_date: str,
    amount: float,
    source_case_id: str,
    note: str | None,
    payment_method_id: str | None = None,
    override_lock: bool = False,
    override_reason: str | None = None,
) -> PaymentDocument:
    return _create_custody_direct_payment(
        db,
        actor,
        session,
        customer_id=customer_id,
        payment_date=payment_date,
        amount=amount,
        source_case_id=source_case_id,
        note=note,
        payment_method_id=payment_method_id,
        document_kind="custody_deposit",
        period_action_key="custody.deposit_collection",
        audit_action="payment_document.custody_deposit_created",
        audit_summary_prefix="Created custody deposit payment",
        override_lock=override_lock,
        override_reason=override_reason,
    )


def create_custody_deposit_refund_payment(
    db: Session,
    actor: User,
    session: dict,
    *,
    customer_id: str,
    payment_date: str,
    amount: float,
    source_case_id: str,
    note: str | None,
    payment_method_id: str | None = None,
    override_lock: bool = False,
    override_reason: str | None = None,
) -> PaymentDocument:
    return _create_custody_direct_payment(
        db,
        actor,
        session,
        customer_id=customer_id,
        payment_date=payment_date,
        amount=amount,
        source_case_id=source_case_id,
        note=note,
        payment_method_id=payment_method_id,
        document_kind="refund",
        period_action_key="custody.deposit_refund",
        audit_action="payment_document.custody_deposit_refund_created",
        audit_summary_prefix="Created custody deposit refund payment",
        override_lock=override_lock,
        override_reason=override_reason,
    )


def _create_custody_direct_payment(
    db: Session,
    actor: User,
    session: dict,
    *,
    customer_id: str,
    payment_date: str,
    amount: float,
    source_case_id: str,
    note: str | None,
    payment_method_id: str | None,
    document_kind: str,
    period_action_key: str,
    audit_action: str,
    audit_summary_prefix: str,
    override_lock: bool = False,
    override_reason: str | None = None,
) -> PaymentDocument:
    branch = ensure_active_branch(db, session)
    company = get_company_settings(db)
    repo = PaymentsRepository(db)
    ensure_payment_sequence(db, company.id)
    payment_method = resolve_payment_method(
        db,
        company_id=company.id,
        payment_method_id=payment_method_id,
        actor_user_id=actor.id,
    )
    parsed_date = parse_payment_date(payment_date)
    normalized_note = clean_optional_text(note)
    override_payload = enforce_not_locked_with_override(
        db,
        action_date=parsed_date,
        action_key=period_action_key,
        actor=actor,
        override_lock=override_lock,
        override_reason=override_reason,
    )
    payment_document = PaymentDocument(
        company_id=company.id,
        branch_id=branch.id,
        customer_id=customer_id,
        payment_method_id=payment_method.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        payment_number=repo.reserve_sequence_number(company.id, PAYMENT_SEQUENCE_KEY),
        payment_date=parsed_date,
        document_kind=document_kind,
        direct_amount=Decimal(str(amount)).quantize(Decimal("0.01")),
        status=PaymentReceiptStatus.ACTIVE.value,
        notes=normalized_note,
    )
    repo.add_payment_document(payment_document)
    db.flush()
    journal_entry = auto_post_payment_document(db, actor, payment_document)
    payment_document.journal_entry_id = journal_entry.id
    payment_document.journal_entry = journal_entry
    db.flush()
    if override_payload is not None:
        record_period_lock_override(
            db,
            actor_user_id=actor.id,
            entity_type="payment_document",
            entity_id=payment_document.id,
            summary=f"Used period-lock override for {document_kind} {payment_document.payment_number}",
            override_payload=override_payload,
        )
    record_audit(
        db,
        actor_user_id=actor.id,
        action=audit_action,
        target_type="payment_document",
        target_id=payment_document.id,
        summary=f"{audit_summary_prefix} {payment_document.payment_number}",
        diff={
            "source_case_id": source_case_id,
            "document_kind": payment_document.document_kind,
            "total_amount": float(payment_document.direct_amount),
            "journal_entry_number": journal_entry.entry_number,
            "entity_version": payment_document.entity_version,
        },
    )
    return payment_document
