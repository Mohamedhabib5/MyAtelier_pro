from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security import norm_text
from app.modules.accounting.models import JournalEntry, JournalEntryLine
from app.modules.accounting.repository import AccountingRepository
from app.modules.accounting.schemas import (
    JournalEntryCreateRequest,
    JournalEntryLineWriteRequest,
    JournalEntryReverseRequest,
    JournalEntryUpdateRequest,
)
from app.modules.accounting.service import DEFAULT_JOURNAL_SEQUENCE_KEY, ensure_accounting_foundation
from app.modules.core_platform.service import record_audit
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings


ZERO = Decimal("0.00")


def list_journal_entries(db: Session) -> list[dict]:
    ensure_accounting_foundation(db)
    company = get_company_settings(db)
    rows = AccountingRepository(db).list_journal_entries(company.id)
    return [_serialize_entry(entry) for entry in rows]


def get_journal_entry(db: Session, entry_id: str) -> dict:
    return _serialize_entry(_get_entry_or_404(db, entry_id))


def create_draft_journal_entry(db: Session, actor: User, payload: JournalEntryCreateRequest) -> dict:
    ensure_accounting_foundation(db)
    company = get_company_settings(db)
    repo = AccountingRepository(db)
    fiscal_period = _resolve_fiscal_period(repo, company.id, payload.fiscal_period_id, payload.entry_date)
    entry_number = repo.reserve_sequence_number(company.id, DEFAULT_JOURNAL_SEQUENCE_KEY)
    lines = _build_lines(repo, company.id, payload.lines)
    entry = JournalEntry(
        company_id=company.id,
        fiscal_period_id=fiscal_period.id,
        entry_number=entry_number,
        entry_date=payload.entry_date,
        status=JournalEntryStatus.DRAFT.value,
        reference=_clean_text(payload.reference),
        notes=_clean_text(payload.notes),
    )
    entry.lines = lines
    repo.add_journal_entry(entry)
    db.flush()
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.journal_draft_created",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Created draft journal entry {entry.entry_number}",
        diff={"line_count": len(lines)},
    )
    db.commit()
    return get_journal_entry(db, entry.id)


def update_draft_journal_entry(db: Session, actor: User, entry_id: str, payload: JournalEntryUpdateRequest) -> dict:
    entry = _get_entry_or_404(db, entry_id)
    if entry.status != JournalEntryStatus.DRAFT.value:
        raise ValidationAppError("يمكن تعديل القيود المسودة فقط")
    repo = AccountingRepository(db)
    fiscal_period = _resolve_fiscal_period(repo, entry.company_id, payload.fiscal_period_id, payload.entry_date)
    lines = _build_lines(repo, entry.company_id, payload.lines)
    entry.fiscal_period_id = fiscal_period.id
    entry.entry_date = payload.entry_date
    entry.reference = _clean_text(payload.reference)
    entry.notes = _clean_text(payload.notes)
    entry.lines.clear()
    entry.lines.extend(lines)
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.journal_draft_updated",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Updated draft journal entry {entry.entry_number}",
        diff={"line_count": len(lines)},
    )
    db.commit()
    return get_journal_entry(db, entry.id)


def post_journal_entry(db: Session, actor: User, entry_id: str) -> dict:
    entry = _get_entry_or_404(db, entry_id)
    if entry.status != JournalEntryStatus.DRAFT.value:
        raise ValidationAppError("يمكن ترحيل القيود المسودة فقط")
    _validate_balanced_lines(entry.lines)
    entry.status = JournalEntryStatus.POSTED.value
    entry.posted_at = datetime.now(UTC)
    entry.posted_by_user_id = actor.id
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.journal_posted",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Posted journal entry {entry.entry_number}",
    )
    db.commit()
    return get_journal_entry(db, entry.id)


def reverse_journal_entry(db: Session, actor: User, entry_id: str, payload: JournalEntryReverseRequest) -> dict:
    entry = _get_entry_or_404(db, entry_id)
    if entry.status != JournalEntryStatus.POSTED.value:
        raise ValidationAppError("يمكن عكس القيود المرحّلة فقط")
    repo = AccountingRepository(db)
    reverse_date = payload.reverse_date or entry.entry_date
    fiscal_period = _resolve_fiscal_period(repo, entry.company_id, entry.fiscal_period_id, reverse_date)
    reversal_number = repo.reserve_sequence_number(entry.company_id, DEFAULT_JOURNAL_SEQUENCE_KEY)
    reversal = JournalEntry(
        company_id=entry.company_id,
        fiscal_period_id=fiscal_period.id,
        entry_number=reversal_number,
        entry_date=reverse_date,
        status=JournalEntryStatus.POSTED.value,
        reference=f"REV-{entry.entry_number}",
        notes=_clean_text(payload.notes) or f"Reversal of {entry.entry_number}",
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
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.journal_reversed",
        target_type="journal_entry",
        target_id=entry.id,
        summary=f"Reversed journal entry {entry.entry_number}",
        diff={"reversal_entry_number": reversal.entry_number},
    )
    db.commit()
    return get_journal_entry(db, reversal.id)


