from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import AccountTypeKey
from app.modules.accounting.models import ChartOfAccount
from app.modules.accounting.repository import AccountingRepository
from app.modules.accounting.schemas import ChartAccountCSVRow
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

    # Seed the accounting bridge configurations
    from app.modules.accounting.bridge_config_service import ensure_accounting_bridge_configs
    ensure_accounting_bridge_configs(db, company.id)

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
    else:
        # Commit if any bridge configs were flushed
        db.commit()



def list_chart_accounts(db: Session) -> list[ChartOfAccount]:
    ensure_accounting_foundation(db)
    company = get_company_settings(db)
    return AccountingRepository(db).list_chart_accounts(company.id)


def validate_chart_of_accounts_csv_rows(rows: list[ChartAccountCSVRow]) -> None:
    """
    تتحقق من صحة أسطر شجرة الحسابات المرفوعة عبر ملف CSV:
    1. عدم تكرار الأكواد.
    2. صحة نوع الحساب من الأنواع المعتمدة بالنظام.
    3. صحة علاقة الحساب الأب (الهيكل الشجري).
    4. منع الحلقات الدائرية (Cycle Detection).
    5. عدم تجاوز عمق الشجرة لـ 5 مستويات.
    """
    from app.core.enums import AccountTypeKey
    from app.core.exceptions import ValidationAppError
    
    valid_types = {t.value for t in AccountTypeKey}
    codes = set()
    code_to_row = {}
    
    for row in rows:
        code = row.code.strip()
        if code in codes:
            raise ValidationAppError(f"⚠️ تكرار في كود الحساب: {code}")
        codes.add(code)
        code_to_row[code] = row
        
        if row.account_type.lower() not in valid_types:
            raise ValidationAppError(f"⚠️ نوع الحساب غير صالح للحساب {code}: {row.account_type}")
            
    for row in rows:
        if row.parent_code:
            parent = row.parent_code.strip()
            if parent not in codes:
                raise ValidationAppError(f"⚠️ الحساب الأب {parent} للحساب {row.code} غير موجود في الملف المرفوع.")

    # منع الحلقات وعمق الشجرة
    for row in rows:
        curr_code = row.code.strip()
        visited_path = {curr_code}
        curr = row
        
        while curr.parent_code:
            parent_code = curr.parent_code.strip()
            if parent_code in visited_path:
                raise ValidationAppError(f"⚠️ حلقة دائرية (Cycle) مكتشفة في الحساب: {parent_code}")
            visited_path.add(parent_code)
            if len(visited_path) > 5:
                raise ValidationAppError(f"⚠️ تجاوز الحد الأقصى للمستويات (5 مستويات) للحساب: {row.code}")
            curr = code_to_row[parent_code]


