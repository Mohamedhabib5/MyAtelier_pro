from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import AccountTypeKey
from app.modules.accounting.models import ChartOfAccount
from app.modules.accounting.repository import AccountingRepository
from app.modules.core_platform.service import record_audit
from app.modules.organization.models import DocumentSequence
from app.modules.organization.service import get_company_settings


DEFAULT_JOURNAL_SEQUENCE_KEY = "journal_entry"
DEFAULT_CHART_TEMPLATE = [
    # Level 1
    {"code": "1000", "name": "الأصول", "account_type": AccountTypeKey.ASSET.value, "parent_code": None, "allows_posting": False},
    {"code": "2000", "name": "الالتزامات", "account_type": AccountTypeKey.LIABILITY.value, "parent_code": None, "allows_posting": False},
    {"code": "3000", "name": "حقوق الملكية", "account_type": AccountTypeKey.EQUITY.value, "parent_code": None, "allows_posting": False},
    {"code": "4000", "name": "الإيرادات", "account_type": AccountTypeKey.REVENUE.value, "parent_code": None, "allows_posting": False},
    {"code": "5000", "name": "المصروفات", "account_type": AccountTypeKey.EXPENSE.value, "parent_code": None, "allows_posting": False},

    # Level 2
    {"code": "1100", "name": "الأصول المتداولة", "account_type": AccountTypeKey.ASSET.value, "parent_code": "1000", "allows_posting": False},
    {"code": "1200", "name": "الأصول غير المتداولة", "account_type": AccountTypeKey.ASSET.value, "parent_code": "1000", "allows_posting": False},
    {"code": "2100", "name": "الالتزامات المتداولة", "account_type": AccountTypeKey.LIABILITY.value, "parent_code": "2000", "allows_posting": False},
    {"code": "2200", "name": "ضريبة المخرجات", "account_type": AccountTypeKey.LIABILITY.value, "parent_code": "2000", "allows_posting": True},
    {"code": "3100", "name": "رأس المال", "account_type": AccountTypeKey.EQUITY.value, "parent_code": "3000", "allows_posting": True},
    {"code": "4100", "name": "إيرادات تشغيلية", "account_type": AccountTypeKey.REVENUE.value, "parent_code": "4000", "allows_posting": False},
    {"code": "5100", "name": "مصروفات تشغيلية", "account_type": AccountTypeKey.EXPENSE.value, "parent_code": "5000", "allows_posting": True},

    # Level 3
    {"code": "1110", "name": "النقدية وما يعادلها", "account_type": AccountTypeKey.ASSET.value, "parent_code": "1100", "allows_posting": False},
    {"code": "1120", "name": "ذمم مدنية", "account_type": AccountTypeKey.ASSET.value, "parent_code": "1100", "allows_posting": False},
    {"code": "2110", "name": "عربون العملاء", "account_type": AccountTypeKey.LIABILITY.value, "parent_code": "2100", "allows_posting": True},
    {"code": "2120", "name": "ذمم دائنة", "account_type": AccountTypeKey.LIABILITY.value, "parent_code": "2100", "allows_posting": False},
    {"code": "4110", "name": "إيرادات الخدمات", "account_type": AccountTypeKey.REVENUE.value, "parent_code": "4100", "allows_posting": True},

    # Level 4
    {"code": "1111", "name": "الصناديق", "account_type": AccountTypeKey.CASH.value, "parent_code": "1110", "allows_posting": False},
    {"code": "1112", "name": "البنوك", "account_type": AccountTypeKey.BANK.value, "parent_code": "1110", "allows_posting": False},
    {"code": "1121", "name": "ذمم العملاء الرئيسية", "account_type": AccountTypeKey.RECEIVABLE.value, "parent_code": "1120", "allows_posting": False},
    {"code": "2121", "name": "ذمم الموردين الرئيسية", "account_type": AccountTypeKey.PAYABLE.value, "parent_code": "2120", "allows_posting": False},

    # Level 5
    {"code": "1111001", "name": "الصندوق الرئيسي", "account_type": AccountTypeKey.CASH.value, "parent_code": "1111", "allows_posting": True},
    {"code": "1112001", "name": "البنك الرئيسي", "account_type": AccountTypeKey.BANK.value, "parent_code": "1112", "allows_posting": True},
    {"code": "1121001", "name": "ذمم العملاء التشغيلي", "account_type": AccountTypeKey.RECEIVABLE.value, "parent_code": "1121", "allows_posting": True},
    {"code": "2121001", "name": "ذمم الموردين التشغيلي", "account_type": AccountTypeKey.PAYABLE.value, "parent_code": "2121", "allows_posting": True},
]


def ensure_accounting_foundation(db: Session) -> None:
    company = get_company_settings(db)
    repo = AccountingRepository(db)
    existing_accounts = repo.list_chart_accounts(company.id)
    code_to_account = {account.code for account in existing_accounts}  # wait, existing list has accounts
    code_to_account = {account.code: account for account in existing_accounts}
    created_codes: list[str] = []
    sequence_created = False

    if repo.get_document_sequence(company.id, DEFAULT_JOURNAL_SEQUENCE_KEY) is None:
        repo.add_document_sequence(
            DocumentSequence(
                company_id=company.id,
                key=DEFAULT_JOURNAL_SEQUENCE_KEY,
                prefix="JV",
                next_number=1,
                padding=6,
            )
        )
        sequence_created = True

    for item in DEFAULT_CHART_TEMPLATE:
        if item["code"] in code_to_account:
            continue
            
        parent_account_id = None
        level = 1
        
        if item["parent_code"]:
            parent = code_to_account.get(item["parent_code"])
            if parent:
                parent_account_id = parent.id
                level = parent.level + 1

        account = ChartOfAccount(
            company_id=company.id,
            code=item["code"],
            name=item["name"],
            account_type=item["account_type"],
            parent_account_id=parent_account_id,
            level=level,
            allows_posting=item["allows_posting"],
            is_active=True,
        )
        repo.add_chart_account(account)
        db.flush()
        code_to_account[item["code"]] = account
        created_codes.append(item["code"])

    if created_codes or sequence_created:
        record_audit(
            db,
            actor_user_id=None,
            action="accounting.foundation_seeded",
            target_type="company",
            target_id=company.id,
            summary="Seeded chart of accounts foundation",
            diff={"account_codes": created_codes, "journal_sequence_created": sequence_created},
        )
        db.commit()


def list_chart_accounts(db: Session) -> list[ChartOfAccount]:
    ensure_accounting_foundation(db)
    company = get_company_settings(db)
    return AccountingRepository(db).list_chart_accounts(company.id)
