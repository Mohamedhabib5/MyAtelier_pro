from __future__ import annotations

import logging
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.exceptions import ValidationAppError
from app.modules.accounting.models import ChartOfAccount, AccountingBridgeConfig
from app.modules.accounting.bridge_config_service import (
    ensure_accounting_bridge_configs,
    resolve_bridge_account,
    BRIDGE_KEYS,
)
from app.modules.accounting.service import ensure_accounting_foundation
from app.modules.organization.service import get_company_settings
from .test_foundation import login


def test_bridge_configs_seeded_on_foundation(app_client: TestClient) -> None:
    """
    تتحقق من أن استدعاء تأسيس الحسابات يقوم بزرع الإعدادات الستة الافتراضية للجسور تلقائياً.
    """
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        company = get_company_settings(db)
        
        # التأكد من التأسيس
        ensure_accounting_foundation(db)
        
        # جلب الإعدادات المزروعة
        configs = db.scalars(
            select(AccountingBridgeConfig).where(AccountingBridgeConfig.company_id == company.id)
        ).all()
        
        assert len(configs) == 6
        config_keys = {cfg.bridge_key for cfg in configs}
        assert config_keys == set(BRIDGE_KEYS.keys())
        
        # تحقق من كود الصندوق الرئيسي الافتراضي
        cash_cfg = next(cfg for cfg in configs if cfg.bridge_key == "cash")
        assert cash_cfg.account_code == "1111001"
        assert cash_cfg.label_ar == "الصندوق الرئيسي"


def test_resolve_bridge_account_success(app_client: TestClient) -> None:
    """
    تتحقق من أن دالة حل الجسور ترجع الحساب الصحيح والمطابق لكود التهيئة.
    """
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        company = get_company_settings(db)
        ensure_accounting_foundation(db)
        
        # حل حساب الصندوق
        cash_account = resolve_bridge_account(db, company.id, "cash")
        assert cash_account is not None
        assert isinstance(cash_account, ChartOfAccount)
        assert cash_account.code == "1111001"
        assert cash_account.allows_posting is True


def test_resolve_bridge_account_fallback(app_client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    """
    تتحقق من آلية الـ Fallback المؤقتة: في حال مسح إعداد الجسر من الجدول،
    تقوم الدالة باستخدام الكود الافتراضي الثابت مع تسجيل تحذير (Warning).
    """
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        company = get_company_settings(db)
        ensure_accounting_foundation(db)
        
        # مسح إعداد الصندوق لمحاكاة عدم وجوده
        db.query(AccountingBridgeConfig).filter(
            AccountingBridgeConfig.company_id == company.id,
            AccountingBridgeConfig.bridge_key == "cash"
        ).delete()
        db.flush()
        
        # استدعاء الحل والتحقق من عمل الـ Fallback
        with caplog.at_level(logging.WARNING):
            cash_account = resolve_bridge_account(db, company.id, "cash")
            
        assert cash_account is not None
        assert cash_account.code == "1111001"
        assert any("[Fallback Warning]" in record.message for record in caplog.records)


def test_resolve_bridge_account_errors(app_client: TestClient) -> None:
    """
    تتحقق من حراسات الأمان وصلاحية الحسابات (معطل، تجميعي، غير موجود)
    وأنها ترمي رسائل عربية واضحة.
    """
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        company = get_company_settings(db)
        ensure_accounting_foundation(db)
        
        # 1. حالة: الحساب غير موجود في شجرة الحسابات
        db.query(AccountingBridgeConfig).filter(
            AccountingBridgeConfig.company_id == company.id,
            AccountingBridgeConfig.bridge_key == "cash"
        ).update({"account_code": "9999999"})
        db.flush()
        
        with pytest.raises(ValidationAppError) as exc_info:
            resolve_bridge_account(db, company.id, "cash")
        assert "غير موجود في شجرة الحسابات" in str(exc_info.value)
        
        # 2. حالة: الحساب معطل (is_active = False)
        # إرجاع الكود وتعديل الحساب في الشجرة ليكون معطلاً
        db.query(AccountingBridgeConfig).filter(
            AccountingBridgeConfig.company_id == company.id,
            AccountingBridgeConfig.bridge_key == "cash"
        ).update({"account_code": "1111001"})
        
        db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company.id,
            ChartOfAccount.code == "1111001"
        ).update({"is_active": False})
        db.flush()
        
        with pytest.raises(ValidationAppError) as exc_info2:
            resolve_bridge_account(db, company.id, "cash")
        assert "معطل حالياً" in str(exc_info2.value)
        
        # 3. حالة: الحساب تجميعي لا يقبل الترحيل (allows_posting = False)
        # إعادة تفعيل الحساب وتغيير allows_posting ليكون False
        db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company.id,
            ChartOfAccount.code == "1111001"
        ).update({"is_active": True, "allows_posting": False})
        db.flush()
        
        with pytest.raises(ValidationAppError) as exc_info3:
            resolve_bridge_account(db, company.id, "cash")
        assert "حساب تجميعي ولا يقبل الترحيل" in str(exc_info3.value)