def import_chart_of_accounts_from_csv(db: Session, rows: list[ChartAccountCSVRow], actor_user_id: str | None) -> None:
    """
    تستقبل أسطر شجرة الحسابات، تتحقق منها، ثم تقوم بمسح الحسابات القديمة (إذا لم توجد قيود)
    وتحفظ الشجرة الجديدة تدريجياً (من المستوى 1 حتى المستويات الأعلى).
    """
    from app.core.exceptions import ValidationAppError
    from app.modules.accounting.models import JournalEntry, ChartOfAccount, AccountingBridgeConfig
    
    # 1. التحقق من صحة الأسطر المرفوعة
    validate_chart_of_accounts_csv_rows(rows)
    
    company = get_company_settings(db)
    repo = AccountingRepository(db)
    
    # 2. منع استبدال الشجرة في حال وجود أي قيود ماليّة مسجلة
    existing_entries_count = db.query(JournalEntry).filter(JournalEntry.company_id == company.id).count()
    if existing_entries_count > 0:
        raise ValidationAppError("⚠️ لا يمكن استيراد شجرة حسابات مخصصة بعد تسجيل قيود يومية في النظام.")
        
    # 3. حذف الشجرة القديمة وإعدادات الجسور للشركة
    db.query(AccountingBridgeConfig).filter(AccountingBridgeConfig.company_id == company.id).delete()
    db.query(ChartOfAccount).filter(ChartOfAccount.company_id == company.id).delete()
    db.flush()
    
    # 4. احتساب مستويات الحسابات لحفظها تدريجياً
    code_to_row = {row.code.strip(): row for row in rows}
    code_to_level = {}
    
    for row in rows:
        curr_code = row.code.strip()
        path = [curr_code]
        curr = row
        while curr.parent_code:
            parent_code = curr.parent_code.strip()
            path.append(parent_code)
            curr = code_to_row[parent_code]
        code_to_level[curr_code] = len(path)
        
    # تجميع الحسابات حسب المستوى (من 1 إلى 5)
    rows_by_level = {i: [] for i in range(1, 6)}
    for row in rows:
        lvl = code_to_level[row.code.strip()]
        rows_by_level[lvl].append(row)
        
    # إدراج الحسابات تدريجياً لضمان وجود المعرفات الفريدة للآباء في قاعدة البيانات
    code_to_db_account = {}
    for lvl in range(1, 6):
        for row in rows_by_level[lvl]:
            parent_account_id = None
            if row.parent_code:
                parent_db = code_to_db_account.get(row.parent_code.strip())
                if parent_db:
                    parent_account_id = parent_db.id
            
            db_account = ChartOfAccount(
                company_id=company.id,
                code=row.code.strip(),
                name=row.name.strip(),
                account_type=row.account_type.strip(),
                parent_account_id=parent_account_id,
                level=lvl,
                allows_posting=row.allows_posting,
                is_active=True,
            )
            repo.add_chart_account(db_account)
            db.flush()
            code_to_db_account[row.code.strip()] = db_account
            
    # 5. إعادة زرع إعدادات الجسور المحاسبية للشجرة الجديدة
    from app.modules.accounting.bridge_config_service import ensure_accounting_bridge_configs
    ensure_accounting_bridge_configs(db, company.id)
    
    # 6. تسجيل العملية بسجل التدقيق
    record_audit(
        db,
        actor_user_id=actor_user_id,
        action="accounting.chart_imported",
        target_type="company",
        target_id=company.id,
        summary=f"Imported custom chart of accounts with {len(rows)} accounts from CSV.",
        diff={"accounts_count": len(rows)},
    )
    db.commit()


def create_chart_account(
    db: Session,
    company_id: str,
    payload: ChartAccountCreateRequest,
    actor_id: str | None,
) -> ChartOfAccount:
    from app.core.exceptions import ValidationAppError
    from app.modules.accounting.schemas import ChartAccountCreateRequest
    
    repo = AccountingRepository(db)
    
    # 1. التحقق من عدم تكرار الكود
    existing = repo.get_chart_account_by_code(company_id, payload.code)
    if existing:
        raise ValidationAppError("⚠️ كود الحساب مستخدم بالفعل.")
    
    level = 1
    parent_account_id = None
    if payload.parent_account_id:
        parent = repo.get_chart_account(payload.parent_account_id)
        if not parent or parent.company_id != company_id:
            raise ValidationAppError("⚠️ الحساب الأب غير موجود.")
        parent_account_id = parent.id
        level = parent.level + 1
        if level > 5:
            raise ValidationAppError("⚠️ لا يمكن أن يتجاوز عمق شجرة الحسابات 5 مستويات.")

    account = ChartOfAccount(
        company_id=company_id,
        code=payload.code.strip(),
        name=payload.name.strip(),
        account_type=payload.account_type.strip(),
        parent_account_id=parent_account_id,
        level=level,
        allows_posting=payload.allows_posting,
        is_active=True,
    )
    repo.add_chart_account(account)
    db.flush()
    
    # تحديث إعدادات الجسور
    from app.modules.accounting.bridge_config_service import ensure_accounting_bridge_configs
    ensure_accounting_bridge_configs(db, company_id)
    
    record_audit(
        db,
        actor_user_id=actor_id,
        action="accounting.account_created",
        target_type="chart_of_account",
        target_id=account.id,
        summary=f"Created chart account: {account.code} - {account.name}",
    )
    db.commit()
    return account


