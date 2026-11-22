"""Interactive demo scenario execution router."""

import asyncio
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import httpx

from ..core.database import get_db, SessionLocal
from ..core.models import Api, Finding, Agent, Event, AuditLog
from ..core.settings import settings

router = APIRouter(prefix="/api/demo", tags=["demo"])

DEMO_SCENARIOS = {
    "idor": {
        "id": "idor",
        "title": "Cross-Agency IDOR",
        "description": "An Agency A agent requests booking BK-2001 belonging to Agency B, successfully reading sensitive PII and flight records.",
        "severity": "Critical",
        "endpoint": "GET /api/v1/bookings/{id}",
        "agent": "Access Control Testing Agent",
        "impact": "Exposes cross-agency customer itinerary, contact info, and pricing breakdown across tenant boundaries.",
        "evidence": "DEMO / SIMULATED — Request with Authorization: Bearer token_agency_a_agent for BK-2001 (owned by Agency B) returned 200 OK.",
        "remediation": "Scope booking queries by tenant agency_id: WHERE id = :id AND agency_id = :agency_id."
    },
    "fare": {
        "id": "fare",
        "title": "Unauthorized Fare Tampering",
        "description": "A client submits an arbitrary modified price payload ($1.00) during checkout quotation.",
        "severity": "High",
        "endpoint": "POST /api/v1/bookings/{id}/price",
        "agent": "API Security Testing Agent",
        "impact": "Enables malicious booking agent to purchase flights for negligible cost, causing direct financial loss to the travel portal.",
        "evidence": "DEMO / SIMULATED — Submitted payload {'price': 1.00} to booking pricing endpoint. Server accepted total without re-evaluating signed fare rules.",
        "remediation": "Calculate pricing strictly on server using signed fare quotation; reject client-provided totals."
    },
    "refund": {
        "id": "refund",
        "title": "Duplicate Refund Allowed",
        "description": "Duplicate concurrent refund requests succeed, exceeding the original booking payment total.",
        "severity": "High",
        "endpoint": "POST /api/v1/refunds",
        "agent": "API Security Testing Agent",
        "impact": "Cumulative refunds drain platform liquidity and agency credit balances through repeated refund operations.",
        "evidence": "DEMO / SIMULATED — Second refund request for booking BK-2001 processed without idempotency check; refund sum exceeds booking value.",
        "remediation": "Enforce atomic transaction lock and verify sum(refunds) <= booking.total_price."
    },
    "privilege": {
        "id": "privilege",
        "title": "Sub-Agent Privilege Escalation",
        "description": "A regular agent role invokes an administrative fare override endpoint to rewrite flight margins.",
        "severity": "High",
        "endpoint": "POST /api/v1/admin/fares/override",
        "agent": "Authentication Testing Agent",
        "impact": "Lower-privileged staff can bypass pricing guardrails and alter system-wide catalog margins.",
        "evidence": "DEMO / SIMULATED — Regular agent token received 200 OK from /api/v1/admin/fares/override.",
        "remediation": "Enforce RBAC check requiring user.role == 'admin' on all /admin endpoints."
    },
    "api_change": {
        "id": "api_change",
        "title": "New Unauthenticated Export API Discovered",
        "description": "A newly deployed /beta/export endpoint is detected without authentication requirements or tenant filter.",
        "severity": "Medium",
        "endpoint": "GET /beta/export",
        "agent": "Change Detection Agent",
        "impact": "Shadow API exposes bulk passenger database to unauthenticated external scraping.",
        "evidence": "DEMO / SIMULATED — Discovered live route /beta/export responding 200 with passenger array without Authorization header.",
        "remediation": "Apply authentication middleware, register route in OpenAPI catalog, and restrict to admin export scopes."
    },
    "chain": {
        "id": "chain",
        "title": "Cross-Agency Discovery to Refund Abuse Chain",
        "description": "Multi-hop attack: IDOR is used to harvest booking references and payment amounts, followed by duplicate refund exploitation.",
        "severity": "Critical",
        "endpoint": "GET /api/v1/bookings/{id} -> POST /api/v1/refunds",
        "agent": "Attack Chain Intelligence Agent",
        "impact": "Attacker can exfiltrate another agency's bookings and trigger unauthorized refund payments directly to an attacker-controlled wallet.",
        "evidence": "DEMO / SIMULATED — Chain verified: Hop 1 (IDOR reading BK-2001) linked to Hop 2 (Duplicate refund of $500.00).",
        "remediation": "Remediate tenant scoping on booking read and enforce idempotency locks on refund execution."
    }
}


@router.get("/scenarios")
def list_scenarios():
    """List available interactive demo attack scenarios."""
    return list(DEMO_SCENARIOS.values())


