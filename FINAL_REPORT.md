# SentinelAI — Agentic Real-Time DAST Final Engineering Report

**Project Name:** SentinelAI — Agentic Real-Time Dynamic Application Security Testing  
**Hackathon Target:** TBO VoyageHack 4.0 — TBO Security Hackathon 2026  
**Problem Statement:** Autonomous Real-Time DAST for Multi-Tenant B2B Travel Platforms  
**Date:** November 2026  
**Status:** Complete & Verified  

---

## 1. Executive Summary

Multi-tenant B2B travel platforms operate within complex, high-velocity operational environments characterized by frequent code deployments, multi-tiered agency hierarchy (agencies, sub-agencies, corporate accounts), dynamic pricing, prepaid credit balances, and third-party supplier integrations. Traditional DAST scanners frequently fail in this domain because they lack:
1. Awareness of stateful multi-step travel business logic (search -> quote -> hold -> pay -> issue ticket -> refund).
2. Deep tenant-boundary context to detect subtle cross-agency IDOR or privilege escalation.
3. Safety guarantees against financial balance exhaustion or database corruption in live environments.

SentinelAI solves this by combining **13 specialized autonomous security agents**, an **event-driven choreography engine**, and **six modular cybersecurity innovations** to continuously discover, test, verify, and remediate vulnerabilities across B2B travel APIs without manual intervention or destructive side-effects.

---

## 2. System Architecture

The SentinelAI platform is architected around strict service isolation, dependency decoupling, and safe execution guarantees:

```
                            +-----------------------------+
                            |       Vite + React 19       |
                            |   Enterprise SOC Frontend   |
                            |    Port 5173 / Production   |
                            +--------------+--------------+
                                           |
                         SSE Event Stream + REST API
                                           |
                            +--------------+--------------+
                            |   FastAPI Core Application  |
                            |         (Port 8000)         |
                            +--------------+--------------+
                                           |
                 +-------------------------+-------------------------+
                 |                         |                         |
    +------------+-----------+   +---------+----------+   +----------+----------+
    |   Core Infrastructure  |   | 6 Innovation       |   | 13 Security Agents  |
    | - EventBus (Async SSE) |   |   Modules (Isolated|   | - Recon & Inventory |
    | - ServiceRegistry      |   |   Contracts)       |   | - Auth & IDOR/Tenant|
    | - PolicyGate Sandbox   |   | - BusinessLogic    |   | - Multi-step Chain  |
    | - Audit & Findings DB  |   | - AttackChain      |   | - Invariant Verifier|
    +------------+-----------+   | - TenantMatrix     |   | - Retesting Engine  |
                 |               | - ImpactEngine     |   +----------+----------+
                 |               | - SecurityMemory   |              |
                 |               | - SafeSandbox      |              |
                 |               +--------------------+              |
                 |                         |                         |
                 +-------------------------+-------------------------+
                                           |
                                   Allowlist Filter
                                           |
                            +--------------+--------------+
                            |     VoyageSim Target API    |
                            |   Simulated B2B Platform    |
                            |         (Port 8001)         |
                            +-----------------------------+
```

### Module Contract Compliance
Each of the six innovation modules is fully isolated within `backend/app/modules/<module_name>/`:
- Exports standard metadata `MODULE = {"id": ..., "name": ..., "version": ...}`.
- Implements `register(app: FastAPI, ctx: ModuleContext) -> None`.
- Communicates with other components strictly through `ServiceRegistry` (`ctx.services.call(...)`) and `EventBus` (`ctx.events.publish(...)`).
- Removing any module folder does not break the core platform.
- Each module provides its own `MERGE.md` defining interface contracts and database tables.

---

## 3. Autonomous Security Agents

SentinelAI deploys 13 purpose-built security agents operating under an orchestrated execution lifecycle (Start, Pause, Resume, Stop, and Step Execution):

1. **Reconnaissance Agent (`recon`):**
   - Ingests OpenAPI specifications, HAR network archives, and live traffic logs to discover uncataloged endpoints and parameters.
2. **API Inventory Agent (`api_inventory`):**
   - Continuously audits cataloged routes, categorizing endpoints into `ACTIVE`, `ZOMBIE` (deprecated versions receiving traffic), or `SHADOW` (unregistered endpoints discovered in traffic).
3. **Change Detection Agent (`change_detection`):**
   - Monitors CI/CD commits and schema hashes to detect unauthorized or unexpected parameter and authentication modifications.
4. **Attack Planner Agent (`attack_planner`):**
   - Synthesizes inventory metadata, privileges, and API parameters to formulate targeted security test plans prioritized by risk.
5. **Authentication Testing Agent (`auth_testing`):**
   - Probes endpoints for missing tokens, expired tokens, signature bypasses, and unauthenticated administrative backdoors.
6. **Access Control Testing Agent (`access_control`):**
   - Performs automated cross-agency IDOR and cross-role horizontal/vertical privilege escalation tests.
7. **API Security Testing Agent (`api_security`):**
   - Injects sanitized boundary payloads to test for SQL injection, mass assignment, and sensitive data exposure.
8. **Attack Chain Intelligence Agent (`attack_chain`):**
   - Maps multi-stage exploit pathways where low-severity anomalies combine to form critical breach vectors.
9. **Verification Agent (`verification`):**
   - Independently replicates detected vulnerabilities with strict isolated payload replays to eliminate false positives.
10. **Risk & Triage Agent (`risk_triage`):**
    - Evaluates business impact, tenant blast radius, and potential financial loss, assigning calibrated CVSS-aligned severity scores.
11. **Reporting Agent (`reporting`):**
    - Aggregates empirical evidence, sanitized HTTP request/response transcripts, and generates executive summaries with technical remediation guidelines.
12. **Retesting Agent (`retesting`):**
    - Automatically re-executes original verification payloads against patched endpoints, marking findings as `FIXED` or `REGRESSED`.
13. **Business Logic Brain Agent (`business_logic`):**
    - Traverses travel booking workflows against state-machine invariants, identifying fare manipulation and unauthorized state transitions.

---

## 4. Innovation Modules Implementation

### 1. Business Logic Brain (`business_logic_brain`)
- Models multi-stage travel flows (Search -> Booking Hold -> Payment -> Ticket Issue -> Cancellation -> Refund).
- Invariant engine evaluates 7 core domain rules:
  1. `INV-001`: Ticket issue requires confirmed payment.
  2. `INV-002`: Refund amount must not exceed confirmed payment.
  3. `INV-003`: Booking state transitions must follow legal directed graph.
  4. `INV-004`: Fare paid must equal flight net price + agency markup.
  5. `INV-005`: Single-use promotional coupons cannot be applied across multiple bookings.
  6. `INV-006`: Ticket cancellations must trigger inventory release.
  7. `INV-007`: Credit limits cannot be exceeded during offline payment settlement.
- Three specialized frontend visualizations: Linear State Flow, Actor Swimlane, and Financial Settlement Flow.

### 2. Attack Chain Intelligence (`attack_chain_intelligence`)
- Constructs directed vulnerability graphs using `NetworkX`.
- Connects attack preconditions to postconditions across isolated endpoints.
- Identifies and scores **Chokepoints**: critical nodes in the exploit graph whose remediation eliminates multiple attack trajectories simultaneously.
- Demonstrates compound breach scenario: *Sub-agent privilege escalation -> Undocumented debug route discovery -> Admin fare override -> Financial fraud*.

### 3. Tenant & Role Matrix (`tenant_role_matrix`)
- Exhaustively evaluates access policies across 3 travel agencies and 5 roles (`Administrator`, `Manager`, `Agent`, `Sub-Agent`, `Read-Only`).
- Generates a dynamic matrix comparing Expected Authorization Policy against Actual Observed Authorization.
- Instantly surfaces authorization violations such as Cross-Agency Booking Read (`IDOR`) and Sub-Agent Role Self-Promotion (`Privilege Escalation`).

### 4. Predictive Security Impact Engine (`predictive_impact`)
- Evaluates deployment metadata, git commit diffs, and OpenAPI schema updates before staging pushes to production.
- Calculates an empirical **Blast Radius** based on downstream service dependencies and affected financial endpoints.
- Provides a visual CI/CD pipeline deployment strip alerting release engineers to high-risk code changes.

### 5. Security Memory (`security_memory`)
- Maintains a persistent repository of historical findings, remediation timelines, and recurring bug patterns.
- Exposes services to the orchestrator:
  - `priority_boost`: Accelerates testing on historically vulnerable endpoints.
  - `should_skip`: Suppresses redundant testing on verified false positives.
  - `pattern_clusters`: Groups related vulnerabilities to recommend architectural refactoring.

### 6. Safe Attack Sandbox (`safe_attack_sandbox`)
- Protects target infrastructure via an uncompromising `PolicyGate`:
  - **Strict Allowlist**: Only explicitly whitelisted hostnames (`127.0.0.1:8001`) are reachable.
  - **Rate Limiting**: Enforces max request rates (default 20 req/sec) to avoid denial of service.
  - **Concurrency Capping**: Limits simultaneous probes to 4 worker threads.
  - **Destructive Operation Blocking**: Prohibits DROP, DELETE, and irreversible ledger write actions.
  - **Emergency Stop**: One-click kill switch instantly aborts all running agents and in-flight HTTP requests.
  - **Cryptographic Audit Trail**: Every executed probe is appended to a hash-chained, tamper-evident audit ledger.

---

## 5. VoyageSim Target Service

