"""Coupons router with coupon reuse vulnerability."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Coupon, User
from ..schemas import CouponOut
from ..auth import get_current_user
from ..vulnerabilities import VulnFlags

router = APIRouter(prefix="/api/v1/coupons", tags=["coupons"])
vulns = VulnFlags()


@router.get("/{code}", response_model=CouponOut)
def get_coupon(code: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve coupon details."""
    coupon = db.query(Coupon).filter(Coupon.code == code.upper()).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon


@router.post("/{code}/apply", response_model=CouponOut)
def apply_coupon(
    code: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply coupon to booking.
    VULNERABILITY: coupon_reuse.
    When enabled, times_used check and agency restriction are bypassed.
    When fixed, limits max_uses and checks agency scope.
    """
    coupon = db.query(Coupon).filter(Coupon.code == code.upper()).first()
    if not coupon or not coupon.is_active:
        raise HTTPException(status_code=404, detail="Active coupon not found")

    if not vulns.is_enabled("coupon_reuse"):
        # Secure check 1: max uses limit
        if coupon.times_used >= coupon.max_uses:
            raise HTTPException(status_code=400, detail="Coupon usage limit has been exceeded")
        # Secure check 2: agency scope if restricted
        if coupon.agency_id and coupon.agency_id != user.agency_id:
            raise HTTPException(status_code=403, detail="Coupon not valid for this agency")

    coupon.times_used += 1
    db.commit()
    db.refresh(coupon)
    return coupon
