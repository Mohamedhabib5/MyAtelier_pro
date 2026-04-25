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
from app.modules.payments.models import PaymentDocument

CASH_ACCOUNT_CODE = "1000"
CUSTOMER_ADVANCES_CODE = "2100"
CUSTOMER_RECEIVABLES_CODE = "1200"
SERVICE_REVENUE_CODE = "4100"
ZERO = Decimal("0.00")
DIRECT_CUSTODY_REVENUE_KINDS = {"custody_compensation"}
DIRECT_CUSTODY_DEPOSIT_COLLECTION_KINDS = {"custody_deposit"}
DIRECT_CUSTODY_REFUND_KINDS = {"refund"}


def auto_post_payment_document(db: Session, actor: User, payment_document: PaymentDocument) -> JournalEntry:
    if payment_document.document_kind in DIRECT_CUSTODY_REVENUE_KINDS:
        return _auto_post_custody_compensation(db, actor, payment_document)
    if payment_document.document_kind in DIRECT_CUSTODY_DEPOSIT_COLLECTION_KINDS:
        return _auto_post_custody_deposit_collection(db, actor, payment_document)
    if payment_document.document_kind in DIRECT_CUSTODY_REFUND_KINDS:
        return _auto_post_custody_deposit_refund(db, actor, payment_document)
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
        entry_number=repo.reserve_sequence_number(payment_document.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=payment_document.payment_date,
        status=JournalEntryStatus.POSTED.value,
        reference=payment_document.payment_number,
        notes=f"Auto-posted from payment document {payment_document.payment_number}",
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
    )
    repo.add_journal_entry(entry)
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
        entry_number=repo.reserve_sequence_number(entry.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=reverse_date,
        status=JournalEntryStatus.POSTED.value,
        reference=f"REV-{entry.entry_number}",
        notes=f"Auto reversal for payment document {payment_document.payment_number}",
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
        )
        for index, line in enumerate(entry.lines, start=1)
    ]
    repo.add_journal_entry(reversal)
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
        diff={"payment_document_id": payment_document.id, "reversal_entry_number": reversal.entry_number},
    )
    return reversal


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


