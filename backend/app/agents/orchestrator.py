"""Agent orchestrator for coordinating autonomous DAST workflows."""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from .base import BaseAgent
from .security_agents import (
    ReconAgent, ApiInventoryAgent, ChangeDetectionAgent,
    AttackPlannerAgent, AuthenticationTestingAgent, AccessControlTestingAgent,
    ApiSecurityTestingAgent, AttackChainIntelligenceAgent, VerificationAgent,
    RiskTriageAgent, ReportingAgent, RetestingAgent, BusinessLogicBrainAgent
)
from ..core.models import Agent as AgentModel


class AgentOrchestrator:
    """Coordinates autonomous security agents and manages assessment lifecycles."""

    def __init__(self, ctx):
        self.ctx = ctx
        self._paused = False
        self._stopped = False
        self._running_task: Optional[asyncio.Task] = None

        # Instantiate all 13 security agents
        self.agents: Dict[str, BaseAgent] = {
            "Recon Agent": ReconAgent(ctx),
            "API Inventory Agent": ApiInventoryAgent(ctx),
            "Change Detection Agent": ChangeDetectionAgent(ctx),
            "Attack Planner Agent": AttackPlannerAgent(ctx),
            "Authentication Testing Agent": AuthenticationTestingAgent(ctx),
            "Access Control Testing Agent": AccessControlTestingAgent(ctx),
            "API Security Testing Agent": ApiSecurityTestingAgent(ctx),
            "Attack Chain Intelligence Agent": AttackChainIntelligenceAgent(ctx),
            "Verification Agent": VerificationAgent(ctx),
            "Risk & Triage Agent": RiskTriageAgent(ctx),
            "Reporting Agent": ReportingAgent(ctx),
            "Retesting Agent": RetestingAgent(ctx),
            "Business Logic Brain": BusinessLogicBrainAgent(ctx),
        }

    def get_agent_names(self) -> List[str]:
        return list(self.agents.keys())

    async def run_single_agent(self, name: str, params: Optional[dict] = None) -> dict:
        """Run an individual agent by name."""
        agent = self.agents.get(name)
        if not agent:
            raise ValueError(f"Agent '{name}' not found")

        db: Session = self.ctx.session_factory()
        try:
            db_agent = db.query(AgentModel).filter(AgentModel.name == name).first()
            if db_agent:
                db_agent.status = "Running"
                db_agent.task = f"Executing {name} workflow"
                db_agent.progress = 10
                db_agent.last_execution = datetime.utcnow()
                db.commit()

            if hasattr(self.ctx, "event_bus"):
                self.ctx.event_bus.emit("agent.started", f"{name} started", {"agent": name})

            result = await agent.run(params)

            if db_agent:
                db_agent = db.query(AgentModel).filter(AgentModel.name == name).first()
                if db_agent:
                    db_agent.status = "Completed"
                    db_agent.task = "Task completed successfully"
                    db_agent.progress = 100
                    db_agent.tests_completed += 1
                    db.commit()

            if hasattr(self.ctx, "event_bus"):
                self.ctx.event_bus.emit("agent.completed", f"{name} completed", {"agent": name, "result": result})

            return result
        except Exception as e:
            if db_agent:
                db_agent = db.query(AgentModel).filter(AgentModel.name == name).first()
                if db_agent:
                    db_agent.status = "Failed"
                    db_agent.task = f"Error: {str(e)}"
                    db.commit()
            if hasattr(self.ctx, "event_bus"):
                self.ctx.event_bus.emit("agent.failed", f"{name} failed: {str(e)}", {"agent": name, "error": str(e)})
            raise
        finally:
            db.close()

    async def _scan_pipeline(self):
        """Execute complete assessment pipeline in sequence."""
        sequence = [
            "Recon Agent",
            "API Inventory Agent",
            "Change Detection Agent",
            "Attack Planner Agent",
            "Access Control Testing Agent",
            "Api Security Testing Agent",
            "Authentication Testing Agent",
            "Business Logic Brain",
            "Verification Agent",
            "Attack Chain Intelligence Agent",
            "Risk & Triage Agent",
            "Reporting Agent",
        ]

        if hasattr(self.ctx, "event_bus"):
            self.ctx.event_bus.emit("scan.started", "Full security assessment started", {"pipeline": sequence})

        for agent_name in sequence:
            if self._stopped:
                break
            while self._paused and not self._stopped:
                await asyncio.sleep(0.5)

            try:
                await self.run_single_agent(agent_name)
            except Exception:
                pass
            await asyncio.sleep(0.2)

        if hasattr(self.ctx, "event_bus"):
            self.ctx.event_bus.emit("scan.completed", "Full security assessment completed", {})

    def start_assessment(self):
        """Start full security assessment."""
        self._stopped = False
        self._paused = False
        if self._running_task and not self._running_task.done():
            return {"status": "already_running"}
        self._running_task = asyncio.create_task(self._scan_pipeline())
        return {"status": "started"}

    def pause(self):
        self._paused = True
        if hasattr(self.ctx, "event_bus"):
            self.ctx.event_bus.emit("scan.paused", "Security assessment paused", {})
        return {"status": "paused"}

    def resume(self):
        self._paused = False
        if hasattr(self.ctx, "event_bus"):
            self.ctx.event_bus.emit("scan.resumed", "Security assessment resumed", {})
        return {"status": "resumed"}

    def stop(self):
        self._stopped = True
        self._paused = False
        if self._running_task and not self._running_task.done():
            self._running_task.cancel()
        if hasattr(self.ctx, "event_bus"):
            self.ctx.event_bus.emit("scan.stopped", "Security assessment stopped", {})
        return {"status": "stopped"}
