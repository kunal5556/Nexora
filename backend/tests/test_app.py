import sqlite3

from fastapi.testclient import TestClient

from app import database
from app.config import settings
from app.main import app

PREFLIGHT_HEADERS = {
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type,x-simulate-failure",
}


def test_health_returns_ok_with_key_count(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["keys_configured"] == 2
    assert body["model"] == "gemini/gemini-3.5-flash-lite"
    assert body["failure_simulation_enabled"] is True


def test_health_reports_cache_enabled(client):
    response = client.get("/health")

    assert response.json()["cache_enabled"] is True


def test_health_returns_503_when_database_is_unreachable(client, monkeypatch):
    monkeypatch.setattr(database, "is_database_reachable", lambda: False)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}


def test_unexpected_error_returns_json_500(tmp_path, monkeypatch):
    def broken_database_check():
        raise RuntimeError("database check crashed")

    monkeypatch.setattr(settings, "database_path", str(tmp_path / "test.db"))
    monkeypatch.setattr(database, "is_database_reachable", broken_database_check)

    with TestClient(app, raise_server_exceptions=False) as error_client:
        response = error_client.get("/health")

    assert response.status_code == 500
    assert response.json() == {"detail": "internal server error"}
    assert "Traceback" not in response.text


def test_cors_allows_configured_origin(client):
    response = client.options("/health", headers={"Origin": "http://localhost:3000", **PREFLIGHT_HEADERS})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_rejects_unknown_origin(client):
    response = client.options("/health", headers={"Origin": "http://evil.example", **PREFLIGHT_HEADERS})

    assert "access-control-allow-origin" not in response.headers


def test_docs_endpoints_are_disabled(client):
    for path in ["/docs", "/redoc", "/openapi.json"]:
        response = client.get(path)
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}


def test_database_schema_is_created_on_startup(client):
    connection = sqlite3.connect(settings.database_path)
    names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'index')")}
    message_columns = [row[1] for row in connection.execute("PRAGMA table_info(messages)")]
    connection.close()

    assert {"messages", "sessions", "idx_messages_session_id"} <= names
    assert message_columns == ["id", "session_id", "role", "content", "metadata", "created_at"]
