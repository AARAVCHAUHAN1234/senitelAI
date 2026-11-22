"""Pydantic schemas for VoyageSim entities."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AgencyBase(BaseModel):
    code: str
    name: str
    tier: str = "standard"


class AgencyOut(AgencyBase):
    id: int
    synthetic: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str
    role: str
    agency_id: int


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    agency_id: Optional[int] = None


class UserOut(UserBase):
    id: int
    is_active: bool
    synthetic: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class WalletOut(BaseModel):
    id: int
    agency_id: int
    currency: str
    balance: float
    credit_limit: float
    synthetic: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class FareOut(BaseModel):
    id: int
    flight_id: int
    cabin_class: str
    supplier_net: float
    markup_pct: float
    selling_price: float
    currency: str

    class Config:
        from_attributes = True


class FlightOut(BaseModel):
    id: int
    flight_number: str
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    airline: str
    aircraft: str
    available_seats: int
    fares: List[FareOut] = []

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    flight_id: int
    fare_id: int
    passenger_name: str
    passenger_email: Optional[str] = None
    quantity: int = 1
    notes: Optional[str] = None


class BookingPriceUpdate(BaseModel):
    price: float


class BookingOut(BaseModel):
    id: int
    reference: str
    agency_id: int
    user_id: int
    flight_id: int
    fare_id: int
    passenger_name: str
    passenger_email: Optional[str] = None
    status: str
    total_price: float
    quantity: int
    notes: Optional[str] = None
    synthetic: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    method: str = "wallet"


class PaymentOut(BaseModel):
    id: int
    booking_id: int
    agency_id: int
    amount: float
    currency: str
    method: str
    status: str
    transaction_ref: Optional[str] = None
    synthetic: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class CouponOut(BaseModel):
    id: int
    code: str
    discount_pct: float
    max_uses: int
    times_used: int
    is_active: bool
    agency_id: Optional[int] = None
    synthetic: bool = True

    class Config:
        from_attributes = True


class RefundCreate(BaseModel):
    booking_id: int
    amount: float
    reason: Optional[str] = None


class RefundOut(BaseModel):
    id: int
    booking_id: int
    agency_id: int
    amount: float
    reason: Optional[str] = None
    status: str
    synthetic: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: int
    agency_id: int
    booking_id: int
    invoice_number: str
    amount: float
    tax: float
    total: float
    status: str
    synthetic: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class RoleAssignment(BaseModel):
    role: str
