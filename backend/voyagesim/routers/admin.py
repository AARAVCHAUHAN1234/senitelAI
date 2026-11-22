"""Admin operations and vulnerability test harness controls."""

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Fare, User
from ..auth import get_current_user
from ..vulnerabilities import VulnFlags

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
vulns = VulnFlags()


class FareOverrideRequest(BaseModel):
    fare_id: int
    new_price: float
    reason: str = "Admin manual price adjustment"


@router.post("/fares/override")
def override_fare(
    req: FareOverrideRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin fare override operation.
    VULNERABILITY: privilege_escalation / missing access control.
    When enabled, any agent can call this endpoint without admin authorization.
    When fixed, requires user.role == 'admin'.
    """
    if not vulns.is_enabled("privilege_escalation"):
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden: Administrator privilege required for fare override")

    fare = db.query(Fare).filter(Fare.id == req.fare_id).first()
    if not fare:
        raise HTTPException(status_code=404, detail="Fare not found")

    fare.selling_price = req.new_price
    db.commit()
    db.refresh(fare)
    return {
        "status": "success",
        "fare_id": fare.id,
        "new_selling_price": fare.selling_price,
        "modified_by": user.username,
        "synthetic": True
    }


@router.get("/vulns")
def list_vulnerabilities():
    """List all toggleable planted vulnerabilities and their active state."""
    return {
        "flags": vulns.list_all(),
        "mode": "DEMO / SIMULATED",
        "description": "True = vulnerable behavior active; False = remediated/fixed behavior active"
    }


@router.post("/vulns/{name}/fix")
def fix_vulnerability(name: str):
    """Remediate/fix a planted vulnerability so retests succeed."""
    if not vulns.fix(name):
        raise HTTPException(status_code=404, detail=f"Vulnerability flag '{name}' not found")
    return {"status": "remediated", "vulnerability": name, "enabled": False}


@router.post("/vulns/{name}/unfix")
def unfix_vulnerability(name: str):
    """Revert a vulnerability back to vulnerable state."""
    if not vulns.unfix(name):
        raise HTTPException(status_code=404, detail=f"Vulnerability flag '{name}' not found")
    return {"status": "reverted_to_vulnerable", "vulnerability": name, "enabled": True}


@router.post("/vulns/reset")
def reset_vulnerabilities():
    """Reset all vulnerability flags to vulnerable default state."""
    vulns.reset()
    return {"status": "reset_all", "flags": vulns.list_all()}
