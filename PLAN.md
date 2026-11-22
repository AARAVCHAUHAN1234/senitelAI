# SentinelAI Implementation Plan

## Overview

SentinelAI is an agentic real-time Dynamic Application Security Testing (DAST)
platform for multi-tenant B2B travel platforms. Built for TBO VoyageHack 4.0.

This plan describes what will be built, in what order, and how the pieces fit
together. Every phase is verified before proceeding to the next.

---

## Phase 1: Core Infrastructure

**Goal:** Database, settings, event bus, service registry, app shell.

### Backend

- `backend/app/core/settings.py` -- Pydantic Settings, reads env vars,
  DATABASE_URL (postgres or sqlite fallback), ENABLED_MODULES, GEMINI_API_KEY
  (optional), CORS_ORIGINS, VOYAGESIM_URL.
- `backend/app/core/database.py` -- SQLAlchemy async engine, session factory,
  Base model. Alembic setup.
- `backend/app/core/events.py` -- Typed event bus. Events are persisted to an
  events table and broadcast via SSE. Types: api.discovered, api.changed,
  agent.started, agent.progress, agent.completed, test.started, test.completed,
  finding.detected, finding.verified, finding.resolved, attack_chain.discovered,
  risk_score.updated, demo.scenario.started, demo.scenario.completed.
- `backend/app/core/services.py` -- ServiceRegistry. Modules register named
  services; callers use `ctx.services.call(name, *args, default=...)`.
- `backend/app/core/executor.py` -- Minimal PolicyGate and test executor.
  Allowlist check, rate limit, synthetic-data guard. Safe Attack Sandbox module
  replaces this with the full implementation.
- `backend/app/core/auth.py` -- Simple token auth for demo (not production
  OAuth). Synthetic users with roles.
- `backend/app/core/models.py` -- Shared SQLAlchemy models: Api, Finding,
  Agent, Event, AuditLog.
- `backend/app/core/schemas.py` -- Pydantic schemas for the shared models.
- `backend/app/core/module_loader.py` -- Auto-discovers modules by scanning
  `backend/app/modules/*/module.py`. Reads ENABLED_MODULES env var. Calls
  `register(app, ctx)` on each.
- `backend/app/main.py` -- FastAPI app factory. Mounts core routers, loads
  modules, starts SSE endpoint, CORS, lifespan.

### Frontend

- `frontend/src/core/` -- App shell with sidebar, top bar, layout, routing.
- Design tokens in `frontend/src/core/tokens.ts`.
- Tailwind config referencing tokens.
- Shared components: Button, Card, Table, Badge, Drawer, LoadingState,
  EmptyState, ErrorState.

### Deliverables

- `docker-compose.yml` with backend, frontend, postgres services.
- `Makefile` with targets: up, seed, reset, test.
- Backend starts, health check passes, SSE endpoint connects.
- Frontend shell renders with sidebar navigation.

---

## Phase 2: VoyageSim (Simulated Travel Platform)

**Goal:** A separate FastAPI service that is the target of security testing.

### Service: `backend/voyagesim/`

- Own FastAPI app on port 8001.
- Own SQLite database (voyagesim.db).
- Roles: administrator, manager, agent, sub-agent, read-only.
- Entities with full CRUD:
  - Agencies (3 seeded).
  - Users (30 seeded across agencies and roles).
  - Wallets (per agency, with balance).
  - Flights and fares (supplier net fare + agency markup).
  - Bookings (200 seeded with states: quoted, held, confirmed, cancelled,
    refunded).
  - Payments (linked to bookings).
  - Coupons (single-use per booking).
  - Refunds (linked to bookings).
  - Invoices (per booking).
