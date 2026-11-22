"""SQLAlchemy ORM models for SentinelAI."""

import datetime

from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime, func
)

from .database import Base


class Api(Base):
    __tablename__ = "apis"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(10), nullable=False, default="GET")
    endpoint = Column(String(512), nullable=False, unique=True)
    category = Column(String(32), nullable=False, default="Active")  # Active/Zombie/Shadow/New
    status_code = Column(Integer, nullable=True)
    auth_required = Column(Boolean, default=False)
    owner = Column(String(128), nullable=True)
    frequency = Column(Integer, default=0)
    risk = Column(Integer, default=0)  # 0-100
    source = Column(String(128), nullable=True)
    last_observed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), nullable=False, unique=True)
    title = Column(String(256), nullable=False)
    severity = Column(String(32), nullable=False, default="Medium")  # Critical/High/Medium/Low/Informational
    confidence = Column(Integer, default=50)  # 0-100
    endpoint = Column(String(512), nullable=True)
    tenant = Column(String(128), nullable=True)
    agent_name = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default="Detected")  # Predicted/Detected/Verified/Fixed/False_Positive
    impact = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    demo_label = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True)
    status = Column(String(32), nullable=False, default="Idle")  # Idle/Running/Completed/Failed/Paused
    task = Column(String(256), nullable=True)
    progress = Column(Integer, default=0)  # 0-100
    tests_completed = Column(Integer, default=0)
    findings_generated = Column(Integer, default=0)
    last_execution = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(64), nullable=False)
    message = Column(String(512), nullable=False)
    detail = Column(Text, nullable=True)  # JSON text
    created_at = Column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(128), nullable=False)
    actor = Column(String(128), nullable=True)
    detail = Column(Text, nullable=True)  # JSON text
    created_at = Column(DateTime, server_default=func.now())
