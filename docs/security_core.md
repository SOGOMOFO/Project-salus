# Security Core v1

Project Salus Security Core v1 introduces a zero-trust security foundation while preserving passphrase compatibility.

## Mission
Move from flat passphrase-only protection to structured authentication and authorization.

## Core Features

### 1. Authentication Foundation
- Passphrase compatibility remains active for all existing clients.
- Token-based auth foundation is supported through `x-salus-token`.
- Caller role can be supplied using `x-salus-role`.

### 2. Role-Based Access Control
Supported roles:
- commander
- family
- agent
- readonly

### 3. Audit Logging
All protected actions are audited with:
- timestamp
- action
- allowed/denied outcome
- principal
- role
- lockdown state
- optional plugin identifier

### 4. Emergency Lockdown
- Emergency lockdown can be toggled.
- When enabled, only `commander` actions are allowed.

### 5. Plugin Permission Model
- Plugin actions are authorized with role checks.
- Enable/disable defaults are restricted to elevated roles.
- Validation and read actions are broadly readable unless overridden.

## Endpoints

### GET /security/status
Returns:
- security operating mode
- zero-trust enabled flag
- role and auth model support
- lockdown status
- audit counters
- plugin permission override summary

### GET /security/audit
Returns latest audited protected actions.

### POST /security/lockdown
Enables emergency lockdown (commander only).

### POST /security/unlock
Disables emergency lockdown (commander only).

## Compatibility Notes
- Existing passphrase-based flows continue to work.
- Security Core v1 adds structure without requiring immediate client migration.
