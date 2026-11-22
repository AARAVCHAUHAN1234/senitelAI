"""Base agent abstraction for SentinelAI autonomous security agents."""

from typing import Any, Dict, Optional
from datetime import datetime


class BaseAgent:
    """Base class for autonomous security agents."""

    name: str = "Base Agent"
    description: str = "Base security agent"

    def __init__(self, ctx: Any = None):
        self.ctx = ctx
        self.status = "Idle"
        self.current_task = "Standing by"
        self.progress = 0

    async def run(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the agent's autonomous task. Must be implemented by subclasses."""
        raise NotImplementedError

    def report_progress(self, progress: int, task: str):
        """Update local state and emit progress event."""
        self.progress = min(100, max(0, progress))
        self.current_task = task
        if self.ctx and hasattr(self.ctx, "event_bus"):
            self.ctx.event_bus.emit(
                kind="agent.progress",
                message=f"{self.name}: {task} ({self.progress}%)",
                detail={"agent": self.name, "progress": self.progress, "task": task}
            )
