# Tenant and Role Matrix Module

## Overview
Provides systematic authorization auditing by testing expected vs actual permissions across all tenant boundaries (Agency A, B, C) and security roles (Administrator, Manager, Agent, Sub-agent, Read-only).

## Files
- `module.py`: Authorization policy matrix definitions, live evaluation engine, CSV export, and baseline seeding.

## Database Tables
- `tenant_matrix_cells`

## Endpoints
- `GET /api/modules/tenant_role_matrix/matrix`
- `POST /api/modules/tenant_role_matrix/run-full`
- `GET /api/modules/tenant_role_matrix/export-csv`

## Events Published & Consumed
- Consumes: `test.completed`
- Publishes: `matrix.cell.evaluated`

## How to Enable/Disable
Include or exclude `tenant_role_matrix` from `ENABLED_MODULES` environment variable (default: `all`).
Removing this module folder does not break the core platform.
