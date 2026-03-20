from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.modules.accounting.repository import AccountingRepository
from app.modules.accounting.service import ensure_accounting_foundation
from app.modules.organization.service import get_company_settings


ZERO = Decimal("0.00")
INCLUDED_STATUSES = [JournalEntryStatus.POSTED.value, JournalEntryStatus.REVERSED.value]


def build_trial_balance(
    db: Session,
    *,
    as_of_date: date | None = None,
    fiscal_period_id: str | None = None,
    include_zero_accounts: bool = False,
) -> dict:
    ensure_accounting_foundation(db)
    company = get_company_settings(db)
    repo = AccountingRepository(db)
    accounts = repo.list_chart_accounts(company.id)
    entries = repo.list_journal_entries(company.id)

    filtered_entries = [
        entry
        for entry in entries
        if entry.status in INCLUDED_STATUSES
        and (fiscal_period_id is None or entry.fiscal_period_id == fiscal_period_id)
        and (as_of_date is None or entry.entry_date <= as_of_date)
    ]

    movement_map: dict[str, dict[str, Decimal]] = {
        account.id: {"debit": ZERO, "credit": ZERO}
        for account in accounts
    }
    for entry in filtered_entries:
        for line in entry.lines:
            movement_map[line.account_id]["debit"] += _normalize(line.debit_amount)
            movement_map[line.account_id]["credit"] += _normalize(line.credit_amount)

    rows: list[dict] = []
    movement_debit_total = ZERO
    movement_credit_total = ZERO
    balance_debit_total = ZERO
    balance_credit_total = ZERO

    for account in accounts:
        movement_debit = movement_map[account.id]["debit"]
        movement_credit = movement_map[account.id]["credit"]
        balance_delta = movement_debit - movement_credit
        balance_debit = balance_delta if balance_delta > ZERO else ZERO
        balance_credit = -balance_delta if balance_delta < ZERO else ZERO
        if not include_zero_accounts and movement_debit == ZERO and movement_credit == ZERO:
            continue
        rows.append(
            {
                "account_id": account.id,
                "account_code": account.code,
                "account_name": account.name,
                "account_type": account.account_type,
                "movement_debit": movement_debit,
                "movement_credit": movement_credit,
                "balance_debit": balance_debit,
                "balance_credit": balance_credit,
            }
        )
        movement_debit_total += movement_debit
        movement_credit_total += movement_credit
        balance_debit_total += balance_debit
        balance_credit_total += balance_credit

    return {
        "as_of_date": as_of_date,
        "fiscal_period_id": fiscal_period_id,
        "included_statuses": INCLUDED_STATUSES,
        "rows": rows,
        "summary": {
            "movement_debit_total": movement_debit_total,
            "movement_credit_total": movement_credit_total,
            "balance_debit_total": balance_debit_total,
            "balance_credit_total": balance_credit_total,
            "entry_count": len(filtered_entries),
        },
    }



def _normalize(value: Decimal | None) -> Decimal:
    return (value or ZERO).quantize(Decimal("0.00"))
