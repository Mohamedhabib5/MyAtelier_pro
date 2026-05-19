"""Party Ledger Service – Customer/Supplier/Employee statement queries.

Provides get_party_statement() which builds a full account statement
for any party, including opening balance, detailed movements, and
closing balance. Party name is resolved dynamically based on party_type.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import and_, select, func
from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.core.exceptions import NotFoundError, ValidationAppError
from app.modules.accounting.models import JournalEntry, JournalEntryLine
from app.modules.accounting.party_validation import ALLOWED_PARTY_TYPES


ZERO = Decimal("0.00")
STATEMENT_STATUSES = {JournalEntryStatus.POSTED.value, JournalEntryStatus.REVERSED.value}


def get_party_statement(
    db: Session,
    company_id: str,
    party_type: str,
    party_id: str,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    """Build a full party statement with opening balance, movements, and closing balance."""
    if party_type not in ALLOWED_PARTY_TYPES:
        raise ValidationAppError(
            f"نوع الطرف '{party_type}' غير مدعوم. "
            f"القيم المسموحة: {', '.join(sorted(ALLOWED_PARTY_TYPES))}"
        )

    party_name = _resolve_party_name(db, party_type, party_id)

    # Build base filter: lines for this party in posted/reversed entries of this company.
    base_filter = and_(
        JournalEntryLine.party_type == party_type,
        JournalEntryLine.party_id == party_id,
        JournalEntry.company_id == company_id,
        JournalEntry.status.in_(list(STATEMENT_STATUSES)),
    )

    # --- Opening balance (movements before from_date) ---
    opening_balance = ZERO
    if from_date is not None:
        opening_stmt = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
                func.coalesce(func.sum(JournalEntryLine.credit_amount), 0),
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .where(base_filter, JournalEntry.entry_date < from_date)
        )
        row = db.execute(opening_stmt).one()
        opening_debit = Decimal(str(row[0])).quantize(Decimal("0.01"))
        opening_credit = Decimal(str(row[1])).quantize(Decimal("0.01"))
        opening_balance = opening_debit - opening_credit

    # --- Detailed movements ---
    movements_filter = base_filter
    if from_date is not None:
        movements_filter = and_(movements_filter, JournalEntry.entry_date >= from_date)
    if to_date is not None:
        movements_filter = and_(movements_filter, JournalEntry.entry_date <= to_date)

    movements_stmt = (
        select(
            JournalEntry.entry_date,
            JournalEntry.entry_number,
            JournalEntry.reference,
            JournalEntryLine.description,
            JournalEntryLine.debit_amount,
            JournalEntryLine.credit_amount,
        )
        .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
        .where(movements_filter)
        .order_by(JournalEntry.entry_date.asc(), JournalEntry.entry_number.asc())
    )
    rows = db.execute(movements_stmt).all()

    running_balance = opening_balance
    total_debit = ZERO
    total_credit = ZERO
    movements: list[dict] = []

    for row in rows:
        debit = Decimal(str(row.debit_amount)).quantize(Decimal("0.01"))
        credit = Decimal(str(row.credit_amount)).quantize(Decimal("0.01"))
        running_balance += debit - credit
        total_debit += debit
        total_credit += credit
        movements.append({
            "entry_date": row.entry_date,
            "entry_number": row.entry_number,
            "reference": row.reference,
            "description": row.description,
            "debit_amount": debit,
            "credit_amount": credit,
            "running_balance": running_balance,
        })

    return {
        "party_type": party_type,
        "party_id": party_id,
        "party_name": party_name,
        "from_date": from_date,
        "to_date": to_date,
        "opening_balance": opening_balance,
        "movements": movements,
        "closing_balance": running_balance,
        "total_debit": total_debit,
        "total_credit": total_credit,
    }


def _resolve_party_name(db: Session, party_type: str, party_id: str) -> str | None:
    """Dynamically resolve the party display name based on party_type."""
    if party_type == "customer":
        from app.modules.customers.models import Customer
        customer = db.get(Customer, party_id)
        return customer.full_name if customer else None
    # Supplier and Employee models don't exist yet — return None gracefully.
    return None
