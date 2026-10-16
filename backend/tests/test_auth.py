from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def register(client: TestClient, email: str = "owner@example.com") -> dict:
    response = client.post("/api/v1/auth/register", json={"full_name": "Test Owner", "email": email, "password": "test-password-123"})
    assert response.status_code == 201, response.text
    return response.json()


def test_registration_login_profile_and_logout(client: TestClient) -> None:
    created = register(client)
    assert created["user"]["email"] == "owner@example.com"
    assert created["access_token"]
    assert client.get("/api/v1/auth/me").status_code == 401
    client.headers.update({"Authorization": f"Bearer {created['access_token']}"})
    profile = client.get("/api/v1/auth/me")
    assert profile.status_code == 200
    assert profile.json()["full_name"] == "Test Owner"
    updated = client.patch("/api/v1/auth/me", json={"full_name": "Updated Owner"})
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Updated Owner"
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401


def test_duplicate_email_and_invalid_login_are_rejected(client: TestClient) -> None:
    register(client)
    duplicate = client.post("/api/v1/auth/register", json={"full_name": "Other Owner", "email": "OWNER@example.com", "password": "test-password-123"})
    assert duplicate.status_code == 409
    invalid = client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "wrong-password"})
    assert invalid.status_code == 401


def test_businesses_are_isolated_between_users(client: TestClient) -> None:
    first = register(client, "first@example.com")
    client.headers.update({"Authorization": f"Bearer {first['access_token']}"})
    created = client.post("/api/v1/businesses", json={"name": "Private Restaurant", "business_type": "restaurant"})
    assert created.status_code == 201, created.text
    business_id = created.json()["id"]

    second = register(client, "second@example.com")
    client.headers.update({"Authorization": f"Bearer {second['access_token']}"})
    assert client.get(f"/api/v1/businesses/{business_id}").status_code == 404
    assert client.get(f"/api/v1/businesses/{business_id}/templates").status_code == 404
    assert client.get(f"/api/v1/businesses/{business_id}/records").status_code == 404
    assert client.get(f"/api/v1/businesses/{business_id}/reports/summary").status_code == 404
    assert client.get(f"/api/v1/businesses/{business_id}/intelligence/issues").status_code == 404
    assert all(item["id"] != business_id for item in client.get("/api/v1/businesses").json())


def test_business_routes_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/businesses").status_code == 401
    assert client.post("/api/v1/businesses", json={"name": "Private Restaurant", "business_type": "restaurant"}).status_code == 401


def test_password_change_invalidates_existing_sessions(client: TestClient) -> None:
    result = register(client)
    client.headers.update({"Authorization": f"Bearer {result['access_token']}"})
    response = client.post("/api/v1/auth/change-password", json={"current_password": "test-password-123", "new_password": "new-test-password-456"})
    assert response.status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401
    login = client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "new-test-password-456"})
    assert login.status_code == 200