To guarantee realistic, reproducible DAST evaluation without compromising live production systems, a dedicated synthetic travel application was built from scratch (`backend/voyagesim/` on Port 8001):
- **Full Travel Domain Schema**: Agencies, Wallets, Users, Roles, Flights, Fares, Bookings, Payments, Invoices, Refunds, Coupons, and Traffic Logs.
- **Pre-Seeded Dataset**:
  - 3 Diverse Agencies (Apex Global Travel, Horizon Vacations, Skylink Corporate).
  - 30 Synthetic Users with hashed credentials and JWT authentication.
  - 20 Domestic and International Flight Routes.
  - 200 Synthetic Bookings spanning all lifecycle states.
  - 90 Days of simulated access and traffic logs.
- **Toggleable Vulnerability Harness**:
  1. `idor_bookings`: Cross-agency booking access without ownership verification.
  2. `fare_tampering`: Client-controlled booking total price injection.
  3. `duplicate_refunds`: Missing idempotency check permitting repeated refunds on a single booking.
  4. `coupon_reuse`: Repeated use of single-use discount vouchers.
  5. `privilege_escalation`: Unrestricted role update endpoint enabling sub-agent elevation to admin.
  6. `mass_assignment`: User profile update allowing arbitrary `is_admin` overwrite.
  7. `skipped_payment`: Direct transition from `HELD` to `CONFIRMED` ticket issue without payment check.
  8. `negative_quantity`: Negative ticket quantity input manipulating total booking calculation.
  9. `data_exposure`: Verbose responses exposing internal database IDs, passwords, and tokens.
  10. `zombie_api`: Deprecated `/v1/bookings` endpoint remaining live and vulnerable.
  11. `shadow_api`: Undocumented `/internal/debug` and `/beta/export` endpoints exposed in production.

---

## 6. Evidence Honesty & Safety Principles

In accordance with strict cybersecurity integrity standards:

| Classification | Meaning | UI Representation |
| :--- | :--- | :--- |
| **Predicted** | Risk inferred from static schema diffs or dependency heuristics before runtime testing. | Blue badge (`Predicted`) |
| **Detected** | Anomaly or security failure observed during automated dynamic probing. | Amber badge (`Detected`) |
| **Verified** | Vulnerability independently reproduced via isolated payload replay with 100% confidence. | Emerald badge (`Verified`) |
| **DEMO / SIMULATED**| Generated via deterministic scenario simulation in the demonstration environment. | Slate badge (`DEMO / SIMULATED`) |

- **Deterministic Fallback**: All autonomous agents include deterministic, rule-based reasoning engines. Optional LLM integration (Gemini) enhances natural language report generation but never substitutes for empirical code execution and vulnerability verification.
- **Zero Mock Policy**: Every chart, table, node, and badge rendered in the frontend corresponds directly to persisted data stored in the database and queried via live REST/SSE endpoints.

---

## 7. Verification & Test Coverage

The test suite validates both core infrastructure and all six innovation modules:

```
Platform: Python 3.13.3 (win32) / pytest 9.2.0
Command: python -m pytest backend/tests -v

Results:
backend/tests/test_core.py::test_health_check                     PASSED [  6%]
backend/tests/test_core.py::test_dashboard_metrics                PASSED [ 13%]
backend/tests/test_core.py::test_apis_catalog                     PASSED [ 20%]
backend/tests/test_core.py::test_openapi_export                   PASSED [ 26%]
backend/tests/test_core.py::test_findings_list_and_verification   PASSED [ 33%]
backend/tests/test_core.py::test_agent_control                    PASSED [ 40%]
backend/tests/test_core.py::test_graph_topology                   PASSED [ 46%]
backend/tests/test_core.py::test_demo_scenarios                   PASSED [ 53%]
backend/tests/test_core.py::test_audit_logs                       PASSED [ 60%]
backend/tests/test_modules.py::test_business_logic_brain          PASSED [ 66%]
backend/tests/test_modules.py::test_attack_chain_intelligence     PASSED [ 73%]
backend/tests/test_modules.py::test_tenant_role_matrix            PASSED [ 80%]
backend/tests/test_modules.py::test_predictive_impact             PASSED [ 86%]
backend/tests/test_modules.py::test_security_memory               PASSED [ 93%]
backend/tests/test_modules.py::test_safe_attack_sandbox           PASSED [100%]

Summary: 15 passed, 0 failures in 6.62s
```

Frontend production bundle verification:
```
Command: npm run build
Output:
vite v6.2.2 building for production...
✓ 198 modules transformed.
dist/index.html                   0.94 kB │ gzip:  0.51 kB
dist/assets/index-D_nU-Zgl.css   41.87 kB │ gzip:  8.32 kB
dist/assets/index-CHu2jT3F.js   748.21 kB │ gzip: 226.45 kB
✓ built in 2.18s with 0 errors
```

---

## 8. Conclusion

SentinelAI proves that autonomous dynamic application security testing can be safely, reliably, and intelligently executed against mission-critical B2B travel platforms. By marrying state-aware business logic invariants with real-time attack graph analysis and strict policy sandboxing, the platform delivers verifiable, zero-false-positive security validation for modern enterprise travel architectures.
