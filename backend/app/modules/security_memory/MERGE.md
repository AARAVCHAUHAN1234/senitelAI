# Security Memory Module

## Overview
Retains organizational security memory: historical findings, fix timelines, recurring vulnerability pattern clusters, and regression detection when remediated vulnerabilities re-occur.

## Files
- `module.py`: Historical memory tracking, SLA metrics, regression detection, and `security_memory.priority_boost` service registration.

## Database Tables
- `security_memory_records`

## Endpoints
- `GET /api/modules/security_memory/kpis`
- `GET /api/modules/security_memory/history`
- `GET /api/modules/security_memory/regressions`
- `GET /api/modules/security_memory/remediation-trends`

## Services Registered
- `security_memory.priority_boost(endpoint: str) -> int`: Returns testing priority boost based on regression history.

## Events Published & Consumed
- Consumes: `finding.resolved`, `finding.verified`
- Publishes: `memory.regression.detected`

## How to Enable/Disable
Include or exclude `security_memory` from `ENABLED_MODULES` environment variable (default: `all`).
Removing this module folder does not break the core platform.
