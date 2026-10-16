from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import business as _business_models  # noqa: F401
from app.models import record_entry as _record_models  # noqa: F401


def _client():
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
    client = TestClient(app)
    registration = client.post("/api/v1/auth/register", json={"full_name": "Test Owner", "email": "owner@example.com", "password": "test-password-123"})
    assert registration.status_code == 201, registration.text
    client.headers.update({"Authorization": f"Bearer {registration.json()['access_token']}"})
    return client, engine


def test_intelligence_flags_stock_variance_and_duplicate_records():
    client, engine = _client()
    try:
        business = client.post("/api/v1/businesses", json={"name": "Intelligence Market", "business_type": "supermarket"}).json()
        bid = business["id"]
        templates = client.get(f"/api/v1/businesses/{bid}/templates").json()
        ids = {item["key"]: item["id"] for item in templates}

        for _ in range(2):
            response = client.post(
                f"/api/v1/businesses/{bid}/templates/{ids['sales']}/records",
                json={"values": {"date": "2026-10-14", "sku": "RICE-1", "quantity": 2, "amount": 5000, "payment_method": "cash"}},
            )
            assert response.status_code == 201, response.text

        stock = client.post(
            f"/api/v1/businesses/{bid}/templates/{ids['stock_counts']}/records",
            json={"values": {"date": "2026-10-14", "product": "Rice", "expected_quantity": 20, "counted_quantity": 17}},
        )
        assert stock.status_code == 201, stock.text

        result = client.get(f"/api/v1/businesses/{bid}/intelligence/issues")
        assert result.status_code == 200, result.text
        data = result.json()
        kinds = {issue["type"] for issue in data["issues"]}
        assert "possible_duplicate" in kinds
        assert "stock_variance" in kinds
        variance = next(issue for issue in data["issues"] if issue["type"] == "stock_variance")
        assert variance["evidence"]["variance"] == "-3"
        assert data["summary"]["total"] == len(data["issues"])
    finally:
        app.dependency_overrides.clear()
        client.close()
        engine.dispose()


def test_intelligence_unknown_business_returns_404():
    client, engine = _client()
    try:
        response = client.get("/api/v1/businesses/00000000-0000-0000-0000-000000000000/intelligence/issues")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        client.close()
        engine.dispose()
