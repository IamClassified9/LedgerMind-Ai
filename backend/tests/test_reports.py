from collections.abc import Generator
from datetime import date
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import business as _business_models  # noqa: F401
from app.models import record_entry as _record_models  # noqa: F401


def _client() -> tuple[TestClient, object]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    registration = client.post("/api/v1/auth/register", json={"full_name": "Test Owner", "email": "owner@example.com", "password": "test-password-123"})
    assert registration.status_code == 201, registration.text
    client.headers.update({"Authorization": f"Bearer {registration.json()['access_token']}"})
    return client, engine


def test_reporting_periods_and_totals() -> None:
    client, engine = _client()
    try:
        business = client.post("/api/v1/businesses", json={"name": "Report Restaurant", "business_type": "restaurant"}).json()
        bid = business["id"]
        templates = client.get(f"/api/v1/businesses/{bid}/templates").json()
        ids = {template["key"]: template["id"] for template in templates}

        for template_key, values in [
            ("daily_sales", {"date": "2026-10-13", "gross_amount": 12500, "payment_method": "cash"}),
            ("daily_sales", {"date": "2026-10-12", "gross_amount": 7500, "payment_method": "transfer"}),
            ("expenses", {"date": "2026-10-13", "category": "utilities", "amount": 1500}),
            ("purchases", {"date": "2026-10-13", "supplier": "Supplier A", "item": "Rice", "quantity": 2, "amount": 3000}),
            ("payments", {"date": "2026-10-13", "direction": "incoming", "amount": 10000}),
        ]:
            response = client.post(
                f"/api/v1/businesses/{bid}/templates/{ids[template_key]}/records",
                json={"values": values},
            )
            assert response.status_code == 201, response.text

        report = client.get(f"/api/v1/businesses/{bid}/reports/summary?period=custom&start_date=2026-10-13&end_date=2026-10-13")
        assert report.status_code == 200, report.text
        payload = report.json()
        assert payload["totals"]["sales_revenue"] == 12500
        assert payload["totals"]["operating_expenses"] == 1500
        assert payload["totals"]["purchases"] == 3000
        assert payload["totals"]["recorded_incoming_payments"] == 10000
        assert payload["reconciliation"]["sales_minus_incoming_payments"] == 2500
        assert payload["counts"]["sales_records"] == 1
        assert payload["supplier_invoice_summary"]["invoice_count"] == 0
        assert payload["supplier_invoice_summary"]["outstanding_balance"] == 0

        for period in ("daily", "weekly", "monthly", "yearly"):
            response = client.get(f"/api/v1/businesses/{bid}/reports/summary?period={period}")
            assert response.status_code == 200, response.text
            assert response.json()["period"] == period

        bad_range = client.get(f"/api/v1/businesses/{bid}/reports/summary?period=custom&start_date=2026-10-14&end_date=2026-10-13")
        assert bad_range.status_code == 422
    finally:
        app.dependency_overrides.clear()
        client.close()
        engine.dispose()


def test_unknown_business_report_returns_404() -> None:
    client, engine = _client()
    try:
        response = client.get("/api/v1/businesses/00000000-0000-0000-0000-000000000000/reports/summary")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        client.close()
        engine.dispose()


def test_calendar_comparison_boundaries() -> None:
    client, engine = _client()
    try:
        business = client.post(
            "/api/v1/businesses",
            json={"name": "Calendar Boundary Test", "business_type": "restaurant"},
        ).json()
        bid = business["id"]

        monthly = client.get(
            f"/api/v1/businesses/{bid}/reports/summary?period=monthly"
        ).json()
        assert monthly["start_date"] == "2026-10-01"
        assert monthly["end_date"] == "2026-10-31"
        assert monthly["comparison_to_previous_period"]["start_date"] == "2026-09-01"
        assert monthly["comparison_to_previous_period"]["end_date"] == "2026-09-30"

        custom = client.get(
            f"/api/v1/businesses/{bid}/reports/summary"
            "?period=custom&start_date=2026-10-10&end_date=2026-10-13"
        ).json()
        assert custom["comparison_to_previous_period"]["start_date"] == "2026-10-06"
        assert custom["comparison_to_previous_period"]["end_date"] == "2026-10-09"
    finally:
        app.dependency_overrides.clear()
        client.close()
        engine.dispose()
