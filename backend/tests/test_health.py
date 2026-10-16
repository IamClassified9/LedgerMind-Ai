from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_identifies_service() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "LedgerMind AI"


def test_liveness_does_not_require_database() -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ledgermind-api"}


def test_openapi_is_available() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "LedgerMind AI" in response.json()["info"]["title"]