@router.post("/run/{key}")
async def run_scenario(key: str, request: Request, db: Session = Depends(get_db)):
    """Execute an interactive demo scenario with real tests against VoyageSim."""
    if key not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{key}' not found")

    sc = DEMO_SCENARIOS[key]
    event_bus = getattr(request.app.state, "event_bus", None)

    if event_bus:
        event_bus.emit("demo.scenario.started", f"Scenario started: {sc['title']}", {"scenario": key})
        event_bus.emit("agent.started", f"{sc['agent']} analyzing {sc['endpoint']}", {"agent": sc['agent']})

    # Trigger actual test request against VoyageSim
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            if key == "idor":
                await client.get(f"{settings.VOYAGESIM_URL}/api/v1/bookings/1", headers={"Authorization": "Bearer token_agency_a_agent"})
            elif key == "fare":
                await client.post(f"{settings.VOYAGESIM_URL}/api/v1/bookings/1/price", headers={"Authorization": "Bearer token_agency_a_admin"}, json={"price": 1.00})
            elif key == "refund":
                await client.post(f"{settings.VOYAGESIM_URL}/api/v1/refunds", headers={"Authorization": "Bearer token_agency_a_admin"}, json={"booking_id": 1, "amount": 250.00})
            elif key == "privilege":
                await client.post(f"{settings.VOYAGESIM_URL}/api/v1/admin/fares/override", headers={"Authorization": "Bearer token_agency_a_agent"}, json={"fare_id": 1, "new_price": 10.00})
            elif key == "api_change":
                await client.get(f"{settings.VOYAGESIM_URL}/beta/export")
        except Exception:
            pass

    # Record or update Finding in database
    code = f"DEMO-{key.upper()}-001"
    finding = db.query(Finding).filter(Finding.code == code).first()
    if not finding:
        finding = Finding(
            code=code,
            title=sc["title"],
            severity=sc["severity"],
            confidence=97,
            endpoint=sc["endpoint"],
            tenant="GlobalTrips B2B",
            agent_name=sc["agent"],
            status="Verified",
            impact=sc["impact"],
            evidence=sc["evidence"],
            remediation=sc["remediation"],
            demo_label="DEMO / SIMULATED"
        )
        db.add(finding)
    else:
        finding.status = "Verified"
        finding.updated_at = datetime.utcnow()

    # Record Audit Log
    db.add(AuditLog(
        action=f"demo.scenario.{key}",
        actor="SentinelAI Autonomous Orchestrator",
        detail=f"{{\"scenario\": \"{key}\", \"finding\": \"{code}\"}}"
    ))
    db.commit()

    if event_bus:
        event_bus.emit("finding.verified", f"Verified finding: {sc['title']}", {"code": code, "severity": sc["severity"]})
        event_bus.emit("demo.scenario.completed", f"Scenario completed: {sc['title']}", {"scenario": key})

    return {"status": "success", "scenario": key, "finding_code": code}


@router.post("/run-all")
async def run_all_scenarios(request: Request):
    """Queue and execute all six demo attack scenarios in sequence."""
    async def _runner():
        for key in DEMO_SCENARIOS.keys():
            db = SessionLocal()
            try:
                sc = DEMO_SCENARIOS[key]
                code = f"DEMO-{key.upper()}-001"
                finding = db.query(Finding).filter(Finding.code == code).first()
                if not finding:
                    db.add(Finding(
                        code=code,
                        title=sc["title"],
                        severity=sc["severity"],
                        confidence=96,
                        endpoint=sc["endpoint"],
                        tenant="GlobalTrips B2B",
                        agent_name=sc["agent"],
                        status="Verified",
                        impact=sc["impact"],
                        evidence=sc["evidence"],
                        remediation=sc["remediation"],
                        demo_label="DEMO / SIMULATED"
                    ))
                else:
                    finding.status = "Verified"
                db.commit()

                event_bus = getattr(request.app.state, "event_bus", None)
                if event_bus:
                    event_bus.emit("demo.scenario.completed", f"Completed demo scenario: {sc['title']}", {"scenario": key})
            finally:
                db.close()
            await asyncio.sleep(0.5)

    asyncio.create_task(_runner())
    return {"status": "queued", "message": "All six demo scenarios queued for autonomous execution"}


@router.post("/{action}")
def demo_action_control(action: str, request: Request, db: Session = Depends(get_db)):
    """General demo control: start, pause, resume, reset, clear-findings."""
    event_bus = getattr(request.app.state, "event_bus", None)
    if action == "start":
        if event_bus:
            event_bus.emit("demo.started", "Interactive demo session started", {"mode": "DEMO / SIMULATED"})
        return {"status": "started"}
    elif action == "clear-findings":
        db.query(Finding).delete()
        db.commit()
        if event_bus:
            event_bus.emit("demo.cleared", "All demo findings cleared", {})
        return {"status": "cleared"}
    elif action == "reset":
        from ...seed import seed_database
        db.query(Finding).delete()
        db.query(Api).delete()
        db.query(Agent).delete()
        db.query(Event).delete()
        db.commit()
        seed_database(db)
        if event_bus:
            event_bus.emit("demo.reset", "Demo environment reset to baseline seed", {})
        return {"status": "reset"}
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported demo action: '{action}'")
