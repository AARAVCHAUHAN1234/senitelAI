"""Deterministic database seed for VoyageSim."""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .models import (
    Agency, User, Wallet, Flight, Fare, Booking, BookingStatus,
    Payment, Coupon, Refund, Invoice, TrafficLog
)


def seed_voyagesim(db: Session = None):
    """Seed VoyageSim database deterministically with random.seed(42)."""
    own_session = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        own_session = True

    try:
        # Check if already seeded
        if db.query(Agency).first():
            return

        random.seed(42)
        base_time = datetime(2026, 11, 1, 10, 0, 0)

        # 1. Agencies
        agencies_data = [
            ("TC-01", "TravelCorp International", "premium"),
            ("GT-02", "GlobalTrips B2B", "standard"),
            ("QF-03", "QuickFly Express", "standard"),
        ]
        agencies = []
        for code, name, tier in agencies_data:
            agency = Agency(code=code, name=name, tier=tier, synthetic=True, created_at=base_time)
            db.add(agency)
            agencies.append(agency)
        db.flush()

        # 2. Wallets for each agency
        for agency in agencies:
            balance = 150000.0 if agency.code == "TC-01" else 85000.0
            wallet = Wallet(
                agency_id=agency.id,
                currency="USD",
                balance=balance,
                credit_limit=25000.0,
                synthetic=True,
                created_at=base_time
            )
            db.add(wallet)
        db.flush()

        # 3. Users (~30 users across 3 agencies)
        users = []
        roles = ["admin", "manager", "agent", "sub-agent", "read-only"]
        for agency in agencies:
            prefix = agency.code.split("-")[0].lower()
            # admin
            u_admin = User(
                agency_id=agency.id,
                username=f"admin_{prefix}",
                email=f"admin@{prefix}.demo",
                role="admin",
                synthetic=True,
                created_at=base_time
            )
            db.add(u_admin)
            users.append(u_admin)

            # manager
            u_mgr = User(
                agency_id=agency.id,
                username=f"mgr_{prefix}",
                email=f"manager@{prefix}.demo",
                role="manager",
                synthetic=True,
                created_at=base_time
            )
            db.add(u_mgr)
            users.append(u_mgr)

            # 4 agents
            for i in range(1, 5):
                u_agent = User(
                    agency_id=agency.id,
                    username=f"agent{i}_{prefix}",
                    email=f"agent{i}@{prefix}.demo",
                    role="agent",
                    synthetic=True,
                    created_at=base_time
                )
                db.add(u_agent)
                users.append(u_agent)

            # 2 sub-agents
            for i in range(1, 3):
                u_sub = User(
                    agency_id=agency.id,
                    username=f"sub{i}_{prefix}",
                    email=f"sub{i}@{prefix}.demo",
                    role="sub-agent",
                    synthetic=True,
                    created_at=base_time
                )
                db.add(u_sub)
                users.append(u_sub)

            # 2 read-only
            for i in range(1, 3):
                u_ro = User(
                    agency_id=agency.id,
                    username=f"view{i}_{prefix}",
                    email=f"readonly{i}@{prefix}.demo",
                    role="read-only",
                    synthetic=True,
                    created_at=base_time
                )
                db.add(u_ro)
                users.append(u_ro)

        db.flush()

        # 4. Flights (20 flights)
        airlines = ["SkyWings", "AeroGlobal", "PacificJet", "NordicAir", "ApexLines"]
        airports = ["JFK", "LHR", "DXB", "SIN", "HND", "FRA", "CDG", "SYD", "ORD", "BOM"]
        flights = []
        for i in range(1, 21):
            origin, dest = random.sample(airports, 2)
            dep = base_time + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
            arr = dep + timedelta(hours=random.randint(2, 14))
            flight = Flight(
                flight_number=f"SW-{1000 + i}",
                origin=origin,
                destination=dest,
                departure=dep,
                arrival=arr,
                airline=random.choice(airlines),
                aircraft="A320" if i % 2 == 0 else "B787",
                available_seats=random.randint(20, 180),
                synthetic=True,
                created_at=base_time
            )
            db.add(flight)
            flights.append(flight)
        db.flush()

        # 5. Fares for each flight (economy, business)
        fares = []
        for flight in flights:
            for cabin in ["economy", "business"]:
                supplier_net = round(random.uniform(200.0, 600.0) if cabin == "economy" else random.uniform(800.0, 2200.0), 2)
                markup_pct = round(random.uniform(10.0, 25.0), 1)
                selling = round(supplier_net * (1 + markup_pct / 100.0), 2)
                fare = Fare(
                    flight_id=flight.id,
                    cabin_class=cabin,
                    supplier_net=supplier_net,
                    markup_pct=markup_pct,
                    selling_price=selling,
                    currency="USD",
                    synthetic=True
                )
                db.add(fare)
                fares.append(fare)
        db.flush()

        # 6. Coupons
        coupons = [
            Coupon(code="VOYAGE10", discount_pct=10.0, max_uses=100, times_used=12, is_active=True, synthetic=True, created_at=base_time),
            Coupon(code="EARLYBIRD20", discount_pct=20.0, max_uses=50, times_used=5, is_active=True, synthetic=True, created_at=base_time),
            Coupon(code="VIP50", discount_pct=50.0, max_uses=10, times_used=8, is_active=True, synthetic=True, created_at=base_time),
            Coupon(code="SINGLE_USE_A", discount_pct=15.0, max_uses=1, times_used=1, is_active=True, agency_id=agencies[0].id, synthetic=True, created_at=base_time),
        ]
        for c in coupons:
            db.add(c)
        db.flush()

        # 7. Bookings (~200 bookings across states)
        bookings = []
        passengers = [
            ("Alex Chen", "alex.chen@example.com"),
            ("Sarah Jenkins", "s.jenkins@example.com"),
            ("Marcus Aurel", "marcus@example.com"),
            ("Elena Rostova", "elena@example.com"),
            ("Devon Patel", "devon.p@example.com"),
            ("Claire Dupont", "c.dupont@example.com"),
            ("Lars Lindqvist", "lars@example.com"),
            ("Amina Diallo", "amina.d@example.com"),
        ]

        status_weights = [
            (BookingStatus.CONFIRMED, 90),
            (BookingStatus.TICKETED, 40),
            (BookingStatus.HELD, 30),
            (BookingStatus.QUOTED, 20),
            (BookingStatus.REFUNDED, 12),
            (BookingStatus.CANCELLED, 8),
        ]
        status_pool = [s for s, count in status_weights for _ in range(count)]

        for i in range(1, 201):
            agency = random.choice(agencies)
            # Find users belonging to this agency
            agency_users = [u for u in users if u.agency_id == agency.id]
            user = random.choice(agency_users)
            flight = random.choice(flights)
            flight_fares = [f for f in fares if f.flight_id == flight.id]
            fare = random.choice(flight_fares)
            p_name, p_email = random.choice(passengers)
            status = status_pool[i - 1] if i - 1 < len(status_pool) else BookingStatus.CONFIRMED

            b_created = base_time - timedelta(days=random.randint(1, 80))
            booking = Booking(
                reference=f"BK-{2000 + i}",
                agency_id=agency.id,
                user_id=user.id,
                flight_id=flight.id,
                fare_id=fare.id,
                passenger_name=p_name,
                passenger_email=p_email,
                status=status,
                total_price=fare.selling_price,
                quantity=1,
                notes=f"Synthetic demo booking {i}",
                synthetic=True,
                created_at=b_created,
                updated_at=b_created + timedelta(hours=1)
            )
            db.add(booking)
            bookings.append(booking)
        db.flush()

        # 8. Payments, Invoices, and Refunds for bookings
        for booking in bookings:
            if booking.status in (BookingStatus.CONFIRMED, BookingStatus.TICKETED, BookingStatus.REFUNDED):
                payment = Payment(
                    booking_id=booking.id,
                    agency_id=booking.agency_id,
                    amount=booking.total_price,
                    currency="USD",
                    method="wallet",
                    status="completed",
                    transaction_ref=f"TXN-{booking.id:05d}",
                    synthetic=True,
                    created_at=booking.created_at + timedelta(minutes=15)
                )
                db.add(payment)

                invoice = Invoice(
                    agency_id=booking.agency_id,
                    booking_id=booking.id,
                    invoice_number=f"INV-{2026}-{booking.id:05d}",
                    amount=booking.total_price,
                    tax=round(booking.total_price * 0.08, 2),
                    total=round(booking.total_price * 1.08, 2),
                    status="paid" if booking.status != BookingStatus.REFUNDED else "cancelled",
                    synthetic=True,
                    created_at=booking.created_at + timedelta(minutes=20)
                )
                db.add(invoice)

            if booking.status == BookingStatus.REFUNDED:
                refund = Refund(
                    booking_id=booking.id,
                    agency_id=booking.agency_id,
                    amount=booking.total_price,
                    reason="Synthetic customer schedule change request",
                    status="processed",
                    synthetic=True,
                    created_at=booking.created_at + timedelta(days=2)
                )
                db.add(refund)
        db.flush()

        # 9. 90 Days of synthetic traffic logs (for API classification: active vs zombie vs shadow)
        methods = ["GET", "POST"]
        endpoints_active = [
            "/api/v1/flights/search",
            "/api/v1/bookings",
            "/api/v1/bookings/{id}",
            "/api/v1/payments",
            "/api/v1/coupons/{code}",
            "/api/v1/agencies",
            "/api/v1/reports",
        ]
        endpoints_shadow = [
            "/api/v1/admin/fares/override",
            "/internal/debug",
            "/beta/export",
        ]
        # Generate 600 traffic log entries spread over last 90 days
        for i in range(600):
            days_ago = random.randint(0, 89)
            log_time = base_time - timedelta(days=days_ago, minutes=random.randint(0, 1400))
            is_shadow = random.random() < 0.05
            path = random.choice(endpoints_shadow) if is_shadow else random.choice(endpoints_active)
            method = "POST" if "payments" in path or "override" in path else "GET"
            user = random.choice(users)
            tlog = TrafficLog(
                method=method,
                path=path,
                status_code=200 if random.random() > 0.04 else 400,
                user_id=user.id,
                agency_id=user.agency_id,
                ip_address=f"10.0.{user.agency_id}.{random.randint(10, 250)}",
                user_agent="VoyageSim-DemoClient/1.0",
                response_time_ms=random.randint(25, 320),
                synthetic=True,
                created_at=log_time
            )
            db.add(tlog)

        db.commit()
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_voyagesim()
    print("VoyageSim seeded successfully!")
