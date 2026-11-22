"""Server-Sent Events (SSE) streaming and event history router."""

from typing import List
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.models import Event
from ..core.schemas import EventOut

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/stream")
async def event_stream(request: Request):
    """
    Server-Sent Events (SSE) real-time streaming endpoint.
    Frontend connects to receive live notifications of agent actions,
    graph topology updates, and newly verified findings.
    """
    event_bus = getattr(request.app.state, "event_bus", None)
    if not event_bus:
        async def empty_stream():
            yield "data: {\"kind\": \"system.info\", \"message\": \"Event bus initialized\"}\n\n"
        return StreamingResponse(empty_stream(), media_type="text/event-stream")

    return StreamingResponse(
        event_bus.subscribe(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("", response_model=List[EventOut])
def list_event_history(limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    """Retrieve historical persisted events."""
    return db.query(Event).order_by(Event.id.desc()).limit(limit).all()
