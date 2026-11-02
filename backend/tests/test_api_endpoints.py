"""
Integration Tests for FastAPI Endpoints.
Uses TestClient to verify the full HTTP request/response lifecycle.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.routers.policies import ensure_default_policies

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    ensure_default_policies(db)
    db.close()
    yield

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_policies_and_default_seed():
    response = client.get("/api/policies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    names = [p["name"] for p in data]
    assert any("Demo Policy" in name or "Section 7" in name for name in names)

def test_run_section_7_demo_endpoint():
    response = client.post("/api/demo/run")
    assert response.status_code == 201
    data = response.json()
    assert data["total_billed"] == 150000.0
    assert data["total_estimated_payable"] == 108000.0
    assert data["total_estimated_shortfall"] == 42000.0
    assert len(data["items"]) == 5
    assert data["total_billed"] == data["total_estimated_payable"] + data["total_estimated_shortfall"]

def test_get_dashboard_stats():
    response = client.get("/api/audits/dashboard/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_audits_count"] >= 1
    assert stats["total_billed_volume"] >= 150000.0
    assert stats["total_estimated_payable_volume"] >= 108000.0
    assert len(stats["recent_audits"]) >= 1

def test_download_pdf_report():
    list_resp = client.get("/api/audits")
    assert list_resp.status_code == 200
    audits = list_resp.json()
    assert len(audits) >= 1
    audit_id = audits[0]["id"]

    pdf_resp = client.get(f"/api/audits/{audit_id}/report-pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 1000
    assert pdf_resp.content.startswith(b"%PDF")

