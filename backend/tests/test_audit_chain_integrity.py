import pytest
from app.modules.core_platform.audit import record_audit, verify_chain_integrity
from app.modules.core_platform.models import AuditLog

pytestmark = pytest.mark.guardrail

def test_audit_hmac_chain_integrity(db_session, setup_company_and_admin):
    # 1. Record an audit log
    admin = setup_company_and_admin["admin_user"]
    log1 = record_audit(
        db_session,
        actor_user_id=admin.id,
        action="test.hmac_1",
        target_type="test",
        target_id="123",
        summary="Test HMAC chain 1"
    )
    db_session.commit()
    
    # 2. Record a second audit log
    log2 = record_audit(
        db_session,
        actor_user_id=admin.id,
        action="test.hmac_2",
        target_type="test",
        target_id="456",
        summary="Test HMAC chain 2"
    )
    db_session.commit()
    
    # Verify chain is intact
    result = verify_chain_integrity(db_session)
    assert result["success"] is True
    
    # 3. Tamper with log1
    log1.action = "tampered.hmac_1"
    db_session.commit()
    
    # Verify chain is broken
    result_tampered = verify_chain_integrity(db_session)
    assert result_tampered["success"] is False
    
    # The recalculation mismatch should happen on log1
    assert any(issue["log_id"] == log1.id for issue in result_tampered["issues"])
