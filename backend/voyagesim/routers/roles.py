"""Roles router with privilege escalation vulnerability."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import RoleAssignment, UserOut
from ..auth import get_current_user
from ..vulnerabilities import VulnFlags

router = APIRouter(prefix="/api/v1/users", tags=["roles"])
vulns = VulnFlags()


@router.post("/{id}/roles", response_model=UserOut)
def assign_role(
    id: int,
    req: RoleAssignment,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign a security role to a user.
    VULNERABILITY: privilege_escalation.
    When enabled, lower-privilege users (e.g. sub-agent or agent) can assign admin role.
    When fixed, only an administrator can assign roles.
    """
    target = db.query(User).filter(User.id == id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if not vulns.is_enabled("idor_booking") and target.agency_id != user.agency_id:
        raise HTTPException(status_code=404, detail="User not found")

    if not vulns.is_enabled("privilege_escalation"):
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Permission denied: administrator role required to assign roles")

    target.role = req.role.lower()
    db.commit()
    db.refresh(target)
    return target
