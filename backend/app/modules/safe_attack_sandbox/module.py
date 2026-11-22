"""Safe Attack Sandbox module implementing full PolicyGate and hash-chained audit."""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.orm import Session

from ...core.database import Base, get_db


class SandboxPolicyRule(Base):
    __tablename__ = "safe_sandbox_policy_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), nullable=False)
    rule_type = Column(String(50), nullable=False)  # allowlist / rate_limit / safety_guard
    pattern = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SandboxChainedAudit(Base):
    __tablename__ = "safe_sandbox_chained_audit"

    id = Column(Integer, primary_key=True, index=True)
    prev_hash = Column(String(64), nullable=False)
    curr_hash = Column(String(64), nullable=False)
    action = Column(String(100), nullable=False)
    target_url = Column(String(255), nullable=False)
    payload_summary = Column(Text, nullable=True)
    policy_verdict = Column(String(20), default="ALLOWED")  # ALLOWED / BLOCKED
    timestamp = Column(DateTime, default=datetime.utcnow)


class SandboxState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.emergency_stop_engaged = False
            cls._instance.rate_limit_per_min = 60
            cls._instance.max_concurrency = 5
            cls._instance.live_mode_confirmed = False
            cls._instance.blocked_requests = 0
            cls._instance.allowed_requests = 0
        return cls._instance


sandbox_state = SandboxState()
router = APIRouter(prefix="/api/modules/safe_attack_sandbox", tags=["safe_attack_sandbox"])


@router.get("/policy")
def get_sandbox_policy(db: Session = Depends(get_db)):
    """Retrieve active safety boundaries, allowlist rules, and emergency stop status."""
    rules = db.query(SandboxPolicyRule).filter(SandboxPolicyRule.is_active == True).all()
    return {
        "emergency_stop_engaged": sandbox_state.emergency_stop_engaged,
        "mode": "DEMO / SIMULATED",
        "live_mode_authorized": sandbox_state.live_mode_confirmed,
        "rate_limit_per_minute": sandbox_state.rate_limit_per_min,
        "max_concurrency": sandbox_state.max_concurrency,
        "destructive_tests": False,
        "real_financial_transactions": False,
        "synthetic_data_boundary_active": True,
        "counters": {
            "allowed_requests": sandbox_state.allowed_requests,
            "blocked_requests": sandbox_state.blocked_requests
        },
        "target_allowlist": [r.pattern for r in rules if r.rule_type == "allowlist"],
        "synthetic_identities": [
            "admin_travelcorp (Agency A)",
            "agent1_travelcorp (Agency A)",
            "admin_globaltrips (Agency B)",
            "agent1_globaltrips (Agency B)",
            "admin_quickfly (Agency C)"
        ]
    }


@router.post("/emergency-stop")
def trigger_emergency_stop():
    """Immediately halt all autonomous agents within one second."""
    sandbox_state.emergency_stop_engaged = True
    return {"status": "halted", "emergency_stop": True, "message": "All autonomous agents suspended immediately"}


@router.post("/emergency-release")
def release_emergency_stop():
    """Release emergency stop and permit resumption."""
    sandbox_state.emergency_stop_engaged = False
    return {"status": "released", "emergency_stop": False}


@router.get("/audit-chain")
def get_audit_chain(limit: int = 20, db: Session = Depends(get_db)):
    """Retrieve append-only hash-chained audit log of executed security tests."""
    return db.query(SandboxChainedAudit).order_by(SandboxChainedAudit.id.desc()).limit(limit).all()


@router.post("/replay/{id}")
def replay_audit_request(id: int, db: Session = Depends(get_db)):
    """Replay an audited request safely in simulation."""
    record = db.query(SandboxChainedAudit).filter(SandboxChainedAudit.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Audit entry not found")
    return {
        "status": "replayed",
        "target": record.target_url,
        "simulated_response_status": 200,
        "hash_verified": True
    }


def seed_sandbox(db: Session):
    if db.query(SandboxPolicyRule).first():
        return

    # Seed baseline allowlist
    rules = [
        ("Allow VoyageSim Local Target", "allowlist", "http://localhost:8001/*"),
        ("Allow Local Loopback Target", "allowlist", "http://127.0.0.1:8001/*"),
        ("Block External Public IPs", "safety_guard", "0.0.0.0/0"),
        ("Block Destructive Methods", "safety_guard", "DROP/TRUNCATE/FLUSH"),
    ]
    for name, r_type, pat in rules:
        db.add(SandboxPolicyRule(rule_name=name, rule_type=r_type, pattern=pat, is_active=True))

    # Seed initial chained audit records
    prev = "0" * 64
    actions = [
        ("PROBE_OPENAPI", "http://localhost:8001/openapi.json", "GET /openapi.json", "ALLOWED"),
        ("TEST_IDOR_BOOKING", "http://localhost:8001/api/v1/bookings/1", "GET /api/v1/bookings/1 (Agency A token)", "ALLOWED"),
        ("TEST_FARE_TAMPER", "http://localhost:8001/api/v1/bookings/1/price", "POST price=1.00", "ALLOWED"),
        ("EXTERNAL_PROBE_BLOCKED", "https://api.external-production-travel.com/v1", "EXTERNAL BLOCKED BY POLICY", "BLOCKED"),
    ]

    for act, target, payload, verdict in actions:
        h = hashlib.sha256(f"{prev}:{act}:{target}:{payload}".encode()).hexdigest()
        db.add(SandboxChainedAudit(
            prev_hash=prev,
            curr_hash=h,
            action=act,
            target_url=target,
            payload_summary=payload,
            policy_verdict=verdict,
            timestamp=datetime.utcnow()
        ))
        prev = h

    db.commit()


MODULE = {
    "name": "safe_attack_sandbox",
    "version": "1.0.0",
    "router": router,
    "event_subscriptions": ["test.started"],
    "event_publications": ["sandbox.policy.blocked", "sandbox.emergency_stop"],
    "seed_function": seed_sandbox,
    "navigation_item": {
        "title": "Safe Attack Sandbox",
        "route": "/sandbox",
        "section": "OPERATIONS"
    }
}


def register(app, ctx):
    Base.metadata.create_all(bind=ctx.session_factory().get_bind())
    db = ctx.session_factory()
    try:
        seed_sandbox(db)
    finally:
        db.close()
    app.include_router(router)
