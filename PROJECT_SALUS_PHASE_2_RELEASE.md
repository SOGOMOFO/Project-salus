# Project Salus Local Phase 2 Foundation Release

## Release Name

Project Salus Local Phase 2 Foundation

## Status

Complete pending final git commit and release tag.

## Purpose

This release establishes Project Salus as a local-first command operating system foundation with missions, records, dashboard operations, agent task structure, connector registry, external action firewall, tool adapters, model-provider abstraction, background jobs, dashboard auth, security baseline, startup checks, and architecture contract.

## Core Capabilities Completed

- Mission Control dashboard
- Commander brief workflow
- Daily loop workflow
- Mission tracker
- SITREP records
- AAR records
- Operator queue
- Agent execution registry
- Agent approval controls
- Agent risk dashboard
- Agent runtime worker
- Connector registry
- External action firewall
- Tool adapter interface
- Local file adapter
- Model provider router
- Local model placeholder
- Background job scheduler
- Snapshot system
- Local dashboard auth gate
- Dashboard overview
- Architecture manifest
- System contract
- Startup validation
- Security hardening baseline
- Docker/dev packaging
- Smoke check script

## Current Safety Position

Project Salus is safe for local development use only.

Do not expose it to the public internet yet.

Before external deployment, Salus still needs hardened authentication, password hashing, CSRF protection, HTTPS, role-based access control, rate limiting, formal migrations, secrets management, backup validation, and connector-specific security reviews.

## Current Primary URLs

- /mission-control/login
- /mission-control/v1
- /api/mission-control/dashboard
- /api/mission-control/mvp-readiness
- /api/mission-control/export
- /api/mission-control/security
- /api/mission-control/system-contract
- /api/mission-control/architecture

## Current Phase 2 Definition of Done

- Tests pass
- Startup check passes
- Security check passes
- Dashboard loads behind local auth
- Runtime files are ignored by git
- System contract exists
- Architecture manifest exists
- Security document exists
- Release document exists
- Git tag created

## Next Phase

Phase 3: Real Connectors + Real Agent Execution

Phase 3 should add real integrations carefully, one connector at a time, behind the external action firewall and approval system.

Recommended Phase 3 order:

1. Local file system read-only connector hardening
2. Gmail read-only connector
3. Google Calendar read-only connector
4. Command approval workflow improvements
5. Real model provider configuration
6. Agent execution sandbox
7. Connector write actions only after audit, approval, and rollback controls

## Commander Note

Phase 2 built the operating foundation. Phase 3 should stop adding broad framework and begin adding real controlled capabilities.
