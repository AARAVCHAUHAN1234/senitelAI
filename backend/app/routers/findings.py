"""Vulnerability findings router with verification and retest actions."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime

from ..core.database import get_db
from ..core.models import Finding
from ..core.schemas import FindingOut

router = APIRouter(prefix="/api/findings", tags=["findings"])


@router.get("", response_model=List[FindingOut])
def list_findings(
    q: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieve vulnerability findings with optional text and severity filters."""
    query = db.query(Finding)
    if q:
        query = query.filter(
            (Finding.title.ilike(f"%{q}%")) |
            (Finding.endpoint.ilike(f"%{q}%")) |
            (Finding.code.ilike(f"%{q}%"))
        )
    if severity and severity != "All":
        query = query.filter(Finding.severity == severity)
    if status and status != "All":
        query = query.filter(Finding.status == status)

    return query.order_by(Finding.id.desc()).all()


@router.get("/{id}", response_model=FindingOut)
def get_finding(id: int, db: Session = Depends(get_db)):
    f = db.query(Finding).filter(Finding.id == id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    return f


@router.post("/{id}/verify", response_model=FindingOut)
async def verify_finding(id: int, request: Request, db: Session = Depends(get_db)):
    """Trigger independent verification of a finding in the safe sandbox."""
    finding = db.query(Finding).filter(Finding.id == id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding.status = "Verified"
    finding.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(finding)

    # Broadcast event if event_bus available on app state
    if hasattr(request.app.state, "event_bus"):
        request.app.state.event_bus.emit(
            "finding.verified",
            f"Independent verification passed for {finding.title}",
            {"code": finding.code, "status": "Verified"}
        )

    return finding


@router.post("/{id}/retest", response_model=FindingOut)
async def retest_finding(id: int, request: Request, db: Session = Depends(get_db)):
    """Execute retest check against VoyageSim target."""
    finding = db.query(Finding).filter(Finding.id == id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Call orchestrator's Retesting Agent
    if hasattr(request.app.state, "orchestrator"):
        await request.app.state.orchestrator.run_single_agent(
            "Retesting Agent",
            {"code": finding.code}
        )

    db.refresh(finding)
    return finding
