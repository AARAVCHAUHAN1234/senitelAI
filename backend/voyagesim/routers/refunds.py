"""Refund router with duplicate refund vulnerability."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Booking, BookingStatus, Refund, User, Wallet
from ..schemas import RefundCreate, RefundOut
from ..auth import get_current_user
from ..vulnerabilities import VulnFlags

router = APIRouter(prefix="/api/v1/refunds", tags=["refunds"])
vulns = VulnFlags()


@router.post("", response_model=RefundOut, status_code=201)
def request_refund(
    req: RefundCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request refund for a booking.
    VULNERABILITY: duplicate_refund.
    When enabled, no idempotency or cumulative refund check is performed.
    Repeated requests can refund the same booking multiple times and exceed paid total.
    When fixed, idempotency and cumulative amount invariant are enforced.
    """
    booking = db.query(Booking).filter(Booking.id == req.booking_id).first()
    if not booking or (booking.agency_id != user.agency_id and not vulns.is_enabled("idor_booking")):
        raise HTTPException(status_code=404, detail="Booking not found")

    if not vulns.is_enabled("duplicate_refund"):
        # Secure check 1: booking must not already be in REFUNDED state
        if booking.status == BookingStatus.REFUNDED:
            raise HTTPException(status_code=400, detail="Booking has already been fully refunded")

        # Secure check 2: sum of existing refunds + requested refund <= total booking price
        existing_refunded = db.query(func.coalesce(func.sum(Refund.amount), 0.0)).filter(
            Refund.booking_id == booking.id,
            Refund.status == "processed"
        ).scalar()

        if existing_refunded + req.amount > booking.total_price:
            raise HTTPException(
                status_code=400,
                detail=f"Refund amount exceeds eligible balance. Remaining: {booking.total_price - existing_refunded:.2f}"
            )

    refund = Refund(
        booking_id=booking.id,
        agency_id=user.agency_id,
        amount=req.amount,
        reason=req.reason or "Synthetic refund request",
        status="processed",
        synthetic=True,
        created_at=datetime.utcnow()
    )
    db.add(refund)

    # Credit back to wallet
    wallet = db.query(Wallet).filter(Wallet.agency_id == user.agency_id).first()
    if wallet:
        wallet.balance += req.amount

    booking.status = BookingStatus.REFUNDED
    booking.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(refund)
    return refund


@router.get("/{id}", response_model=RefundOut)
def get_refund(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    refund = db.query(Refund).filter(Refund.id == id).first()
    if not refund or (refund.agency_id != user.agency_id and not vulns.is_enabled("idor_booking")):
        raise HTTPException(status_code=404, detail="Refund record not found")
    return refund