def _get_entry_or_404(db: Session, entry_id: str) -> JournalEntry:
    entry = AccountingRepository(db).get_journal_entry(entry_id)
    if entry is None:
        raise NotFoundError("لم يتم العثور على القيد اليومي")
    return entry


def _resolve_fiscal_period(repo: AccountingRepository, company_id: str, fiscal_period_id: str | None, entry_date: date):
    fiscal_period = repo.get_fiscal_period(fiscal_period_id) if fiscal_period_id else repo.get_active_fiscal_period(company_id)
    if fiscal_period is None or fiscal_period.company_id != company_id:
        raise ValidationAppError("لم يتم العثور على الفترة المالية")
    if fiscal_period.is_locked:
        raise ValidationAppError("لا يمكن إضافة قيود إلى فترة مالية مقفلة")
    if entry_date < fiscal_period.starts_on or entry_date > fiscal_period.ends_on:
        raise ValidationAppError("يجب أن يقع تاريخ القيد داخل الفترة المالية")
    return fiscal_period


def _build_lines(repo: AccountingRepository, company_id: str, rows: list[JournalEntryLineWriteRequest]) -> list[JournalEntryLine]:
    if len(rows) < 2:
        raise ValidationAppError("يتطلب القيد سطرين على الأقل")
    built: list[JournalEntryLine] = []
    for index, row in enumerate(rows, start=1):
        account = repo.get_chart_account(row.account_id)
        if account is None or account.company_id != company_id:
            raise ValidationAppError("لم يتم العثور على حساب القيد")
        if not account.is_active or not account.allows_posting:
            raise ValidationAppError(f"الحساب {account.code} غير متاح للترحيل")
        line = JournalEntryLine(
            line_number=index,
            account_id=account.id,
            description=_clean_text(row.description),
            debit_amount=row.debit_amount,
            credit_amount=row.credit_amount,
        )
        built.append(line)
    _validate_balanced_lines(built)
    return built


def _validate_balanced_lines(lines: list[JournalEntryLine]) -> None:
    total_debit = ZERO
    total_credit = ZERO
    for line in lines:
        debit = _normalize_amount(line.debit_amount)
        credit = _normalize_amount(line.credit_amount)
        if debit == ZERO and credit == ZERO:
            raise ValidationAppError("لا يمكن أن يكون سطر القيد صفريًا من الجانبين")
        if debit > ZERO and credit > ZERO:
            raise ValidationAppError("لا يمكن أن يكون سطر القيد مدينًا ودائنًا في الوقت نفسه")
        total_debit += debit
        total_credit += credit
    if total_debit == ZERO or total_credit == ZERO:
        raise ValidationAppError("يجب أن يحتوي القيد على إجمالي مدين ودائن")
    if total_debit != total_credit:
        raise ValidationAppError("القيد غير متوازن")


def _serialize_entry(entry: JournalEntry) -> dict:
    total_debit = sum((_normalize_amount(line.debit_amount) for line in entry.lines), ZERO)
    total_credit = sum((_normalize_amount(line.credit_amount) for line in entry.lines), ZERO)
    return {
        "id": entry.id,
        "company_id": entry.company_id,
        "fiscal_period_id": entry.fiscal_period_id,
        "entry_number": entry.entry_number,
        "entry_date": entry.entry_date,
        "status": entry.status,
        "reference": entry.reference,
        "notes": entry.notes,
        "posted_at": entry.posted_at,
        "posted_by_user_id": entry.posted_by_user_id,
        "reversed_at": entry.reversed_at,
        "reversed_by_user_id": entry.reversed_by_user_id,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "lines": [
            {
                "id": line.id,
                "line_number": line.line_number,
                "account_id": line.account_id,
                "account_code": line.account.code,
                "account_name": line.account.name,
                "description": line.description,
                "debit_amount": _normalize_amount(line.debit_amount),
                "credit_amount": _normalize_amount(line.credit_amount),
            }
            for line in entry.lines
        ],
    }


def _normalize_amount(value: Decimal | None) -> Decimal:
    return (value or ZERO).quantize(Decimal("0.01"))


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = norm_text(value)
    return text or None
