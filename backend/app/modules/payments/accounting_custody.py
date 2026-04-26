from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.core.exceptions import ValidationAppError
from app.modules.accounting.models import JournalEntry, JournalEntryLine
from app.modules.accounting.repository import AccountingRepository
from app.modules.accounting.service import DEFAULT_JOURNAL_SEQUENCE_KEY
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.payments.models import PaymentDocument

CASH_ACCOUNT_CODE = "1000"
CUSTOMER_ADVANCES_CODE = "2100"
SERVICE_REVENUE_CODE = "4100"
ZERO = Decimal("0.00")

def _auto_post_custody_compensation(db: Session, actor: User, payment_document: PaymentDocument) -> JournalEntry:
    from app.modules.payments.accounting_bridge import _resolve_fiscal_period, _get_account
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
    from app.modules.payments.accounting_bridge import _resolve_fiscal_period, _get_account
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
    from app.modules.payments.accounting_bridge import _resolve_fiscal_period, _get_account
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
