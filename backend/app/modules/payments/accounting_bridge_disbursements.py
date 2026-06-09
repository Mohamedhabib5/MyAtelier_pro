from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.core.exceptions import NotFoundError, ValidationAppError
from app.modules.accounting.bridge_config_service import resolve_bridge_account
from app.modules.accounting.models import JournalEntry, JournalEntryLine
from app.modules.accounting.repository import AccountingRepository
from app.modules.accounting.service import DEFAULT_JOURNAL_SEQUENCE_KEY
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.payments.accounting_bridge_utils import resolve_fiscal_period
from app.modules.payments.models import DisbursementVoucher

ZERO = Decimal("0.00")


def auto_post_disbursement_voucher(db: Session, actor: User, voucher: DisbursementVoucher) -> JournalEntry:
    repo = AccountingRepository(db)
    fiscal_period = resolve_fiscal_period(repo, voucher.company_id, voucher.voucher_date)
    
    if voucher.payment_method.linked_account_id:
        from app.modules.accounting.models import ChartOfAccount
        cash_account = db.get(ChartOfAccount, voucher.payment_method.linked_account_id)
        if not cash_account or not cash_account.is_active:
            cash_account = resolve_bridge_account(db, voucher.company_id, "cash")
    else:
        cash_account = resolve_bridge_account(db, voucher.company_id, "cash")

    if voucher.payee_type == "customer":
        debit_account = resolve_bridge_account(db, voucher.company_id, "customer_advances")
    elif voucher.payee_type == "expense":
        if not voucher.expense_account_id:
            raise ValidationAppError("يجب تحديد حساب المصروف من شجرة الحسابات")
        from app.modules.accounting.models import ChartOfAccount
        debit_account = db.get(ChartOfAccount, voucher.expense_account_id)
        if not debit_account or not debit_account.is_active:
            raise NotFoundError("حساب المصروف غير موجود أو معطل في شجرة الحسابات")
    elif voucher.payee_type == "supplier":
        debit_account = resolve_bridge_account(db, voucher.company_id, "supplier_payables")
    else:
        debit_account = resolve_bridge_account(db, voucher.company_id, "customer_receivables")

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
            line_number=1, account_id=debit_account.id,
            description=f"Disbursement {voucher.voucher_number}",
            debit_amount=voucher.amount, credit_amount=ZERO,
            party_type=voucher.payee_type, party_id=voucher.payee_id,
        ),
        JournalEntryLine(
            line_number=2, account_id=cash_account.id,
            description=f"Disbursement {voucher.voucher_number}",
            debit_amount=ZERO, credit_amount=voucher.amount,
        ),
    ]
    repo.add_journal_entry(entry)
    from app.modules.accounting.journal_integrity import warn_missing_branch
    warn_missing_branch(entry)
    db.flush()
    record_audit(
        db, actor_user_id=actor.id,
        action="accounting.disbursement_voucher_auto_posted",
        target_type="journal_entry", target_id=entry.id,
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
    db: Session, actor: User, voucher: DisbursementVoucher, reverse_date: date,
) -> JournalEntry | None:
    if not voucher.journal_entry_id:
        return None
    repo = AccountingRepository(db)
    entry = repo.get_journal_entry(voucher.journal_entry_id)
    if entry is None:
        raise NotFoundError("لم يتم العثور على القيد المحاسبي المرتبط")
    if entry.status != JournalEntryStatus.POSTED.value:
        raise ValidationAppError("يمكن عكس القيود المرحلة فقط")

    fiscal_period = resolve_fiscal_period(repo, voucher.company_id, reverse_date)
    reversal = JournalEntry(
        company_id=entry.company_id, fiscal_period_id=fiscal_period.id,
        branch_id=entry.branch_id,
        entry_number=repo.reserve_sequence_number(entry.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=reverse_date, status=JournalEntryStatus.POSTED.value,
        reference=f"REV-{entry.entry_number}",
        notes=f"Auto reversal for disbursement voucher {voucher.voucher_number}",
        reference_type=entry.reference_type, reference_id=entry.reference_id,
        posted_at=datetime.now(UTC), posted_by_user_id=actor.id,
    )
    reversal.lines = [
        JournalEntryLine(
            line_number=index, account_id=line.account_id, description=line.description,
            debit_amount=line.credit_amount, credit_amount=line.debit_amount,
            party_type=line.party_type, party_id=line.party_id,
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
        db, actor_user_id=actor.id,
        action="accounting.disbursement_voucher_entry_reversed",
        target_type="journal_entry", target_id=entry.id,
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
        db, actor_user_id=actor.id,
        action="accounting.journal_entry_deleted",
        target_type="journal_entry", target_id=entry.id,
        summary=f"Permanently deleted journal entry {entry.entry_number} linked to disbursement {voucher.voucher_number}",
        diff={"disbursement_voucher_id": voucher.id},
    )
    db.delete(entry)
    db.flush()
