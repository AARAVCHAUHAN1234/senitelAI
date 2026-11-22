"""Authentication and token handling for VoyageSim."""

from typing import Optional
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

# Pre-configured demo tokens mapped to synthetic identities
DEMO_TOKENS = {
    "token_agency_a_admin": {"agency_id": 1, "username": "admin_travelcorp", "role": "admin"},
    "token_agency_a_manager": {"agency_id": 1, "username": "mgr_travelcorp", "role": "manager"},
    "token_agency_a_agent": {"agency_id": 1, "username": "agent1_travelcorp", "role": "agent"},
    "token_agency_a_subagent": {"agency_id": 1, "username": "sub1_travelcorp", "role": "sub-agent"},
    "token_agency_a_readonly": {"agency_id": 1, "username": "view_travelcorp", "role": "read-only"},
    "token_agency_b_admin": {"agency_id": 2, "username": "admin_globaltrips", "role": "admin"},
    "token_agency_b_manager": {"agency_id": 2, "username": "mgr_globaltrips", "role": "manager"},
    "token_agency_b_agent": {"agency_id": 2, "username": "agent1_globaltrips", "role": "agent"},
    "token_agency_c_admin": {"agency_id": 3, "username": "admin_quickfly", "role": "admin"},
    "token_agency_c_agent": {"agency_id": 3, "username": "agent1_quickfly", "role": "agent"},
}


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Validate Bearer token and return active synthetic User."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    parts = authorization.split(" ")
    token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else parts[0]
    
    if token in DEMO_TOKENS:
        info = DEMO_TOKENS[token]
        user = db.query(User).filter(User.username == info["username"]).first()
        if user:
            return user
        # Fallback if DB user record not found yet: lookup by agency and role
        user = db.query(User).filter(User.agency_id == info["agency_id"], User.role == info["role"]).first()
        if user:
            return user

    # Lookup user directly by username or token string matching username
    user = db.query(User).filter(User.username == token).first()
    if user:
        return user
        
    raise HTTPException(status_code=401, detail="Invalid synthetic token")


def require_role(*allowed_roles: str):
    """Dependency factory checking if current user has an allowed role."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"Role '{current_user.role}' not authorized. Required: {allowed_roles}")
        return current_user
    return role_checker
