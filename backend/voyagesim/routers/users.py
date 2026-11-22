"""Users router with mass assignment vulnerability."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserOut, UserUpdate
from ..auth import get_current_user
from ..vulnerabilities import VulnFlags

router = APIRouter(prefix="/api/v1/users", tags=["users"])
vulns = VulnFlags()


@router.get("", response_model=List[UserOut])
def list_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List users in the caller's agency."""
    return db.query(User).filter(User.agency_id == user.agency_id).all()


@router.get("/{id}", response_model=UserOut)
def get_user(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user by ID."""
    u = db.query(User).filter(User.id == id).first()
    if not u or (u.agency_id != user.agency_id and not vulns.is_enabled("idor_booking")):
        raise HTTPException(status_code=404, detail="User not found")
    return u


@router.put("/{id}", response_model=UserOut)
def update_user(
    id: int,
    req: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile.
    VULNERABILITY: mass_assignment.
    When enabled, a regular agent can update the `role` field (e.g. promoting self to admin)
    or switch `agency_id`.
    When fixed, only admin can change roles, and agency_id is immutable.
    """
    u = db.query(User).filter(User.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    if not vulns.is_enabled("idor_booking") and u.agency_id != user.agency_id:
        raise HTTPException(status_code=404, detail="User not found")

    if req.email is not None:
        u.email = req.email
    if req.is_active is not None:
        u.is_active = req.is_active

    if req.role is not None:
        if vulns.is_enabled("mass_assignment"):
            # Vulnerable: accept role upgrade from anyone
            u.role = req.role
        else:
            # Secure: require admin role to change user role
            if user.role != "admin":
                raise HTTPException(status_code=403, detail="Only administrators can update user roles")
            u.role = req.role

    if req.agency_id is not None:
        if vulns.is_enabled("mass_assignment"):
            u.agency_id = req.agency_id
        else:
            raise HTTPException(status_code=400, detail="agency_id cannot be modified")

    db.commit()
    db.refresh(u)
    return u
