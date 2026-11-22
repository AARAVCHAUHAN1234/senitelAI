"""Deterministic seed for SentinelAI platform database."""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .app.core.database import Base, engine, SessionLocal
from .app.core.models import Api, Finding, Agent, Event, AuditLog


def seed_database(db: Session = None):
    """Seed SentinelAI platform database deterministically."""
    own_session = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        own_session = True

    try:
        # Check if already seeded
        if db.query(Api).first():
            return

        random.seed(42)
        base_time = datetime(2026, 11, 10, 12, 0, 0)

        # 1. APIs (11 baseline APIs: Active, Zombie, Shadow)
        apis_data = [
            ("GET", "/api/v1/bookings/{id}", "Active", 200, True, "TravelCore", 4820, 92, "OpenAPI Recon"),
            ("POST", "/api/v1/bookings", "Active", 201, True, "TravelCore", 1980, 28, "OpenAPI Recon"),
            ("POST", "/api/v1/bookings/{id}/price", "Active", 200, True, "Pricing Engine", 350, 77, "Traffic Log"),
            ("POST", "/api/v1/refunds", "Active", 201, True, "Settlement Service", 142, 84, "Traffic Log"),
            ("POST", "/api/v1/admin/fares/override", "Shadow", 200, False, "Undocumented", 4, 88, "Shadow Probe"),
            ("GET", "/v1/bookings", "Zombie", 200, False, "Legacy Deprecated", 0, 75, "Zombie Probe"),
            ("GET", "/api/v1/flights/search", "Active", 200, False, "Catalog Service", 10920, 18, "OpenAPI Recon"),
            ("POST", "/api/v1/payments", "Active", 201, True, "Payment Gateway", 7200, 22, "OpenAPI Recon"),
            ("GET", "/api/v1/coupons/{code}", "Active", 200, True, "Promotions", 630, 49, "OpenAPI Recon"),
            ("POST", "/api/v1/bookings/{id}/cancel", "Active", 200, True, "TravelCore", 250, 43, "OpenAPI Recon"),
            ("GET", "/internal/debug", "Shadow", 200, False, "Undocumented", 12, 86, "Shadow Probe"),
        ]

        for method, ep, cat, status, auth, owner, freq, risk, src in apis_data:
            db.add(Api(
                method=method,
                endpoint=ep,
                category=cat,
                status_code=status,
                auth_required=auth,
                owner=owner,
                frequency=freq,
                risk=risk,
                source=src,
                last_observed=base_time - timedelta(minutes=random.randint(5, 500))
            ))
        db.flush()

        # 2. 13 Agents
        agent_names = [
            "Recon Agent",
            "API Inventory Agent",
            "Change Detection Agent",
            "Attack Planner Agent",
            "Authentication Testing Agent",
            "Access Control Testing Agent",
            "API Security Testing Agent",
            "Attack Chain Intelligence Agent",
            "Verification Agent",
            "Risk & Triage Agent",
            "Reporting Agent",
            "Retesting Agent",
            "Business Logic Brain",
        ]
        for name in agent_names:
            db.add(Agent(
                name=name,
                status="Idle",
                task="Standing by for assignment",
                progress=0,
                tests_completed=0,
                findings_generated=0,
                last_execution=base_time - timedelta(hours=2)
            ))
        db.flush()

        # 3. Verified Initial Findings (4 baseline findings, all DEMO / SIMULATED)
        initial_findings = [
            (
                "DEMO-IDOR-001",
                "Cross-Agency IDOR on Booking Records",
                "Critical",
                98,
                "GET /api/v1/bookings/{id}",
                "GlobalTrips B2B",
                "Access Control Testing Agent",
                "Verified",
                "An Agency A agent can read synthetic Agency B bookings and sensitive passenger data.",
                "DEMO / SIMULATED — Agency A token requested BK-2001 (owned by Agency B); response 200 included synthetic booking record.",
                "Bind booking lookup to authenticated agency scope: WHERE id = :id AND agency_id = :agency_id."
            ),
            (
                "DEMO-FARE-001",
                "Unauthorized Client-Side Fare Tampering",
                "High",
                95,
                "POST /api/v1/bookings/{id}/price",
                "TravelCorp International",
                "Business Logic Brain",
                "Verified",
                "A client-controlled fare parameter reduces payable total before booking confirmation.",
                "DEMO / SIMULATED — Submitted fare 1.00 USD; server accepted total below quoted fare invariant.",
                "Recompute fare server-side from signed quotation and reject client-supplied totals."
            ),
            (
                "DEMO-REFUND-001",
                "Duplicate Refund without Idempotency Invariant",
                "High",
                92,
                "POST /api/v1/refunds",
                "TravelCorp International",
                "API Security Testing Agent",
                "Verified",
                "Repeated refund requests succeed, allowing cumulative refunds to exceed original booking payment.",
                "DEMO / SIMULATED — Second refund for synthetic booking BK-1001 processed without idempotency check.",
                "Enforce atomic transaction lock and assert sum(refunds) <= booking.total_price."
            ),
            (
                "DEMO-PRIV-001",
                "Sub-Agent Privilege Escalation on Admin Fare Override",
                "High",
                96,
                "POST /api/v1/admin/fares/override",
                "TravelCorp International",
                "Authentication Testing Agent",
                "Verified",
                "A lower-privilege agent role can invoke restricted administrative pricing operations.",
                "DEMO / SIMULATED — Synthetic Agent role received 200 OK from admin fare override operation.",
                "Apply server-side role authorization to the operation requiring role == 'admin'."
            ),
        ]

        for code, title, sev, conf, ep, tenant, agent, status, impact, ev, rem in initial_findings:
            db.add(Finding(
                code=code,
                title=title,
                severity=sev,
                confidence=conf,
                endpoint=ep,
                tenant=tenant,
                agent_name=agent,
                status=status,
                impact=impact,
                evidence=ev,
                remediation=rem,
                demo_label="DEMO / SIMULATED",
                created_at=base_time - timedelta(minutes=random.randint(10, 180))
            ))
        db.flush()

        # 4. Initial Events
        events_data = [
            ("system.ready", "SentinelAI Security Platform operational", {"mode": "DEMO / SIMULATED"}),
            ("api.discovered", "Discovered 11 API endpoints across active, zombie, and shadow categories", {"total": 11}),
            ("finding.verified", "Verified finding: Cross-Agency IDOR on Booking Records", {"code": "DEMO-IDOR-001"}),
            ("finding.verified", "Verified finding: Unauthorized Client-Side Fare Tampering", {"code": "DEMO-FARE-001"}),
            ("risk_score.updated", "Platform risk score calculated: 76/100 (elevated)", {"score": 76}),
        ]
        for kind, msg, detail in events_data:
            import json
            db.add(Event(
                kind=kind,
                message=msg,
                detail=json.dumps(detail),
                created_at=base_time - timedelta(minutes=random.randint(1, 30))
            ))

        # 5. Initial Audit Log
        db.add(AuditLog(
            action="system.startup",
            actor="SentinelAI Autonomous Orchestrator",
            detail='{"status": "initialized", "mode": "DEMO / SIMULATED"}',
            created_at=base_time
        ))

        db.commit()
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_database()
    print("SentinelAI platform seeded successfully!")
