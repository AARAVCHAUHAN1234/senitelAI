"""Event bus for SSE broadcasting and event persistence."""

import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, Optional

from sqlalchemy.orm import Session

from .models import Event

# Event type constants
EVENT_SCAN_STARTED = "scan.started"
EVENT_SCAN_COMPLETED = "scan.completed"
EVENT_SCAN_PAUSED = "scan.paused"
EVENT_SCAN_RESUMED = "scan.resumed"
EVENT_SCAN_STOPPED = "scan.stopped"
EVENT_FINDING_CREATED = "finding.created"
EVENT_FINDING_VERIFIED = "finding.verified"
EVENT_AGENT_STARTED = "agent.started"
EVENT_AGENT_COMPLETED = "agent.completed"
EVENT_AGENT_FAILED = "agent.failed"
EVENT_DEMO_STARTED = "demo.started"
EVENT_DEMO_COMPLETED = "demo.completed"
EVENT_SYSTEM_INFO = "system.info"


class EventBus:
    """Broadcasts events to SSE subscribers and persists them to the database."""

    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._subscribers: list[asyncio.Queue] = []

    def emit(self, kind: str, message: str, detail: Optional[dict] = None) -> None:
        """Persist an event and broadcast to all SSE subscribers."""
        detail_json = json.dumps(detail) if detail else None

        db: Session = self._session_factory()
        try:
            event = Event(kind=kind, message=message, detail=detail_json)
            db.add(event)
            db.commit()
            db.refresh(event)
            event_id = event.id
            created_at = str(event.created_at) if event.created_at else datetime.utcnow().isoformat()
        finally:
            db.close()

        payload = json.dumps({
            "id": event_id,
            "kind": kind,
            "message": message,
            "detail": detail_json,
            "created_at": created_at,
        })

        stale: list[asyncio.Queue] = []
        for q in self._subscribers:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                stale.append(q)
        for q in stale:
            self._subscribers.remove(q)

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """Yield SSE-formatted events as they arrive."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=256)
        self._subscribers.append(queue)
        try:
            while True:
                data = await queue.get()
                yield f"data: {data}\n\n"
        finally:
            if queue in self._subscribers:
                self._subscribers.remove(queue)
