from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.business import Business, RecordTemplate
from app.models.record_entry import RecordEntry
from app.models import business as _business_models  # noqa: F401
from app.models import record_entry as _record_models  # noqa: F401


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(bind=test_engine, class_=Session, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        registration = test_client.post("/api/v1/auth/register", json={"full_name": "Test Owner", "email": "owner@example.com", "password": "test-password-123"})
        assert registration.status_code == 201, registration.text
        test_client.headers.update({"Authorization": f"Bearer {registration.json()['access_token']}"})
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def create_restaurant(client: TestClient) -> tuple[str, str]:
    response = client.post("/api/v1/businesses", json={"name": "Test Restaurant", "business_type": "restaurant"})
    assert response.status_code == 201
    business_id = response.json()["id"]
    templates = client.get(f"/api/v1/businesses/{business_id}/templates").json()
    sales = next(template for template in templates if template["key"] == "daily_sales")
    return business_id, sales["id"]


def test_create_and_list_records(client: TestClient) -> None:
    business_id, template_id = create_restaurant(client)
    response = client.post(
        f"/api/v1/businesses/{business_id}/templates/{template_id}/records",
        json={"values": {"date": "2026-10-13", "gross_amount": 12500, "payment_method": "cash", "notes": "Lunch"}},
    )
    assert response.status_code == 201, response.text
    created = response.json()
    assert created["values"]["gross_amount"] == 12500
    listing = client.get(f"/api/v1/businesses/{business_id}/records?template_id={template_id}")
    assert listing.status_code == 200
    assert len(listing.json()) == 1
    assert listing.json()[0]["id"] == created["id"]


def test_required_fields_and_unknown_fields_are_rejected(client: TestClient) -> None:
    business_id, template_id = create_restaurant(client)
    missing = client.post(
        f"/api/v1/businesses/{business_id}/templates/{template_id}/records",
        json={"values": {"date": "2026-10-13", "payment_method": "cash"}},
    )
    assert missing.status_code == 422
    unknown = client.post(
        f"/api/v1/businesses/{business_id}/templates/{template_id}/records",
        json={"values": {"date": "2026-10-13", "gross_amount": 10, "payment_method": "cash", "unapproved": "x"}},
    )
    assert unknown.status_code == 422


def test_select_values_are_validated(client: TestClient) -> None:
    business_id, template_id = create_restaurant(client)
    response = client.post(
        f"/api/v1/businesses/{business_id}/templates/{template_id}/records",
        json={"values": {"date": "2026-10-13", "gross_amount": 10, "payment_method": "bitcoin"}},
    )
    assert response.status_code == 422


def test_update_and_delete_record(client: TestClient) -> None:
    business_id, template_id = create_restaurant(client)
    created = client.post(
        f"/api/v1/businesses/{business_id}/templates/{template_id}/records",
        json={"values": {"date": "2026-10-13", "gross_amount": 100, "payment_method": "cash"}},
    ).json()
    record_id = created["id"]
    updated = client.patch(
        f"/api/v1/businesses/{business_id}/records/{record_id}",
        json={"values": {"gross_amount": 250, "notes": "Corrected"}},
    )
    assert updated.status_code == 200
    assert updated.json()["values"]["gross_amount"] == 250
    assert updated.json()["values"]["notes"] == "Corrected"
    deleted = client.delete(f"/api/v1/businesses/{business_id}/records/{record_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/businesses/{business_id}/records/{record_id}").status_code == 404


def test_business_isolation_and_template_ownership(client: TestClient) -> None:
    business_id, template_id = create_restaurant(client)
    other = client.post("/api/v1/businesses", json={"name": "Other Restaurant", "business_type": "restaurant"}).json()
    foreign_template = client.post(
        f"/api/v1/businesses/{other['id']}/templates/{template_id}/records",
        json={"values": {"date": "2026-10-13", "gross_amount": 1, "payment_method": "cash"}},
    )
    assert foreign_template.status_code == 404
    created = client.post(
        f"/api/v1/businesses/{business_id}/templates/{template_id}/records",
        json={"values": {"date": "2026-10-13", "gross_amount": 1, "payment_method": "cash"}},
    ).json()
    foreign_read = client.get(f"/api/v1/businesses/{other['id']}/records/{created['id']}")
    assert foreign_read.status_code == 404
