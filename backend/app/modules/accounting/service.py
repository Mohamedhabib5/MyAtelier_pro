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
    {"code": "1000", "name": "الصندوق", "account_type": AccountTypeKey.ASSET.value},
    {"code": "1100", "name": "البنك", "account_type": AccountTypeKey.ASSET.value},
    {"code": "1200", "name": "ذمم العملاء", "account_type": AccountTypeKey.ASSET.value},
    {"code": "2100", "name": "عربون العملاء", "account_type": AccountTypeKey.LIABILITY.value},
    {"code": "2200", "name": "ضريبة المخرجات", "account_type": AccountTypeKey.LIABILITY.value},
    {"code": "3100", "name": "حقوق الملكية", "account_type": AccountTypeKey.EQUITY.value},
    {"code": "4100", "name": "إيرادات الخدمات", "account_type": AccountTypeKey.REVENUE.value},
    {"code": "5100", "name": "مصروفات تشغيلية", "account_type": AccountTypeKey.EXPENSE.value},
]


def ensure_accounting_foundation(db: Session) -> None:
    company = get_company_settings(db)
    repo = AccountingRepository(db)
    existing_accounts = repo.list_chart_accounts(company.id)
    existing_codes = {account.code for account in existing_accounts}
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
        if item["code"] in existing_codes:
            continue
        repo.add_chart_account(
            ChartOfAccount(
                company_id=company.id,
                code=item["code"],
                name=item["name"],
                account_type=item["account_type"],
                allows_posting=True,
                is_active=True,
            )
        )
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
