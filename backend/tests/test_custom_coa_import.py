import io
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.accounting.models import ChartOfAccount, JournalEntry, JournalEntryLine
from app.modules.accounting.service import ensure_accounting_foundation
from app.modules.organization.service import get_company_settings
from app.modules.core_platform.models import AuditLog
from .test_foundation import login


def test_api_import_custom_coa_success(app_client: TestClient) -> None:
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        ensure_accounting_foundation(db)
        company = get_company_settings(db)
        
    csv_content = (
        "code,name,account_type,parent_code,allows_posting\n"
        "1000,الأصول,asset,,False\n"
        "1100,الأصول المتداولة,asset,1000,False\n"
        "1110,النقدية وما يعادلها,asset,1100,False\n"
        "1111,الصناديق,cash,1110,False\n"
        "1111001,الصندوق الرئيسي,cash,1111,True\n"
        "2000,الالتزامات,liability,,False\n"
        "2100,الالتزامات المتداولة,liability,2000,False\n"
        "2110,عربون العملاء,liability,2100,True\n"
        "1121001,ذمم العملاء التشغيلي,receivable,1110,True\n"
        "2121001,ذمم الموردين التشغيلي,payable,2100,True\n"
        "4110,إيرادات الخدمات,revenue,,True\n"
        "2200,ضريبة المخرجات,liability,,True\n"
    )
    
    files = {"file": ("chart.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = app_client.post("/api/accounting/chart-of-accounts/import", files=files)
    assert response.status_code == 200, response.text
    assert "تم استيراد شجرة الحسابات وتحديث إعدادات الجسور بنجاح" in response.json()["message"]
    
    with session_factory() as db:
        accounts = db.query(ChartOfAccount).filter_by(company_id=company.id).all()
        # Verify specific accounts were created
        codes = {a.code for a in accounts}
        assert "1111001" in codes
        assert "2110" in codes
        assert "1121001" in codes
        
        # Verify that parent_account_id relationships are correctly set
        acc_1111001 = db.query(ChartOfAccount).filter_by(company_id=company.id, code="1111001").first()
        acc_1111 = db.query(ChartOfAccount).filter_by(company_id=company.id, code="1111").first()
        assert acc_1111001.parent_account_id == acc_1111.id
        assert acc_1111001.level == 5
        
        # Verify Audit Log
        audit = db.query(AuditLog).filter_by(action="accounting.chart_imported").order_by(AuditLog.occurred_at.desc()).first()
        assert audit is not None
        diff_data = json.loads(audit.diff_json or "{}")
        assert diff_data["accounts_count"] == 12


def test_api_import_custom_coa_arabic_headers(app_client: TestClient) -> None:
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    csv_content = (
        "كود الحساب,اسم الحساب,نوع الحساب,كود الأب,يقبل الترحيل\n"
        "1000,الأصول,asset,,False\n"
        "1111001,الصندوق الرئيسي,cash,1000,True\n"
    )
    
    files = {"file": ("chart_ar.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = app_client.post("/api/accounting/chart-of-accounts/import", files=files)
    assert response.status_code == 200, response.text
    
    with session_factory() as db:
        company = get_company_settings(db)
        acc = db.query(ChartOfAccount).filter_by(company_id=company.id, code="1111001").first()
        assert acc is not None
        assert acc.name == "الصندوق الرئيسي"


def test_api_import_custom_coa_duplicate_code_error(app_client: TestClient) -> None:
    login(app_client)
    
    csv_content = (
        "code,name,account_type,parent_code,allows_posting\n"
        "1000,الأصول,asset,,False\n"
        "1000,مكرر الأصول,asset,,False\n"
    )
    
    files = {"file": ("duplicate.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = app_client.post("/api/accounting/chart-of-accounts/import", files=files)
    assert response.status_code == 422
    assert "تكرار في كود الحساب" in response.json()["detail"]


def test_api_import_custom_coa_cycle_error(app_client: TestClient) -> None:
    login(app_client)
    
    csv_content = (
        "code,name,account_type,parent_code,allows_posting\n"
        "1000,الحساب أ,asset,2000,False\n"
        "2000,الحساب ب,asset,1000,False\n"
    )
    
    files = {"file": ("cycle.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = app_client.post("/api/accounting/chart-of-accounts/import", files=files)
    assert response.status_code == 422
    assert "حلقة دائرية" in response.json()["detail"]


def test_api_import_custom_coa_max_depth_error(app_client: TestClient) -> None:
    login(app_client)
    
    csv_content = (
        "code,name,account_type,parent_code,allows_posting\n"
        "1,المستوى 1,asset,,False\n"
        "2,المستوى 2,asset,1,False\n"
        "3,المستوى 3,asset,2,False\n"
        "4,المستوى 4,asset,3,False\n"
        "5,المستوى 5,asset,4,False\n"
        "6,المستوى 6,asset,5,True\n"
    )
    
    files = {"file": ("deep.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = app_client.post("/api/accounting/chart-of-accounts/import", files=files)
    assert response.status_code == 422
    assert "تجاوز الحد الأقصى للمستويات" in response.json()["detail"]


def test_api_import_custom_coa_locked_by_transactions(app_client: TestClient) -> None:
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        ensure_accounting_foundation(db)
        company = get_company_settings(db)
        
        # Create a mock journal entry to lock the chart of accounts
        from app.modules.organization.models import FiscalPeriod
        fp = db.query(FiscalPeriod).filter_by(company_id=company.id, is_active=True).first()
        
        from app.modules.identity.models import User
        admin_user = db.query(User).filter_by(username="admin").first()
        
        acc = db.query(ChartOfAccount).filter_by(company_id=company.id, allows_posting=True).first()
        
        entry = JournalEntry(
            company_id=company.id,
            fiscal_period_id=fp.id,
            entry_number="JV000001",
            entry_date=fp.starts_on,
            status="posted"
        )
        db.add(entry)
        db.flush()
        
        line1 = JournalEntryLine(journal_entry_id=entry.id, account_id=acc.id, line_number=1, debit_amount=100)
        line2 = JournalEntryLine(journal_entry_id=entry.id, account_id=acc.id, line_number=2, credit_amount=100)
        db.add(line1)
        db.add(line2)
        db.commit()
        
    csv_content = (
        "code,name,account_type,parent_code,allows_posting\n"
        "1000,الأصول,asset,,False\n"
    )
    
    files = {"file": ("locked.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = app_client.post("/api/accounting/chart-of-accounts/import", files=files)
    
    assert response.status_code == 422
    assert "لا يمكن استيراد شجرة حسابات مخصصة بعد تسجيل قيود يومية" in response.json()["detail"]
    
    # Clean up entry for potential subsequent tests
    with session_factory() as db:
        db.query(JournalEntryLine).filter(JournalEntryLine.journal_entry_id == entry.id).delete()
        db.query(JournalEntry).filter(JournalEntry.id == entry.id).delete()
        db.commit()
