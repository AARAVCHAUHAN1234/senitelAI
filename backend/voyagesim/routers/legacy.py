"""Legacy and zombie API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking
from ..vulnerabilities import VulnFlags

router = APIRouter(tags=["legacy"])
vulns = VulnFlags()


@router.get("/v1/bookings")
def legacy_v1_bookings(db: Session = Depends(get_db)):
    """
    Zombie API endpoint: Old deprecated /v1/bookings that was supposed to be decommissioned.
    VULNERABILITY: zombie_v1_api.
    When enabled, route still responds with unauthenticated passenger booking data.
    When fixed, returns 410 Gone.
    """
    if not vulns.is_enabled("zombie_v1_api"):
        raise HTTPException(status_code=410, detail="Endpoint decommissioned. Please migrate to /api/v3/bookings")

    # Zombie endpoint returns unauthenticated records
    bookings = db.query(Booking).limit(20).all()
    return {
        "api_version": "v1-deprecated",
        "warning": "This API version is deprecated and unmaintained",
        "count": len(bookings),
        "items": [
            {
                "id": b.id,
                "ref": b.reference,
                "passenger": b.passenger_name,
                "status": b.status.value if hasattr(b.status, "value") else str(b.status),
                "total": b.total_price
            }
            for b in bookings
        ]
    }


@router.get("/api/v3/bookings")
def modern_v3_bookings(db: Session = Depends(get_db)):
    """Modern active API version with proper pagination schema."""
    count = db.query(Booking).count()
    return {
        "api_version": "v3",
        "total_records": count,
        "status": "active"
    }