- Endpoints (40+):
  - `/api/v1/flights/search` -- search flights.
  - `/api/v1/bookings` -- CRUD, hold, confirm, cancel.
  - `/api/v1/bookings/{id}` -- get booking (IDOR vuln flag).
  - `/api/v1/bookings/{id}/price` -- set price (fare tamper vuln flag).
  - `/api/v1/payments` -- process payment.
  - `/api/v1/refunds` -- request refund (duplicate refund vuln flag).
  - `/api/v1/coupons/{code}` -- apply coupon (reuse vuln flag).
  - `/api/v1/users` -- user management.
  - `/api/v1/users/{id}/roles` -- role assignment (priv esc vuln flag).
  - `/api/v1/admin/fares/override` -- admin fare override.
  - `/api/v1/agencies/{id}` -- agency management.
  - `/api/v1/invoices/{id}` -- invoice retrieval.
  - `/api/v1/reports` -- reporting.
  - `/api/v3/bookings` -- current version.
  - `/v1/bookings` -- zombie API (old, still responds).
  - `/internal/debug` -- undocumented debug route.
  - `/beta/export` -- undocumented beta route.
- Planted vulnerabilities, each with a feature flag:
  1. Cross-agency IDOR on booking and invoice IDs.
  2. Fare tampering via client-supplied price.
  3. Duplicate refund.
  4. Coupon reuse.
  5. Sub-agent privilege escalation via role assignment.
  6. Mass assignment on user update.
  7. Skipped payment step before ticket issue.
  8. Negative quantity in booking.
  9. Excessive data exposure in responses.
  10. Missing rate limit.
  11. Old /v1 route still live after /v3.
  12. Undocumented /internal and /beta routes.
- Admin endpoint to flip vulnerability flags to "fixed" for retesting.
- Deterministic seeding with fixed random seed.

---

## Phase 3: Shared Agents and Core Pages

**Goal:** Agent orchestrator, all 13 agents with deterministic checks, and the
core dashboard pages.

### Agents

- `backend/app/agents/orchestrator.py` -- Manages agent lifecycle: start,
  pause, resume, stop. Runs agents in sequence or parallel as configured.
- `backend/app/agents/base.py` -- Base agent class with common interface.
- Individual agents:
  1. Recon Agent -- discovers endpoints from VoyageSim OpenAPI and traffic.
  2. API Inventory Agent -- classifies active/zombie/shadow using traffic log
     window (30-90 days).
  3. Change Detection Agent -- diffs endpoint snapshots.
  4. Attack Planner Agent -- plans tests based on findings and risk.
  5. Authentication Testing Agent -- tests auth requirements.
  6. Access Control Testing Agent -- tests IDOR, tenant isolation.
  7. API Security Testing Agent -- tests input validation, injection.
  8. Verification Agent -- independently reproduces findings.
  9. Risk and Triage Agent -- scores and prioritizes.
  10. Reporting Agent -- generates report data.
  11. Retesting Agent -- retests fixed findings.
  12. Business Logic Brain agent (stub, full impl in module).
  13. Attack Chain Intelligence agent (stub, full impl in module).

### Core Pages

1. **Overview** -- Metric cards, severity distribution (Recharts donut), activity
   timeline (Recharts area), API status breakdown, risk trend, agent activity,
   recent findings.
2. **Live Security Graph** -- React Flow interactive topology. Nodes: app,
   endpoint, database, agency, role, vulnerability. Edges: exposes, accesses,
   owns, has_permission, participates_in, affects, connects, tests. Zoom, pan,
   drag, select, search, filter by node type and severity. Architecture view
   and attack-path view toggle. Nodes added live via SSE.
3. **Agent Control Center** -- Agent cards with status, task, progress, tests,
   findings, logs. Controls: start, pause, resume, stop, run individual, run
   assessment.
4. **API Discovery** -- Inventory table with method, endpoint, classification,
   auth, status, requests, risk, source. Search, filter, sort. OpenAPI import
   and export.
5. **Vulnerability Findings** -- Table with severity, confidence, endpoint,
   tenant, agent, verification status, evidence, impact, remediation. Filters.
   Retest button.
6. **Reports and Evidence** -- PDF and JSON export. Executive summary, metrics,
   evidence graph.
7. **Audit Logs** -- Searchable table with time, action, actor, detail.
8. **Settings** -- Mode toggle, WebSocket status, demo data controls,
   VoyageSim configuration.

### Ingestion

