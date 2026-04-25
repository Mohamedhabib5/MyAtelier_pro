from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.core.exceptions import ValidationAppError
from app.modules.accounting.models import JournalEntry, JournalEntryLine
from app.modules.accounting.repository import AccountingRepository
from app.modules.accounting.service import DEFAULT_JOURNAL_SEQUENCE_KEY
from app.modules.bookings.calculations import line_paid_total, quantize_amount
from app.modules.bookings.models import BookingLine
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.payments.models import PaymentAllocation

CUSTOMER_ADVANCES_CODE = '2100'
CUSTOMER_RECEIVABLES_CODE = '1200'
TAX_PAYABLE_CODE = '2200'
SERVICE_REVENUE_CODE = '4100'
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

    fiscal_period = _resolve_fiscal_period(repo, line.booking.company_id, recognition_date)
    advances_account = _get_account(repo, line.booking.company_id, CUSTOMER_ADVANCES_CODE)
    receivables_account = _get_account(repo, line.booking.company_id, CUSTOMER_RECEIVABLES_CODE)
    tax_payable_account = _get_account(repo, line.booking.company_id, TAX_PAYABLE_CODE)
    revenue_account = _get_account(repo, line.booking.company_id, SERVICE_REVENUE_CODE)
    entry = JournalEntry(
        company_id=line.booking.company_id,
        fiscal_period_id=fiscal_period.id,
        entry_number=repo.reserve_sequence_number(line.booking.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=recognition_date,
        status=JournalEntryStatus.POSTED.value,
        reference=f'{line.booking.booking_number}-L{line.line_number}',
        notes=f'Revenue recognition for booking {line.booking.booking_number} line {line.line_number}',
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    entry.lines = _build_recognition_lines(
        line,
        revenue_amount,
        tax_amount,
        collected,
        receivable_amount,
        advances_account.id,
        receivables_account.id,
        revenue_account.id,
        tax_payable_account.id,
    )
    repo.add_journal_entry(entry)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action='accounting.booking_line_revenue_recognized',
        target_type='journal_entry',
        target_id=entry.id,
        summary=f'Recognized revenue for booking {line.booking.booking_number} line {line.line_number} in journal {entry.entry_number}',
        diff={'booking_id': line.booking_id, 'line_id': line.id, 'line_price': float(line_price), 'tax_amount': float(tax_amount), 'revenue_amount': float(revenue_amount), 'collected_amount': float(collected), 'receivable_amount': float(receivable_amount)},
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
    if _has_active_post_recognition_collections(line):
        raise ValidationAppError('لا يمكن عكس إيراد هذا السطر قبل معالجة التحصيلات اللاحقة')

    fiscal_period = _resolve_fiscal_period(repo, line.booking.company_id, reverse_date)
    reversal = JournalEntry(
        company_id=entry.company_id,
        fiscal_period_id=fiscal_period.id,
        entry_number=repo.reserve_sequence_number(entry.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY),
        entry_date=reverse_date,
        status=JournalEntryStatus.POSTED.value,
        reference=f'REV-{entry.entry_number}',
        notes=f'Auto reversal for booking {line.booking.booking_number} line {line.line_number}',
        posted_at=datetime.now(UTC),
        posted_by_user_id=actor.id,
    )
    reversal.lines = [
        JournalEntryLine(
            line_number=index,
            account_id=entry_line.account_id,
            description=entry_line.description,
            debit_amount=entry_line.credit_amount,
            credit_amount=entry_line.debit_amount,
        )
        for index, entry_line in enumerate(entry.lines, start=1)
    ]
    repo.add_journal_entry(reversal)
    entry.status = JournalEntryStatus.REVERSED.value
    entry.reversed_at = datetime.now(UTC)
    entry.reversed_by_user_id = actor.id
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action='accounting.booking_line_revenue_reversed',
        target_type='journal_entry',
        target_id=entry.id,
        summary=f'Reversed booking revenue entry {entry.entry_number} for booking {line.booking.booking_number} line {line.line_number}',
        diff={'booking_id': line.booking_id, 'line_id': line.id, 'reversal_entry_number': reversal.entry_number},
    )
    return reversal


def _build_recognition_lines(line: BookingLine, revenue_amount: Decimal, tax_amount: Decimal, collected: Decimal, receivable_amount: Decimal, advances_account_id: str, receivables_account_id: str, revenue_account_id: str, tax_payable_account_id: str) -> list[JournalEntryLine]:
    description = f'Booking {line.booking.booking_number} line {line.line_number}'
    lines: list[JournalEntryLine] = []
    line_number = 1
    if collected > ZERO:
        lines.append(JournalEntryLine(line_number=line_number, account_id=advances_account_id, description=description, debit_amount=collected, credit_amount=ZERO))
        line_number += 1
    if receivable_amount > ZERO:
        lines.append(JournalEntryLine(line_number=line_number, account_id=receivables_account_id, description=description, debit_amount=receivable_amount, credit_amount=ZERO))
        line_number += 1
    if revenue_amount > ZERO:
        lines.append(JournalEntryLine(line_number=line_number, account_id=revenue_account_id, description=description, debit_amount=ZERO, credit_amount=revenue_amount))
        line_number += 1
    if tax_amount > ZERO:
        lines.append(JournalEntryLine(line_number=line_number, account_id=tax_payable_account_id, description=description, debit_amount=ZERO, credit_amount=tax_amount))
    return lines


def _resolve_fiscal_period(repo: AccountingRepository, company_id: str, entry_date: date):
    fiscal_period = repo.get_active_fiscal_period(company_id)
    if fiscal_period is None:
        raise ValidationAppError('لم يتم العثور على الفترة المالية النشطة')
    if fiscal_period.is_locked:
        raise ValidationAppError('لا يمكن الاعتراف بالإيراد داخل فترة مالية مقفلة')
    if entry_date < fiscal_period.starts_on or entry_date > fiscal_period.ends_on:
        raise ValidationAppError('يجب أن يقع تاريخ الاعتراف داخل الفترة المالية النشطة')
    return fiscal_period


def _get_account(repo: AccountingRepository, company_id: str, code: str):
    account = repo.get_chart_account_by_code(company_id, code)
    if account is None or not account.is_active or not account.allows_posting:
        raise ValidationAppError(f'حساب الترحيل {code} غير متاح')
    return account


def _has_active_post_recognition_collections(line: BookingLine) -> bool:
    active_allocations: list[PaymentAllocation] = [allocation for allocation in line.payment_allocations if allocation.payment_document.status != 'voided']
    for allocation in active_allocations:
        journal = allocation.payment_document.journal_entry
        if journal is None:
            continue
        if any(entry_line.account.code == CUSTOMER_RECEIVABLES_CODE and entry_line.credit_amount > ZERO for entry_line in journal.lines):
            return True
    return False
