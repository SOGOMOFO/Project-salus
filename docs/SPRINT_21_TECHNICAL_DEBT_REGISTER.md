# Sprint 21 Technical Debt Register

## Current Local MVP Status
Project Salus has reached local MVP status.

## Primary Technical Debt

### 1. backend/main.py is too large
Most sprint-built routes and helpers currently live in backend/main.py.

Risk:
- Harder to debug
- Harder to test by module
- Higher chance of route conflicts
- More difficult future database/auth/cloud migration

Recommended action:
Split route groups into dedicated modules.

---

### 2. JSON persistence is spread across sprint helper functions
Persistence exists, but helper logic is not yet centralized.

Risk:
- Future bugs during database migration
- Inconsistent save behavior
- Harder backup/export logic

Recommended action:
Create a dedicated persistence layer before moving to database.

---

### 3. UI pages are inline HTML strings
This is acceptable for the local MVP but not ideal long-term.

Risk:
- Harder UI maintenance
- Repeated styles
- No shared layout system

Recommended action:
Create shared templates or static frontend once backend is modular.

---

### 4. No authentication
Local-only mode is acceptable for Kyle's machine, but not for cloud or multi-user use.

Risk:
- Unsafe if exposed outside localhost
- No user separation
- No permissions

Recommended action:
Add authentication before cloud deployment or external access.

---

### 5. No formal connector layer yet
Connectors are a core Project Salus requirement, but not implemented in the local MVP.

Risk:
- Future integrations may be added inconsistently
- Permission model could become messy

Recommended action:
Design connector interface after core route refactor.
