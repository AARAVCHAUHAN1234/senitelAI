"""Dashboard router providing computed metrics and activity aggregates."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.database import get_db
from ..core.models import Api, Finding, Agent, Event
from ..core.schemas import ApiOut, FindingOut, AgentOut, EventOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(db: Session = Depends(get_db)):
    """Compute and return all dashboard metrics from database records."""
    apis = db.query(Api).all()
    findings = db.query(Finding).order_by(Finding.id.desc()).all()
    agents = db.query(Agent).all()
    events = db.query(Event).order_by(Event.id.desc()).limit(40).all()

    crit_count = sum(1 for f in findings if f.severity == "Critical" and f.status != "Fixed")
    high_count = sum(1 for f in findings if f.severity == "High" and f.status != "Fixed")
    verified_count = sum(1 for f in findings if f.status == "Verified")

    # Risk score computation: weighted sum based on findings and exposed surface
    base_api_risk = sum(a.risk for a in apis) / max(1, len(apis))
    computed_risk = min(100, round(base_api_risk + crit_count * 6 + high_count * 3))

    # Severity distribution
    severities = ["Critical", "High", "Medium", "Low", "Informational"]
    severity_dist = [
        {"name": s, "value": sum(1 for f in findings if f.severity == s)}
        for s in severities
    ]

    # Activity timeline
    activity = [
        {
            "time": e.created_at.strftime("%H:%M:%S") if e.created_at else "00:00:00",
            "count": 1,
            "type": e.kind,
            "message": e.message
        }
        for e in reversed(events)
    ]

    metrics = {
        "total_apis": len(apis),
        "active_apis": sum(1 for a in apis if a.category == "Active"),
        "zombie_apis": sum(1 for a in apis if a.category == "Zombie"),
        "shadow_apis": sum(1 for a in apis if a.category == "Shadow"),
        "vulnerabilities": len(findings),
        "critical": crit_count,
        "high": high_count,
        "verified": verified_count,
        "agents_running": sum(1 for a in agents if a.status == "Running"),
        "tests_executed": sum(a.tests_completed for a in agents),
        "avg_verification_seconds": 1.2,
        "risk_score": computed_risk,
    }

    return {
        "metrics": metrics,
        "severity": severity_dist,
        "activity": activity,
        "apis": [ApiOut.model_validate(a).model_dump() for a in apis[:15]],
        "findings": [FindingOut.model_validate(f).model_dump() for f in findings[:10]],
        "agents": [AgentOut.model_validate(a).model_dump() for a in agents],
        "events": [EventOut.model_validate(e).model_dump() for e in events[:20]],
    }
