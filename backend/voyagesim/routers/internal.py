"""Undocumented and shadow API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, User
from ..vulnerabilities import VulnFlags

router = APIRouter(tags=["internal"])
vulns = VulnFlags()


@router.get("/internal/debug")
def internal_debug_dump(db: Session = Depends(get_db)):
    """
    Shadow API endpoint: Undocumented internal debug interface left accessible.
    VULNERABILITY: undocumented_routes.
    When enabled, exposes sensitive system architecture details.
    When fixed, returns 404.
    """
    if not vulns.is_enabled("undocumented_routes"):
        raise HTTPException(status_code=404, detail="Not found")

    user_count = db.query(User).count()
    booking_count = db.query(Booking).count()
    return {
        "status": "debug_active",
        "service": "VoyageSim Travel Engine",
        "database": "sqlite3_voyagesim.db",
        "user_records": user_count,
        "booking_records": booking_count,
        "debug_mode": True,
        "environment": "synthetic_staging",
        "note": "SHADOW API -- Should not be reachable from public interface"
    }


@router.get("/beta/export")
def beta_bulk_export(db: Session = Depends(get_db)):
    """
    Shadow API endpoint: Undocumented bulk export API without rate limiting or tenant scoping.
    VULNERABILITY: undocumented_routes.
    When enabled, dumps raw passenger and booking records across all agencies.
    When fixed, returns 404.
    """
    if not vulns.is_enabled("undocumented_routes"):
        raise HTTPException(status_code=404, detail="Not found")

    bookings = db.query(Booking).limit(50).all()
    return {
        "export_channel": "beta_pipeline",
        "record_count": len(bookings),
        "data": [
            {
                "id": b.id,
                "ref": b.reference,
                "agency_id": b.agency_id,
                "passenger": b.passenger_name,
                "email": b.passenger_email,
                "total": b.total_price
            }
            for b in bookings
        ]
    }
