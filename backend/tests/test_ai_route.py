from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.api.routes import ai


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
        registration = test_client.post("/api/v1/auth/register", json={"full_name": "AI Test Owner", "email": "ai@example.com", "password": "test-password-123"})
        test_client.headers.update({"Authorization": f"Bearer {registration.json()['access_token']}"})
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_ai_interpret_endpoint_returns_review_required(client: TestClient, monkeypatch) -> None:
    sample = {
        "transaction_type": "invoice", "party_name": "Frank", "direction": "business_owes_party",
        "invoice_amount": 50000, "amount_paid": 40000, "currency": "NGN", "transaction_date": None,
        "reference": None, "note": "Balance remains unpaid.", "missing_information": ["invoice date"], "ambiguity": [],
    }
    monkeypatch.setattr(ai, "interpret_business_note", lambda note: sample)
    response = client.post("/api/v1/ai/interpret-record", json={"note": "Frank invoice ₦50000, paid ₦40000"})
    assert response.status_code == 200
    body = response.json()
    assert body["saved"] is False
    assert body["review_required"] is True
    assert body["extraction"]["invoice_amount"] == 50000
    assert body["extraction"]["record_type"] == "supplier_invoice"


def test_ai_interpret_endpoint_rejects_short_note(client: TestClient) -> None:
    response = client.post("/api/v1/ai/interpret-record", json={"note": "bad"})
    assert response.status_code == 422


def test_supplier_invoice_requires_business_access_and_persists(client: TestClient) -> None:
    business_response = client.post(
        "/api/v1/businesses",
        json={"name": "Invoice Test Shop", "business_type": "restaurant"},
    )
    assert business_response.status_code == 201, business_response.text
    business = business_response.json()
    response = client.post(
        f"/api/v1/businesses/{business['id']}/supplier-invoices",
        json={
            "supplier": "Musa Supplies",
            "invoice_amount": 50000,
            "amount_paid": 30000,
            "transaction_date": "2026-10-14",
            "reference": "INV-1042",
            "direction": "business_owes_party",
            "note": "Supplier invoice",
            "source_note": "Test note",
        },
    )
    assert response.status_code == 201, response.text
    invoice = response.json()
    assert invoice["supplier"] == "Musa Supplies"
    assert float(invoice["outstanding_amount"]) == 20000

    listed = client.get(f"/api/v1/businesses/{business['id']}/supplier-invoices")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    report = client.get(
        f"/api/v1/businesses/{business['id']}/reports/summary?period=custom&start_date=2026-10-14&end_date=2026-10-14"
    )
    assert report.status_code == 200, report.text
    summary = report.json()["supplier_invoice_summary"]
    assert summary["invoice_count"] == 1
    assert summary["invoice_total"] == 50000
    assert summary["amount_paid"] == 30000
    assert summary["outstanding_balance"] == 20000


def test_business_analysis_uses_calculated_report_and_scopes_business(client: TestClient, monkeypatch) -> None:
    business_response = client.post(
        "/api/v1/businesses",
        json={"name": "Analysis Test Shop", "business_type": "restaurant"},
    )
    assert business_response.status_code == 201, business_response.text
    business_id = business_response.json()["id"]
    monkeypatch.setattr(ai, "analyze_business_question", lambda question, report: f"Analysis for {report['business_name']} with {report['data_quality']['records_in_period']} records.")
    response = client.post(
        f"/api/v1/ai/businesses/{business_id}/analysis",
        json={"question": "Give me a comprehensive analysis for this week", "period": "weekly"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["period"] == "weekly"
    assert "Analysis Test Shop" in payload["answer"]

    denied = client.post(
        "/api/v1/ai/businesses/00000000-0000-0000-0000-000000000000/analysis",
        json={"question": "Summarize this week", "period": "weekly"},
    )
    assert denied.status_code == 404
