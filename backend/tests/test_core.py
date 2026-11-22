"""Integration tests for SentinelAI core platform."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["mode"] == "DEMO / SIMULATED"


def test_dashboard_metrics(client):
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "metrics" in data
    assert data["metrics"]["total_apis"] >= 10
    assert data["metrics"]["vulnerabilities"] >= 4
    assert len(data["severity"]) == 5
    assert len(data["activity"]) >= 1


def test_apis_catalog(client):
    resp = client.get("/api/apis")
    assert resp.status_code == 200
    apis = resp.json()
    assert len(apis) >= 10
    categories = {a["category"] for a in apis}
    assert "Active" in categories
    assert "Zombie" in categories
    assert "Shadow" in categories


def test_openapi_export(client):
    resp = client.get("/api/apis/openapi")
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["openapi"] == "3.1.0"
    assert "paths" in doc


def test_findings_list_and_verification(client):
    resp = client.get("/api/findings")
    assert resp.status_code == 200
    findings = resp.json()
    assert len(findings) >= 4
    first_id = findings[0]["id"]

    # Verify endpoint
    v_resp = client.post(f"/api/findings/{first_id}/verify")
    assert v_resp.status_code == 200
    assert v_resp.json()["status"] == "Verified"


def test_agent_control(client):
    resp = client.get("/api/agents")
    assert resp.status_code == 200
    agents = resp.json()
    assert len(agents) == 13

    # Scan control
    pause_resp = client.post("/api/scan/pause")
    assert pause_resp.status_code == 200
    resume_resp = client.post("/api/scan/resume")
    assert resume_resp.status_code == 200


def test_graph_topology(client):
    resp = client.get("/api/graph/topology?view=architecture")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["nodes"]) >= 15
    assert len(data["edges"]) >= 10


def test_demo_scenarios(client):
    resp = client.get("/api/demo/scenarios")
    assert resp.status_code == 200
    scenarios = resp.json()
    assert len(scenarios) == 6


def test_audit_logs(client):
    resp = client.get("/api/audit")
    assert resp.status_code == 200
    logs = resp.json()
    assert isinstance(logs, list)
