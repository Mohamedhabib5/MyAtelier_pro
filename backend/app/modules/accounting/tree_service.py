from __future__ import annotations

from datetime import date
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.modules.accounting.models import ChartOfAccount, JournalEntryLine, JournalEntry
from app.core.enums import JournalEntryStatus


def validate_account_creation(db: Session, company_id: str, code: str, parent_account_id: str | None) -> int:
    """
    Validates account creation rules:
    1. Parent account existence and company boundary check.
    2. Depth level limit (maximum 5 levels).
    3. Blocks creating children under a parent that has postings.
    4. Updates the parent allows_posting flag to False.
    Returns the calculated level of the new account.
    """
    # 1. Root account check (Level 1)
    if parent_account_id is None:
        return 1

    # 2. Parent validation
    parent = db.query(ChartOfAccount).filter(
        ChartOfAccount.id == parent_account_id,
        ChartOfAccount.company_id == company_id
    ).first()

    if not parent:
        raise ValidationAppError("الحساب الأب المحدد غير موجود أو غير تابع للشركة")

    # 3. Depth Level Validation (Max 5)
    if parent.level >= 5:
        raise ValidationAppError("لا يمكن إنشاء حساب في مستوى يتعدى 5 مستويات")

    # 4. Check if Parent has postings
    has_postings = db.query(JournalEntryLine).filter(
        JournalEntryLine.account_id == parent.id
    ).first() is not None

    if has_postings:
        raise ValidationAppError(
            f"لا يمكن إضافة حساب ابن للحساب {parent.code} لأنه يحتوي على قيود يومية مسجلة سابقاً"
        )

    # 5. Disable posting on parent as it is now a summary account
    if parent.allows_posting:
        parent.allows_posting = False
        db.add(parent)

    return parent.level + 1


def get_hierarchical_balances(
    db: Session,
    company_id: str,
    *,
    as_of_date: date | None = None,
    fiscal_period_id: str | None = None,
    branch_id: str | None = None,
    status_in: list[str] | None = None,
) -> list[dict]:
    """
    Fetches the complete Chart of Accounts tree with aggregate balances using a Recursive CTE.
    Aggregates leaf balances up through all parent accounts in a single high-performance query.
    Optionally filters by branch_id, as_of_date, and fiscal_period_id.
    """
    if status_in is None:
        status_in = [JournalEntryStatus.POSTED.value, JournalEntryStatus.REVERSED.value]

    status_placeholders = ", ".join(f":status_{i}" for i in range(len(status_in)))
    params = {
        "company_id": company_id,
    }
    for i, s in enumerate(status_in):
        params[f"status_{i}"] = s
    
    date_filter = ""
    if as_of_date:
        date_filter = "AND je.entry_date <= :as_of_date"
        params["as_of_date"] = as_of_date
        
    period_filter = ""
    if fiscal_period_id:
        period_filter = "AND je.fiscal_period_id = :fiscal_period_id"
        params["fiscal_period_id"] = fiscal_period_id

    branch_filter = ""
    if branch_id:
        branch_filter = "AND je.branch_id = :branch_id"
        params["branch_id"] = branch_id

    query = f"""
        WITH RECURSIVE account_hierarchy AS (
            -- Anchor: Get all accounts in the company
            SELECT id, parent_account_id, id AS descendant_id
            FROM chart_of_accounts
            WHERE company_id = :company_id

            UNION ALL

            -- Recursive step: link parent accounts to the descendants of their children
            SELECT c.id, c.parent_account_id, h.descendant_id
            FROM chart_of_accounts c
            JOIN account_hierarchy h ON c.id = h.parent_account_id
        ),
        leaf_balances AS (
            -- Summarize direct posted balances for each leaf account
            SELECT 
                jl.account_id,
                COALESCE(SUM(jl.debit_amount), 0) AS total_debit,
                COALESCE(SUM(jl.credit_amount), 0) AS total_credit
            FROM journal_entry_lines jl
            JOIN journal_entries je ON jl.journal_entry_id = je.id
            WHERE je.company_id = :company_id 
              AND je.status IN ({status_placeholders})
              {date_filter}
              {period_filter}
              {branch_filter}
            GROUP BY jl.account_id
        )
        SELECT 
            coa.id,
            coa.code,
            coa.name,
            coa.account_type,
            coa.parent_account_id,
            coa.level,
            coa.allows_posting,
            coa.is_active,
            COALESCE(SUM(lb.total_debit), 0) AS balance_debit,
            COALESCE(SUM(lb.total_credit), 0) AS balance_credit
        FROM chart_of_accounts coa
        LEFT JOIN account_hierarchy ah ON coa.id = ah.id
        LEFT JOIN leaf_balances lb ON ah.descendant_id = lb.account_id
        WHERE coa.company_id = :company_id
        GROUP BY 
            coa.id, coa.code, coa.name, coa.account_type, coa.parent_account_id, coa.level, coa.allows_posting, coa.is_active
        ORDER BY coa.code;
    """
    
    result = db.execute(text(query), params).fetchall()
    
    return [
        {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "account_type": row.account_type,
            "parent_account_id": row.parent_account_id,
            "level": row.level,
            "allows_posting": bool(row.allows_posting),
            "is_active": bool(row.is_active),
            "balance_debit": Decimal(str(row.balance_debit)).quantize(Decimal("0.01")),
            "balance_credit": Decimal(str(row.balance_credit)).quantize(Decimal("0.01")),
            "net_balance": (Decimal(str(row.balance_debit)) - Decimal(str(row.balance_credit))).quantize(Decimal("0.01")),
        }
        for row in result
    ]
