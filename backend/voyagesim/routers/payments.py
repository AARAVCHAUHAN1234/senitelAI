"""Payments processing router."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, BookingStatus, Payment, User, Wallet
from ..schemas import PaymentCreate, PaymentOut
from ..auth import get_current_user

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("", response_model=PaymentOut, status_code=201)
def process_payment(
    req: PaymentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process payment for a booking using agency wallet."""
    booking = db.query(Booking).filter(Booking.id == req.booking_id).first()
    if not booking or booking.agency_id != user.agency_id:
        raise HTTPException(status_code=404, detail="Booking not found")

    wallet = db.query(Wallet).filter(Wallet.agency_id == user.agency_id).first()
    if not wallet:
        raise HTTPException(status_code=400, detail="Agency wallet not found")

    if wallet.balance + wallet.credit_limit < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    # Deduct wallet balance
    wallet.balance -= req.amount

    payment = Payment(
        booking_id=booking.id,
        agency_id=user.agency_id,
        amount=req.amount,
        currency="USD",
        method=req.method,
        status="completed",
        transaction_ref=f"TXN-{booking.id}-{int(datetime.utcnow().timestamp())}",
        synthetic=True,
        created_at=datetime.utcnow()
    )
    db.add(payment)

    # Mark booking confirmed
    booking.status = BookingStatus.CONFIRMED
    booking.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(payment)
    return payment


@router.get("/{id}", response_model=PaymentOut)
def get_payment(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve payment receipt."""
    payment = db.query(Payment).filter(Payment.id == id).first()
    if not payment or payment.agency_id != user.agency_id:
        raise HTTPException(status_code=404, detail="Payment record not found")
    return payment
