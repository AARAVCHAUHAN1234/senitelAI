"""Agencies management router."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Agency, User
from ..schemas import AgencyOut
from ..auth import get_current_user

router = APIRouter(prefix="/api/v1/agencies", tags=["agencies"])


@router.get("", response_model=List[AgencyOut])
def list_agencies(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List registered B2B agencies."""
    return db.query(Agency).all()


@router.get("/{id}", response_model=AgencyOut)
def get_agency(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve agency profile."""
    agency = db.query(Agency).filter(Agency.id == id).first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")
    return agency
