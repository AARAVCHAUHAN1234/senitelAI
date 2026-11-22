"""Pydantic schemas for request and response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Api ---

class ApiBase(BaseModel):
    method: str = "GET"
    endpoint: str
    category: str = "Active"
    status_code: Optional[int] = None
    auth_required: bool = False
    owner: Optional[str] = None
    frequency: int = 0
    risk: int = Field(0, ge=0, le=100)
    source: Optional[str] = None
    last_observed: Optional[datetime] = None


class ApiCreate(ApiBase):
    pass


class ApiUpdate(BaseModel):
    method: Optional[str] = None
    endpoint: Optional[str] = None
    category: Optional[str] = None
    status_code: Optional[int] = None
    auth_required: Optional[bool] = None
    owner: Optional[str] = None
    frequency: Optional[int] = None
    risk: Optional[int] = None
    source: Optional[str] = None
    last_observed: Optional[datetime] = None


class ApiOut(ApiBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Finding ---

class FindingBase(BaseModel):
    code: str
    title: str
    severity: str = "Medium"
    confidence: int = Field(50, ge=0, le=100)
    endpoint: Optional[str] = None
    tenant: Optional[str] = None
    agent_name: Optional[str] = None
    status: str = "Detected"
    impact: Optional[str] = None
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    demo_label: Optional[str] = None


class FindingCreate(FindingBase):
    pass


class FindingUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[int] = None
    endpoint: Optional[str] = None
    tenant: Optional[str] = None
    agent_name: Optional[str] = None
    status: Optional[str] = None
    impact: Optional[str] = None
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    demo_label: Optional[str] = None


class FindingOut(FindingBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Agent ---

class AgentBase(BaseModel):
    name: str
    status: str = "Idle"
    task: Optional[str] = None
    progress: int = Field(0, ge=0, le=100)
    tests_completed: int = 0
    findings_generated: int = 0
    last_execution: Optional[datetime] = None


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    status: Optional[str] = None
    task: Optional[str] = None
    progress: Optional[int] = None
    tests_completed: Optional[int] = None
    findings_generated: Optional[int] = None
    last_execution: Optional[datetime] = None


class AgentOut(AgentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Event ---

class EventBase(BaseModel):
    kind: str
    message: str
    detail: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventOut(EventBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- AuditLog ---

class AuditLogBase(BaseModel):
    action: str
    actor: Optional[str] = None
    detail: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogOut(AuditLogBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Dashboard ---

class SeverityBreakdown(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    informational: int = 0


class DashboardMetrics(BaseModel):
    total_apis: int = 0
    total_findings: int = 0
    total_agents: int = 0
    active_agents: int = 0
    total_events: int = 0
    severity: SeverityBreakdown = SeverityBreakdown()
    api_categories: dict = {}
    recent_findings: list[FindingOut] = []
    recent_events: list[EventOut] = []
    agents: list[AgentOut] = []
    apis: list[ApiOut] = []
