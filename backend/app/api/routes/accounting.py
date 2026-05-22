from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, status, Response, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import require_accounting_manage, require_accounting_view
from app.db.session import get_db
from app.modules.accounting.journal_service import (
    create_draft_journal_entry,
    get_journal_entry,
    list_journal_entries,
    post_journal_entry,
    reverse_journal_entry,
    update_draft_journal_entry,
    delete_draft_journal_entry,
)
from app.modules.accounting.schemas import (
    ChartAccountResponse,
    JournalEntryCreateRequest,
    JournalEntryResponse,
    JournalEntryReverseRequest,
    JournalEntryUpdateRequest,
    TrialBalanceResponse,
    IncomeStatementResponse,
    AgingReportResponse,
    AccountingBridgeConfigResponse,
    AccountingBridgeConfigUpdateRequest,
    ChartAccountCSVRow,
    ChartAccountCreateRequest,
    ChartAccountUpdateRequest,
)
from app.modules.accounting.service import (
    list_chart_accounts,
    import_chart_of_accounts_from_csv,
    create_chart_account,
    update_chart_account,
    delete_chart_account,
)
from app.modules.accounting.trial_balance_service import build_trial_balance
from app.modules.accounting.income_statement_service import build_income_statement
from app.modules.accounting.aging_report_service import build_aging_report
from app.modules.identity.models import User
from app.modules.accounting.exports_service import (
    export_trial_balance_excel,
    export_income_statement_excel,
    export_aging_report_excel,
)
from app.modules.accounting.bridge_config_service import (
    list_bridge_configs,
    update_bridge_config,
    reset_bridge_config,
)

router = APIRouter(prefix="/accounting", tags=["accounting"])


@router.get("/chart-of-accounts", response_model=list[ChartAccountResponse])
def get_chart_of_accounts(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
) -> list[ChartAccountResponse]:
    return [ChartAccountResponse.model_validate(item) for item in list_chart_accounts(db)]


