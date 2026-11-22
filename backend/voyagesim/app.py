"""VoyageSim simulated B2B travel platform application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .seed import seed_voyagesim
from .routers import (
    flights, bookings, payments, refunds, coupons,
    users, roles, agencies, invoices, reports, admin, legacy, internal
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables created and seed data loaded
    Base.metadata.create_all(bind=engine)
    seed_voyagesim()
    yield


app = FastAPI(
    title="VoyageSim B2B Travel Platform",
    version="1.0.0",
    description="Simulated multi-tenant travel platform target for SentinelAI DAST security assessment",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all business and security test routers
app.include_router(flights.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(refunds.router)
app.include_router(coupons.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(agencies.router)
app.include_router(invoices.router)
app.include_router(reports.router)
app.include_router(admin.router)
app.include_router(legacy.router)
app.include_router(internal.router)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "VoyageSim B2B Travel Platform",
        "mode": "DEMO / SIMULATED",
        "synthetic": True,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.voyagesim.app:app", host="0.0.0.0", port=8001, reload=False)
