from __future__ import annotations

from decimal import Decimal
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError, ConflictError
from app.core.enums import PaymentReceiptStatus
from app.modules.core_platform.destructive_reasons import normalize_destructive_reason_code
from app.modules.core_platform.period_lock import enforce_not_locked_with_override, record_period_lock_override
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.branch_context import resolve_branch_by_id
from app.modules.organization.service import get_company_settings
from app.modules.payments.accounting_bridge import (
    auto_post_disbursement_voucher,
    reverse_linked_disbursement_voucher_entry,
    delete_linked_disbursement_voucher_entry,
)
from app.modules.payments.document_access import (
    DISBURSEMENT_SEQUENCE_KEY,
    ensure_payment_sequence,
)
from app.modules.payments.models import DisbursementVoucher
from app.modules.payments.payment_methods import resolve_payment_method
from app.modules.payments.repository import PaymentsRepository
from app.modules.payments.rules import clean_optional_text, parse_payment_date, clean_required_text
from app.modules.payments.serializers import serialize_disbursement
from app.modules.payments.schemas import (
    DisbursementVoucherCreateRequest,
    DisbursementVoucherUpdateRequest,
    PaymentVoidRequest,
)

def list_disbursements(db: Session, branch_id: str) -> list[dict]:
    company = get_company_settings(db)
    rows = PaymentsRepository(db).list_disbursement_vouchers(company.id, branch_id)
    return [serialize_disbursement(row) for row in rows]


def list_disbursement_page(
    db: Session,
    branch_id: str,
    *,
    search: str | None = None,
    status: str | None = None,
    payee_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 25,
    sort_by: str = "voucher_date",
    sort_dir: str = "desc",
) -> dict:
    company = get_company_settings(db)
    rows, total = PaymentsRepository(db).list_disbursement_voucher_page(
        company.id,
        branch_id=branch_id,
        search=clean_optional_text(search),
        status=clean_optional_text(status),
        payee_type=clean_optional_text(payee_type),
        date_from=parse_payment_date(date_from) if date_from else None,
        date_to=parse_payment_date(date_to) if date_to else None,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir="asc" if sort_dir == "asc" else "desc",
    )
    return {"items": [serialize_disbursement(row) for row in rows], "total": total, "page": page, "page_size": page_size}


def get_disbursement_voucher(db: Session, disbursement_voucher_id: str, branch_id: str) -> dict:
    company = get_company_settings(db)
    voucher = PaymentsRepository(db).get_disbursement_voucher(disbursement_voucher_id)
    if voucher is None or voucher.company_id != company.id or voucher.branch_id != branch_id:
        raise ValidationAppError("لم يتم العثور على سند الصرف")
    return serialize_disbursement(voucher)


def create_disbursement(db: Session, actor: User, payload: DisbursementVoucherCreateRequest, branch_id: str) -> dict:
    branch = resolve_branch_by_id(db, branch_id)
    company = get_company_settings(db)
    repo = PaymentsRepository(db)
    
    # Seed/ensure sequence exists
    ensure_payment_sequence(db, company.id)
    
    payment_method = resolve_payment_method(
        db,
        company_id=company.id,
        payment_method_id=payload.payment_method_id,
        actor_user_id=actor.id,
    )
    
    voucher = DisbursementVoucher(
        company_id=company.id,
        branch_id=branch.id,
        payment_method_id=payment_method.id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        entity_version=1,
        voucher_number=repo.reserve_sequence_number(company.id, DISBURSEMENT_SEQUENCE_KEY),
        voucher_date=parse_payment_date(payload.voucher_date),
        amount=Decimal(str(payload.amount)),
        payee_type=payload.payee_type,
        payee_id=payload.payee_id,
        payee_name=clean_optional_text(payload.payee_name),
        expense_category_id=payload.expense_category_id,
        status=PaymentReceiptStatus.ACTIVE.value,
        notes=clean_optional_text(payload.notes),
    )
    
    repo.add_disbursement_voucher(voucher)
    db.flush()
    
    journal_entry = auto_post_disbursement_voucher(db, actor, voucher)
    voucher.journal_entry_id = journal_entry.id
    voucher.journal_entry = journal_entry
    db.flush()
    
    record_audit(
        db,
        actor_user_id=actor.id,
        action="disbursement_voucher.created",
        target_type="disbursement_voucher",
        target_id=voucher.id,
        summary=f"Created disbursement voucher {voucher.voucher_number}",
        diff={
            "total_amount": float(voucher.amount),
            "branch_id": voucher.branch_id,
            "entity_version": voucher.entity_version,
            "payee_type": voucher.payee_type,
            "payee_name": voucher.payee_name,
        },
    )
    db.commit()
    
    return serialize_disbursement(voucher)


