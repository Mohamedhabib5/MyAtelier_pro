import pytest
from .test_foundation import login


@pytest.mark.guardrail
def test_download_endpoint_requires_authentication(app_client):
    """C6 regression: /download/{ticket_id} يجب أن يتطلب مصادقة."""
    response = app_client.get("/api/exports/download/any-fake-ticket-id")
    # Should require login, returning 401 Unauthorized
    assert response.status_code == 401


def test_download_ticket_owned_by_other_user_rejected(app_client):
    """C6 regression: تنزيل تذكرة مستخدم آخر يجب أن يُرفض."""
    # 1. Login as admin
    login(app_client)

    # 2. Generate download ticket
    response = app_client.post("/api/exports/tickets?target_path=/api/exports/customers.xlsx")
    assert response.status_code == 200
    ticket_id = response.json()["ticket"]

    # 3. Create a second client to login as regular user and try to consume ticket
    # Wait, instead of a second client, we logout and login as another user
    app_client.post("/api/auth/logout")

    # Create and login as team.user
    login_admin = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_admin.status_code == 200
    create_user = app_client.post(
        "/api/users",
        json={
            "username": "other.user",
            "full_name": "Other User",
            "password": "secret123",
            "role_names": ["admin"],
        },
    )
    assert create_user.status_code == 201
    app_client.post("/api/auth/logout")

    login(app_client, username="other.user", password="secret123")

    # Try consuming the ticket owned by admin
    consume_response = app_client.get(f"/api/exports/download/{ticket_id}")
    assert consume_response.status_code == 403
    assert "belong to current user" in consume_response.json()["detail"]


def test_ticket_store_works_with_redis():
    """C6 regression: ticket_store should create and consume tickets correctly."""
    from app.modules.exports.ticket_service import ticket_store
    
    ticket_id = ticket_store.create_ticket(
        user_id="user-123",
        path="/api/exports/customers.xlsx",
        params={"branch_id": "b1"}
    )
    assert ticket_id is not None
    
    ticket = ticket_store.consume_ticket(ticket_id)
    assert ticket is not None
    assert ticket["user_id"] == "user-123"
    assert ticket["path"] == "/api/exports/customers.xlsx"
    assert ticket["params"]["branch_id"] == "b1"
    
    # Second consume should return None (single-use)
    assert ticket_store.consume_ticket(ticket_id) is None
