"""Booking management router with toggleable security vulnerabilities."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, BookingStatus, Fare, Payment, User
from ..schemas import BookingCreate, BookingOut, BookingPriceUpdate
from ..auth import get_current_user
from ..vulnerabilities import VulnFlags

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])
vulns = VulnFlags()


@router.get("", response_model=List[BookingOut])
def list_bookings(
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List bookings belonging to the authenticated agency."""
    q = db.query(Booking).filter(Booking.agency_id == user.agency_id)
    if status:
        q = q.filter(Booking.status == status.upper())
    return q.order_by(Booking.id.desc()).limit(limit).all()


@router.get("/{id}", response_model=BookingOut)
def get_booking(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve booking details by ID.
    VULNERABILITY: IDOR (idor_booking).
    When enabled, agency boundary check is omitted, allowing cross-agency booking access.
    When fixed, returns 404 if booking does not belong to user's agency.
    """
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if not vulns.is_enabled("idor_booking"):
        # Secure implementation: verify agency scope
        if booking.agency_id != user.agency_id:
            raise HTTPException(status_code=404, detail="Booking not found")

    return booking


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    req: BookingCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new booking.
    VULNERABILITY: negative_quantity.
    When enabled, negative seat quantities are accepted.
    """
    if not vulns.is_enabled("negative_quantity") and req.quantity <= 0:
        raise HTTPException(status_code=400, detail="Booking quantity must be greater than zero")

    fare = db.query(Fare).filter(Fare.id == req.fare_id).first()
    if not fare:
        raise HTTPException(status_code=400, detail="Invalid fare ID")

    total = fare.selling_price * req.quantity
    now = datetime.utcnow()
    ref_count = db.query(Booking).count() + 1
    booking = Booking(
        reference=f"BK-{3000 + ref_count}",
        agency_id=user.agency_id,
        user_id=user.id,
        flight_id=req.flight_id,
        fare_id=req.fare_id,
        passenger_name=req.passenger_name,
        passenger_email=req.passenger_email,
        status=BookingStatus.QUOTED,
        total_price=total,
        quantity=req.quantity,
        notes=req.notes,
        synthetic=True,
        created_at=now,
        updated_at=now
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{id}/price", response_model=BookingOut)
def update_booking_price(
    id: int,
    req: BookingPriceUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update booking price before confirmation.
    VULNERABILITY: fare_tamper.
    When enabled, accepts client-supplied price directly without recomputing from signed fare.
    When fixed, recomputes from database fare and rejects client modification.
    """
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.agency_id != user.agency_id and not vulns.is_enabled("idor_booking"):
        raise HTTPException(status_code=404, detail="Booking not found")

    if vulns.is_enabled("fare_tamper"):
        # Vulnerable: directly accept client's price (e.g. 1.00 USD)
        booking.total_price = req.price
    else:
        # Secure: recompute price from fare and reject tampering
        fare = db.query(Fare).filter(Fare.id == booking.fare_id).first()
        if not fare:
            raise HTTPException(status_code=400, detail="Associated fare not found")
        recomputed = fare.selling_price * booking.quantity
        if abs(req.price - recomputed) > 0.01:
            raise HTTPException(status_code=400, detail="Fare tampering detected: price must match approved quotation")
        booking.total_price = recomputed

    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{id}/hold", response_model=BookingOut)
def hold_booking(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Transition booking from QUOTED to HELD."""
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking or (booking.agency_id != user.agency_id and not vulns.is_enabled("idor_booking")):
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = BookingStatus.HELD
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{id}/confirm", response_model=BookingOut)
def confirm_booking(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Transition booking to CONFIRMED."""
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking or (booking.agency_id != user.agency_id and not vulns.is_enabled("idor_booking")):
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = BookingStatus.CONFIRMED
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{id}/ticket", response_model=BookingOut)
def ticket_booking(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Transition booking to TICKETED.
    VULNERABILITY: skip_payment.
    When enabled, allows ticketing without checking whether payment was received.
    When fixed, requires confirmed payment.
    """
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking or (booking.agency_id != user.agency_id and not vulns.is_enabled("idor_booking")):
        raise HTTPException(status_code=404, detail="Booking not found")

    if not vulns.is_enabled("skip_payment"):
        # Secure check: ensure payment exists and is completed
        payment = db.query(Payment).filter(
            Payment.booking_id == booking.id,
            Payment.status == "completed"
        ).first()
        if not payment:
            raise HTTPException(status_code=400, detail="Cannot ticket: payment not received or pending")

    booking.status = BookingStatus.TICKETED
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{id}/cancel", response_model=BookingOut)
def cancel_booking(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Cancel booking."""
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking or (booking.agency_id != user.agency_id and not vulns.is_enabled("idor_booking")):
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = BookingStatus.CANCELLED
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking
