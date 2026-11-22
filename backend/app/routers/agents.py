"""Agents control center router."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.models import Agent
from ..core.schemas import AgentOut

router = APIRouter(tags=["agents"])


@router.get("/api/agents", response_model=List[AgentOut])
def list_agents(db: Session = Depends(get_db)):
    """List all autonomous security agents with live execution status."""
    return db.query(Agent).all()


@router.post("/api/agents/{name}/run")
async def run_agent(name: str, request: Request):
    """Trigger execution of an individual agent by name."""
    clean_name = name.replace("_", " ")
    if not hasattr(request.app.state, "orchestrator"):
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        result = await request.app.state.orchestrator.run_single_agent(clean_name)
        return {"status": "success", "agent": clean_name, "result": result}
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Agent '{clean_name}' not found")


@router.post("/api/scan/{action}")
def scan_control(action: str, request: Request):
    """Control full DAST scan lifecycle: start, pause, resume, stop."""
    if not hasattr(request.app.state, "orchestrator"):
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    orchestrator = request.app.state.orchestrator
    if action == "start":
        return orchestrator.start_assessment()
    elif action == "pause":
        return orchestrator.pause()
    elif action == "resume":
        return orchestrator.resume()
    elif action == "stop":
        return orchestrator.stop()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported scan action: '{action}'")