def update_disbursement(db: Session, actor: User, disbursement_voucher_id: str, payload: DisbursementVoucherUpdateRequest, branch_id: str) -> dict:
    company = get_company_settings(db)
    repo = PaymentsRepository(db)
    voucher = repo.get_disbursement_voucher(disbursement_voucher_id)
    if voucher is None or voucher.company_id != company.id or voucher.branch_id != branch_id:
        raise ValidationAppError("لم يتم العثور على سند الصرف")
        
    if voucher.status == PaymentReceiptStatus.VOIDED.value:
        raise ValidationAppError("لا يمكن تعديل سند صرف ملغي")
        
    action_date = parse_payment_date(payload.voucher_date) if payload.voucher_date else voucher.voucher_date
    override_payload = enforce_not_locked_with_override(
        db,
        action_date=action_date,
        action_key="disbursement.update",
        actor=actor,
        override_lock=payload.override_lock,
        override_reason=payload.override_reason,
    )
    
    previous_journal_entry_id = voucher.journal_entry_id
    if voucher.journal_entry_id:
        reverse_linked_disbursement_voucher_entry(db, actor, voucher, action_date)
        voucher.journal_entry_id = None
        voucher.journal_entry = None
        
    if payload.payment_method_id is not None:
        payment_method = resolve_payment_method(db, company_id=company.id, payment_method_id=payload.payment_method_id, actor_user_id=actor.id)
        voucher.payment_method_id = payment_method.id
    if payload.voucher_date is not None:
        voucher.voucher_date = parse_payment_date(payload.voucher_date)
    if payload.amount is not None:
        voucher.amount = Decimal(str(payload.amount))
    if payload.payee_type is not None:
        voucher.payee_type = payload.payee_type
    if payload.payee_id is not None:
        voucher.payee_id = payload.payee_id
    if payload.payee_name is not None:
        voucher.payee_name = clean_optional_text(payload.payee_name)
    if payload.expense_category_id is not None:
        voucher.expense_category_id = payload.expense_category_id
    if payload.notes is not None:
        voucher.notes = clean_optional_text(payload.notes)
        
    voucher.updated_by_user_id = actor.id
    voucher.entity_version += 1
    db.flush()
    
    journal_entry = auto_post_disbursement_voucher(db, actor, voucher)
    voucher.journal_entry_id = journal_entry.id
    voucher.journal_entry = journal_entry
    db.flush()
    
    if override_payload is not None:
        record_period_lock_override(
            db,
            actor_user_id=actor.id,
            entity_type="disbursement_voucher",
            entity_id=voucher.id,
            summary=f"Used period-lock override for disbursement update {voucher.voucher_number}",
            override_payload=override_payload,
        )
        
    record_audit(
        db,
        actor_user_id=actor.id,
        action="disbursement_voucher.updated",
        target_type="disbursement_voucher",
        target_id=voucher.id,
        summary=f"Updated disbursement voucher {voucher.voucher_number}",
        diff={
            "total_amount": float(voucher.amount),
            "entity_version": voucher.entity_version,
            "previous_journal_entry_id": previous_journal_entry_id,
            "new_journal_entry_id": journal_entry.id,
        },
    )
    db.commit()
    return serialize_disbursement(voucher)


def void_disbursement(db: Session, actor: User, disbursement_voucher_id: str, payload: PaymentVoidRequest, branch_id: str) -> dict:
    company = get_company_settings(db)
    repo = PaymentsRepository(db)
    voucher = repo.get_disbursement_voucher(disbursement_voucher_id)
    if voucher is None or voucher.company_id != company.id or voucher.branch_id != branch_id:
        raise ValidationAppError("لم يتم العثور على سند الصرف")
        
    if voucher.status == PaymentReceiptStatus.VOIDED.value:
        raise ValidationAppError("سند الصرف ملغي بالفعل")
        
    void_date = parse_payment_date(payload.void_date)
    override_payload = enforce_not_locked_with_override(
        db,
        action_date=void_date,
        action_key="disbursement.void",
        actor=actor,
        override_lock=payload.override_lock,
        override_reason=payload.override_reason,
    )
    
    reversal = (
        reverse_linked_disbursement_voucher_entry(db, actor, voucher, void_date)
        if voucher.journal_entry_id
        else None
    )
    
    voucher.status = PaymentReceiptStatus.VOIDED.value
    voucher.voided_at = datetime.now(UTC)
    voucher.voided_by_user_id = actor.id
    voucher.updated_by_user_id = actor.id
    voucher.entity_version += 1
    reason_code = normalize_destructive_reason_code(payload.reason_code, action="void", default_code="financial_correction")
    voucher.void_reason = clean_required_text(payload.reason, "سبب الإبطال مطلوب")
    db.flush()
    
    if override_payload is not None:
        record_period_lock_override(
            db,
            actor_user_id=actor.id,
            entity_type="disbursement_voucher",
            entity_id=voucher.id,
            summary=f"Used period-lock override for disbursement void {voucher.voucher_number}",
            override_payload=override_payload,
        )
        
    record_audit(
        db,
        actor_user_id=actor.id,
        action="disbursement_voucher.voided",
        target_type="disbursement_voucher",
        target_id=voucher.id,
        summary=f"Voided disbursement voucher {voucher.voucher_number}",
        diff={
            "reason_code": reason_code,
            "reason": voucher.void_reason,
            "journal_entry_id": voucher.journal_entry_id,
            "reversal_entry_number": reversal.entry_number if reversal else None,
            "entity_version": voucher.entity_version,
        },
    )
    db.commit()
    return serialize_disbursement(voucher)


def delete_disbursement(db: Session, actor: User, disbursement_voucher_id: str, branch_id: str) -> None:
    company = get_company_settings(db)
    repo = PaymentsRepository(db)
    voucher = repo.get_disbursement_voucher(disbursement_voucher_id)
    if voucher is None or voucher.company_id != company.id or voucher.branch_id != branch_id:
        raise ValidationAppError("لم يتم العثور على سند الصرف")
        
    delete_linked_disbursement_voucher_entry(db, actor, voucher)
    
    record_audit(
        db,
        actor_user_id=actor.id,
        action="disbursement_voucher.deleted",
        target_type="disbursement_voucher",
        target_id=voucher.id,
        summary=f"Permanently deleted disbursement voucher {voucher.voucher_number}",
        diff={"total_amount": float(voucher.amount)},
    )
    db.delete(voucher)
    db.commit()
