from __future__ import annotations

from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.enums import JournalEntryStatus
from app.modules.accounting.tree_service import get_hierarchical_balances
from app.modules.accounting.service import ensure_accounting_foundation
from app.modules.organization.service import get_company_settings

ZERO = Decimal("0.00")
INCLUDED_STATUSES = [JournalEntryStatus.POSTED.value, JournalEntryStatus.REVERSED.value]


def build_income_statement(
    db: Session,
    *,
    as_of_date: date | None = None,
    branch_id: str | None = None,
) -> dict:
    """
    Builds an income statement by retrieving hierarchical balances
    and categorizing accounts starting with '4' as revenue
    and accounts starting with '5' as expense.
    Calculates net income: Total Revenue - Total Expense.
    """
    ensure_accounting_foundation(db)
    company = get_company_settings(db)

    # Fetch hierarchical data using tree_service
    hierarchical_data = get_hierarchical_balances(
        db,
        company.id,
        as_of_date=as_of_date,
        branch_id=branch_id,
        status_in=INCLUDED_STATUSES,
    )

    revenue_items = []
    expense_items = []

    total_revenue = ZERO
    total_expense = ZERO

    for item in hierarchical_data:
        code = item["code"]
        debit = (item["balance_debit"] or ZERO).quantize(Decimal("0.00"))
        credit = (item["balance_credit"] or ZERO).quantize(Decimal("0.00"))

        # Skip zero balance accounts to keep report clean
        if debit == ZERO and credit == ZERO:
            continue

        if code.startswith("4"):
            # Revenue: balance = credit - debit
            balance = credit - debit
            revenue_items.append({
                "account_id": item["id"],
                "account_code": code,
                "account_name": item["name"],
                "account_type": item["account_type"],
                "parent_account_id": item["parent_account_id"],
                "level": item["level"],
                "debit": debit,
                "credit": credit,
                "balance": balance,
            })
            # Aggregate ONLY for leaf accounts to prevent double-counting
            if item["allows_posting"]:
                total_revenue += balance

        elif code.startswith("5"):
            # Expense: balance = debit - credit
            balance = debit - credit
            expense_items.append({
                "account_id": item["id"],
                "account_code": code,
                "account_name": item["name"],
                "account_type": item["account_type"],
                "parent_account_id": item["parent_account_id"],
                "level": item["level"],
                "debit": debit,
                "credit": credit,
                "balance": balance,
            })
            # Aggregate ONLY for leaf accounts to prevent double-counting
            if item["allows_posting"]:
                total_expense += balance

    net_income = total_revenue - total_expense

    return {
        "as_of_date": as_of_date,
        "branch_id": branch_id,
        "revenues": {
            "items": revenue_items,
            "total": total_revenue,
        },
        "expenses": {
            "items": expense_items,
            "total": total_expense,
        },
        "net_income": net_income,
    }
