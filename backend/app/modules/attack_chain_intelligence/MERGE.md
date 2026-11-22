# Attack Chain Intelligence Module

## Overview
Correlates individual vulnerability findings into multi-hop directed graphs using NetworkX. Analyzes exploitation paths, calculates chokepoint remediation priorities, and assesses combined business impact.

## Files
- `module.py`: Directed graph construction, shortest path traversal, chokepoint analysis, and chain persistence.

## Database Tables
- `attack_chain_chains`

## Endpoints
- `GET /api/modules/attack_chain_intelligence/chains`
- `GET /api/modules/attack_chain_intelligence/paths`
- `GET /api/modules/attack_chain_intelligence/chokepoints`
- `POST /api/modules/attack_chain_intelligence/reverify`

## Events Published & Consumed
- Consumes: `finding.verified`
- Publishes: `attack_chain.discovered`

## How to Enable/Disable
Include or exclude `attack_chain_intelligence` from `ENABLED_MODULES` environment variable (default: `all`).
Removing this module folder does not break the core platform.
