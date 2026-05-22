import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.accounting.models import ChartOfAccount, AccountingBridgeConfig
from app.modules.accounting.service import ensure_accounting_foundation
from app.modules.organization.service import get_company_settings
from app.modules.core_platform.models import AuditLog
from .test_foundation import login



def test_api_get_bridge_configs(app_client: TestClient) -> None:
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        ensure_accounting_foundation(db)
        
    response = app_client.get("/api/accounting/bridge-configs")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 6
    for item in data:
        assert "bridge_key" in item
        assert "account_code" in item
        assert "label_ar" in item
        assert "label_en" in item
        assert "account_name" in item


def test_api_update_bridge_config_success(app_client: TestClient) -> None:
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        ensure_accounting_foundation(db)
        company = get_company_settings(db)
        
    payload = {"account_code": "1112001"}
    response = app_client.patch("/api/accounting/bridge-configs/cash", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["account_code"] == "1112001"
    assert data["bridge_key"] == "cash"
    
    # Verify in DB and Audit Log
    with session_factory() as db:
        cfg = db.query(AccountingBridgeConfig).filter_by(company_id=company.id, bridge_key="cash").first()
        assert cfg.account_code == "1112001"
        
        audit = db.query(AuditLog).filter_by(action="accounting.bridge_config_updated").order_by(AuditLog.occurred_at.desc()).first()
        assert audit is not None
        diff_data = json.loads(audit.diff_json or "{}")
        assert diff_data["old_value"] == "1111001"
        assert diff_data["new_value"] == "1112001"


def test_api_update_bridge_config_validation_errors(app_client: TestClient) -> None:
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        ensure_accounting_foundation(db)
        company = get_company_settings(db)
        
    # 1. Non-existent account
    response = app_client.patch("/api/accounting/bridge-configs/cash", json={"account_code": "9999999"})
    assert response.status_code == 422
    assert "غير موجود في شجرة الحسابات" in response.json()["detail"]
    
    # 2. Inactive account
    with session_factory() as db:
        db.query(ChartOfAccount).filter_by(company_id=company.id, code="1112001").update({"is_active": False})
        db.commit()
        
    response = app_client.patch("/api/accounting/bridge-configs/cash", json={"account_code": "1112001"})
    assert response.status_code == 422
    assert "معطل حالياً" in response.json()["detail"]
    
    # Reset active state
    with session_factory() as db:
        db.query(ChartOfAccount).filter_by(company_id=company.id, code="1112001").update({"is_active": True})
        db.commit()

    # 3. Summation account (not posting-eligible)
    response = app_client.patch("/api/accounting/bridge-configs/cash", json={"account_code": "1110"})
    assert response.status_code == 422
    assert "حساب تجميعي ولا يقبل الترحيل" in response.json()["detail"]


def test_api_reset_bridge_config(app_client: TestClient) -> None:
    login(app_client)
    session_factory = app_client.app.state.session_factory
    
    with session_factory() as db:
        ensure_accounting_foundation(db)
        company = get_company_settings(db)
        db.query(AccountingBridgeConfig).filter_by(company_id=company.id, bridge_key="cash").update({"account_code": "1112001"})
        db.commit()
        
    response = app_client.post("/api/accounting/bridge-configs/cash/reset")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["account_code"] == "1111001"
    
    with session_factory() as db:
        cfg = db.query(AccountingBridgeConfig).filter_by(company_id=company.id, bridge_key="cash").first()
        assert cfg.account_code == "1111001"
        
        audit = db.query(AuditLog).filter_by(action="accounting.bridge_config_reset").order_by(AuditLog.occurred_at.desc()).first()
        assert audit is not None
        diff_data = json.loads(audit.diff_json or "{}")
        assert diff_data["old_value"] == "1112001"
        assert diff_data["new_value"] == "1111001"


def test_api_bridge_configs_permissions(app_client: TestClient) -> None:
    login(app_client)
    create_response = app_client.post(
        "/api/users",
        json={
            "username": "regular.user",
            "full_name": "Regular User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_response.status_code == 201
    
    app_client.post("/api/auth/logout")
    login(app_client, username="regular.user", password="secret123")
    
    response_get = app_client.get("/api/accounting/bridge-configs")
    assert response_get.status_code == 200
    
    response_patch = app_client.patch("/api/accounting/bridge-configs/cash", json={"account_code": "1112001"})
    assert response_patch.status_code == 403
    
    response_reset = app_client.post("/api/accounting/bridge-configs/cash/reset")
    assert response_reset.status_code == 403
