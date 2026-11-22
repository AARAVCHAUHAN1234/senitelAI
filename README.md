# SentinelAI — Agentic Real-Time DAST

Autonomous Dynamic Application Security Testing platform engineered specifically for multi-tenant B2B travel platforms (TBO VoyageHack 4.0, TBO Security Hackathon 2026).

SentinelAI continuously discovers API surfaces, maps stateful travel booking workflows, plans safe non-destructive dynamic security tests, validates tenant boundary isolations, verifies multi-step attack chains, and delivers actionable remediation intelligence.

---

## Architecture Overview

```
                      +-----------------------------+
                      |   Frontend (Port 5173)      |
                      |   React 19 + TypeScript     |
                      |   Tailwind CSS v4           |
                      |   @xyflow/react + Recharts  |
                      +--------------+--------------+
                                     |
                       REST API + SSE Stream
                                     |
                      +--------------+--------------+
                      |   Backend API (Port 8000)   |
                      |   FastAPI + Pydantic        |
                      |   SQLAlchemy (SQLite/PG)    |
                      +--------------+--------------+
                                     |
             +-----------------------+-----------------------+
             |                       |                       |
+------------+-----------+  +--------+----------+  +---------+-----------+
| Core & Shared DB       |  | 6 Innovation      |  | 13 Security Agents  |
| - EventBus (SSE)       |  |   Modules         |  | - Recon & Inventory |
| - ServiceRegistry      |  | - BusinessLogic   |  | - Auth & IDOR/Tenant|
| - PolicyGate Executor  |  | - AttackChain     |  | - Chain & Logic     |
| - Audit & Findings     |  | - TenantMatrix    |  | - Verification      |
+------------+-----------+  | - ImpactEngine    |  | - Retest & Triage   |
             |              | - SecurityMemory  |  +---------+-----------+
             |              | - SafeSandbox     |            |
             |              +-------------------+            |
             |                                               |
             +-----------------------+-----------------------+
                                     |
                     Allowlisted Synthetic Target
                                     |
                      +--------------+--------------+
                      |   VoyageSim (Port 8001)     |
                      |   Multi-Tenant Travel B2B   |
                      |   Agencies, Wallets, Fares, |
                      |   Bookings, Refunds, Admin  |
                      +-----------------------------+
```

---

## The Six Innovation Modules

1. **Business Logic Brain** (`backend/app/modules/business_logic_brain`)
   - Models travel workflows as deterministic finite state machines.
   - Enforces 7 strict travel domain invariants (e.g., ticket issue requires confirmed payment; refund amount cannot exceed confirmed payment; currency and fare consistency).
   - Generates and executes state-aware dynamic test cases.

2. **Attack Chain Intelligence** (`backend/app/modules/attack_chain_intelligence`)
   - Uses NetworkX directed graph analysis to discover multi-step privilege escalation and data theft chains across disparate vulnerabilities.
   - Identifies critical chokepoints where a single remediation breaks multiple compound attack vectors.

3. **Tenant & Role Matrix** (`backend/app/modules/tenant_role_matrix`)
   - Dynamically evaluates cross-tenant boundaries across 3 simulated travel agencies and 5 authorization roles (Administrator, Manager, Agent, Sub-Agent, Read-Only).
   - Compares expected vs. actual authorization access, highlighting unauthorized cross-tenant leakage.

4. **Predictive Security Impact Engine** (`backend/app/modules/predictive_impact`)
   - Listens to CI/CD deployment notifications, OpenAPI schema diffs, and traffic shifts.
   - Computes Blast Radius and Risk Delta scores before deployment to production.

5. **Security Memory** (`backend/app/modules/security_memory`)
   - Historical ledger of all validated findings, false positive suppressions, and recurring vulnerability patterns.
   - Prevents duplicate testing loops and detects regressions across code releases.

6. **Safe Attack Sandbox** (`backend/app/modules/safe_attack_sandbox`)
   - Enterprise PolicyGate enforcing strict target allowlists (only `127.0.0.1:8001` VoyageSim is permitted).
   - Rate limiting, concurrency capping, emergency kill switch, and hash-chained cryptographically auditable transaction logs.

---

## VoyageSim Simulated Platform (Port 8001)

VoyageSim is an isolated, synthetic B2B travel backend populated with realistic data:
- 3 Travel Agencies (Apex Global Travel, Horizon Vacations, Skylink Corporate).
- 30 Synthetic Users across 5 Roles.
- Agency Prepaid Wallets and Credit Lines.
- 20 Flights with Dynamic Net Fares and Agency Markups.
- 200 Synthetic Bookings with lifecycle states: `QUOTED`, `HELD`, `CONFIRMED`, `CANCELLED`, `REFUNDED`.
- Toggleable vulnerability flags for controlled, repeatable DAST verification (IDOR, fare tampering, duplicate refunds, privilege escalation, coupon reuse, zombie v1 APIs).

---

## Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) Docker and Docker Compose

### Option 1: Docker Compose (All Services)
```bash
docker-compose up --build
```
Access points:
- Frontend Dashboard: `http://localhost:5173`
- SentinelAI API: `http://localhost:8000/docs`
- VoyageSim Target API: `http://localhost:8001/docs`

---

### Option 2: Local Manual Setup

#### Step 1: Install Dependencies
```bash
# Python dependencies
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

#### Step 2: Seed the Databases
```bash
# Seed VoyageSim target database
python backend/voyagesim/seed.py

# Seed SentinelAI core catalog and agents
python backend/seed.py
```

#### Step 3: Launch Services in Separate Terminals

**Terminal 1 (VoyageSim Target Service - Port 8001):**
```bash
uvicorn backend.voyagesim.app:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 (SentinelAI Core Engine - Port 8000):**
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3 (Frontend Dashboard - Port 5173):**
```bash
cd frontend
npm run dev
```

---

## Testing & Verification

Run the complete backend test suite:
```bash
python -m pytest backend/tests -v
```

Run frontend production bundle validation:
```bash
cd frontend
npm run build
```

---

## Operating Principles & Safety Guarantees

1. **Evidence Honesty:** Findings are strictly labelled with their empirical confidence:
   - `Predicted`: Discovered via static diff or predictive heuristic.
   - `Detected`: Triggered during automated dynamic probe.
   - `Verified`: Independently reproduced via isolated deterministic payload replay.
   - `DEMO / SIMULATED`: Explicitly marked when generated in demo sandbox scenarios.
2. **Target Isolation:** Only explicitly allowlisted local synthetic domains are targetable.
3. **Zero Financial Impact:** Testing executes solely against synthetic wallets and test bookings. Destructive operations are strictly rejected by the PolicyGate.
4. **No External Dependency:** All AI assessment steps include deterministic rule-based fallbacks, ensuring 100% operational capability without an external API key.
