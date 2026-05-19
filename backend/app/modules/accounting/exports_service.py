from datetime import date
from sqlalchemy.orm import Session

from app.modules.exports.rendering import build_xlsx
from app.modules.accounting.trial_balance_service import build_trial_balance
from app.modules.accounting.income_statement_service import build_income_statement
from app.modules.accounting.aging_report_service import build_aging_report

# Column configurations & translations
TRIAL_BALANCE_COLUMNS = [
    'account_code', 'account_name', 'account_type',
    'movement_debit', 'movement_credit', 'balance_debit', 'balance_credit'
]
TRIAL_BALANCE_TRANSLATIONS = {
    'account_code': 'كود الحساب (Code)',
    'account_name': 'اسم الحساب (Account)',
    'account_type': 'النوع (Type)',
    'movement_debit': 'حركة مدين (Mov Debit)',
    'movement_credit': 'حركة دائن (Mov Credit)',
    'balance_debit': 'رصيد مدين (Bal Debit)',
    'balance_credit': 'رصيد دائن (Bal Credit)'
}

INCOME_STATEMENT_COLUMNS = ['section', 'account_code', 'account_name', 'balance']
INCOME_STATEMENT_TRANSLATIONS = {
    'section': 'القسم (Section)',
    'account_code': 'كود الحساب (Code)',
    'account_name': 'اسم الحساب (Account)',
    'balance': 'الرصيد (Balance)'
}

AGING_REPORT_COLUMNS = ['party_name', 'total_outstanding', 'bucket_current', 'bucket_31_60', 'bucket_61_90', 'bucket_91']
AGING_REPORT_TRANSLATIONS = {
    'party_name': 'الطرف (Party)',
    'total_outstanding': 'إجمالي المستحق (Total)',
    'bucket_current': 'حالي (Current)',
    'bucket_31_60': '31-60 يوم (Days)',
    'bucket_61_90': '61-90 يوم (Days)',
    'bucket_91': '91+ يوم (Days)'
}


def export_trial_balance_excel(
    db: Session,
    as_of_date: date | None = None,
    fiscal_period_id: str | None = None,
    branch_id: str | None = None,
    include_zero_accounts: bool = False,
) -> bytes:
    tb_data = build_trial_balance(
        db,
        as_of_date=as_of_date,
        fiscal_period_id=fiscal_period_id,
        branch_id=branch_id,
        include_zero_accounts=include_zero_accounts,
    )
    
    rows = []
    for r in tb_data.get('rows', []):
        rows.append({
            'account_code': r['account_code'],
            'account_name': r['account_name'],
            'account_type': r['account_type'],
            'movement_debit': float(r['movement_debit']),
            'movement_credit': float(r['movement_credit']),
            'balance_debit': float(r['balance_debit']),
            'balance_credit': float(r['balance_credit']),
        })
        
    # Append Total row
    summary = tb_data.get('summary', {})
    rows.append({
        'account_code': 'الإجمالي (Total)',
        'account_name': '',
        'account_type': '',
        'movement_debit': float(summary.get('movement_debit_total', 0)),
        'movement_credit': float(summary.get('movement_credit_total', 0)),
        'balance_debit': float(summary.get('balance_debit_total', 0)),
        'balance_credit': float(summary.get('balance_credit_total', 0)),
    })
    
    return build_xlsx(rows, TRIAL_BALANCE_COLUMNS, TRIAL_BALANCE_TRANSLATIONS)


def export_income_statement_excel(
    db: Session,
    as_of_date: date | None = None,
    branch_id: str | None = None,
) -> bytes:
    is_data = build_income_statement(db, as_of_date=as_of_date, branch_id=branch_id)
    
    rows = []
    # 1. Revenues Section
    for item in is_data.get('revenues', {}).get('items', []):
        rows.append({
            'section': 'الإيرادات (Revenues)',
            'account_code': item['account_code'],
            'account_name': item['account_name'],
            'balance': float(item['balance']),
        })
    rows.append({
        'section': 'إجمالي الإيرادات (Total Revenues)',
        'account_code': '',
        'account_name': '',
        'balance': float(is_data.get('revenues', {}).get('total', 0)),
    })
    
    # Empty space
    rows.append({'section': '', 'account_code': '', 'account_name': '', 'balance': ''})
    
    # 2. Expenses Section
    for item in is_data.get('expenses', {}).get('items', []):
        rows.append({
            'section': 'المصروفات (Expenses)',
            'account_code': item['account_code'],
            'account_name': item['account_name'],
            'balance': float(item['balance']),
        })
    rows.append({
        'section': 'إجمالي المصروفات (Total Expenses)',
        'account_code': '',
        'account_name': '',
        'balance': float(is_data.get('expenses', {}).get('total', 0)),
    })
    
    # Empty space
    rows.append({'section': '', 'account_code': '', 'account_name': '', 'balance': ''})
    
    # 3. Net Income row
    rows.append({
        'section': 'صافي الدخل / الربح أو الخسارة (Net Income)',
        'account_code': '',
        'account_name': '',
        'balance': float(is_data.get('net_income', 0)),
    })
    
    return build_xlsx(rows, INCOME_STATEMENT_COLUMNS, INCOME_STATEMENT_TRANSLATIONS)


def export_aging_report_excel(
    db: Session,
    party_type: str,
    as_of_date: date | None = None,
) -> bytes:
    aging_data = build_aging_report(db, party_type=party_type, as_of_date=as_of_date)
    
    rows = []
    for r in aging_data.get('rows', []):
        rows.append({
            'party_name': r['party_name'],
            'total_outstanding': float(r['total_outstanding']),
            'bucket_current': float(r['buckets']['current']),
            'bucket_31_60': float(r['buckets']['31-60']),
            'bucket_61_90': float(r['buckets']['61-90']),
            'bucket_91': float(r['buckets']['91+']),
        })
        
    # Append Total row
    rows.append({
        'party_name': 'الإجمالي (Total)',
        'total_outstanding': float(aging_data.get('total_receivable_or_payable', 0)),
        'bucket_current': '',
        'bucket_31_60': '',
        'bucket_61_90': '',
        'bucket_91': '',
    })
    
    return build_xlsx(rows, AGING_REPORT_COLUMNS, AGING_REPORT_TRANSLATIONS)
