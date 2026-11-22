"""FastAPI application factory for SentinelAI backend."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import Base, engine, SessionLocal
from .core.settings import settings
from .core.events import EventBus
from .core.services import ServiceRegistry
from .core.module_loader import load_modules
from .agents.orchestrator import AgentOrchestrator
from ..seed import seed_database
from .routers import (
    dashboard, apis, findings, agents, events,
    audit, demo, reports, settings_router, ingest, graph
)


class AppContext:
    def __init__(self, session_factory, event_bus, service_registry):
        self.session_factory = session_factory
        self.event_bus = event_bus
        self.services = service_registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed baseline data
    Base.metadata.create_all(bind=engine)
    seed_database()

    # Initialize EventBus and ServiceRegistry
    event_bus = EventBus(SessionLocal)
    service_registry = ServiceRegistry()
    ctx = AppContext(SessionLocal, event_bus, service_registry)

    # Initialize AgentOrchestrator
    orchestrator = AgentOrchestrator(ctx)

    # Attach to app.state
    app.state.event_bus = event_bus
    app.state.services = service_registry
    app.state.orchestrator = orchestrator
    app.state.ctx = ctx

    # Dynamically load isolated innovation modules
    load_modules(app, ctx)

    event_bus.emit("system.ready", "SentinelAI DAST platform engine started", {"mode": "DEMO / SIMULATED"})
    yield


app = FastAPI(
    title="SentinelAI Platform API",
    version="1.0.0",
    description="Agentic Real-Time DAST Security Testing Platform for Multi-Tenant Travel Platforms",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Routers
app.include_router(dashboard.router)
app.include_router(apis.router)
app.include_router(findings.router)
app.include_router(agents.router)
app.include_router(events.router)
app.include_router(audit.router)
app.include_router(demo.router)
app.include_router(reports.router)
app.include_router(settings_router.router)
app.include_router(ingest.router)
app.include_router(graph.router)


@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "SentinelAI DAST Engine",
        "mode": "DEMO / SIMULATED",
        "live_testing": False,
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