def update_chart_account(
    db: Session,
    account_id: str,
    payload: ChartAccountUpdateRequest,
    actor_id: str | None,
) -> ChartOfAccount:
    from app.core.exceptions import ValidationAppError, NotFoundError
    from app.modules.accounting.schemas import ChartAccountUpdateRequest
    
    repo = AccountingRepository(db)
    account = repo.get_chart_account(account_id)
    if not account:
        raise NotFoundError("⚠️ لم يتم العثور على الحساب.")
        
    # التحقق من الأب وتغيير المستوى والدورة الدائرية
    parent_account_id = None
    level = 1
    if payload.parent_account_id:
        if payload.parent_account_id == account_id:
            raise ValidationAppError("⚠️ لا يمكن تعيين الحساب كأب لنفسه.")
        parent = repo.get_chart_account(payload.parent_account_id)
        if not parent or parent.company_id != account.company_id:
            raise ValidationAppError("⚠️ الحساب الأب غير موجود.")
            
        # كشف الدورة الدائرية (Cycle Detection)
        curr = parent
        depth = 1
        while curr.parent_account_id:
            if curr.parent_account_id == account_id:
                raise ValidationAppError("⚠️ علاقة أب دائرية مكتشفة (Cycle).")
            curr = repo.get_chart_account(curr.parent_account_id)
            depth += 1
            
        if depth + 1 > 5:
            raise ValidationAppError("⚠️ تجاوز الحد الأقصى لمستويات شجرة الحسابات (5 مستويات).")
            
        parent_account_id = parent.id
        level = parent.level + 1
        
    # تحديث الحقول
    account.name = payload.name.strip()
    account.account_type = payload.account_type.strip()
    account.parent_account_id = parent_account_id
    account.level = level
    account.allows_posting = payload.allows_posting
    
    db.flush()
    
    # تحديث إعدادات الجسور
    from app.modules.accounting.bridge_config_service import ensure_accounting_bridge_configs
    ensure_accounting_bridge_configs(db, account.company_id)
    
    record_audit(
        db,
        actor_user_id=actor_id,
        action="accounting.account_updated",
        target_type="chart_of_account",
        target_id=account.id,
        summary=f"Updated chart account: {account.code} - {account.name}",
    )
    db.commit()
    return account


def delete_chart_account(
    db: Session,
    account_id: str,
    actor_id: str | None,
) -> None:
    from app.core.exceptions import ValidationAppError, NotFoundError
    from app.modules.accounting.models import JournalEntryLine
    
    repo = AccountingRepository(db)
    account = repo.get_chart_account(account_id)
    if not account:
        raise NotFoundError("⚠️ لم يتم العثور على الحساب.")
        
    # 1. منع الحذف إذا كان للحساب أبناء
    has_children = db.query(ChartOfAccount).filter(ChartOfAccount.parent_account_id == account_id).first() is not None
    if has_children:
        raise ValidationAppError("⚠️ لا يمكن حذف هذا الحساب لوجود حسابات فرعية تابعة له.")
        
    # 2. منع الحذف إذا كان للحساب حركات مالية
    has_movements = db.query(JournalEntryLine).filter(JournalEntryLine.account_id == account_id).first() is not None
    if has_movements:
        raise ValidationAppError("⚠️ لا يمكن حذف الحساب لوجود حركات مالية (قيود يومية) مسجلة عليه.")
        
    db.delete(account)
    db.flush()
    
    # تحديث إعدادات الجسور
    from app.modules.accounting.bridge_config_service import ensure_accounting_bridge_configs
    ensure_accounting_bridge_configs(db, account.company_id)
    
    record_audit(
        db,
        actor_user_id=actor_id,
        action="accounting.account_deleted",
        target_type="chart_of_account",
        target_id=account_id,
        summary=f"Deleted chart account: {account.code} - {account.name}",
    )
    db.commit()


