# Predictive Security Impact Engine Module

## Overview
Predicts which endpoints and travel workflows are impacted by code changes, schema drifts, and deployment events, prioritizing tests before they run.

## Files
- `module.py`: Change tracking, service dependency modeling, priority score computation, and CI/CD stage mapping.

## Database Tables
- `predictive_impact_changes`

## Endpoints
- `GET /api/modules/predictive_impact/changes`
- `GET /api/modules/predictive_impact/dependency-graph`
- `POST /api/modules/predictive_impact/simulate-deployment`

## Events Published & Consumed
- Consumes: `api.changed`
- Publishes: `impact.prediction.created`

## How to Enable/Disable
Include or exclude `predictive_impact` from `ENABLED_MODULES` environment variable (default: `all`).
Removing this module folder does not break the core platform.
