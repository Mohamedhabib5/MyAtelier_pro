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
    from sqlalchemy import select, or_
    from sqlalchemy.orm import joinedload
    from app.modules.payments.models import PaymentDocument, PaymentAllocation
    from app.modules.customers.models import Customer
    from app.modules.bookings.models import Booking
    from app.modules.payments.serializers import document_total

    company = get_company_settings(db)
    parsed_search = clean_optional_text(search)
    parsed_status = clean_optional_text(status)
    parsed_payee_type = clean_optional_text(payee_type)
    parsed_date_from = parse_payment_date(date_from) if date_from else None
    parsed_date_to = parse_payment_date(date_to) if date_to else None

    # 1. Fetch matching DisbursementVoucher records
    stmt_dv = select(DisbursementVoucher).where(DisbursementVoucher.company_id == company.id)
    if branch_id:
        stmt_dv = stmt_dv.where(DisbursementVoucher.branch_id == branch_id)
    if parsed_status:
        stmt_dv = stmt_dv.where(DisbursementVoucher.status == parsed_status)
    if parsed_payee_type:
        stmt_dv = stmt_dv.where(DisbursementVoucher.payee_type == parsed_payee_type)
    if parsed_date_from:
        stmt_dv = stmt_dv.where(DisbursementVoucher.voucher_date >= parsed_date_from)
    if parsed_date_to:
        stmt_dv = stmt_dv.where(DisbursementVoucher.voucher_date <= parsed_date_to)
    if parsed_search:
        pattern = f"%{parsed_search.strip()}%"
        stmt_dv = stmt_dv.where(
            or_(
                DisbursementVoucher.voucher_number.ilike(pattern),
                DisbursementVoucher.payee_name.ilike(pattern),
                DisbursementVoucher.notes.ilike(pattern),
            )
        )
    stmt_dv = stmt_dv.options(
        joinedload(DisbursementVoucher.branch),
        joinedload(DisbursementVoucher.payment_method),
        joinedload(DisbursementVoucher.journal_entry),
    )
    dv_rows = list(db.scalars(stmt_dv).all())

    # 2. Fetch matching PaymentDocument records (refund kind only)
    pd_rows = []
    if parsed_payee_type is None or parsed_payee_type == "customer":
        stmt_pd = select(PaymentDocument).join(PaymentDocument.customer).where(
            PaymentDocument.company_id == company.id,
            PaymentDocument.document_kind == "refund"
        )
        if branch_id:
            stmt_pd = stmt_pd.where(PaymentDocument.branch_id == branch_id)
        if parsed_status:
            stmt_pd = stmt_pd.where(PaymentDocument.status == parsed_status)
        if parsed_date_from:
            stmt_pd = stmt_pd.where(PaymentDocument.payment_date >= parsed_date_from)
        if parsed_date_to:
            stmt_pd = stmt_pd.where(PaymentDocument.payment_date <= parsed_date_to)
        if parsed_search:
            pattern = f"%{parsed_search.strip()}%"
            stmt_pd = stmt_pd.outerjoin(PaymentDocument.allocations).outerjoin(PaymentAllocation.booking).where(
                or_(
                    PaymentDocument.payment_number.ilike(pattern),
                    Customer.full_name.ilike(pattern),
                    Customer.phone.ilike(pattern),
                    PaymentDocument.notes.ilike(pattern),
                    Booking.booking_number.ilike(pattern),
                )
            )
        stmt_pd = stmt_pd.options(
            joinedload(PaymentDocument.branch),
            joinedload(PaymentDocument.customer),
            joinedload(PaymentDocument.payment_method),
            joinedload(PaymentDocument.journal_entry),
        )
        pd_rows = list(db.scalars(stmt_pd.distinct()).all())

    # 3. Serialize and merge the two lists
    items = []
    for row in dv_rows:
        data = serialize_disbursement(row)
        data["source_table"] = "disbursement_vouchers"
        data["booking_numbers"] = []
        items.append(data)

    for row in pd_rows:
        booking_numbers = sorted({alloc.booking.booking_number for alloc in row.allocations if alloc.booking})
        items.append({
            "id": row.id,
            "company_id": row.company_id,
            "branch_id": row.branch_id,
            "created_by_user_id": row.created_by_user_id,
            "updated_by_user_id": row.updated_by_user_id,
            "entity_version": row.entity_version,
            "branch_name": row.branch.name if row.branch else None,
            "payment_method_id": row.payment_method_id,
            "payment_method_name": row.payment_method.name if row.payment_method else None,
            "voucher_number": row.payment_number,
            "voucher_date": row.payment_date.isoformat() if hasattr(row.payment_date, "isoformat") else str(row.payment_date),
            "amount": float(document_total(row)),
            "payee_type": "customer",
            "payee_id": row.customer_id,
            "payee_name": row.customer.full_name if row.customer else None,
            "expense_account_id": None,
            "expense_account_code": None,
            "expense_account_name": None,
            "status": row.status,
            "journal_entry_id": row.journal_entry_id,
            "journal_entry_number": row.journal_entry.entry_number if row.journal_entry else None,
            "journal_entry_status": row.journal_entry.status if row.journal_entry else None,
            "voided_at": row.voided_at.isoformat() if row.voided_at else None,
            "void_reason": row.void_reason,
            "notes": row.notes,
            "source_table": "payment_documents",
            "booking_numbers": booking_numbers,
        })

    # 4. Sorting
    sort_key_map = {
        "voucher_date": "voucher_date",
        "voucher_number": "voucher_number",
        "payee_name": "payee_name",
        "status": "status",
        "amount": "amount"
    }
    key_to_sort = sort_key_map.get(sort_by, "voucher_date")

    def get_sort_val(x):
        val = x.get(key_to_sort)
        if val is None:
            if key_to_sort == "amount":
                return 0.0
            return ""
        if isinstance(val, str) and key_to_sort != "amount":
            return val.lower()
        return val

    is_desc = sort_dir == "desc"
    items.sort(key=get_sort_val, reverse=is_desc)

    # 5. Pagination
    total = len(items)
    start_offset = (page - 1) * page_size
    end_offset = start_offset + page_size
    sliced_items = items[start_offset:end_offset]

    return {
        "items": sliced_items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


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
        expense_account_id=payload.expense_account_id,
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
    try:
        from app.modules.exports.notification_service import dispatch_payment_notification
        dispatch_payment_notification(db, voucher, is_refund=True)
    except Exception as e:
        import logging
        logging.getLogger("payments").error(f"Failed to dispatch disbursement notification: {str(e)}")
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
    if payload.expense_account_id is not None:
        voucher.expense_account_id = payload.expense_account_id
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
    try:
        from app.modules.exports.notification_service import dispatch_payment_notification
        dispatch_payment_notification(db, voucher, is_refund=True)
    except Exception as e:
        import logging
        logging.getLogger("payments").error(f"Failed to dispatch disbursement notification: {str(e)}")
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
    try:
        from app.modules.exports.notification_service import dispatch_financial_critical_notification
        dispatch_financial_critical_notification(
            db,
            actor_username=actor.username,
            action="disbursement_voucher.voided",
            details=f"Voided disbursement voucher {voucher.voucher_number}. Reason: {voucher.void_reason}"
        )
    except Exception as e:
        import logging
        logging.getLogger("payments").error(f"Failed to dispatch critical notification for void: {str(e)}")
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
