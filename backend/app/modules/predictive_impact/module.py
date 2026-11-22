"""Predictive Security Impact Engine module for SentinelAI."""

import json
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import Session

from ...core.database import Base, get_db
from ...core.models import Api


class PredictiveChange(Base):
    __tablename__ = "predictive_impact_changes"

    id = Column(Integer, primary_key=True, index=True)
    change_type = Column(String(50), nullable=False)  # Added / Modified / Auth Changed
    endpoint = Column(String(255), nullable=False)
    service = Column(String(100), default="VoyageSim Core")
    risk_priority = Column(Integer, default=50)  # 0-100
    affected_workflows = Column(Text, nullable=False)  # JSON list
    recommended_test = Column(Text, nullable=False)
    pipeline_stage = Column(String(50), default="DAST scan")
    status = Column(String(30), default="Predicted")
    created_at = Column(DateTime, default=datetime.utcnow)


router = APIRouter(prefix="/api/modules/predictive_impact", tags=["predictive_impact"])


@router.get("/changes")
def list_predicted_changes(db: Session = Depends(get_db)):
    """List prioritized changes with recommended security test suites."""
    changes = db.query(PredictiveChange).order_by(PredictiveChange.risk_priority.desc()).all()
    results = []
    for c in changes:
        results.append({
            "id": c.id,
            "change_type": c.change_type,
            "endpoint": c.endpoint,
            "service": c.service,
            "risk_priority": c.risk_priority,
            "affected_workflows": json.loads(c.affected_workflows),
            "recommended_test": c.recommended_test,
            "pipeline_stage": c.pipeline_stage,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None
        })
    return results


@router.get("/dependency-graph")
def get_dependency_graph(db: Session = Depends(get_db)):
    """Retrieve layered service dependency graph mapped to workflows."""
    return {
        "services": [
            {"id": "gateway", "name": "API Gateway", "layer": "ingress", "status": "monitored"},
            {"id": "booking_svc", "name": "Booking Core Service", "layer": "business_logic", "status": "critical"},
            {"id": "payment_svc", "name": "Payment & Wallet Gateway", "layer": "financial", "status": "high_risk"},
            {"id": "flight_catalog", "name": "Flight & Fares Catalog", "layer": "data_layer", "status": "normal"},
            {"id": "reporting_svc", "name": "Invoices & Analytics", "layer": "async_worker", "status": "normal"},
        ],
        "dependencies": [
            {"source": "gateway", "target": "booking_svc", "weight": 5},
            {"source": "gateway", "target": "payment_svc", "weight": 8},
            {"source": "booking_svc", "target": "payment_svc", "weight": 10},
            {"source": "booking_svc", "target": "flight_catalog", "weight": 4},
            {"source": "payment_svc", "target": "reporting_svc", "weight": 3},
        ],
        "pipeline_stages": [
            {"id": "code", "label": "Write code", "status": "completed"},
            {"id": "push", "label": "Push", "status": "completed"},
            {"id": "ci", "label": "CI build & tests", "status": "completed"},
            {"id": "deploy_staging", "label": "Deploy to staging", "status": "completed"},
            {"id": "dast_scan", "label": "DAST scan", "status": "active"},
            {"id": "decision", "label": "Policy gate", "status": "pending"},
            {"id": "deploy_prod", "label": "Deploy to prod", "status": "pending"},
            {"id": "monitor", "label": "Monitor", "status": "pending"},
        ]
    }


@router.post("/simulate-deployment")
def simulate_deployment(service: str = "Booking Engine v2.4", db: Session = Depends(get_db)):
    """Simulate a new deployment webhook and prioritize affected API surfaces."""
    new_change = PredictiveChange(
        change_type="Modified",
        endpoint="POST /api/v1/bookings/{id}/price",
        service=service,
        risk_priority=88,
        affected_workflows=json.dumps(["Booking", "Payment Gateway", "Settlement"]),
        recommended_test="Execute client-side parameter tampering test suite and verify quotation signature enforcement",
        pipeline_stage="DAST scan",
        status="Predicted",
        created_at=datetime.utcnow()
    )
    db.add(new_change)
    db.commit()
    return {"status": "simulated", "change_id": new_change.id, "priority": new_change.risk_priority}


def seed_predictive_impact(db: Session):
    if db.query(PredictiveChange).first():
        return

    changes = [
        (
            "Auth Changed",
            "POST /api/v1/admin/fares/override",
            "Pricing Engine",
            92,
            ["Admin Margin Override", "Inventory Quotation"],
            "Run privilege escalation and non-admin role boundary tests",
            "DAST scan"
        ),
        (
            "Added",
            "GET /beta/export",
            "Itinerary Service",
            85,
            ["Passenger Analytics", "Bulk Reporting"],
            "Verify tenant scoping, authentication requirements, and data masking",
            "DAST scan"
        ),
        (
            "Modified",
            "POST /api/v1/refunds",
            "Settlement Service",
            82,
            ["Refund", "Wallet Credit"],
            "Execute race condition and duplicate liquidation checks",
            "DAST scan"
        ),
        (
            "Parameter Drift",
            "POST /api/v1/bookings",
            "Booking Core",
            68,
            ["Booking Creation"],
            "Test negative seat count and boundary integer parsing",
            "DAST scan"
        ),
    ]

    for c_type, ep, svc, risk, wf, rec, stage in changes:
        db.add(PredictiveChange(
            change_type=c_type,
            endpoint=ep,
            service=svc,
            risk_priority=risk,
            affected_workflows=json.dumps(wf),
            recommended_test=rec,
            pipeline_stage=stage,
            status="Predicted",
            created_at=datetime.utcnow()
        ))
    db.commit()


MODULE = {
    "name": "predictive_impact",
    "version": "1.0.0",
    "router": router,
    "event_subscriptions": ["api.changed"],
    "event_publications": ["impact.prediction.created"],
    "seed_function": seed_predictive_impact,
    "navigation_item": {
        "title": "Predictive Security Impact",
        "route": "/predictive-impact",
        "section": "INTELLIGENCE"
    }
}


def register(app, ctx):
    Base.metadata.create_all(bind=ctx.session_factory().get_bind())
    db = ctx.session_factory()
    try:
        seed_predictive_impact(db)
    finally:
        db.close()
    app.include_router(router)
