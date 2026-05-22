from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.core.exceptions import ValidationAppError
from app.modules.accounting.bridge_config_service import resolve_bridge_account
from app.modules.accounting.models import JournalEntry, JournalEntryLine
from app.modules.accounting.repository import AccountingRepository
from app.modules.accounting.service import DEFAULT_JOURNAL_SEQUENCE_KEY
from app.modules.bookings.calculations import line_paid_total, quantize_amount
from app.modules.bookings.models import BookingLine
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.payments.accounting_bridge_utils import resolve_fiscal_period
from app.modules.payments.models import PaymentAllocation

ZERO = Decimal('0.00')


def post_booking_line_revenue_recognition(db: Session, actor: User, line: BookingLine, recognition_date: date) -> JournalEntry:
    repo = AccountingRepository(db)
    line_price = quantize_amount(line.line_price)
    if line_price <= ZERO:
        raise ValidationAppError('يجب أن يكون لسطر الحجز المكتمل سعر موجب')

    collected = line_paid_total(line)
    tax_amount = quantize_amount(line.tax_amount)
    if tax_amount < ZERO or tax_amount > line_price:
        raise ValidationAppError('قيمة الضريبة على السطر غير صالحة')
    revenue_amount = quantize_amount(line_price - tax_amount)
    if collected < ZERO or collected > line_price:
        raise ValidationAppError('لا يمكن أن يتجاوز المبلغ المحصل سعر السطر عند الإكمال')
    receivable_amount = quantize_amount(line_price - collected)

    fiscal_period = resolve_fiscal_period(repo, line.booking.company_id, recognition_date)
    advances_account = resolve_bridge_account(db, line.booking.company_id, "customer_advances")
    receivables_account = resolve_bridge_account(db, line.booking.company_id, "customer_receivables")
    tax_payable_account = resolve_bridge_account(db, line.booking.company_id, "tax_payable")
    revenue_account = resolve_bridge_account(db, line.booking.company_id, "service_revenue")
    entry = JournalEntry(
        company_id=line.booking.company_id,
        fiscal_period_id=fiscal_period.id,
        branch_id=line.booking.branch_id,
        entry_number=repo.reserve_sequence_number(line.booking.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=recognition_date,
        status=JournalEntryStatus.POSTED.value,
        reference=f'{line.booking.booking_number}-L{line.line_number}',
        notes=f'Revenue recognition for booking {line.booking.booking_number} line {line.line_number}',
        reference_type='booking_line',
        reference_id=line.id,
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    entry.lines = _build_recognition_lines(
        line, revenue_amount, tax_amount, collected, receivable_amount,
        advances_account.id, receivables_account.id, revenue_account.id, tax_payable_account.id,
        party_type='customer', party_id=line.booking.customer_id,
    )
    repo.add_journal_entry(entry)
    from app.modules.accounting.journal_integrity import warn_missing_branch
    warn_missing_branch(entry)
    db.flush()
    record_audit(
        db, actor_user_id=actor.id,
        action='accounting.booking_line_revenue_recognized',
        target_type='journal_entry', target_id=entry.id,
        summary=f'Recognized revenue for booking {line.booking.booking_number} line {line.line_number} in journal {entry.entry_number}',
        diff={
            'booking_id': line.booking_id,
            'line_id': line.id,
            'line_price': float(line_price),
            'tax_amount': float(tax_amount),
            'revenue_amount': float(revenue_amount),
            'collected_amount': float(collected),
            'receivable_amount': float(receivable_amount),
            'branch_id': entry.branch_id,
            'reference_type': entry.reference_type,
            'reference_id': entry.reference_id,
            'party_type': 'customer',
            'party_id': line.booking.customer_id,
        },
    )
    return entry


def reverse_booking_line_revenue_recognition(db: Session, actor: User, line: BookingLine, reverse_date: date) -> JournalEntry:
    if not line.revenue_journal_entry_id:
        raise ValidationAppError('لا يوجد قيد إيراد مرتبط بهذا السطر')
    repo = AccountingRepository(db)
    entry = repo.get_journal_entry(line.revenue_journal_entry_id)
    if entry is None:
        raise ValidationAppError('لم يتم العثور على قيد الإيراد المرتبط بالسطر')
    if entry.status != JournalEntryStatus.POSTED.value:
        raise ValidationAppError('يمكن عكس قيد الإيراد المرحّل فقط')
    if _has_active_post_recognition_collections(db, line):
        raise ValidationAppError('لا يمكن عكس إيراد هذا السطر قبل معالجة التحصيلات اللاحقة')

    fiscal_period = resolve_fiscal_period(repo, line.booking.company_id, reverse_date)
    reversal = JournalEntry(
        company_id=entry.company_id, fiscal_period_id=fiscal_period.id,
        branch_id=entry.branch_id,
        entry_number=repo.reserve_sequence_number(entry.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=reverse_date, status=JournalEntryStatus.POSTED.value,
        reference=f'REV-{entry.entry_number}',
        notes=f'Auto reversal for booking {line.booking.booking_number} line {line.line_number}',
        reference_type=entry.reference_type, reference_id=entry.reference_id,
        posted_at=datetime.now(UTC), posted_by_user_id=actor.id,
    )
    reversal.lines = [
        JournalEntryLine(
            line_number=index, account_id=entry_line.account_id,
            description=entry_line.description,
            debit_amount=entry_line.credit_amount, credit_amount=entry_line.debit_amount,
            party_type=entry_line.party_type, party_id=entry_line.party_id,
        )
        for index, entry_line in enumerate(entry.lines, start=1)
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
        action='accounting.booking_line_revenue_reversed',
        target_type='journal_entry', target_id=entry.id,
        summary=f'Reversed booking revenue entry {entry.entry_number} for booking {line.booking.booking_number} line {line.line_number}',
        diff={
            'booking_id': line.booking_id,
            'line_id': line.id,
            'reversal_entry_number': reversal.entry_number,
            'branch_id': reversal.branch_id,
            'reference_type': reversal.reference_type,
            'reference_id': reversal.reference_id,
        },
    )
    return reversal


def _build_recognition_lines(
    line: BookingLine,
    revenue_amount: Decimal, tax_amount: Decimal,
    collected: Decimal, receivable_amount: Decimal,
    advances_account_id: str, receivables_account_id: str,
    revenue_account_id: str, tax_payable_account_id: str,
    party_type: str | None = None, party_id: str | None = None,
) -> list[JournalEntryLine]:
    description = f'Booking {line.booking.booking_number} line {line.line_number}'
    lines: list[JournalEntryLine] = []
    line_number = 1
    if collected > ZERO:
        lines.append(JournalEntryLine(
            line_number=line_number, account_id=advances_account_id,
            description=description, debit_amount=collected, credit_amount=ZERO,
            party_type=party_type, party_id=party_id,
        ))
        line_number += 1
    if receivable_amount > ZERO:
        lines.append(JournalEntryLine(
            line_number=line_number, account_id=receivables_account_id,
            description=description, debit_amount=receivable_amount, credit_amount=ZERO,
            party_type=party_type, party_id=party_id,
        ))
        line_number += 1
    if revenue_amount > ZERO:
        lines.append(JournalEntryLine(
            line_number=line_number, account_id=revenue_account_id,
            description=description, debit_amount=ZERO, credit_amount=revenue_amount,
        ))
        line_number += 1
    if tax_amount > ZERO:
        lines.append(JournalEntryLine(
            line_number=line_number, account_id=tax_payable_account_id,
            description=description, debit_amount=ZERO, credit_amount=tax_amount,
        ))
    return lines


def _has_active_post_recognition_collections(db: Session, line: BookingLine) -> bool:
    """Check if any post-recognition payment allocated to this line credits the receivables account."""
    receivables_account = resolve_bridge_account(db, line.booking.company_id, "customer_receivables")
    active_allocations: list[PaymentAllocation] = [
        allocation for allocation in line.payment_allocations
        if allocation.payment_document.status != 'voided'
    ]
    for allocation in active_allocations:
        journal = allocation.payment_document.journal_entry
        if journal is None:
            continue
        if any(
            entry_line.account_id == receivables_account.id and entry_line.credit_amount > ZERO
            for entry_line in journal.lines
        ):
            return True
    return False
