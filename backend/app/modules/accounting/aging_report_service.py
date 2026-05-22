from __future__ import annotations

from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.core.exceptions import ValidationAppError
from app.modules.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccount
from app.modules.accounting.party_ledger_service import _resolve_party_name
from app.modules.accounting.party_validation import ALLOWED_PARTY_TYPES
from app.modules.organization.service import get_company_settings

ZERO = Decimal("0.00")
INCLUDED_STATUSES = [JournalEntryStatus.POSTED.value, JournalEntryStatus.REVERSED.value]


def build_aging_report(
    db: Session,
    party_type: str,
    *,
    as_of_date: date | None = None,
) -> dict:
    """
    Generates an AR or AP aging report using FIFO allocation.
    AR uses Account '1121001' (Customer Receivable).
    AP uses Account '2121001' (Supplier Payable).
    Classifies outstanding balances into buckets: 0-30, 31-60, 61-90, 91+ days.
    """
    if party_type not in {"customer", "supplier"}:
        raise ValidationAppError(
            f"نوع الطرف '{party_type}' غير مدعوم لتقرير أعمار الذمم. "
            "القيم المسموحة هي 'customer' أو 'supplier'"
        )

    if as_of_date is None:
        as_of_date = date.today()

    company = get_company_settings(db)
    from app.modules.accounting.bridge_config_service import resolve_bridge_account
    bridge_key = "customer_receivables" if party_type == "customer" else "supplier_payables"
    account_code = resolve_bridge_account(db, company.id, bridge_key).code

    # Query all journal entry lines for the specified party type and account code
    stmt = (
        select(
            JournalEntryLine.party_id,
            JournalEntryLine.debit_amount,
            JournalEntryLine.credit_amount,
            JournalEntry.entry_date,
        )
        .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
        .join(ChartOfAccount, JournalEntryLine.account_id == ChartOfAccount.id)
        .where(
            JournalEntry.company_id == company.id,
            JournalEntry.status.in_(INCLUDED_STATUSES),
            JournalEntry.entry_date <= as_of_date,
            JournalEntryLine.party_type == party_type,
            ChartOfAccount.code == account_code,
        )
        .order_by(JournalEntry.entry_date.asc(), JournalEntry.entry_number.asc(), JournalEntryLine.id.asc())
    )

    rows = db.execute(stmt).all()

    # Group transactions by party_id
    party_txs: dict[str, list] = {}
    for r in rows:
        party_id = r.party_id
        if not party_id:
            continue
        if party_id not in party_txs:
            party_txs[party_id] = []
        party_txs[party_id].append(r)

    report_rows = []
    total_receivable_or_payable = ZERO

    # Apply FIFO aging calculation per party
    for party_id, txs in party_txs.items():
        increases = []
        total_increases = ZERO
        total_decreases = ZERO

        for tx in txs:
            debit = Decimal(str(tx.debit_amount)).quantize(Decimal("0.00"))
            credit = Decimal(str(tx.credit_amount)).quantize(Decimal("0.00"))

            if party_type == "customer":
                inc = debit
                dec = credit
            else:
                inc = credit
                dec = debit

            total_increases += inc
            total_decreases += dec

            if inc > ZERO:
                increases.append({
                    "date": tx.entry_date,
                    "amount": inc
                })

        total_outstanding = total_increases - total_decreases

        # If fully settled and net balance is zero, we skip to keep the report focused
        if total_outstanding == ZERO:
            continue

        buckets = {
            "current": ZERO,
            "past_31_60": ZERO,
            "past_61_90": ZERO,
            "critical_90_plus": ZERO,
        }

        if total_outstanding < ZERO:
            # Net credit balance (overpayment/advance payment) is classified as current (0-30 days)
            buckets["current"] = total_outstanding
        else:
            # FIFO matching algorithm: apply payments against the oldest increases
            remaining_decreases = total_decreases
            for inc in increases:
                inc_amount = inc["amount"]
                inc_date = inc["date"]

                if remaining_decreases >= inc_amount:
                    remaining_decreases -= inc_amount
                    outstanding = ZERO
                else:
                    outstanding = inc_amount - remaining_decreases
                    remaining_decreases = ZERO

                if outstanding > ZERO:
                    age_days = (as_of_date - inc_date).days
                    if age_days <= 30:
                        buckets["current"] += outstanding
                    elif age_days <= 60:
                        buckets["past_31_60"] += outstanding
                    elif age_days <= 90:
                        buckets["past_61_90"] += outstanding
                    else:
                        buckets["critical_90_plus"] += outstanding

        # Resolve party display name
        raw_name = _resolve_party_name(db, party_type, party_id)
        party_name = raw_name or f"{party_type.capitalize()} ({party_id[:8]})"

        report_rows.append({
            "party_id": party_id,
            "party_name": party_name,
            "party_type": party_type,
            "total_outstanding": total_outstanding.quantize(Decimal("0.00")),
            "buckets": {
                "current": buckets["current"].quantize(Decimal("0.00")),
                "31-60": buckets["past_31_60"].quantize(Decimal("0.00")),
                "61-90": buckets["past_61_90"].quantize(Decimal("0.00")),
                "91+": buckets["critical_90_plus"].quantize(Decimal("0.00")),
            }
        })
        total_receivable_or_payable += total_outstanding

    # Sort report rows by descending outstanding balance
    report_rows.sort(key=lambda x: x["total_outstanding"], reverse=True)

    return {
        "as_of_date": as_of_date,
        "party_type": party_type,
        "rows": report_rows,
        "total_receivable_or_payable": total_receivable_or_payable.quantize(Decimal("0.00")),
    }
