from __future__ import annotations

from fastapi.testclient import TestClient

from .test_foundation import login


def test_login_accepts_language_override(app_client: TestClient) -> None:
    response = app_client.post("/api/auth/login", json={"username": "admin", "password": "admin123", "language": "en"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["preferred_language"] == "ar"
    assert payload["session_language"] == "en"
    assert payload["effective_language"] == "en"

    me_response = app_client.get("/api/auth/me")
    assert me_response.status_code == 200
    me_payload = me_response.json()
    assert me_payload["session_language"] == "en"
    assert me_payload["effective_language"] == "en"


def test_session_language_can_change_after_login(app_client: TestClient) -> None:
    login(app_client)

    response = app_client.post("/api/auth/language", json={"language": "en"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["preferred_language"] == "ar"
    assert payload["session_language"] == "en"
    assert payload["effective_language"] == "en"

    me_response = app_client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["effective_language"] == "en"


def test_preferred_language_is_used_for_next_login(app_client: TestClient) -> None:
    login(app_client)

    create_response = app_client.post(
        "/api/users",
        json={
            "username": "lang.user",
            "full_name": "Language User",
            "password": "secret123",
            "role_names": ["user"],
        },
    )
    assert create_response.status_code == 201, create_response.text

    app_client.post("/api/auth/logout")
    login(app_client, username="lang.user", password="secret123")

    update_response = app_client.patch("/api/users/me", json={"preferred_language": "en"})
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["preferred_language"] == "en"

    app_client.post("/api/auth/logout")
    relogin_response = app_client.post("/api/auth/login", json={"username": "lang.user", "password": "secret123"})
    assert relogin_response.status_code == 200, relogin_response.text
    relogin_payload = relogin_response.json()
    assert relogin_payload["preferred_language"] == "en"
    assert relogin_payload["session_language"] == "en"
    assert relogin_payload["effective_language"] == "en"