def _auto_post_custody_compensation(db: Session, actor: User, payment_document: PaymentDocument) -> JournalEntry:
    amount = Decimal(str(payment_document.direct_amount)).quantize(Decimal("0.01"))
    if amount <= ZERO:
        raise ValidationAppError("قيمة تعويض العهدة يجب أن تكون أكبر من صفر")
    repo = AccountingRepository(db)
    fiscal_period = _resolve_fiscal_period(repo, payment_document.company_id, payment_document.payment_date)
    cash_account = _get_account(repo, payment_document.company_id, CASH_ACCOUNT_CODE)
    revenue_account = _get_account(repo, payment_document.company_id, SERVICE_REVENUE_CODE)
    entry = JournalEntry(
        company_id=payment_document.company_id,
        fiscal_period_id=fiscal_period.id,
        entry_number=repo.reserve_sequence_number(payment_document.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=payment_document.payment_date,
        status=JournalEntryStatus.POSTED.value,
        reference=payment_document.payment_number,
        notes=f"Auto-posted custody compensation {payment_document.payment_number}",
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    entry.lines = [
        JournalEntryLine(
            line_number=1,
            account_id=cash_account.id,
            description=f"Custody compensation {payment_document.payment_number}",
            debit_amount=amount,
            credit_amount=ZERO,
        ),
        JournalEntryLine(
            line_number=2,
            account_id=revenue_account.id,
            description=f"Custody compensation {payment_document.payment_number}",
            debit_amount=ZERO,
            credit_amount=amount,
        ),
    ]
    repo.add_journal_entry(entry)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.custody_compensation_auto_posted",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Auto-posted custody compensation {payment_document.payment_number} to journal {entry.entry_number}",
        diff={"payment_document_id": payment_document.id, "total_amount": float(amount)},
    )
    return entry


def _auto_post_custody_deposit_collection(db: Session, actor: User, payment_document: PaymentDocument) -> JournalEntry:
    amount = Decimal(str(payment_document.direct_amount)).quantize(Decimal("0.01"))
    if amount <= ZERO:
        raise ValidationAppError("قيمة تأمين الحيازة يجب أن تكون أكبر من صفر")
    repo = AccountingRepository(db)
    fiscal_period = _resolve_fiscal_period(repo, payment_document.company_id, payment_document.payment_date)
    cash_account = _get_account(repo, payment_document.company_id, CASH_ACCOUNT_CODE)
    advances_account = _get_account(repo, payment_document.company_id, CUSTOMER_ADVANCES_CODE)
    entry = JournalEntry(
        company_id=payment_document.company_id,
        fiscal_period_id=fiscal_period.id,
        entry_number=repo.reserve_sequence_number(payment_document.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=payment_document.payment_date,
        status=JournalEntryStatus.POSTED.value,
        reference=payment_document.payment_number,
        notes=f"Auto-posted custody deposit {payment_document.payment_number}",
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    entry.lines = [
        JournalEntryLine(
            line_number=1,
            account_id=cash_account.id,
            description=f"Custody deposit {payment_document.payment_number}",
            debit_amount=amount,
            credit_amount=ZERO,
        ),
        JournalEntryLine(
            line_number=2,
            account_id=advances_account.id,
            description=f"Custody deposit {payment_document.payment_number}",
            debit_amount=ZERO,
            credit_amount=amount,
        ),
    ]
    repo.add_journal_entry(entry)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.custody_deposit_auto_posted",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Auto-posted custody deposit {payment_document.payment_number} to journal {entry.entry_number}",
        diff={"payment_document_id": payment_document.id, "total_amount": float(amount)},
    )
    return entry


def _auto_post_custody_deposit_refund(db: Session, actor: User, payment_document: PaymentDocument) -> JournalEntry:
    amount = Decimal(str(payment_document.direct_amount)).quantize(Decimal("0.01"))
    if amount <= ZERO:
        raise ValidationAppError("قيمة رد تأمين الحيازة يجب أن تكون أكبر من صفر")
    repo = AccountingRepository(db)
    fiscal_period = _resolve_fiscal_period(repo, payment_document.company_id, payment_document.payment_date)
    cash_account = _get_account(repo, payment_document.company_id, CASH_ACCOUNT_CODE)
    advances_account = _get_account(repo, payment_document.company_id, CUSTOMER_ADVANCES_CODE)
    entry = JournalEntry(
        company_id=payment_document.company_id,
        fiscal_period_id=fiscal_period.id,
        entry_number=repo.reserve_sequence_number(payment_document.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=payment_document.payment_date,
        status=JournalEntryStatus.POSTED.value,
        reference=payment_document.payment_number,
        notes=f"Auto-posted custody deposit refund {payment_document.payment_number}",
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    entry.lines = [
        JournalEntryLine(
            line_number=1,
            account_id=advances_account.id,
            description=f"Custody deposit refund {payment_document.payment_number}",
            debit_amount=amount,
            credit_amount=ZERO,
        ),
        JournalEntryLine(
            line_number=2,
            account_id=cash_account.id,
            description=f"Custody deposit refund {payment_document.payment_number}",
            debit_amount=ZERO,
            credit_amount=amount,
        ),
    ]
    repo.add_journal_entry(entry)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.custody_deposit_refund_auto_posted",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Auto-posted custody deposit refund {payment_document.payment_number} to journal {entry.entry_number}",
        diff={"payment_document_id": payment_document.id, "total_amount": float(amount)},
    )
    return entry


def _build_payment_lines(
    total_amount: Decimal,
    advances_amount: Decimal,
    receivables_amount: Decimal,
    cash_account_id: str,
    advances_account_id: str,
    receivables_account_id: str,
    payment_number: str,
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
