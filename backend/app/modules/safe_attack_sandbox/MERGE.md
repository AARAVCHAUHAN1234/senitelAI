# Safe Attack Sandbox Module

## Overview
Enforces execution bounds, target allowlisting, method restrictions, rate limits, synthetic-data guards, emergency stop capabilities, and an append-only hash-chained audit log.

## Files
- `module.py`: PolicyGate implementation, allowlist management, emergency stop handler, and cryptographic audit hashing.

## Database Tables
- `safe_sandbox_policy_rules`
- `safe_sandbox_chained_audit`

## Endpoints
- `GET /api/modules/safe_attack_sandbox/policy`
- `POST /api/modules/safe_attack_sandbox/emergency-stop`
- `POST /api/modules/safe_attack_sandbox/emergency-release`
- `GET /api/modules/safe_attack_sandbox/audit-chain`
- `POST /api/modules/safe_attack_sandbox/replay/{id}`

## Events Published & Consumed
- Consumes: `test.started`
- Publishes: `sandbox.policy.blocked`, `sandbox.emergency_stop`

## How to Enable/Disable
Include or exclude `safe_attack_sandbox` from `ENABLED_MODULES` environment variable (default: `all`).
Removing this module folder does not break the core platform.