@router.post("/chart-of-accounts", response_model=ChartAccountResponse, status_code=status.HTTP_201_CREATED)
def create_chart_account_route(
    payload: ChartAccountCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> ChartAccountResponse:
    from app.modules.organization.service import get_company_settings
    company = get_company_settings(db)
    return ChartAccountResponse.model_validate(
        create_chart_account(db, company.id, payload, current_user.id)
    )


@router.patch("/chart-of-accounts/{account_id}", response_model=ChartAccountResponse)
def update_chart_account_route(
    account_id: str,
    payload: ChartAccountUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> ChartAccountResponse:
    return ChartAccountResponse.model_validate(
        update_chart_account(db, account_id, payload, current_user.id)
    )


@router.delete("/chart-of-accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chart_account_route(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
):
    delete_chart_account(db, account_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/journal-entries", response_model=list[JournalEntryResponse])
def get_journal_entries(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
) -> list[JournalEntryResponse]:
    return [JournalEntryResponse.model_validate(item) for item in list_journal_entries(db)]


@router.get("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
def get_journal_entry_route(
    entry_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(get_journal_entry(db, entry_id))


@router.post("/journal-entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_journal_entry_route(
    payload: JournalEntryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(create_draft_journal_entry(db, current_user, payload))


@router.patch("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
def update_journal_entry_route(
    entry_id: str,
    payload: JournalEntryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(update_draft_journal_entry(db, current_user, entry_id, payload))


@router.delete("/journal-entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry_route(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
):
    delete_draft_journal_entry(db, current_user, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/journal-entries/{entry_id}/post", response_model=JournalEntryResponse)
def post_journal_entry_route(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(post_journal_entry(db, current_user, entry_id))


@router.post("/journal-entries/{entry_id}/reverse", response_model=JournalEntryResponse)
def reverse_journal_entry_route(
    entry_id: str,
    payload: JournalEntryReverseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_manage),
) -> JournalEntryResponse:
    return JournalEntryResponse.model_validate(reverse_journal_entry(db, current_user, entry_id, payload))


@router.get("/trial-balance", response_model=TrialBalanceResponse)
def get_trial_balance(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
    as_of_date: date | None = Query(default=None),
    fiscal_period_id: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    include_zero_accounts: bool = Query(default=False),
) -> TrialBalanceResponse:
    return TrialBalanceResponse.model_validate(
        build_trial_balance(
            db,
            as_of_date=as_of_date,
            fiscal_period_id=fiscal_period_id,
            branch_id=branch_id,
            include_zero_accounts=include_zero_accounts,
        )
    )


@router.get("/income-statement", response_model=IncomeStatementResponse)
def get_income_statement(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
    as_of_date: date | None = Query(default=None),
    branch_id: str | None = Query(default=None),
) -> IncomeStatementResponse:
    return IncomeStatementResponse.model_validate(
        build_income_statement(
            db,
            as_of_date=as_of_date,
            branch_id=branch_id,
        )
    )


@router.get("/aging", response_model=AgingReportResponse)
def get_aging_report(
    party_type: str = Query(..., description="Either 'customer' or 'supplier'"),
    as_of_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
) -> AgingReportResponse:
    return AgingReportResponse.model_validate(
        build_aging_report(
            db,
            party_type=party_type,
            as_of_date=as_of_date,
        )
    )


@router.get("/trial-balance/export")
def export_trial_balance_excel_route(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
    as_of_date: date | None = Query(default=None),
    fiscal_period_id: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    include_zero_accounts: bool = Query(default=False),
) -> Response:
    content = export_trial_balance_excel(
        db,
        as_of_date=as_of_date,
        fiscal_period_id=fiscal_period_id,
        branch_id=branch_id,
        include_zero_accounts=include_zero_accounts,
    )
    headers = {
        "Content-Disposition": f"attachment; filename=trial_balance_{date.today().isoformat()}.xlsx"
    }
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/income-statement/export")
def export_income_statement_excel_route(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
    as_of_date: date | None = Query(default=None),
    branch_id: str | None = Query(default=None),
) -> Response:
    content = export_income_statement_excel(
        db,
        as_of_date=as_of_date,
        branch_id=branch_id,
    )
    headers = {
        "Content-Disposition": f"attachment; filename=income_statement_{date.today().isoformat()}.xlsx"
    }
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/aging/export")
def export_aging_report_excel_route(
    party_type: str = Query(..., description="Either 'customer' or 'supplier'"),
    as_of_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
) -> Response:
    content = export_aging_report_excel(
        db,
        party_type=party_type,
        as_of_date=as_of_date,
    )
    headers = {
        "Content-Disposition": f"attachment; filename=aging_report_{party_type}_{date.today().isoformat()}.xlsx"
    }
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


# --- Accounting Bridge Configuration Endpoints ---

from app.api.deps import PermissionRequired, get_current_user
from app.core.exceptions import AuthorizationError
from app.modules.organization.service import get_company_settings


def require_accounting_bridge_manage(current_user: User = Depends(get_current_user)) -> User:
    try:
        return PermissionRequired("accounting.bridge_manage")(current_user)
    except AuthorizationError:
        return PermissionRequired("accounting.manage")(current_user)


@router.get("/bridge-configs", response_model=list[AccountingBridgeConfigResponse])
def get_bridge_configs_route(
    db: Session = Depends(get_db),
    _: User = Depends(require_accounting_view),
) -> list[AccountingBridgeConfigResponse]:
    company = get_company_settings(db)
    return [AccountingBridgeConfigResponse.model_validate(item) for item in list_bridge_configs(db, company.id)]


@router.patch("/bridge-configs/{bridge_key}", response_model=AccountingBridgeConfigResponse)
def update_bridge_config_route(
    bridge_key: str,
    payload: AccountingBridgeConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_bridge_manage),
) -> AccountingBridgeConfigResponse:
    company = get_company_settings(db)
    result = update_bridge_config(db, company.id, bridge_key, payload, current_user)
    return AccountingBridgeConfigResponse.model_validate(result)


@router.post("/bridge-configs/{bridge_key}/reset", response_model=AccountingBridgeConfigResponse)
def reset_bridge_config_route(
    bridge_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_bridge_manage),
) -> AccountingBridgeConfigResponse:
    company = get_company_settings(db)
    result = reset_bridge_config(db, company.id, bridge_key, current_user)
    return AccountingBridgeConfigResponse.model_validate(result)


@router.post("/chart-of-accounts/import", status_code=status.HTTP_200_OK)
async def import_chart_of_accounts_route(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_accounting_bridge_manage),
) -> dict:
    import csv
    import io
    from app.core.exceptions import ValidationAppError
    
    # التحقق من نوع الملف المرفوع
    if not file.filename.endswith(".csv"):
        raise ValidationAppError("⚠️ يجب أن يكون الملف المرفوع بصيغة CSV فقط.")
        
    content = await file.read()
    try:
        csv_text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            csv_text = content.decode("windows-1256")
        except UnicodeDecodeError:
            raise ValidationAppError("⚠️ ترميز الملف غير مدعوم. يرجى استخدام ترميز UTF-8.")
            
    f = io.StringIO(csv_text)
    reader = csv.DictReader(f)
    
    headers = reader.fieldnames or []
    field_mapping = {}
    
    def clean_header(h: str) -> str:
        return h.strip().lower().replace(" ", "_")
        
    for h in headers:
        cleaned = clean_header(h)
        if cleaned in ["code", "كود_الحساب", "الكود", "كود"]:
            field_mapping["code"] = h
        elif cleaned in ["name", "اسم_الحساب", "الاسم", "اسم"]:
            field_mapping["name"] = h
        elif cleaned in ["account_type", "نوع_الحساب", "النوع", "نوع"]:
            field_mapping["account_type"] = h
        elif cleaned in ["parent_code", "كود_الأب", "الحساب_الأب", "كود_الحساب_الأب", "الأب", "الاب", "كود_الاب"]:
            field_mapping["parent_code"] = h
        elif cleaned in ["allows_posting", "يقبل_الترحيل", "مرحل", "يقبل_الترصيد"]:
            field_mapping["allows_posting"] = h
            
    # التحقق من وجود الأعمدة المطلوبة
    for req in ["code", "name", "account_type"]:
        if req not in field_mapping:
            raise ValidationAppError(f"⚠️ رأس العمود المطلوب '{req}' غير موجود في ملف الـ CSV المرفوع.")
            
    rows = []
    for idx, row in enumerate(reader, start=2):
        code_val = row.get(field_mapping["code"])
        name_val = row.get(field_mapping["name"])
        type_val = row.get(field_mapping["account_type"])
        
        if not code_val or not name_val or not type_val:
            raise ValidationAppError(f"⚠️ الحقول الأساسية (الكود، الاسم، النوع) فارغة في السطر {idx}")
            
        parent_val = None
        if "parent_code" in field_mapping:
            parent_raw = row.get(field_mapping["parent_code"])
            if parent_raw and parent_raw.strip():
                parent_val = parent_raw.strip()
                
        allows_posting_val = False
        if "allows_posting" in field_mapping:
            raw_post = row.get(field_mapping["allows_posting"])
            if raw_post:
                raw_post_str = str(raw_post).strip().lower()
                if raw_post_str in ["true", "1", "نعم", "yes", "y", "t"]:
                    allows_posting_val = True
                    
        rows.append(ChartAccountCSVRow(
            code=code_val.strip(),
            name=name_val.strip(),
            account_type=type_val.strip().lower(),
            parent_code=parent_val,
            allows_posting=allows_posting_val
        ))
        
    import_chart_of_accounts_from_csv(db, rows, current_user.id)
    return {"message": "تم استيراد شجرة الحسابات وتحديث إعدادات الجسور بنجاح."}

