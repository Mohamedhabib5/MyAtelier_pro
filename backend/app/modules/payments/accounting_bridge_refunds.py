from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.modules.accounting.bridge_config_service import resolve_bridge_account
from app.modules.accounting.models import JournalEntry, JournalEntryLine
from app.modules.accounting.repository import AccountingRepository
from app.modules.accounting.service import DEFAULT_JOURNAL_SEQUENCE_KEY
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.payments.accounting_bridge_utils import resolve_fiscal_period
from app.modules.payments.models import PaymentDocument

ZERO = Decimal("0.00")


def _auto_post_booking_refund(db: Session, actor: User, payment_document: PaymentDocument) -> JournalEntry:
    from app.modules.payments.accounting_bridge_payments import _allocation_split
    total_amount, advances_amount, receivables_amount = _allocation_split(payment_document)
    repo = AccountingRepository(db)
    fiscal_period = resolve_fiscal_period(repo, payment_document.company_id, payment_document.payment_date)
    cash_account = resolve_bridge_account(db, payment_document.company_id, "cash")
    advances_account = resolve_bridge_account(db, payment_document.company_id, "customer_advances")
    receivables_account = resolve_bridge_account(db, payment_document.company_id, "customer_receivables")

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
        total_amount, advances_amount, receivables_amount,
        cash_account.id, advances_account.id, receivables_account.id,
        payment_document.payment_number,
        party_type="customer", party_id=payment_document.customer_id,
    )
    repo.add_journal_entry(entry)
    from app.modules.accounting.journal_integrity import warn_missing_branch
    warn_missing_branch(entry)
    db.flush()
    record_audit(
        db, actor_user_id=actor.id,
        action="accounting.payment_document_auto_posted",
        target_type="journal_entry", target_id=entry.id,
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
    total_amount: Decimal, advances_amount: Decimal, receivables_amount: Decimal,
    cash_account_id: str, advances_account_id: str, receivables_account_id: str,
    payment_number: str, party_type: str | None = None, party_id: str | None = None,
) -> list[JournalEntryLine]:
    description = f"Refund document {payment_number}"
    lines = []
    line_number = 1

    if advances_amount > ZERO:
        lines.append(JournalEntryLine(
            line_number=line_number, account_id=advances_account_id,
            description=description, debit_amount=advances_amount, credit_amount=ZERO,
            party_type=party_type, party_id=party_id,
        ))
        line_number += 1

    if receivables_amount > ZERO:
        lines.append(JournalEntryLine(
            line_number=line_number, account_id=receivables_account_id,
            description=description, debit_amount=receivables_amount, credit_amount=ZERO,
            party_type=party_type, party_id=party_id,
        ))
        line_number += 1

    lines.append(JournalEntryLine(
        line_number=line_number, account_id=cash_account_id,
        description=description, debit_amount=ZERO, credit_amount=total_amount,
    ))
    return lines
