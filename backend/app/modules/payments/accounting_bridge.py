from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.core.exceptions import NotFoundError, ValidationAppError
from app.modules.accounting.models import JournalEntry, JournalEntryLine
from app.modules.accounting.repository import AccountingRepository
from app.modules.accounting.service import DEFAULT_JOURNAL_SEQUENCE_KEY
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.payments.models import PaymentDocument, DisbursementVoucher


CASH_ACCOUNT_CODE = "1111001"
CUSTOMER_ADVANCES_CODE = "2110"
CUSTOMER_RECEIVABLES_CODE = "1121001"
SERVICE_REVENUE_CODE = "4110"
ZERO = Decimal("0.00")
DIRECT_CUSTODY_REVENUE_KINDS = {"custody_compensation"}
DIRECT_CUSTODY_DEPOSIT_COLLECTION_KINDS = {"custody_deposit"}
DIRECT_CUSTODY_REFUND_KINDS = {"refund"}


def auto_post_payment_document(db: Session, actor: User, payment_document: PaymentDocument) -> JournalEntry:
    if payment_document.document_kind in DIRECT_CUSTODY_REVENUE_KINDS:
        from app.modules.payments.accounting_custody import _auto_post_custody_compensation
        return _auto_post_custody_compensation(db, actor, payment_document)
    if payment_document.document_kind in DIRECT_CUSTODY_DEPOSIT_COLLECTION_KINDS:
        from app.modules.payments.accounting_custody import _auto_post_custody_deposit_collection
        return _auto_post_custody_deposit_collection(db, actor, payment_document)
    
    # --- Refund Distinctions ---
    if payment_document.document_kind == "refund":
        if payment_document.direct_amount > ZERO:
            # This is a custody refund (standalone amount)
            from app.modules.payments.accounting_custody import _auto_post_custody_deposit_refund
            return _auto_post_custody_deposit_refund(db, actor, payment_document)
        # This is a booking refund (allocated to lines)
        return _auto_post_booking_refund(db, actor, payment_document)
    if payment_document.document_kind != "collection":
        raise ValidationAppError("يمكن ترحيل سندات التحصيل فقط تلقائيًا")

    total_amount, advances_amount, receivables_amount = _allocation_split(payment_document)
    repo = AccountingRepository(db)
    fiscal_period = _resolve_fiscal_period(repo, payment_document.company_id, payment_document.payment_date)
    cash_account = _get_account(repo, payment_document.company_id, CASH_ACCOUNT_CODE)
    advances_account = _get_account(repo, payment_document.company_id, CUSTOMER_ADVANCES_CODE)
    receivables_account = _get_account(repo, payment_document.company_id, CUSTOMER_RECEIVABLES_CODE)
    entry = JournalEntry(
        company_id=payment_document.company_id,
        fiscal_period_id=fiscal_period.id,
        branch_id=payment_document.branch_id,
        entry_number=repo.reserve_sequence_number(payment_document.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=payment_document.payment_date,
        status=JournalEntryStatus.POSTED.value,
        reference=payment_document.payment_number,
        notes=f"Auto-posted from payment document {payment_document.payment_number}",
        reference_type="payment_document",
        reference_id=payment_document.id,
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    entry.lines = _build_payment_lines(
        total_amount,
        advances_amount,
        receivables_amount,
        cash_account.id,
        advances_account.id,
        receivables_account.id,
        payment_document.payment_number,
        party_type="customer",
        party_id=payment_document.customer_id,
    )
    repo.add_journal_entry(entry)
    from app.modules.accounting.journal_integrity import warn_missing_branch
    warn_missing_branch(entry)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.payment_document_auto_posted",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Auto-posted payment document {payment_document.payment_number} to journal {entry.entry_number}",
        diff={
            "payment_document_id": payment_document.id,
            "total_amount": float(total_amount),
            "advances_amount": float(advances_amount),
            "receivables_amount": float(receivables_amount),
            "branch_id": entry.branch_id,
            "reference_type": entry.reference_type,
            "reference_id": entry.reference_id,
            "party_type": "customer",
            "party_id": payment_document.customer_id,
        },
    )
    return entry


def reverse_linked_payment_document_entry(
    db: Session,
    actor: User,
    payment_document: PaymentDocument,
    reverse_date: date,
) -> JournalEntry | None:
    if not payment_document.journal_entry_id:
        return None
    repo = AccountingRepository(db)
    entry = repo.get_journal_entry(payment_document.journal_entry_id)
    if entry is None:
        raise NotFoundError("لم يتم العثور على القيد المحاسبي المرتبط")
    if entry.status != JournalEntryStatus.POSTED.value:
        raise ValidationAppError("يمكن عكس القيود المرحلة فقط")

    fiscal_period = _resolve_fiscal_period(repo, payment_document.company_id, reverse_date)
    reversal = JournalEntry(
        company_id=entry.company_id,
        fiscal_period_id=fiscal_period.id,
        branch_id=entry.branch_id,
        entry_number=repo.reserve_sequence_number(entry.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=reverse_date,
        status=JournalEntryStatus.POSTED.value,
        reference=f"REV-{entry.entry_number}",
        notes=f"Auto reversal for payment document {payment_document.payment_number}",
        reference_type=entry.reference_type,
        reference_id=entry.reference_id,
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    reversal.lines = [
        JournalEntryLine(
            line_number=index,
            account_id=line.account_id,
            description=line.description,
            debit_amount=line.credit_amount,
            credit_amount=line.debit_amount,
            party_type=line.party_type,
            party_id=line.party_id,
        )
        for index, line in enumerate(entry.lines, start=1)
    ]
    repo.add_journal_entry(reversal)
    from app.modules.accounting.journal_integrity import warn_missing_branch
    warn_missing_branch(reversal)
    entry.status = JournalEntryStatus.REVERSED.value
    entry.reversed_at = datetime.now(UTC)
    entry.reversed_by_user_id = actor.id
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.payment_document_entry_reversed",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Reversed linked journal entry {entry.entry_number} for payment document {payment_document.payment_number}",
        diff={
            "payment_document_id": payment_document.id,
            "reversal_entry_number": reversal.entry_number,
            "branch_id": reversal.branch_id,
            "reference_type": reversal.reference_type,
            "reference_id": reversal.reference_id,
        },
    )
    return reversal


def delete_linked_payment_document_entry(db: Session, actor: User, payment_document: PaymentDocument) -> None:
    if not payment_document.journal_entry_id:
        return
    repo = AccountingRepository(db)
    entry = repo.get_journal_entry(payment_document.journal_entry_id)
    if entry is None:
        return

    # For Hard Delete, if the entry is already posted, we should ideally reverse it first.
    # But if the user wants to "Delete everything", and they have permission, we delete it.
    # Safety Check: If it's in a locked period, we rely on the caller having checked the lock.
    
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.journal_entry_deleted",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Permanently deleted journal entry {entry.entry_number} linked to payment {payment_document.payment_number}",
        diff={"payment_document_id": payment_document.id},
    )
    db.delete(entry)
    db.flush()


def _allocation_split(payment_document: PaymentDocument) -> tuple[Decimal, Decimal, Decimal]:
    total_amount = ZERO
    advances_amount = ZERO
    receivables_amount = ZERO
    for allocation in payment_document.allocations:
        amount = Decimal(str(allocation.allocated_amount)).quantize(Decimal("0.01"))
        total_amount += amount
        if allocation.booking_line.revenue_journal_entry_id:
            receivables_amount += amount
        else:
            advances_amount += amount
    return total_amount, advances_amount, receivables_amount


def _build_payment_lines(
    total_amount: Decimal,
    advances_amount: Decimal,
    receivables_amount: Decimal,
    cash_account_id: str,
    advances_account_id: str,
    receivables_account_id: str,
    payment_number: str,
    party_type: str | None = None,
    party_id: str | None = None,
) -> list[JournalEntryLine]:
    description = f"Payment document {payment_number}"
    lines = [
        JournalEntryLine(
            line_number=1,
            account_id=cash_account_id,
            description=description,
            debit_amount=total_amount,
            credit_amount=ZERO,
        )
    ]
    line_number = 2
    if advances_amount > ZERO:
        lines.append(
            JournalEntryLine(
                line_number=line_number,
                account_id=advances_account_id,
                description=description,
                debit_amount=ZERO,
                credit_amount=advances_amount,
                party_type=party_type,
                party_id=party_id,
            )
        )
        line_number += 1
    if receivables_amount > ZERO:
        lines.append(
            JournalEntryLine(
                line_number=line_number,
                account_id=receivables_account_id,
                description=description,
                debit_amount=ZERO,
                credit_amount=receivables_amount,
                party_type=party_type,
                party_id=party_id,
            )
        )
    return lines


def _auto_post_booking_refund(db: Session, actor: User, payment_document: PaymentDocument) -> JournalEntry:
    total_amount, advances_amount, receivables_amount = _allocation_split(payment_document)
    repo = AccountingRepository(db)
    fiscal_period = _resolve_fiscal_period(repo, payment_document.company_id, payment_document.payment_date)
    cash_account = _get_account(repo, payment_document.company_id, CASH_ACCOUNT_CODE)
    advances_account = _get_account(repo, payment_document.company_id, CUSTOMER_ADVANCES_CODE)
    receivables_account = _get_account(repo, payment_document.company_id, CUSTOMER_RECEIVABLES_CODE)
    
    entry = JournalEntry(
        company_id=payment_document.company_id,
        fiscal_period_id=fiscal_period.id,
        branch_id=payment_document.branch_id,
        entry_number=repo.reserve_sequence_number(payment_document.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=payment_document.payment_date,
        status=JournalEntryStatus.POSTED.value,
        reference=payment_document.payment_number,
        notes=f"Auto-posted refund document {payment_document.payment_number}",
        reference_type="payment_document",
        reference_id=payment_document.id,
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    entry.lines = _build_refund_lines(
        total_amount,
        advances_amount,
        receivables_amount,
        cash_account.id,
        advances_account.id,
        receivables_account.id,
        payment_document.payment_number,
        party_type="customer",
        party_id=payment_document.customer_id,
    )
    repo.add_journal_entry(entry)
    from app.modules.accounting.journal_integrity import warn_missing_branch
    warn_missing_branch(entry)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.payment_document_auto_posted",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Auto-posted refund document {payment_document.payment_number} to journal {entry.entry_number}",
        diff={
            "payment_document_id": payment_document.id,
            "total_amount": float(total_amount),
            "advances_amount": float(advances_amount),
            "receivables_amount": float(receivables_amount),
            "branch_id": entry.branch_id,
            "reference_type": entry.reference_type,
            "reference_id": entry.reference_id,
            "party_type": "customer",
            "party_id": payment_document.customer_id,
        },
    )
    return entry


def _build_refund_lines(
    total_amount: Decimal,
    advances_amount: Decimal,
    receivables_amount: Decimal,
    cash_account_id: str,
    advances_account_id: str,
    receivables_account_id: str,
    payment_number: str,
    party_type: str | None = None,
    party_id: str | None = None,
) -> list[JournalEntryLine]:
    description = f"Refund document {payment_number}"
    lines = []
    line_number = 1
    
    if advances_amount > ZERO:
        lines.append(
            JournalEntryLine(
                line_number=line_number,
                account_id=advances_account_id,
                description=description,
                debit_amount=advances_amount,
                credit_amount=ZERO,
                party_type=party_type,
                party_id=party_id,
            )
        )
        line_number += 1
        
    if receivables_amount > ZERO:
        lines.append(
            JournalEntryLine(
                line_number=line_number,
                account_id=receivables_account_id,
                description=description,
                debit_amount=receivables_amount,
                credit_amount=ZERO,
                party_type=party_type,
                party_id=party_id,
            )
        )
        line_number += 1
        
    lines.append(
        JournalEntryLine(
            line_number=line_number,
            account_id=cash_account_id,
            description=description,
            debit_amount=ZERO,
            credit_amount=total_amount,
        )
    )
    return lines


def _resolve_fiscal_period(repo: AccountingRepository, company_id: str, entry_date: date):
    fiscal_period = repo.get_active_fiscal_period(company_id)
    if fiscal_period is None:
        raise ValidationAppError("لم يتم العثور على الفترة المالية النشطة")
    if fiscal_period.is_locked:
        raise ValidationAppError("لا يمكن ترحيل الدفع داخل فترة مالية مقفلة")
    if entry_date < fiscal_period.starts_on or entry_date > fiscal_period.ends_on:
        raise ValidationAppError("يجب أن يقع تاريخ الدفع داخل الفترة المالية النشطة")
    return fiscal_period


def _get_account(repo: AccountingRepository, company_id: str, code: str):
    account = repo.get_chart_account_by_code(company_id, code)
    if account is None or not account.is_active or not account.allows_posting:
        raise ValidationAppError(f"حساب الترحيل {code} غير متاح")
    return account


def auto_post_disbursement_voucher(db: Session, actor: User, voucher: DisbursementVoucher) -> JournalEntry:
    repo = AccountingRepository(db)
    fiscal_period = _resolve_fiscal_period(repo, voucher.company_id, voucher.voucher_date)
    cash_account = _get_account(repo, voucher.company_id, CASH_ACCOUNT_CODE)
    
    if voucher.payee_type == "customer":
        advances_account = _get_account(repo, voucher.company_id, CUSTOMER_ADVANCES_CODE)
        debit_account = advances_account
    else:
        receivables_account = _get_account(repo, voucher.company_id, CUSTOMER_RECEIVABLES_CODE)
        debit_account = receivables_account
        
    entry = JournalEntry(
        company_id=voucher.company_id,
        fiscal_period_id=fiscal_period.id,
        branch_id=voucher.branch_id,
        entry_number=repo.reserve_sequence_number(voucher.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=voucher.voucher_date,
        status=JournalEntryStatus.POSTED.value,
        reference=voucher.voucher_number,
        notes=f"Auto-posted disbursement voucher {voucher.voucher_number}",
        reference_type="disbursement_voucher",
        reference_id=voucher.id,
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    
    entry.lines = [
        JournalEntryLine(
            line_number=1,
            account_id=debit_account.id,
            description=f"Disbursement {voucher.voucher_number}",
            debit_amount=voucher.amount,
            credit_amount=ZERO,
            party_type=voucher.payee_type,
            party_id=voucher.payee_id,
        ),
        JournalEntryLine(
            line_number=2,
            account_id=cash_account.id,
            description=f"Disbursement {voucher.voucher_number}",
            debit_amount=ZERO,
            credit_amount=voucher.amount,
        )
    ]
    repo.add_journal_entry(entry)
    from app.modules.accounting.journal_integrity import warn_missing_branch
    warn_missing_branch(entry)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.disbursement_voucher_auto_posted",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Auto-posted disbursement voucher {voucher.voucher_number} to journal {entry.entry_number}",
        diff={
            "disbursement_voucher_id": voucher.id,
            "total_amount": float(voucher.amount),
            "branch_id": entry.branch_id,
            "reference_type": entry.reference_type,
            "reference_id": entry.reference_id,
            "party_type": voucher.payee_type,
            "party_id": voucher.payee_id,
        },
    )
    return entry


def reverse_linked_disbursement_voucher_entry(
    db: Session,
    actor: User,
    voucher: DisbursementVoucher,
    reverse_date: date,
) -> JournalEntry | None:
    if not voucher.journal_entry_id:
        return None
    repo = AccountingRepository(db)
    entry = repo.get_journal_entry(voucher.journal_entry_id)
    if entry is None:
        raise NotFoundError("لم يتم العثور على القيد المحاسبي المرتبط")
    if entry.status != JournalEntryStatus.POSTED.value:
        raise ValidationAppError("يمكن عكس القيود المرحلة فقط")

    fiscal_period = _resolve_fiscal_period(repo, voucher.company_id, reverse_date)
    reversal = JournalEntry(
        company_id=entry.company_id,
        fiscal_period_id=fiscal_period.id,
        branch_id=entry.branch_id,
        entry_number=repo.reserve_sequence_number(entry.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=reverse_date,
        status=JournalEntryStatus.POSTED.value,
        reference=f"REV-{entry.entry_number}",
        notes=f"Auto reversal for disbursement voucher {voucher.voucher_number}",
        reference_type=entry.reference_type,
        reference_id=entry.reference_id,
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    reversal.lines = [
        JournalEntryLine(
            line_number=index,
            account_id=line.account_id,
            description=line.description,
            debit_amount=line.credit_amount,
            credit_amount=line.debit_amount,
            party_type=line.party_type,
            party_id=line.party_id,
        )
        for index, line in enumerate(entry.lines, start=1)
    ]
    repo.add_journal_entry(reversal)
    from app.modules.accounting.journal_integrity import warn_missing_branch
    warn_missing_branch(reversal)
    entry.status = JournalEntryStatus.REVERSED.value
    entry.reversed_at = datetime.now(UTC)
    entry.reversed_by_user_id = actor.id
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.disbursement_voucher_entry_reversed",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Reversed linked journal entry {entry.entry_number} for disbursement voucher {voucher.voucher_number}",
        diff={
            "disbursement_voucher_id": voucher.id,
            "reversal_entry_number": reversal.entry_number,
            "branch_id": reversal.branch_id,
            "reference_type": reversal.reference_type,
            "reference_id": reversal.reference_id,
        },
    )
    return reversal


def delete_linked_disbursement_voucher_entry(db: Session, actor: User, voucher: DisbursementVoucher) -> None:
    if not voucher.journal_entry_id:
        return
    repo = AccountingRepository(db)
    entry = repo.get_journal_entry(voucher.journal_entry_id)
    if entry is None:
        return
    
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.journal_entry_deleted",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Permanently deleted journal entry {entry.entry_number} linked to disbursement {voucher.voucher_number}",
        diff={"disbursement_voucher_id": voucher.id},
    )
    db.delete(entry)
    db.flush()

