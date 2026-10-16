from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import business as _business_models  # noqa: F401 - register model metadata


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


def test_lists_only_supported_business_types(client: TestClient) -> None:
    response = client.get("/api/v1/business-types")
    assert response.status_code == 200
    assert [item["key"] for item in response.json()] == ["restaurant", "supermarket", "trucking", "contractor", "hotel", "farm", "rental_property", "school", "salon", "training", "pharmacy"]


def test_creating_restaurant_provisions_restaurant_templates(client: TestClient) -> None:
    response = client.post(
        "/api/v1/businesses",
        json={"name": "  The   Green Plate ", "business_type": "restaurant"},
    )
    assert response.status_code == 201
    business = response.json()
    assert business["name"] == "The Green Plate"
    assert business["business_type"] == "restaurant"
    assert business["currency"] == "NGN"

    templates_response = client.get(f"/api/v1/businesses/{business['id']}/templates")
    assert templates_response.status_code == 200
    templates = templates_response.json()
    assert len(templates) == 6
    assert {template["key"] for template in templates} == {
        "daily_sales", "purchases", "stock_movements", "waste", "expenses", "payments"
    }


def test_creating_supermarket_provisions_supermarket_templates(client: TestClient) -> None:
    response = client.post(
        "/api/v1/businesses",
        json={"name": "Corner Market", "business_type": "supermarket", "currency": "ngn"},
    )
    assert response.status_code == 201
    business = response.json()
    assert business["currency"] == "NGN"

    templates_response = client.get(f"/api/v1/businesses/{business['id']}/templates")
    assert templates_response.status_code == 200
    templates = templates_response.json()
    assert len(templates) == 8
    assert {template["key"] for template in templates} == {
        "products", "sales", "supplier_orders", "deliveries", "returns", "stock_counts", "expenses", "supplier_payments"
    }


def test_creating_trucking_business_provisions_trucking_templates(client: TestClient) -> None:
    response = client.post(
        "/api/v1/businesses",
        json={"name": "Northstar Logistics", "business_type": "trucking"},
    )
    assert response.status_code == 201, response.text
    business = response.json()
    assert business["business_type"] == "trucking"

    templates_response = client.get(f"/api/v1/businesses/{business['id']}/templates")
    assert templates_response.status_code == 200, templates_response.text
    templates = {template["key"]: template for template in templates_response.json()}
    assert set(templates) == {"trips", "fleet", "trip_expenses", "payments", "maintenance", "drivers"}
    assert {field["key"] for field in templates["trips"]["fields"]} >= {
        "date", "reference", "customer", "driver", "truck_registration",
        "pickup_location", "delivery_location", "amount", "amount_paid", "payment_status"
    }
    assert {field["key"] for field in templates["maintenance"]["fields"]} >= {
        "truck_registration", "service_type", "next_service_date", "amount"
    }


def test_invalid_business_type_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/businesses",
        json={"name": "A Bakery", "business_type": "bakery"},
    )
    assert response.status_code == 422


def test_unknown_business_returns_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/businesses/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Business not found."


@pytest.mark.parametrize("business_type,minimum_templates", [("contractor", 3), ("hotel", 3), ("rental_property", 3), ("school", 3), ("salon", 3), ("training", 3), ("pharmacy", 3)])
def test_new_template_business_types_provision_templates(client: TestClient, business_type: str, minimum_templates: int) -> None:
    response = client.post("/api/v1/businesses", json={"name": f"Test {business_type}", "business_type": business_type})
    assert response.status_code == 201, response.text
    templates = client.get(f"/api/v1/businesses/{response.json()['id']}/templates")
    assert templates.status_code == 200
    assert len(templates.json()) >= minimum_templates


def test_farm_includes_only_selected_modules(client: TestClient) -> None:
    response = client.post("/api/v1/businesses", json={"name": "Mixed Farm", "business_type": "farm", "farm_modules": ["crops", "poultry"]})
    assert response.status_code == 201, response.text
    templates = client.get(f"/api/v1/businesses/{response.json()['id']}/templates").json()
    keys = {item["key"] for item in templates}
    assert {"farm_overview", "farm_cashbook", "crop_cycles", "crop_inputs", "flock_register", "poultry_feed_eggs"} <= keys
    assert "livestock_register" not in keys
    assert "livestock_health_feed" not in keys


def test_farm_without_selected_modules_has_only_shared_templates(client: TestClient) -> None:
    response = client.post("/api/v1/businesses", json={"name": "Basic Farm", "business_type": "farm"})
    assert response.status_code == 201, response.text
    templates = client.get(f"/api/v1/businesses/{response.json()['id']}/templates").json()
    assert {item["key"] for item in templates} == {"farm_overview", "farm_cashbook"}


def test_country_currency_and_timezone_are_selected_from_country(client: TestClient) -> None:
    response = client.post("/api/v1/businesses", json={"name":"Tokyo Shop", "business_type":"supermarket", "country":"JP", "currency":"JPY", "timezone":"Asia/Tokyo"})
    assert response.status_code == 201, response.text
    assert response.json()["country"] == "JP"
    assert response.json()["currency"] == "JPY"
    assert response.json()["timezone"] == "Asia/Tokyo"

def test_currency_cannot_change_after_record_exists(client: TestClient) -> None:
    created = client.post("/api/v1/businesses", json={"name":"Currency Lock", "business_type":"restaurant", "country":"NG", "currency":"NGN", "timezone":"Africa/Lagos"})
    assert created.status_code == 201, created.text
    business = created.json()
    templates = client.get(f"/api/v1/businesses/{business['id']}/templates").json()
    daily_sales = next(template for template in templates if template["key"] == "daily_sales")
    values = {"date": "2026-10-16", "gross_amount": 100, "payment_method": "cash", "notes": "currency lock test"}
    record = client.post(f"/api/v1/businesses/{business['id']}/templates/{daily_sales['id']}/records", json={"values":values})
    assert record.status_code == 201, record.text
    changed = client.patch(f"/api/v1/businesses/{business['id']}/settings", json={"country":"GB", "currency":"GBP", "timezone":"Europe/London"})
    assert changed.status_code == 409, changed.text
