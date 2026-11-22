"""Reporting and financial summary router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Booking, Payment, Refund, User
from ..auth import get_current_user

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("")
def get_agency_report(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve financial and booking aggregates for caller agency."""
    total_bookings = db.query(Booking).filter(Booking.agency_id == user.agency_id).count()
    total_sales = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(
        Payment.agency_id == user.agency_id,
        Payment.status == "completed"
    ).scalar()
    total_refunded = db.query(func.coalesce(func.sum(Refund.amount), 0.0)).filter(
        Refund.agency_id == user.agency_id,
        Refund.status == "processed"
    ).scalar()

    return {
        "agency_id": user.agency_id,
        "total_bookings": total_bookings,
        "total_sales_usd": round(total_sales, 2),
        "total_refunded_usd": round(total_refunded, 2),
        "net_revenue_usd": round(total_sales - total_refunded, 2),
        "synthetic": True
    }
