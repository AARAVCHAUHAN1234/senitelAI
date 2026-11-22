"""Flight search and retrieval router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Flight
from ..schemas import FlightOut

router = APIRouter(prefix="/api/v1/flights", tags=["flights"])


@router.get("/search", response_model=List[FlightOut])
def search_flights(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    airline: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search available flights with matching fares."""
    q = db.query(Flight)
    if origin:
        q = q.filter(Flight.origin == origin.upper())
    if destination:
        q = q.filter(Flight.destination == destination.upper())
    if airline:
        q = q.filter(Flight.airline.ilike(f"%{airline}%"))
    return q.limit(50).all()


@router.get("/{id}", response_model=FlightOut)
def get_flight(id: int, db: Session = Depends(get_db)):
    """Get flight details by ID."""
    flight = db.query(Flight).filter(Flight.id == id).first()
    if not flight:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight
