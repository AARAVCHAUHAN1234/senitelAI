"""Unit and integration tests for the six innovation modules."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_business_logic_brain(client):
    r = client.get("/api/modules/business_logic_brain/workflows")
    assert r.status_code == 200
    wfs = r.json()["workflows"]
    assert len(wfs) >= 3
    names = {w["name"] for w in wfs}
    assert "Booking" in names
    assert "Refund" in names


def test_attack_chain_intelligence(client):
    r_chains = client.get("/api/modules/attack_chain_intelligence/chains")
    assert r_chains.status_code == 200
    assert len(r_chains.json()) >= 1

    r_paths = client.get("/api/modules/attack_chain_intelligence/paths")
    assert r_paths.status_code == 200
    assert "cypher_query" in r_paths.json()

    r_choke = client.get("/api/modules/attack_chain_intelligence/chokepoints")
    assert r_choke.status_code == 200
    assert len(r_choke.json()["chokepoints"]) >= 2


def test_tenant_role_matrix(client):
    r = client.get("/api/modules/tenant_role_matrix/matrix")
    assert r.status_code == 200
    data = r.json()
    assert data["coverage_pct"] > 0
    assert len(data["cells"]) >= 10
    assert data["mismatches"] >= 1


def test_predictive_impact(client):
    r_changes = client.get("/api/modules/predictive_impact/changes")
    assert r_changes.status_code == 200
    assert len(r_changes.json()) >= 3

    r_graph = client.get("/api/modules/predictive_impact/dependency-graph")
    assert r_graph.status_code == 200
    assert len(r_graph.json()["services"]) >= 4


def test_security_memory(client):
    r_kpis = client.get("/api/modules/security_memory/kpis")
    assert r_kpis.status_code == 200
    assert r_kpis.json()["total_open_findings"] >= 4

    r_trends = client.get("/api/modules/security_memory/remediation-trends")
    assert r_trends.status_code == 200
    assert "averages_hours" in r_trends.json()


def test_safe_attack_sandbox(client):
    r = client.get("/api/modules/safe_attack_sandbox/policy")
    assert r.status_code == 200
    data = r.json()
    assert data["mode"] == "DEMO / SIMULATED"
    assert data["synthetic_data_boundary_active"] is True

    # Test emergency stop and release
    r_stop = client.post("/api/modules/safe_attack_sandbox/emergency-stop")
    assert r_stop.status_code == 200
    assert r_stop.json()["emergency_stop"] is True

    r_release = client.post("/api/modules/safe_attack_sandbox/emergency-release")
    assert r_release.status_code == 200
    assert r_release.json()["emergency_stop"] is False