- Upload HAR files -- parsed, endpoints extracted, fed into pipeline.
- Upload traffic logs (CSV/JSON) -- same.
- Upload OpenAPI files -- parsed, endpoints extracted.
- Upload deployment events -- trigger change detection.
- Forms to create agencies, users, bookings manually.

---

## Phase 4: Module 1 -- Business Logic Brain

Folder: `backend/app/modules/business_logic_brain/`

- Workflow definitions as state machines (stored in DB, editable).
- Invariant library with deterministic checks.
- Test generator: invariant produces concrete test cases.
- Three frontend views: linear workflow, swimlane by actor, money-flow.
- Endpoints: workflows CRUD, invariants CRUD, run tests, results.

---

## Phase 5: Module 2 -- Attack Chain Intelligence

Folder: `backend/app/modules/attack_chain_intelligence/`

- Directed graph from findings using networkx.
- Path search over preconditions/postconditions.
- Chokepoint analysis and remediation ranking.
- React Flow graph with layered layout, severity-colored nodes.
- Tabs: Graph View, Attack Paths, Chokepoints, Business Impact.

---

## Phase 6: Module 3 -- Tenant and Role Matrix

Folder: `backend/app/modules/tenant_role_matrix/`

- Policy model: tenants, roles, actions, expected access.
- Observed access by executing synthetic requests.
- Matrix UI with check/cross icons, expected vs actual.
- Cell-level evidence drawer.

---

## Phase 7: Module 4 -- Predictive Security Impact Engine

Folder: `backend/app/modules/predictive_impact/`

- Ingest deployment events, OpenAPI diffs, traffic changes.
- Dependency graph between services and endpoints.
- Priority scoring with workflow criticality weighting.
- CI/CD pipeline visualization strip.

---

## Phase 8: Module 5 -- Security Memory

Folder: `backend/app/modules/security_memory/`

- Finding history, false positives, regression detection.
- ServiceRegistry services: priority_boost, should_skip, pattern_clusters.
- KPI cards, stacked bar chart, remediation timeline.

---

## Phase 9: Module 6 -- Safe Attack Sandbox

Folder: `backend/app/modules/safe_attack_sandbox/`

- Full PolicyGate implementation replacing core stub.
- Target allowlist, rate limiter, concurrency cap.
- Health monitor, destructive-action classifier.
- Approval queue, emergency stop.
- Append-only audit log with hash chain.
- Blueprint-style UI with animated request flow.

---

## Phase 10: Demo Mode, Reports, Polish

- Start Interactive Demo button.
- Six scenarios running real tests against VoyageSim.
- Controls: Start, Pause, Resume, Reset, Run All, Run Individual.
- PDF export.
- Final visual polish and responsive testing.

---

## Phase 11: Testing and Final Report

- pytest suites for core and each module.
- Safety tests for PolicyGate.
- Playwright e2e tests.
- Final checklist verification.
- FINAL_REPORT.md documenting what is implemented, what is rule-based vs
  AI-assisted vs simulated, test results, known limitations.

---

## Architecture Diagram

```
                    +------------------+
                    |   Frontend       |
                    |   React + TS     |
                    |   Port 5173      |
                    +--------+---------+
                             |
                    REST + SSE/WebSocket
                             |
                    +--------+---------+
                    |   Backend API    |
                    |   FastAPI        |
                    |   Port 8000      |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------+--+  +--------+--+  +--------+--+
     | Core      |  | Modules   |  | Agents    |
     | DB, Events|  | 6 modules |  | 13 agents |
     | Services  |  | isolated  |  | orchestr. |
     +--------+--+  +--------+--+  +--------+--+
              |              |              |
              |      +-------+-------+      |
              |      |               |      |
              +------+  VoyageSim    +------+
                     |  Port 8001    |
                     |  Target app   |
                     +---------------+
```

## File Naming Conventions

- Backend: snake_case for files and folders.
- Frontend: camelCase for files, PascalCase for components.
- Database tables: prefixed with module name for module tables.
- Tests: `test_<name>.py` in backend, `<name>.test.tsx` in frontend.
