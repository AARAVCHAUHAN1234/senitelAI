# Business Logic Brain Module

## Overview
Models approved business workflows as state machines, formalizes security invariants, generates test cases, and flags deterministic logic violations.

## Files
- `module.py`: Workflow state machine definitions, invariants repository, execution endpoints, and seed functions.

## Database Tables
- `business_logic_workflows`
- `business_logic_invariants`
- `business_logic_test_results`

## Endpoints
- `GET /api/modules/business_logic_brain/workflows`
- `GET /api/modules/business_logic_brain/results`
- `POST /api/modules/business_logic_brain/run-tests`
- `GET /api/modules/business_logic_brain/export`

## Events Published & Consumed
- Consumes: `finding.detected`
- Publishes: `workflow.invariant.violated`

## How to Enable/Disable
Include or exclude `business_logic_brain` from `ENABLED_MODULES` environment variable (default: `all`).
Removing this module folder does not break the core platform.
