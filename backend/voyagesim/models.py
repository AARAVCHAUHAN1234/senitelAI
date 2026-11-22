"""SQLAlchemy models for VoyageSim."""

import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class BookingStatus(str, enum.Enum):
    QUOTED = "QUOTED"
    HELD = "HELD"
    CONFIRMED = "CONFIRMED"
    TICKETED = "TICKETED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    tier = Column(String(50), default="standard")
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="agency")
    wallets = relationship("Wallet", back_populates="agency")
    bookings = relationship("Booking", back_populates="agency")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)  # admin, manager, agent, sub-agent, read-only
    is_active = Column(Boolean, default=True)
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    agency = relationship("Agency", back_populates="users")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False)
    currency = Column(String(3), default="USD")
    balance = Column(Float, nullable=False)
    credit_limit = Column(Float, default=0.0)
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    agency = relationship("Agency", back_populates="wallets")


class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(20), nullable=False)
    origin = Column(String(10), nullable=False)
    destination = Column(String(10), nullable=False)
    departure = Column(DateTime, nullable=False)
    arrival = Column(DateTime, nullable=False)
    airline = Column(String(100), nullable=False)
    aircraft = Column(String(50), default="A320")
    available_seats = Column(Integer, default=180)
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    fares = relationship("Fare", back_populates="flight")


class Fare(Base):
    __tablename__ = "fares"

    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    cabin_class = Column(String(20), nullable=False)  # economy, business, first
    supplier_net = Column(Float, nullable=False)
    markup_pct = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    synthetic = Column(Boolean, default=True)

    flight = relationship("Flight", back_populates="fares")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(20), unique=True, nullable=False)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    fare_id = Column(Integer, ForeignKey("fares.id"), nullable=False)
    passenger_name = Column(String(200), nullable=False)
    passenger_email = Column(String(200), nullable=True)
    status = Column(Enum(BookingStatus), default=BookingStatus.QUOTED)
    total_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agency = relationship("Agency", back_populates="bookings")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    method = Column(String(50), default="wallet")
    status = Column(String(20), default="completed")  # pending, completed, failed
    transaction_ref = Column(String(50), nullable=True)
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_pct = Column(Float, nullable=False)
    max_uses = Column(Integer, default=1)
    times_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=True)  # null = any agency
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String(500), nullable=True)
    status = Column(String(20), default="processed")  # pending, processed, rejected
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    tax = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    status = Column(String(20), default="issued")  # draft, issued, paid, cancelled
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    status_code = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
