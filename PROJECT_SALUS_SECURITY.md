# Project Salus Security Hardening

## Phase

Local Phase 2 Foundation

## Security Position

Project Salus is local-first and should not be exposed to the public internet yet.

## Current Controls

- Local dashboard login
- Local token support
- External action firewall
- Agent approval controls
- Audit logs
- Connector registry
- Tool adapter boundary
- Model-provider abstraction
- Snapshot system
- Security headers middleware
- Startup check
- Security check script

## Required Local Environment Settings

SALUS_AUTH_ENABLED=true
SALUS_LOCAL_PASSWORD=change-this-local-password
SALUS_LOCAL_TOKEN=change-this-local-token
SALUS_ALLOW_EXTERNAL_ACTIONS=false
SALUS_ALLOW_MODEL_PROVIDER_EXTERNAL_CALLS=false
SALUS_ALLOW_CONNECTOR_WRITES=false

## Production Warning

Before internet-facing deployment, Salus still needs real user auth, password hashing, CSRF protection, HTTPS, secrets management, RBAC, rate limiting, migration handling, backup testing, and connector security review.
